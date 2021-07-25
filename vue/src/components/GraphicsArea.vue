<template>
<div v-if="current_preset_idx === idx">
  <!-- Video Settings -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="video_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :setting-disabled="settingDisabled"
                :show-performance="showPerformance"
                :search="search" header-icon="film"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
    <template #footer v-if="!compact">
      <div class="float-left video-indicator">
        <template v-if="preset.resolution_settings.options[0].value !== null">
          <b-iconstack>
            <b-icon stacked icon="display" variant="white" />
            <b-icon stacked shift-v="1.25" icon="check" variant="success" />
          </b-iconstack>
        </template>
        <template v-else>
          <b-icon icon="display-fill" variant="secondary" />
        </template>
      </div>
      <div class="float-right">
        <b-button @click="launchConfig" size="sm"
                  v-b-popover.lefttop.hover="'Launch rf Config to change resolution, refresh rate ' +
                   'and window mode.'">
          <b-icon icon="display-fill" /><span class="ml-2">Video Setup</span>
        </b-button>
      </div>
    </template>
  </SettingsCard>

  <!-- Display Settings -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="graphic_options"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :show-performance="showPerformance"
                :view_mode="viewMode"
                :search="search" header-icon="display"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
    <template #footer v-if="!compact">
      <div class="float-right">
        <b-button size="sm" @click="showPerformance = !showPerformance"
                  v-b-popover.lefttop.hover="'Show performance data next to supported settings in ' +
                   'the dropdown menu. ' +
                   'G=relative GPU performance impact | C=relative CPU performance impact'">
          <b-icon :icon="showPerformance ? 'bar-chart-line-fill' : 'bar-chart-line'"></b-icon>
        </b-button>
      </div>
    </template>
  </SettingsCard>

  <!-- Advanced Display Settings -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="advanced_graphic_options"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :show_performance="showPerformance"
                :view_mode="viewMode"
                :search="search" header-icon="card-list"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>

  <!-- VRToolKit Settings -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="reshade_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
    <template #footer v-if="!compact">
      <div style="font-size: small;">
        Visit
        <b-link class="text-rf-orange" target="_blank" href="https://vrtoolkit.retrolux.de/">
          vrtoolkit.retrolux.de
        </b-link>
        for more information.
        <br /><br />
        If you want to adjust settings in-game: create a new preset inside the ReShade UI.
        The settings you adjust here will override the default "generic_vr.ini" settings.
        <div class="float-right">
          <b-button size="sm" @click="showAllReshade = !showAllReshade"
                    v-b-popover.lefttop.hover="'Show all VRToolKit setting details even if they are not activated.'">
            <b-icon :icon="showAllReshade ? 'chevron-double-up' : 'chevron-double-down'"></b-icon>
          </b-button>
        </div>
      </div>
    </template>
  </SettingsCard>

  <!-- ReShade FAS Settings -->
  <SettingsCard v-if="sharpeningFas"
                :preset="preset" :idx="idx" settings-key="reshade_fas_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
  <!-- ReShade CAS Settings -->
  <SettingsCard v-if="sharpeningCas"
                :preset="preset" :idx="idx" settings-key="reshade_cas_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
  <!-- ReShade LUT Settings -->
  <SettingsCard v-if="applyLUT"
                :preset="preset" :idx="idx" settings-key="reshade_lut_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
  <!-- ReShade CC Settings -->
  <SettingsCard v-if="colorCorrection"
                :preset="preset" :idx="idx" settings-key="reshade_cc_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
  <!-- ReShade AA Settings -->
  <SettingsCard v-if="antiAliasing"
                :preset="preset" :idx="idx" settings-key="reshade_aa_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>

  <!-- Video Setup Modal -->
  <b-modal id="video-modal" centered hide-header-close no-close-on-backdrop no-close-on-esc>
    <template #modal-title>
      <b-icon icon="display-fill" variant="primary"></b-icon><span class="ml-2">Video Setup</span>
    </template>
    <div class="d-block">
      <p>rFactor Video Setup application launched. <b>Check your taskbar</b> if the window does not appear
      in front of you.</p>
      <p>Window, Resolution and Refresh Rate settings will be saved to
        <i>{{ preset.name }}</i> once you finished rFactor's Video Setup dialog.
      </p>
    </div>

    <template #modal-footer>
      <div class="d-block" style="font-size: small">
        <p>
          If you do not want to store rFactor's Video Setup settings in the {{ preset.name }} Preset choose
          abort below.
        </p>
        <p>
          Use the Delete button if you want to erase the existing Video Setup settings from this Preset.
        </p>
      </div>
      <div class="d-block text-right">
        <b-button variant="warning" @click="deleteConfig" class="mr-2">Delete Settings</b-button>
        <b-button variant="secondary" @click="abortConfig">Abort</b-button>
      </div>
    </template>
  </b-modal>
