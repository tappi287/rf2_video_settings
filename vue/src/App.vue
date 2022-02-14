<template>
  <div id="app">
    <!-- Handle Preset file drops -->
    <div id="dropzone" v-if="error === ''">
      <b-overlay :show="dragActive" variant="white" :no-center="true" opacity="0.9" :fixed="true">

        <!-- Main component -->
        <MainPage v-on:error="setError" ref="main" :rfactor-version="rfactorVersion"/>

        <!-- Drag Overlay Content-->
        <template #overlay>
          <div id="drop-animation" class="text-center">
            <b-icon icon="file-arrow-down-fill" font-scale="3" animation="cylon-vertical"
                    variant="dark"></b-icon>
            <p class="text-dark mt-4">Drop a Preset JSON file to import...</p>
          </div>
        </template>
      </b-overlay>
    </div>

    <!-- Report missing rF2 installation or missing privileges or App Exceptions -->
    <template v-if="error !== ''">
      <b-container fluid="sm">
        <b-card class="mt-3" bg-variant="dark" text-variant="white">
          <template #header>
            <h6 class="mb-0"><span class="title">Critical Error</span></h6>
          </template>
          <b-card-text class="text-left">
            <pre class="text-white">{{ error }}</pre>
          </b-card-text>
          <b-card-text>
            If you think the error relates to missing privileges:
            try to re-run this application with administrative privileges:
            <b-button class="mt-2 mb-2" @click="reRunAsAdmin" size="sm">UAC Re-Run-as-Admin</b-button>
          </b-card-text>
          <b-card-text>
            If you have previously set this app to request Admin privileges. You can set the App to not
            request administrative privileges on start up:
            <b-button class="mt-2 mb-2" @click="resetAdmin" size="sm">Reset UAC</b-button>
          </b-card-text>
          <b-card-text class="mt-3 mb-3">
            <h5>rFactor 2 Location</h5>
            If you have trouble locating the correct rFactor 2 installation path, enter it manually here and restart the app.
            <b-form-group class="mt-2" :state="rfOverwriteLocationValid"
                          :valid-feedback="'rF2 install detected! ' + rfactorPath"
                          :invalid-feedback="'Could not detect valid rF2 install ' + rfactorPath">
              <b-input-group>
                <b-form-input v-model="rfOverwriteLocation" :state="rfOverwriteLocationValid"
                              :placeholder="rfactorLocationPlaceholder">
                </b-form-input>
                <b-input-group-append>
                  <b-button variant="warning" @click="rfOverwriteLocation=''">Reset</b-button>
                </b-input-group-append>
              </b-input-group>
            </b-form-group>
          </b-card-text>
          <template #footer>
            <span class="small">
              Please make sure that a rFactor 2 Steam installation is present on your machine and that you have at least
              <b>once started the game</b>.
            </span>
          </template>
        </b-card>
        <div class="mt-3">
          <b-button @click="requestClose" size="sm">Exit</b-button>
        </div>
      </b-container>
    </template>
    <!-- Footer -->
    <div class="mt-3 main-footer small font-weight-lighter">
      <AppUpdater></AppUpdater>
    </div>

    <!-- Audio -->
    <div style="display: none">
      <audio src="@/assets/UI_Confirm.mp4" id="audioConfirm"></audio>
      <audio src="@/assets/UI_Ping.mp4" id="audioPing"></audio>
      <audio src="@/assets/UI_Indicator.mp4" id="audioIndicator"></audio>
      <audio src="@/assets/UI_Cute-Select.mp4" id="audioCuteSelect"></audio>
      <audio src="@/assets/UI_Switch.mp4" id="audioSwitch"></audio>
      <audio src="@/assets/UI_SwitchOn.mp4" id="audioSwitchOn"></audio>
      <audio src="@/assets/UI_SwitchOff.mp4" id="audioSwitchOff"></audio>
      <audio src="@/assets/UI_Select.mp4" id="audioSelect"></audio>
      <audio src="@/assets/UI_Flash.mp4" id="audioFlash"></audio>
    </div>
  </div>
</template>

<script>
import './assets/app.scss'
import MainPage from "./components/MainPage.vue";
import AppUpdater from "@/components/Updater";
import {createPopperLite as createPopper, flip, preventOverflow} from "@popperjs/core";
import {getEelJsonObject} from "@/main";
// --- </ Prepare receiving App Exceptions
window.eel.expose(appExceptionFunc, 'app_exception')
async function appExceptionFunc (event) {
  const excEvent = new CustomEvent('app-exception-event', {detail: event})
  window.dispatchEvent(excEvent)
}
// --- />
// --- </ Prepare receiving play audio events
window.eel.expose(playAudio, 'play_audio')
async function playAudio (event) {
  const audioEvent = new CustomEvent('play-audio-event', {detail: event})
  window.dispatchEvent(audioEvent)
}
// --- />
// --- </ Prepare receiving rfactor live events
window.eel.expose(rfactorLiveFunc, 'rfactor_live')
async function rfactorLiveFunc (event) {
  const liveEvent = new CustomEvent('rfactor-live-event', {detail: event})
  window.dispatchEvent(liveEvent)
}
// --- />
// --- </ Prepare receiving rfactor status events
window.eel.expose(rfactorStatusFunc, 'rfactor_status')
async function rfactorStatusFunc (event) {
  const statusEvent = new CustomEvent('rfactor-status-event', {detail: event})
  window.dispatchEvent(statusEvent)
}

