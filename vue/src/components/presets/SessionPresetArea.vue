<template>
  <div>
    <PresetUi ref="sesUi" id-ref="ses" display-name="Session Settings"
            :presets="sesHandler.presets"
            :previous-preset-name="sesHandler.previousPresetName"
            :selected-preset-idx="sesHandler.selectedPresetIdx"
            :preset-dir="sesHandler.userPresetsDir"
            @save-preset="sesHandler.savePreset"
            @refresh="sesHandler.getPresets"
            @update-presets-dir="sesHandler.setPresetsDir"
            @export-current="sesHandler.exportPreset"
            @select-preset="sesHandler.selectPreset"
            @create-preset="sesHandler.createPreset"
            @delete-preset="sesHandler.deletePreset"
            @update-setting="sesHandler.updateSetting"
            @update-desc="sesHandler.updateDesc"
            @update-view-mode="sesHandler.viewMode=$event"
            @make-toast="makeToast" />

    <div v-for="(sesPreset, idx) in sesHandler.presets" :key="sesPreset.name">
      <SessionArea :preset="sesPreset" :idx="idx" :search="search"
                   :fixed-width="fixedWidth" :compact="compact" :frozen="frozen"
                   :current_preset_idx="sesHandler.selectedPresetIdx"
                   :previous-preset-name="sesHandler.previousPresetName"
                   :view_mode="sesHandler.viewMode"
                   :hide-apply-webui-settings="hideApplyWebuiSettings"
                   @update-setting="sesHandler.updateSetting"
                   @set-busy="setBusy"
                   @make-toast="makeToast" />
    </div>
  </div>
</template>

<script>
import PresetUi from "@/components/presets/PresetUi";
import SessionArea from "@/components/SessionArea";

export default {
  name: "SessionPresetArea",
  props: {sesHandler: Object, search: String, fixedWidth: Boolean, compact: Boolean, frozen: Boolean,
          hideApplyWebuiSettings: Boolean
         },
  components: {SessionArea, PresetUi},
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) {this.$emit('set-busy', busy) },
  }
}
</script>

<style scoped>

</style>