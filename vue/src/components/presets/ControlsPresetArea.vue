<template>
  <div>
    <PresetUi ref="conUi" :id-ref="idRef" :display-name="displayName"
              :presets="conHandler.presets"
              :previous-preset-name="conHandler.previousPresetName"
              :selected-preset-idx="conHandler.selectedPresetIdx"
              :preset-dir="conHandler.userPresetsDir"
              @save-preset="conHandler.savePreset"
              @refresh="conHandler.getPresets"
              @update-presets-dir="conHandler.setPresetsDir"
              @export-current="conHandler.exportPreset"
              @select-preset="conHandler.selectPreset"
              @create-preset="conHandler.createPreset"
              @delete-preset="conHandler.deletePreset"
              @update-setting="conHandler.updateSetting"
              @update-desc="conHandler.updateDesc"
              @update-view-mode="conHandler.updateViewMode"
              @make-toast="makeToast" />

    <div>
      <div v-for="(conPreset, idx) in conHandler.presets" :key="conPreset.name">
        <SettingsCard :preset="conPreset" :idx="idx" :search="search" fixed-width
                      settings-key="freelook_settings" header-icon="card-list"
                      :current_preset_idx="conHandler.selectedPresetIdx"
                      :previous-preset-name="conHandler.previousPresetName"
                      :view_mode="conHandler.viewMode"
                      @update-setting="conHandler.updateSetting"
                      @set-busy="setBusy"
                      @make-toast="makeToast"/>
        <SettingsCard :preset="conPreset" :idx="idx" :search="search" fixed-width
                      settings-key="gamepad_mouse_settings" header-icon="receipt"
                      :current_preset_idx="conHandler.selectedPresetIdx"
                      :previous-preset-name="conHandler.previousPresetName"
                      :view_mode="conHandler.viewMode"
                      @update-setting="conHandler.updateSetting"
                      @set-busy="setBusy"
                      @make-toast="makeToast"/>
        <SettingsCard :preset="conPreset" :idx="idx" :search="search" fixed-width
                      settings-key="general_steering_settings" header-icon="filter-circle"
                      :current_preset_idx="conHandler.selectedPresetIdx"
                      :previous-preset-name="conHandler.previousPresetName"
                      :view_mode="conHandler.viewMode"
                      @update-setting="conHandler.updateSetting"
                      @set-busy="setBusy"
                      @make-toast="makeToast"/>
      </div>
    </div>
  </div>
</template>

<script>
import PresetUi from "@/components/presets/PresetUi";
import SettingsCard from "@/components/settings/SettingsCard";

export default {
  name: "ControlsPresetArea",
  data: function () {
    return {
      displayDefaultName: 'Controls'
    }
  },
  props: {conHandler: Object, idRef: String, name: String, search: String, fixedWidth: Boolean},
  components: {PresetUi, SettingsCard},
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) {
      this.$emit('set-busy', busy)
    },
    receiveControllerDeviceEvent (event) {
      console.log(event.detail)
    },
  },
  computed: {
    displayName: function () {
      if (this.name === undefined) { return this.displayDefaultName }
      return this.name
    },
  }
}
</script>

<style scoped>

</style>