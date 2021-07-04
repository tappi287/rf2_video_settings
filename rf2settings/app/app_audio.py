import eel


class AppAudioFx:
    confirm = "audioConfirm"
    ping = "audioPing"
    indicator = "audioIndicator"
    select = "audioSelect"
    cute_select = "audioCuteSelect"
    switch = "audioSwitch"
    switch_on = "audioSwitchOn"
    switch_off = "audioSwitchOff"
    flash = "audioFlash"

    @classmethod
    def play_audio(cls, audio_fx_id: str):
        if not audio_fx_id:
            return
        eel.play_audio(audio_fx_id)
