<template>
  <div id="headlights">
    <b-card class="mt-2 setting-card" bg-variant="dark" text-variant="white">
      <h6 class="mb-0 title">rF2 Headlights</h6>
      <b-card-text class="text-left" style="font-size: small;">
       Advanced controls for your rFactor 2 in-game headlight.
      </b-card-text>
      <b-card-text class="text-left" style="font-size: small;">
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
      </b-card-text>
    </b-card>

    <!-- Headlight rFactor Control Mapping -->
    <b-card class="mt-2 setting-card" id="hdl-controller-json-area"
            bg-variant="dark" text-variant="white">
      <template #header>
        <h6 class="mb-0 title">rFactor 2 Headlight Control</h6>
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
        </div>
      </template>
    </b-card>

    <!-- Headlight App Settings -->
    <b-card class="mt-2 setting-card" id="headlight-settings-area"
            bg-variant="dark" text-variant="white">
      <template #header>
        <h6 class="mb-0 title">{{ headlightSettings.title }}</h6>
      </template>
      <Setting v-for="setting in headlightSettings.options" :key="setting.key"
               :setting="setting" variant="rf-orange" class="mr-3 mb-3"
               group-id="headlight-settings-area" :fix-width="true"
               @setting-changed="updateSetting"
               @make-toast="makeToast">
      </Setting>
    </b-card>

    <!-- Headlight Controller Mappings -->
    <b-card class="mt-2 setting-card" id="hdl-controller-area"
            bg-variant="dark" text-variant="white">
      <template #header>
        <h6 class="mb-0 title">Controller Assignments</h6>
      </template>
      <ControllerAssignment
          v-for="setting in controllerAssignments.options" :key="setting.key"
          :setting="setting" variant="rf-orange" class="mr-3 mb-3"
          group-id="hdl-controller-area" :fix-width="true"
          @update-assignment="updateAssignment"
          @make-toast="makeToast">
      </ControllerAssignment>
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
      message: '',
      headlightSettings: {},
      controllerAssignments: {},
      headlightControllerJsonSettings: {},
      groupId: 'headlight-area',
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) { this.$emit('set-busy', busy) },
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

</style>