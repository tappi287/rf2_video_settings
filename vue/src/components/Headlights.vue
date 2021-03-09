<template>
  <div id="headlights">
    <b-input-group>
      <b-input-group-prepend>
        <!-- Headlight Icon -->
        <div class="p-1 position-relative bg-transparent rounded-left">
          <b-img width=".3rem" class="hdl-icon pulse" v-if="isHeadlightAppEnabled"
                 src="@/assets/rf2_headlights_glow.svg"></b-img>
          <b-img width=".3rem" class="hdl-icon bottom" src="@/assets/rf2_headlights_off.svg"></b-img>
        </div>
        <!-- Title -->
        <b-input-group-text class="bg-transparent no-border section-title text-white pl-1">
          rF2 Headlights
        </b-input-group-text>
      </b-input-group-prepend>

      <!-- Spacer -->
      <div class="form-control bg-transparent no-border"></div>
    </b-input-group>

    <!-- Headlight rFactor Control Mapping -->
    <b-card class="mt-2 setting-card" id="hdl-controller-json-area"
            bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h6 class="mb-0 title headlight-title-line">rFactor 2 Headlight Control</h6>
        <div class="float-right headlight-title-line">
          <b-button size="sm" class="rounded-right" @click="getSettings"
                    v-b-popover.hover.bottom="'Refresh Settings if you updated a setting in-game'">
            <b-icon icon="arrow-repeat"></b-icon>
          </b-button>
        </div>
      </template>
      <ControllerAssignment
          v-for="setting in headlightControllerJsonSettings.options" :key="setting.key"
          :setting="setting" variant="rf-orange" class="mr-3 mb-3" :rf-json="true"
          group-id="hdl-controller-json-area" :fix-width="true"
          @update-assignment="updateJsonAssignment"
          @make-toast="makeToast">
      </ControllerAssignment>
      <template #footer>
        <div style="font-size: small;">
          <template v-if="isRfactorKeyboardMapped">
            <b-icon class="text-warning" icon="exclamation-triangle-fill"></b-icon>
            <span class="ml-2">
              Your rFactor 2 headlight control is mapped to a Controller or Wheel button. Please click on
              the control setting above and map it to a keyboard key for this functionality to work.
            </span>
          </template>
          <template v-else>
            You can remap your rFactor 2 headlight control binding to a keyboard key here.
          </template>
        </div>
      </template>
    </b-card>

    <!-- Headlight App Settings -->
    <b-card class="mt-2 setting-card" id="headlight-settings-area"
            bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h6 class="mb-0 title headlight-title-line">{{ headlightSettings.title }}</h6>
        <div class="float-right headlight-title-line">
          <b-button size="sm" @click="showSettingsWiki = !showSettingsWiki">
            <b-icon :icon="showSettingsWiki ? 'exclamation' : 'question'"></b-icon>
          </b-button>
        </div>
      </template>
      <Setting v-for="setting in headlightSettings.options" :key="setting.key"
               :setting="setting" class="mr-3 mb-3" group-id="headlight-settings-area" :fix-width="true"
               :variant="isHeadlightAppEnabled || setting.key === 'enabled' ? 'rf-orange' : 'secondary'"
               @setting-changed="updateSetting"
               @make-toast="makeToast">
      </Setting>
      <template #footer v-if="showSettingsWiki">
        <div class="text-left" style="font-size: small;">
          To control the headlights
          <b-link href="https://github.com/TonyWhitley/rF2headlights/wiki">rF2headlights</b-link>
          depends on
          <b-link href="https://forum.studio-397.com/index.php?threads/rf2-shared-memory-tools-for-developers.54282/"
                  target="_blank">
            rF2 Shared Memory Tools
          </b-link>
          by
          <b-link href="https://forum.studio-397.com/index.php?members/44836/" target="_blank">The Iron Wolf</b-link>
          which must be installed in rFactor. If you have already installed
          <b-link href="http://thecrewchief.org/forum.php" target="_blank">Crew Chief</b-link>
          (and if you haven't, you're missing out!) that will have installed the Shared Memory PlugIn already.
          If not, follow the instructions in
          <b-link href="https://forum.studio-397.com/index.php?threads/rf2-shared-memory-tools-for-developers.54282/"
                  target="_blank">
            rF2 Shared Memory Tools
          </b-link>
        </div>
      </template>
    </b-card>

    <!-- Headlight Controller Mappings -->
    <b-card class="mt-2 setting-card" id="hdl-controller-area"
            bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h6 class="mb-0 title headlight-title-line">Controller Assignments</h6>
        <div class="float-right headlight-title-line">
          <b-button size="sm" @click="showAssignWiki = !showAssignWiki">
            <b-icon :icon="showAssignWiki ? 'exclamation' : 'question'"></b-icon>
          </b-button>
        </div>
      </template>
      <ControllerAssignment
          v-for="setting in controllerAssignments.options" :key="setting.key"
          :setting="setting" class="mr-3 mb-3" group-id="hdl-controller-area" :fix-width="true"
          :variant="isHeadlightAppEnabled ? 'rf-orange' : 'secondary'"
          @update-assignment="updateAssignment"
          @make-toast="makeToast">
      </ControllerAssignment>
      <template #footer v-if="showAssignWiki">
        <div class="text-left" style="font-size: small;">
          These assignments will be used to control this rf2headlights app functionality. You need to have this app
          opened and running for these controller mappings to work in-game.
        </div>
      </template>
    </b-card>

    <!-- Footer -->
    <div class="mt-3 main-footer small font-weight-lighter">
      <span>Idea, functionality and code portions courtesy of: </span>
      <a href="https://github.com/TonyWhitley/rF2headlights" target="_blank">rf2headlights</a>
    </div>
  </div>
