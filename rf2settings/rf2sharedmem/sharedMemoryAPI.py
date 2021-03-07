"""
Inherit Python mapping of The Iron Wolf's rF2 Shared Memory Tools
and add access functions to it.
"""
# pylint: disable=invalid-name

import psutil

try:
    from . import rF2data
except ImportError:  # standalone, not package
    import rF2data


class SimInfoAPI(rF2data.SimInfo):
    """
    API for rF2 shared memory
    """
    __HELP = "\nShared Memory is installed by Crew Chief or you can install it yourself.\n" \
        "Please update rFactor2SharedMemoryMapPlugin64.dll, see\n" \
        "https://forum.studio-397.com/index.php?threads/rf2-shared-memory-tools-for-developers.54282/"

    sharedMemoryVerified = False
    minimumSupportedVersionParts = ['3', '6', '0', '0']
    rf2_pid = None          # Once we've found rF2 running
    rf2_pid_counter = 0     # Counter to check if running
    rf2_running = False

    def __init__(self):
        rF2data.SimInfo.__init__(self)
        self.versionCheckMsg = self.versionCheck()
        self.__find_rf2_pid()

    def versionCheck(self):
        """
        Lifted from
        https://gitlab.com/mr_belowski/CrewChiefV4/blob/master/CrewChiefV4/RF2/RF2GameStateMapper.cs
        and translated.
        """
        self.sharedMemoryVerified = False    # Verify every time it is called.

        versionStr = Cbytestring2Python(self.Rf2Ext.mVersion)
        msg = ''

        if versionStr == '':
            msg = "\nrFactor 2 Shared Memory not present." + self.__HELP
            return msg

        versionParts = versionStr.split('.')
        if len(versionParts) != 4:
            msg = "Corrupt or leaked rFactor 2 Shared Memory.  Version string: " \
                + versionStr + self.__HELP
            return msg

        smVer = 0
        minVer = 0
        partFactor = 1
        for i in range(3, -1, -1):
            versionPart = 0
            try:
                versionPart = int(versionParts[i])
            except BaseException:  # pylint: disable=bare-except
                msg = "Corrupt or leaked rFactor 2 Shared Memory version.  Version string: " \
                    + versionStr + self.__HELP
                return msg

            smVer += (versionPart * partFactor)
            minVer += (int(self.minimumSupportedVersionParts[i]) * partFactor)
            partFactor *= 100

        if smVer < minVer:
            minVerStr = ".".join(self.minimumSupportedVersionParts)
            msg = "Unsupported rFactor 2 Shared Memory version: " \
                + versionStr \
                + "  Minimum supported version is: " \
                + minVerStr + self.__HELP
        else:
            msg = "\nrFactor 2 Shared Memory\nversion: " + versionStr + " 64bit."
            if self.Rf2Ext.mDirectMemoryAccessEnabled:
                if self.Rf2Ext.mSCRPluginEnabled:
                    msg += "  Stock Car Rules plugin enabled. (DFT:%d" % \
                        self.Rf2Ext.mSCRPluginDoubleFileType
                else:
                    msg += "  DMA enabled."
            if self.Rf2Ext.is64bit == 0:
                msg += "\nOnly 64bit version of rFactor 2 is supported."
            else:
                self.sharedMemoryVerified = True

        return msg

    ###########################################################
    def __find_rf2_pid(self):
        """ Find the process ID for rfactor2.exe.  Takes a while """
        for pid in psutil.pids():
            try:
                p = psutil.Process(pid)
            except psutil.NoSuchProcess:
                continue
            if p.name().lower().startswith('rfactor2.exe'):
                self.rf2_pid = pid
                break

    def __playersDriverNum(self):
        """ Find the player's driver number """
        for _player in range(50):  # self.Rf2Tele.mVehicles[0].mNumVehicles:
            if self.Rf2Scor.mVehicles[_player].mIsPlayer:
                break
        return _player

    ###########################################################
    # Access functions

    def isRF2running(self, find_counter=200, found_counter=5):
        """
        Both "rFactor 2 Launcher" and "rf2" processes are found
        whether it's the launcher or the game that's running BUT
        rfactor2.exe is only present if the game is running.
        Beacuse this takes some time, control how often it's checked using:
        find_counter: how often to check if rF2 is not running
        found_counter: how often to check once rF2 is running
        """
        if self.rf2_pid_counter == 0:  # first time
            self.rf2_pid_counter = find_counter
        if self.isSharedMemoryAvailable():
            # No need to check if Shared Memory is OK!
            self.rf2_running = True
        elif self.rf2_pid:
            if self.rf2_pid_counter >= found_counter:
                self.rf2_pid_counter = 0
                try:
                    p = psutil.Process(self.rf2_pid)
                except psutil.NoSuchProcess:
                    self.rf2_pid = None
                    return False
                if p.name().lower().startswith('rfactor2.exe'):
                    self.rf2_running = True
        else:
            if self.rf2_pid_counter >= find_counter:
                self.rf2_pid_counter = 0
                self.__find_rf2_pid()
                self.rf2_running = False
        self.rf2_pid_counter += 1
        return self.rf2_running

    def isSharedMemoryAvailable(self):
        """
        True: The correct memory map is loaded
        """
        self.versionCheck()
        return self.sharedMemoryVerified

    def isTrackLoaded(self):
        """
        True: rF2 is running and the track is loaded
        """
        started = self.Rf2Ext.mSessionStarted
        return started != 0

    def isOnTrack(self):
        """
        True: rF2 is running and the player is on track
        """
        realtime = self.Rf2Ext.mInRealtimeFC
        return realtime != 0

    def isAiDriving(self):
        """
        True: rF2 is running and the player is on track
        """
        return self.Rf2Scor.mVehicles[self.__playersDriverNum()].mControl == 1
        # who's in control: -1=nobody (shouldn't get this), 0=local player,
        # 1=local AI, 2=remote, 3=replay (shouldn't get this)

        # didn't work self.Rf2Ext.mPhysics.mAIControl

    def driverName(self):
        """
        Get the player's name
        """
        return Cbytestring2Python(
            self.Rf2Scor.mVehicles[self.__playersDriverNum()].mDriverName)

    def playersVehicleTelemetry(self):
        """ Get the variable for the player's vehicle """
        self.__playersDriverNum()
        return self.Rf2Tele.mVehicles[self.__playersDriverNum()]

    def playersVehicleScoring(self):
        """ Get the variable for the player's vehicle """
        self.__playersDriverNum()
        return self.Rf2Scor.mVehicles[self.__playersDriverNum()]

    def close(self):
        # This didn't help with the errors
        try:
            self._rf2_tele.close()
            self._rf2_scor.close()
            self._rf2_ext.close()
        except BufferError:  # "cannot close exported pointers exist"
            pass

    def __del__(self):
        self.close()


