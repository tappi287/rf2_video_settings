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
          <b-form-checkbox :button-variant="applyWebUiSettings ? 'rf-orange' :  'rf-blue'"
                           v-model="applyWebUiSettings" button size="sm"
                           @change="setApplyWebUiSetting">
            <b-icon :icon="applyWebUiSettings ? 'check-square' : 'square'" />
            <span class="ml-2">Apply these settings upon game launch.</span>
          </b-form-checkbox>
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
      <template #footer v-if="!hideApplyWebuiSettings">
        <div class="float-right">
          <b-form-checkbox :button-variant="applyWebUiSettings ? 'rf-orange' :  'rf-blue'"
                           v-model="applyWebUiSettings" button size="sm"
                           @change="setApplyWebUiSetting">
            <b-icon :icon="applyWebUiSettings ? 'check-square' : 'square'" />
            <span class="ml-2">Apply these settings upon game launch.</span>
          </b-form-checkbox>
        </div>
      </template>
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

export default {
  name: "SessionArea",
  props: {preset: Object, idx: Number, current_preset_idx: Number, view_mode: Number, search: String,
          previousPresetName: String, fixedWidth: Boolean, compact: Boolean, frozen: Boolean,
          hideApplyWebuiSettings: Boolean
         },
  data: function () {
    return {
      applyWebUiSettings: true,
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    updateSetting: function (setting, value) {
      this.$emit('update-setting', setting, value)
    },
    getApplyWebUiSetting: async function () {
      const r = await getEelJsonObject(window.eel.get_apply_webui_settings()())
      this.applyWebUiSettings = r.setting
    },
    setApplyWebUiSetting: async function () {
      await getEelJsonObject(window.eel.set_apply_webui_settings(this.applyWebUiSettings)())
    },
    setBusy: function (busy) { this.$emit('set-busy', busy) },
    settingDisabled: function(setting) {
      if (setting.key === 'UseFXAA' && this._getFsaaEnabled()) {
        // Disable FXAA and do not trigger a preset save
        this.$emit('update-setting', setting, 0, false)
        return true
      }
      // Enabled
      return false
    }
  },
  components: {
      SettingsCard
  },
  computed: {
    viewMode: function () {
      if (this.view_mode !== undefined) { return this.view_mode }
      return 0
    },
  },
  async mounted() {
    await this.getApplyWebUiSetting()
  }
}
</script>

<style scoped>
.video-indicator {
  padding: .25rem .5rem;
  font-size: 1.275rem;
}
</style>