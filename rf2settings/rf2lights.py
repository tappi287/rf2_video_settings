import logging
from threading import Timer

import gevent

from .directInputKeySend import PressReleaseKey
from .rf2connect import RfactorConnect
from .rf2sharedmem import sharedMemoryAPI


def update_status(message):
    logging.info(message)


def set_timer(ms, callback, _args=None):
    if ms <= 0:
        return

    t = Timer(ms / 1000, callback, args=_args)
    t.start()


def timer(ms, callback, args):
    gevent.sleep(ms / 1000)
    callback(*args)


def __set_timer(ms, callback, _args=None) -> None:
    if ms > 0:
        timer(ms, callback, _args)
    else:
        pass


class RfactorHeadlight:
    def __init__(self, headlight_toggle_dik: str = None, rf2_auto_headlights_enabled: bool = False):
        self.headlight_state = None
        self.headlight_toggle_dik = headlight_toggle_dik or 'DIK_H'
        self.rf2_auto_headlights_enabled = False
        info = RfactorConnect.shared_memory_obj
        self._flashing = False
        self._count = 0
        self.timer = (0, 0)  # On time, off time
        self._timestamp = 0
        self._in_pit_lane = False
        self.escape_pressed = False
        self._fake_escape_pressed = False
        self._car_has_headlights = True  # Until we find otherwise
        self.tested_car_has_headlights = False
        self._headlights_state_on_pit_entry = False  # Initially

    def set_toggle_key(self, dik: str):
        self.headlight_toggle_dik = dik

    def count_down(self) -> bool:
        """ Stopping callback function
            Returns True is count is expired. """
        self._count -= 1
        return self._count <= 0

    def four_flashes(self, flash_duration, flash_count) -> None:
        """ Flash four times (e.g. for overtaking) """
        self._count = flash_count * 2
        self.start_flashing(self.count_down, flash_duration)

    def pit_limiter_flashes(self, pit_flash_duration) -> None:
        """ Flash while the pit limiter is on """
        self.start_flashing(self.__pit_limiter_is_off, pit_flash_duration)

    def check_pit_limiter(self, pit_flash_duration) -> None:
        """ Is the pit limiter on? """
        if self.info.isOnTrack():
            if not self.__pit_limiter_is_off():
                self.pit_limiter_flashes(pit_flash_duration)

    def pit_lane_flashes(self, pit_flash_duration) -> None:
        """ Flash while in the pit lane """
        self.start_flashing(self.__not_in_pit_lane, pit_flash_duration)

    def check_pit_lane(self, pit_flash_duration) -> None:
        """ Has the car entered the pit lane? """
        if self.info.isOnTrack():
            if not self.__not_in_pit_lane():
                if not self._in_pit_lane:
                    update_status('Entered pit lane')
                    self._headlights_state_on_pit_entry = self.are_headlights_on()
                    self.pit_lane_flashes(pit_flash_duration)
                    self._in_pit_lane = True
            else:
                if self._in_pit_lane:
                    update_status('Left pit lane')
                    self._in_pit_lane = False
        else:
            self._in_pit_lane = False

    def on(self) -> None:
        """ Turn them on regardless """
        # status_poker_fn('on')
        if not self.are_headlights_on():
            self.toggle()

    def off(self) -> None:
        """ Turn them off regardless """
        # status_poker_fn('off')
        if self.are_headlights_on():
            self.toggle()

    def automatic_headlights(self, on_automatically) -> None:
        """
        # Headlights on when:
                    # 0     Driver turns them on
                    # 1     At least one other driver has them on
                    # 2     More than one other driver has them on
                    # 3     At least half of the other drivers have them on
                    # 4     All the other drivers have them on
        """
        _on = False
        if self._flashing:
            return  # Don't turn headlights on when flashing

        if on_automatically and not self.are_headlights_on():
            _num_drivers = self.info.Rf2Scor.mScoringInfo.mNumVehicles
            _num_drivers_with_lights = 0
            for _driver in range(_num_drivers):
                if self.info.Rf2Tele.mVehicles[_driver].mHeadlights:
                    _num_drivers_with_lights += 1
            # Total includes the player so
            _num_drivers -= 1

            if on_automatically == 1 and _num_drivers_with_lights:
                _on = True
                update_status('At least one other driver has headlights on')
            if on_automatically == 2 and _num_drivers_with_lights > 1:
                _on = True
                update_status('More than one other driver has headlights on')
            if on_automatically == 3 and \
                    _num_drivers_with_lights >= (_num_drivers / 2):
                _on = True
                update_status(
                    'At least half of the other drivers have headlights on')
            if on_automatically == 4 and \
                    _num_drivers_with_lights >= _num_drivers:
                _on = True
                update_status('All the other drivers have headlights on')
            if _on:
                self.on()

    def car_has_headlights(self) -> bool:
        """ Need to retest every time the track is loaded """
        if not self.tested_car_has_headlights:
            _save = self.are_headlights_on()
            self.toggle(testing_car_has_headlights=True)
            if sharedMemoryAPI.Cbytestring2Python(self.info.Rf2Ext.mLastHistoryMessage) == \
                    'Headlights: N/A':
                self._car_has_headlights = False

            try:
                _car = self.info.vehicleName()
            except AttributeError:
                _car = 'Unknown'

            if self._car_has_headlights:
                update_status(_car + " has headlights")
            else:
                update_status(_car + " has no headlights")
            self.tested_car_has_headlights = True
        return self._car_has_headlights

    def car_is_moving(self) -> bool:
        # return self._info.playersVehicleTelemetry().mLocalVel.x > 1
        return self.info.playersVehicleTelemetry().mClutchRPM > 10

    def esc_check(self) -> bool:
        """
        If mElapsedTime is not changing then player has pressed Esc
        or rFactor does not have focus
        """
        if self._fake_escape_pressed:
            return False
        if not self.info.isOnTrack() or self._timestamp < self.info.playersVehicleTelemetry().mElapsedTime:
            self.escape_pressed = False
        else:
            self.escape_pressed = True
        self._timestamp = self.info.playersVehicleTelemetry().mElapsedTime
        return self.escape_pressed

    def toggle(self, testing_car_has_headlights=False) -> None:
        """
        Now this program is controlling the headlights a replacement
        for the headlight control is needed.
        """
        # status_poker_fn('H')
        # self._info.playersVehicleTelemetry().mHeadlights = not \
        #    self._info.playersVehicleTelemetry().mHeadlights
        if testing_car_has_headlights or self.car_has_headlights():
            PressReleaseKey(self.headlight_toggle_dik)

    def start_flashing(self, stopping_callback, flash_timer) -> None:
        """ Start flashing (if not already) """
        if not self._flashing:
            self.timer = flash_timer
            self.headlight_state = self.are_headlights_on()
            if self.headlight_state:
                self.__toggle_off(stopping_callback)
            else:
                self.__toggle_on(stopping_callback)

    def headlight_control_is_live(self) -> bool:
        """ Player is driving the car, headlight control is active """
        if self.info.isSharedMemoryAvailable():
            if self.info.isTrackLoaded():
                if self.info.isOnTrack():
                    if not self.escape_pressed:
                        return True
                    else:
                        update_status('Esc pressed')
                else:
                    update_status('Not on track')
            else:
                update_status('Track not loaded')
        else:
            update_status('rFactor 2 not running')
        self._in_pit_lane = False
        return False

    def __toggle_on(self, stopping_callback) -> None:
        """ Toggle the headlights on unless it's time to stop """
        if self.headlight_control_is_live() and not stopping_callback():
            self._flashing = True
            if self.__ignition_is_on():
                if self.car_is_moving():  # Only flash if the car is moving
                    self.on()
            else:
                update_status('Engine not running')
            set_timer(self.timer[0], self.__toggle_off, _args=[stopping_callback])
            return
        self.stop_flashing()

    def __toggle_off(self, stopping_callback) -> None:
        """ Toggle the headlights off unless it's time to stop """
        if self.headlight_control_is_live() and not stopping_callback():
            self._flashing = True
            self.off()
            set_timer(self.timer[1], self.__toggle_on, _args=[stopping_callback])
            return
        self.stop_flashing()

    def stop_flashing(self):
        """ docstring """
        if self._flashing:
            # Check that headlights in same start as originally
            if self.headlight_state != self.are_headlights_on():
                # toggle the headlights again
                self.toggle()
            self._flashing = False

    def are_headlights_on(self) -> bool:
        """ Are they on? """
        return self.info.playersVehicleTelemetry().mHeadlights != 0

    def __not_in_pit_lane(self) -> bool:
        """ Used to stop when not in the pit lane """
        res = not self.info.playersVehicleScoring().mInPits
        return res

    def __pit_limiter_is_off(self) -> bool:
        """ Used to stop when the pit limiter is off """
        return not self.info.playersVehicleTelemetry().mSpeedLimiter

    def __ignition_is_on(self) -> bool:
        """ Is it on? """
        return self.info.playersVehicleTelemetry().mIgnitionStarter != 0

    def flashing(self) -> bool:
        """ Are the headlights being flashed? """
        return self._flashing

    def player_is_driving(self) -> bool:
        """ If not there's no point trying to control the headlights """
        if self.info.versionCheckMsg != '' and self.info.isTrackLoaded():
            if self.info.isOnTrack():
                return True
        else:
            self.tested_car_has_headlights = False
        return False
