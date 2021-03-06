<template>
  <div id="headlights">
    <p>{{ message }}</p>
    <b-card class="mt-2 setting-card" id="headlight-settings-area"
            bg-variant="dark" text-variant="white">
      <template #header>
        <h6 class="mb-0 title">{{ headlightSettings.title }}</h6>
      </template>
      <Setting v-for="setting in headlightSettings.options" :key="setting.key"
               :setting="setting" variant="rf-orange" class="mr-3 mb-3"
               group-id="headlight-settings-area" :fix-width="true"
               @setting-changed="updateSetting">
      </Setting>
    </b-card>
    <b-card class="mt-2 setting-card" id="headlight-controller-area"
            bg-variant="dark" text-variant="white">
      <template #header>
        <h6 class="mb-0 title">Controller Assignments</h6>
      </template>
      <ControllerAssignment
          v-for="setting in controllerAssignments.options" :key="setting.key"
          :setting="setting" variant="rf-orange" class="mr-3 mb-3"
          group-id="headlight-controller-area" :fix-width="true"
          @update-assignment="updateAssignment">
      </ControllerAssignment>
    </b-card>
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
      groupId: 'headlight-area',
    }
  },
  methods: {
    setBusy: function (busy) { this.$emit('set-busy', busy) },
    getSettings: async function () {
      const r = await getEelJsonObject(window.eel.get_headlights_settings()())
      if (r.result) {
        this.headlightSettings = r.headlight_settings
        this.controllerAssignments = r.headlight_controller_assignments
      } else if (!r.result && r.msg !== undefined) {
        this.makeToast(r.msg, 'danger')
      }
      console.log(r)
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

      let value = null
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
    saveSettings: async function () {
      let settings = {headlight_settings: this.headlightSettings,
                      headlight_controller_assignments: this.controllerAssignments}

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
  created() {
    this.getSettings()
  },
  components: {ControllerAssignment, Setting }
}
</script>

<style scoped>

</style>