</div>
</template>

<script>
import SettingsCard from "@/components/SettingsCard";
import {getEelJsonObject} from "@/main";

export default {
  name: "GraphicsArea",
  data: function () {
    return {
      showPerformance: true, showAllReshade: false,
      abortResolutionUpdate: false,
    }
  },
  props: {preset: Object, idx: Number, current_preset_idx: Number, view_mode: Number, search: String,
          previousPresetName: String, fixedWidth: Boolean, compact: Boolean, frozen: Boolean },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    updateSetting: function (setting, value) {
      this.$emit('update-setting', setting, value)
    },
    setBusy: function (busy) { this.$emit('set-busy', busy) },
    updateResolutionSettings: async function () {
      this.$emit('set-busy', true)
      let r = await getEelJsonObject(window.eel.get_current_dx_config()())
      if (!r.result) {
        this.makeToast('Could not load current resolution settings', 'danger', 'Error')
        this.$emit('set-busy', false)
        return
      }

      // Update current preset from settings read from disk
      console.log('Saving resolution settings:', r.preset.resolution_settings)
      r.preset.resolution_settings.options.forEach(disk_setting => {
        this.preset.resolution_settings.options.forEach(setting => {
          if (disk_setting.key === setting.key) {
            this.$emit('update-setting', setting, disk_setting.value, false)
          }
        })
      })
      // Trigger a preset save
      const setting = this.preset.resolution_settings.options[0]
      this.$emit('update-setting', setting, setting.value, true)
      this.$emit('set-busy', false)
      this.makeToast('Video Settings for Resolution, Refresh Rate and Window Mode successfully updated.',
          'success', 'Video Setup')
    },
    _getFsaaEnabled() {
      let result = true
      this.preset.video_settings.options.forEach(setting => {
        if (setting.key === 'FSAA') {
          if (setting.value === 0) { result = false }
        }
      })
      return result
    },
    _getReshadeOption(key) {
      let result = null
      this.preset.reshade_settings.options.forEach(o => {
        if (o.key === key) { result = o.value }
      })
      return result
    },
    settingDisabled: function(setting) {
      if (setting.key === 'UseFXAA' && this._getFsaaEnabled()) {
        // Disable FXAA and do not trigger a preset save
        this.$emit('update-setting', setting, 0, false)
        return true
      }
      // Enabled
      return false
    },
    deleteConfig() {
      this.preset.resolution_settings.options.forEach(setting => {
        this.$emit('update-setting', setting, null, false)
      })
      // Trigger a preset save
      const setting = this.preset.resolution_settings.options[0]
      this.$emit('update-setting', setting, null, true)

      // Abort Video Setup
      this.abortConfig()
    },
    abortConfig() {
      this.$bvModal.hide('video-modal')
      this.abortResolutionUpdate = true
    },
    launchConfig: async function() {
      this.$bvModal.show('video-modal')
      let r = await getEelJsonObject(window.eel.run_rfactor_config()())
      if (r === undefined || !r.result) {
        this.makeToast('rFactor 2 Video Setup was aborted.', 'warning', 'Video Setup')
        this.$bvModal.hide('video-modal')
        return
      }
      if (this.abortResolutionUpdate) { this.abortResolutionUpdate = false; return }
      this.$bvModal.hide('video-modal')
      await this.updateResolutionSettings()
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
    // Display Reshade Setting Details if setting active
    sharpeningFas: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getReshadeOption('VRT_SHARPENING_MODE') === 1;
    },
    sharpeningCas: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getReshadeOption('VRT_SHARPENING_MODE') === 2;
    },
    applyLUT: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getReshadeOption('VRT_COLOR_CORRECTION_MODE') === 1;
    },
    colorCorrection: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getReshadeOption('VRT_COLOR_CORRECTION_MODE') === 2;
    },
    antiAliasing: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getReshadeOption('VRT_ANTIALIASING_MODE') === 1;
    },
  },
  created() {
    // Show detailed VRToolKit settings if there are settings differences
    if (this.previousPresetName !== '') { this.showAllReshade = true }
  }
}
</script>

<style scoped>
.video-indicator {
  padding: .25rem .5rem;
  font-size: 1.275rem;
}
</style>