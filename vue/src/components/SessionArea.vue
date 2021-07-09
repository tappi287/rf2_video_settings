<template>
  <div v-if="current_preset_idx === idx">
    <SettingsCard :preset="preset" :idx="idx" :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                  settings-key="content_ui_settings"
                  content-selection
                  :search="search" header-icon="box-seam"
                  :current_preset_idx="current_preset_idx"
                  :previous-preset-name="previousPresetName"
                  :view_mode="viewMode"
                  @update-setting="updateSetting"
                  @set-busy="setBusy"
                  @make-toast="makeToast">
      <template #contentFooter v-if="!hideApplyWebuiSettings">
        <div class="float-right">
          <LaunchRfactorBtn :text="'Launch and apply Content Settings'"
                            @make-toast="makeToast" @launch="rFactorLaunched" />
        </div>
      </template>
    </SettingsCard>
    <SettingsCard :preset="preset" :idx="idx" :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                  settings-key="session_ui_settings"
                  :search="search" header-icon="card-text"
                  :current_preset_idx="current_preset_idx"
                  :previous-preset-name="previousPresetName"
                  :view_mode="viewMode"
                  @update-setting="updateSetting"
                  @set-busy="setBusy"
                  @make-toast="makeToast">
    </SettingsCard>
    <SettingsCard :preset="preset" :idx="idx" :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                  settings-key="session_game_settings"
                  :search="search" header-icon="collection"
                  :current_preset_idx="current_preset_idx"
                  :previous-preset-name="previousPresetName"
                  :view_mode="viewMode"
                  @update-setting="updateSetting"
                  @set-busy="setBusy"
                  @make-toast="makeToast"/>
    <SettingsCard :preset="preset" :idx="idx" :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                  settings-key="session_condition_settings"
                  :search="search" header-icon="droplet"
                  :current_preset_idx="current_preset_idx"
                  :previous-preset-name="previousPresetName"
                  :view_mode="viewMode"
                  @update-setting="updateSetting"
                  @set-busy="setBusy"
                  @make-toast="makeToast"/>
  </div>
</template>

<script>
import {getEelJsonObject} from "@/main";
import SettingsCard from "@/components/SettingsCard";
import LaunchRfactorBtn from "@/components/LaunchRfactorBtn";

export default {
  name: "SessionArea",
  props: {preset: Object, idx: Number, current_preset_idx: Number, view_mode: Number, search: String,
          previousPresetName: String, fixedWidth: Boolean, compact: Boolean, frozen: Boolean,
          hideApplyWebuiSettings: Boolean
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    updateSetting: function (setting, value) {
      this.$emit('update-setting', setting, value)
    },
    setApplyWebUiSetting: async function (value) {
      const r = await getEelJsonObject(window.eel.set_apply_webui_settings(value)())
      if (!r.result) {
        this.makeToast(r.msg, 'danger', 'WebUi Settings')
      }
    },
    setBusy: function (busy) { this.$emit('set-busy', busy) },
    rFactorLaunched: function (){
      this.setApplyWebUiSetting(true)
    },
  },
  components: {
    LaunchRfactorBtn, SettingsCard
  },
  computed: {
    viewMode: function () {
      if (this.view_mode !== undefined) { return this.view_mode }
      return 0
    },
  },
}
</script>

<style scoped>
.video-indicator {
  padding: .25rem .5rem;
  font-size: 1.275rem;
}
</style>