export default {
  name: 'App',
  data: function () {
    return {
      dragActive: false,
      error: '',
      rfactorVersion: '',
      rfactorPath: '',
      rfOverwriteLocation: null,
      rfOverwriteLocationValid: null,
    }
  },
  methods: {
    handleDragOver: function (event) {
      event.stopPropagation()
      event.preventDefault()
      event.dataTransfer.dropEffect = 'copy'
      this.dragActive = true
    },
    handleDragLeave () {
      this.dragActive = false
    },
    handleFileDrop: async function (evt) {
      evt.stopPropagation()
      evt.preventDefault()
      this.dragActive = false

      let files = evt.dataTransfer.files

      for (let i = 0; i < files.length; i++) {
        let f = files[i]
        if (f.type !== 'application/json') {
          this.MainPage.methods.makeToast(
              'The dropped file is of the wrong type.', 'danger', 'File Import')
          break
        }
        let importPreset = JSON.parse(await f.text())
        await this.$refs.main.importPreset(importPreset)
      }
    },
    getRfVersion: async function () {
      let r = await getEelJsonObject(window.eel.get_rf_version()())
      if (r !== undefined) {
        let version = r.version
        this.rfactorPath = r.location

        version = version.replace('.', '')
        version = version.replace('\n', '')
        this.rfactorVersion = version
        console.log('App found rF version:', this.rfactorVersion)
      }
    },
    getRfLocationValid: async function () {
      let r = await getEelJsonObject(window.eel.rf_is_valid()())
      if (r !== undefined) { this.rfOverwriteLocationValid = r }
    },
    setException: function (event) {
      this.setError(event.detail)
    },
    setError: function (error) {
      console.error(error)
      this.error = error
    },
    requestClose: async function () {
      await window.eel.close_request()
    },
    reRunAsAdmin: async function () {
      await window.eel.re_run_admin()
    },
    resetAdmin: async function () {
      await window.eel.reset_admin()
    },
    forceReRender() {
      this.mainComponentKey += 1
    },
    externalPlayAudioEvent(event) {
      if (event.detail === undefined) {
        console.error('Received external play audio event but no event.details provided!')
        return
      }
      this.playAudio(event.detail)
    },
    playAudio(elemId) {
      let a = document.getElementById(elemId)
      console.log('Playing audio element:', a)
      if (a !== undefined) { a.play() }
    },
  },
  components: {
    AppUpdater,
    MainPage
  },
  watch: {
    rfOverwriteLocation: async function (newValue) {
      let r = await getEelJsonObject(window.eel.overwrite_rf_location(newValue)())
      if (r !== undefined) {
        await this.getRfVersion()  // Update rF location
        await this.getRfLocationValid()  // Update rf install valid state
      }
    },
  },
  mounted() {
    // Setup the dnd listeners.
    let dropZone = document.getElementById('dropzone')
    dropZone.addEventListener('dragover', this.handleDragOver, false)
    dropZone.addEventListener('dragleave', this.handleDragLeave, false)
    dropZone.addEventListener('drop', this.handleFileDrop, false)

    window.addEventListener('beforeunload', this.requestClose)

    window.addEventListener('rfactor-live-event', this.$refs.main.updateRfactorLiveState)
    window.addEventListener('rfactor-status-event', this.$refs.main.updateRfactorStatus)
  },
  async created() {
    window.addEventListener('app-exception-event', this.setException)
    window.addEventListener('play-audio-event', this.externalPlayAudioEvent)

    await this.getRfVersion()

    this.$eventHub.$on('play-audio', this.playAudio)
  },
  computed: {
    rfactorLocationPlaceholder: function () {
      if (this.rfactorPath !== '') { return 'Auto detected: ' + this.rfactorPath }
      return 'Path eg. D:\\Steam\\steamapps\\common\\rFactor 2\\'
    }
  },
  beforeDestroy() {
    window.removeEventListener('rfactor-live-event', this.$refs.main.updateRfactorLiveState)
    window.removeEventListener('rfactor-status-event', this.$refs.main.updateRfactorStatus)
    this.requestClose()
  },
  destroyed() {
    this.$eventHub.$off('play-audio')
    window.removeEventListener('app-exception-event', this.setException)
    window.removeEventListener('play-audio-event', this.externalPlayAudioEvent)
  }
}

function neverCalled() {
  createPopper()
  preventOverflow()
  flip()
}

let pass = true
if (!pass) {
  neverCalled()
}
</script>

<style scoped>

</style>