def Cbytestring2Python(bytestring):
    """
    C string to Python string
    """
    try:
        return bytes(bytestring).partition(b'\0')[0].decode('utf_8').rstrip()
    except BaseException:
        pass
    try:    # Codepage 1252 includes Scandinavian characters
        return bytes(bytestring).partition(b'\0')[0].decode('cp1252').rstrip()
    except BaseException:
        pass
    try:    # OK, struggling, just ignore errors
        return bytes(bytestring).partition(b'\0')[
            0].decode('utf_8', 'ignore').rstrip()
    except Exception as e:
        print('Trouble decoding a string')
        print(e)


def test_main():    # pylint: disable=too-many-statements
    """ Example usage """
    info = SimInfoAPI()
    if info.isRF2running():
        print('rfactor2.exe is running')
        print(info.versionCheckMsg, '\n')
        if info.isSharedMemoryAvailable():
            print('Memory map is loaded')
            version = Cbytestring2Python(info.Rf2Ext.mVersion)
            # 2019/04/23:  3.5.0.9
            print('Shared memory version:', version)

            if info.isTrackLoaded():
                trackName = Cbytestring2Python(
                    info.Rf2Scor.mScoringInfo.mTrackName)
                print('%s is loaded' % trackName)
                if info.isOnTrack():
                    driver = Cbytestring2Python(
                        info.playersVehicleScoring().mDriverName)
                    print('Driver "%s" is on track' % driver)
                    clutch = info.playersVehicleTelemetry().mUnfilteredClutch
                    # 1.0 clutch down, 0 clutch up

                    driver = Cbytestring2Python(
                        info.playersVehicleScoring().mDriverName)
                    gear = info.playersVehicleTelemetry().mGear
                    print('Driver: "%s", Gear: %d, Clutch position: %d' %
                          (driver, gear, clutch))

                    # Test that memory map can be poked
                    info.playersVehicleTelemetry().mGear = 1
                    gear = info.playersVehicleTelemetry().mGear  # -1 to 6
                    assert info.playersVehicleTelemetry().mGear == 1
                    info.playersVehicleTelemetry().mGear = 2
                    assert info.playersVehicleTelemetry().mGear == 2
                    gear = info.playersVehicleTelemetry().mGear  # -1 to 6
                    info.playersVehicleTelemetry().mGear = 1
                    assert info.playersVehicleTelemetry().mGear == 1

                    _vehicleName = Cbytestring2Python(
                        info.playersVehicleScoring().mVehicleName)
                    _vehicleClass = Cbytestring2Python(
                        info.playersVehicleScoring().mVehicleClass)

                    print('vehicleName:', _vehicleName)
                    print('vehicleClass:', _vehicleClass)

                    started = info.Rf2Ext.mSessionStarted
                    print('SessionStarted:', started)
                    realtime = info.Rf2Ext.mInRealtimeFC
                    print('InRealtimeFC:', realtime)
                    if info.isAiDriving():
                        print('AI is driving the car')
                    else:
                        print('Car not under AI control')
                else:
                    print('Driver is not on track')
            else:
                print('Track is not loaded')

            print('\nBreaking the version string...')
            info.Rf2Ext.mVersion[0] = 32

            assert not info.isSharedMemoryAvailable()
            print('\n' + info.versionCheck())
            info.Rf2Ext.mVersion[0] = 51  # restore it

            info.Rf2Ext.mVersion[0] = 50
            assert not info.isSharedMemoryAvailable()
            print('\n' + info.versionCheck())
            info.Rf2Ext.mVersion[0] = 51  # restore it

            info.Rf2Ext.mVersion[2] = 53
            assert not info.isSharedMemoryAvailable()
            print('\n' + info.versionCheck())
            info.Rf2Ext.mVersion[2] = 54  # restore it

            print('\nBreaking 64 bit info...')
            info.Rf2Ext.is64bit = 0
            assert not info.isSharedMemoryAvailable()
            print(info.versionCheck())
            info.Rf2Ext.is64bit = 1

            print('\nPit Menu')
            while True:
                if info.Rf2PitMenu.changed:
                    print(Cbytestring2Python(
                        info.Rf2PitMenu.mCategoryName))
                    info.Rf2PitMenu.changed = 0

            print('\nOK')
        else:
            print('Incorrect shared memory')
    else:
        print('rFactor 2 not running')

    s = bytearray(range(0xA1, 0xff))
    print(Cbytestring2Python(s))
    return 'OK'


if __name__ == '__main__':
    test_main()