</template>

<script>
import Setting from "@/components/Setting";
import {getControllerDeviceTypeName, getControllerValueName, getEelJsonObject} from "@/main";
import ControllerAssignment from "@/components/ControllerAssignment";

export default {
name: "Headlights",
  data: function () {
    return {
      viewMode: 0,
      headlightSettings: {},
      controllerAssignments: {},
      headlightControllerJsonSettings: {},
      groupId: 'headlight-area',
      isHeadlightAppEnabled: false,
      showSettingsWiki: false,
      showAssignWiki: false,
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) { this.$emit('set-busy', busy) },
    toggleViewMode: function () {
      this.viewMode = !this.viewMode ? 1 : 0
    },
    getSettings: async function () {
      const r = await getEelJsonObject(window.eel.get_headlights_settings()())
      if (r.result) {
        this.headlightSettings = r.headlight_settings
        this.controllerAssignments = r.headlight_controller_assignments
        this.headlightControllerJsonSettings = r.headlight_controller_json
      } else if (!r.result && r.msg !== undefined) {
        this.makeToast(r.msg, 'danger')
      }
    },
    updateSetting: async function (setting, value, save = true) {
      this.setBusy(true)
      setting.value = value
      if (save) { await this.saveSettings() }
      this.setBusy(false)
    },
    updateAssignment: async function(setting, capturedEvent, save = true) {
      this.setBusy(true)
      setting.device_name = capturedEvent.name
      setting.guid = capturedEvent.guid
      setting.hat = capturedEvent.hat
      setting.axis = capturedEvent.axis
      setting.type = capturedEvent.type

      let value
      if (capturedEvent.value !== undefined && capturedEvent.value !== '' && capturedEvent.value !== null) {
        value = capturedEvent.value
      } else {
        value = getControllerValueName(capturedEvent)
      }
      setting.value = value

      if (save) {
        console.log('Updating assignment:', setting.guid, setting.device_name, getControllerDeviceTypeName(setting),
                    getControllerValueName(setting.value))
        await this.saveSettings()
      }
      this.setBusy(false)
    },
    updateJsonAssignment: async function(setting, capturedEvent, save = true) {
      setting.value = capturedEvent.value
      if (save) {
        console.log('Updating Controller.JSON assignment', capturedEvent)
        await this.saveSettings()
      }
    },
    saveSettings: async function () {
      const settings = {headlight_settings: this.headlightSettings,
                        headlight_controller_assignments: this.controllerAssignments,
                        headlight_controller_json: this.headlightControllerJsonSettings}

      const r = await getEelJsonObject(window.eel.save_headlights_settings(settings)())

      if (!r.result) {
        this.makeToast(r.msg, 'danger')
        console.error('Error writing App Settings!', r.msg)
        console.log(r)
      } else {
        console.log('Saved Headlights settings.')
      }
    },
  },
  watch: {
    'headlightSettings.options': {
      handler(val) {
        console.log('Update:', val)
        val.forEach(opt => {
          if (opt.key === 'enabled') { this.isHeadlightAppEnabled = opt.value }
        })
      },
      deep: true
    }
  },
  computed: {
    isRfactorKeyboardMapped: function () {
      // If rFactor Headlight control is mapped to keyboard
      if (this.headlightControllerJsonSettings.options !== undefined) {
        if (Array.isArray(this.headlightControllerJsonSettings.options[0].value)) {
          return this.headlightControllerJsonSettings.options[0].value[0] !== 0
        }
      }
      return false
    }
  },
  created() {
    this.getSettings()
  },
  components: {ControllerAssignment, Setting }
}
</script>

<style scoped>
.section-title { font-family: Ubuntu, sans-serif; }
.headlight-title-line { display: inline-block; }
.hdl-icon { width: 2.275rem; }
.hdl-icon.bottom { position: relative; }
@keyframes headlightFlash {
  0% { opacity: 1; }
  40% { opacity: 0.9; }
  50% { opacity: 0; }
  80% { opacity: 0; }
  100% { opacity: 1; }
}
.hdl-icon.pulse {
  position: absolute; z-index: 2;
  animation-name: headlightFlash;
  animation-duration: 300ms;
  animation-iteration-count: 4;
  animation-direction: normal;
}
</style>