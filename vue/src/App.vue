<template>
  <div id="app">
    <!-- Handle Preset file drops -->
    <div id="dropzone" v-if="error === ''">
      <b-overlay :show="dragActive" variant="white" :no-center="true" opacity="0.9" :fixed="true">

        <!-- Main component -->
        <Main v-on:error="setError" ref="main" :rfactor-version="rfactorVersion"></Main>

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
      <Updater></Updater>
    </div>
  </div>
</template>

<script>
import Main from "./components/Main.vue";
import Updater from "@/components/Updater";
import {createPopperLite as createPopper, flip, preventOverflow} from "@popperjs/core";
import {getEelJsonObject} from "@/main";
// --- </ Prepare receiving App Exceptions
window.eel.expose(appExceptionFunc, 'app_exception')
async function appExceptionFunc (event) {
  const excEvent = new CustomEvent('app-exception-event', {detail: event})
  window.dispatchEvent(excEvent)
}
// --- />

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
          this.Main.methods.makeToast(
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
  },
  components: {
    Updater,
    Main
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
  },
  created() {
    window.addEventListener('app-exception-event', this.setException)
    this.getRfVersion()
  },
  computed: {
    rfactorLocationPlaceholder: function () {
      if (this.rfactorPath !== '') { return 'Auto detected: ' + this.rfactorPath }
      return 'Path eg. D:\\Steam\\steamapps\\common\\rFactor 2\\'
    }
  },
  destroyed() {
    window.removeEventListener('app-exception-event', this.setException)
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

<style>
#app {
  /*font-family: Avenir, Helvetica, Arial, sans-serif;*/
  /* font-family: "Ubuntu", sans-serif;*/
  font-family: "Segoe UI", system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #efefef;
}
#drop-animation {
  position: relative;
  top: 30%; margin: auto;
}
body {
  background: none !important;
}

html {
  /*background-image: linear-gradient(60deg, #172122 0%, #0c1013 100%);*/
  background: #16161a;
}

.hidden { display: none; }
.no-border { border: none; }
.main-footer {
  margin-bottom: 3rem;
}

.info-field {
  background-image: linear-gradient(to left, #ddd9de 0%, #c6c7cd 100%), radial-gradient(88% 271%, rgba(255, 255, 255, 0.25) 0%, rgba(254, 254, 254, 0.25) 1%, rgba(0, 0, 0, 0.25) 100%), radial-gradient(50% 100%, rgba(255, 255, 255, 0.30) 0%, rgba(0, 0, 0, 0.30) 100%);
  background-blend-mode: normal, lighten, soft-light;
}
.info-field.diff {
  background-image: linear-gradient(120deg, #ddd9de 70%, #fa7c56 100%);
  border: none;
}
.setting { display: inline-block }
.setting-item { min-width: 7.0rem; font-weight: lighter; }
.setting-field {
  box-shadow: 0 6px 15px rgba(36, 37, 38, 0.3);
}
/* Remove plastic bootstrap style */
.setting-card .card-header, .card-body, .card-footer {
  background: none; border: none;
}

.logo-style {
  box-shadow: 0 6px 15px rgba(36, 37, 38, 0.9);
  border-radius: 0.25rem;
  background-image: linear-gradient(120deg, #fdfbfb 0%, #ebedee 100%);
  padding: 2px 3px 2px 4px;
}

.title {
  text-shadow: 0px 3px 7px rgba(36, 37, 38, 0.9);
  font-family: "Ubuntu", sans-serif;
}

.btn-rf-yellow, .btn-rf-yellow:hover, .rf-yellow {
  color: #161616;
  background-color: #FF9900;
}

.b-popover-rf-yellow .popover-header {
  color: #161616;
  background-color: #fac87c;
}

.btn-rf-orange-light, .btn-rf-orange-light:hover, .rf-orange-light {
  color: #efefef;
  background-color: #FF3000;
}

.b-popover-rf-orange-light .popover-header, .badge-rf-orange-light {
  color: #efefef;
  background-color: #fc9982;
}

.btn-rf-orange, .btn-rf-orange:hover, .rf-orange {
  color: #ffffff;
  border: none;
  font-weight: lighter;
  background: #fa5a57; /* fallback for old browsers */
  background: -webkit-linear-gradient(to left, #cf4947, #ab6942); /* Chrome 10-25, Safari 5.1-6 */
  background: linear-gradient(to left, #cf4947, #ab6942); /* W3C, IE 10+/ Edge, Firefox 16+, Chrome 26+, Opera 12+, Safari 7+ */
}

.b-popover-rf-orange .popover-header, .badge-rf-orange {
  color: #efefef;
  background-color: #E06119;
}

.text-rf-orange {
  color: #E06119;
}

.btn-rf-blue, .btn-rf-blue:hover, .rf-blue {
  color: #efefef;
  border: none;
  background: #9D50BB; /* fallback for old browsers */
  background: -webkit-linear-gradient(to left, #463ea6, #745ac4); /* Chrome 10-25, Safari 5.1-6 */
  background: linear-gradient(to left, #463ea6, #745ac4); /* W3C, IE 10+/ Edge, Firefox 16+, Chrome 26+, Opera 12+, Safari 7+ */
}

.b-popover-rf-blue .popover-header {
  color: #161616;
  background-color: #728bb0;
}

.btn-rf-red, .btn-rf-red:hover, .rf-red {
  color: #efefef;
  border: none;
  background: #fa523c; /* fallback for old browsers */
  background: -webkit-linear-gradient(to left, #fa523c, #fa7c56); /* Chrome 10-25, Safari 5.1-6 */
  background: linear-gradient(to left, #fa523c, #fa7c56); /* W3C, IE 10+/ Edge, Firefox 16+, Chrome 26+, Opera 12+, Safari 7+ */
}

.btn:focus,.btn:active:focus,.btn.active:focus,
.btn.focus,.btn:active.focus,.btn.active.focus {
  outline: none !important;
  box-shadow: none !important;
}

.bg-dark {
  background-color: #172122;
}

.flex-grow { flex-grow: 1; }

@keyframes backgroundColorPalette {
  0% {
    background: #ecaaa8;
  }
  100% {
    background: white;
  }
}
.filter-warn {
  animation-name: backgroundColorPalette;
  animation-duration: 4s;
  animation-iteration-count: infinite;
  animation-direction: alternate;
}
.server-list * td { vertical-align: baseline !important; }
.server-list { margin-bottom: 0; font-family: "Segoe UI", system-ui, sans-serif; }
</style>
