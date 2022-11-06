<template>
<div v-if="current_preset_idx === idx">
  <!-- Video Settings -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="video_settings" v-if="showVideoSettings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :show-performance="showPerformance"
                :search="search" header-icon="film"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
    <template #footer v-if="!compact">
      <div class="float-left">
        <template v-if="preset.resolution_settings.options[0].value !== null">
          <div v-b-popover.auto.hover="'Screen Resolution, Window Mode and Refresh Rate have been saved and ' +
               'will be applied with this Graphics Preset.'"
               class="h3 mt-0 mb-0 video-indicator">
            <b-iconstack>
              <b-icon stacked shift-v="0.0" icon="display" variant="white" />
              <b-icon stacked shift-v="0.85" icon="check" variant="success" />
            </b-iconstack>
          </div>
        </template>
        <template v-else>
          <div v-b-popover.auto.hover="'Click the Video Setup button to save and apply Screen Resolution, Window Mode ' +
               'and Refresh Rate with this Graphics Preset.'"
                class="h3 mt-0 mb-0 video-indicator">
            <b-icon icon="display-fill" variant="secondary" />
          </div>
        </template>
      </div>
      <div class="float-right">
        <b-button @click="launchConfig" size="sm" variant="rf-secondary"
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
        <b-button size="sm" @click="showPerformance = !showPerformance" variant="rf-scondary"
                  v-b-popover.lefttop.hover="'Show performance data next to supported settings in ' +
                   'the dropdown menu. ' +
                   'G=relative GPU performance impact | C=relative CPU performance impact'">
          <b-icon :icon="showPerformance ? 'bar-chart-line-fill' : 'bar-chart-line'"></b-icon>
        </b-button>
      </div>
    </template>
  </SettingsCard>

  <!-- View Settings -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="graphic_view_options"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                :current_preset_idx="current_preset_idx"
                :previous-preset-name="previousPresetName"
                :show-performance="showPerformance"
                :view_mode="viewMode"
                :search="search" header-icon="person-square"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
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
                :current_preset_idx="current_preset_idx" :settingDisabled="reshadeSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
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
        The settings you adjust here will use a custom Reshade preset "rf2_widget_preset.ini".
        <br />
        To use these enhancements in PanCake mode: set the <i>"Use Center Mask"</i> setting to <i>Disabled</i>
        <div class="float-right">
          <b-button size="sm" @click="showAllReshade = !showAllReshade" variant="rf-secondary"
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
                :current_preset_idx="current_preset_idx" :settingDisabled="reshadeSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
  <!-- ReShade CAS Settings -->
  <SettingsCard v-if="sharpeningCas"
                :preset="preset" :idx="idx" settings-key="reshade_cas_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="reshadeSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
  <!-- ReShade LUT Settings -->
  <SettingsCard v-if="applyLUT"
                :preset="preset" :idx="idx" settings-key="reshade_lut_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="reshadeSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
  <!-- ReShade CC Settings -->
  <SettingsCard v-if="colorCorrection"
                :preset="preset" :idx="idx" settings-key="reshade_cc_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="reshadeSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
  <!-- ReShade AA Settings -->
  <SettingsCard v-if="antiAliasing"
                :preset="preset" :idx="idx" settings-key="reshade_aa_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="reshadeSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>

  <!-- ReShade Clarity2.fx PreProcessor Definitions -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="reshade_clarity_fx_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="claritySettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled && clarityEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>
  <!-- ReShade Clarity2.fx Options -->
  <SettingsCard v-if="clarity"
                :preset="preset" :idx="idx" settings-key="reshade_clarity_settings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="claritySettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="reshadeEnabled && clarityEnabled ? 'reshadeEnabled' : 'reshadeDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>

  <!-- OpenVR FSR Settings -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="openvrfsr_settings" v-if="showOpenVrSettings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                :current_preset_idx="current_preset_idx" :settingDisabled="openVrFsrSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="openVrFsrEnabled ? 'openvrModEnabled' : 'openvrModDisabled'"
                :search="search" header-icon="exclude"
                @update-setting="updateOpenVrFsrSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
    <template #footer v-if="!compact">
      <div style="font-size: small;">
        Visit
        <b-link class="text-rf-orange" target="_blank" href="https://github.com/fholger/openvr_fsr#modified-openvr-dll-with-amd-fidelityfx-superresolution--nvidia-image-scaling">
          github.com/fholger/openvr_fsr
        </b-link>
        for detailed information.
        <br />
        Leave Apply MIP bias: Off and use the rF2 Advanced Display Setting: Texture Sharpening instead!
        <template v-if="openVrFoveatedEnabled">
          <div class="mt-2">You need to disable Open VR Foveated to use this Mod.</div>
        </template>
      </div>
    </template>
  </SettingsCard>
  <!-- OpenVR FSR HotKey Settings - Hidden -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="openvrfsr_hk_settings" v-if="false"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="openVrFsrSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="openVrFsrEnabled ? 'openvrModEnabled' : 'openvrModDisabled'"
                :search="search" header-icon="image"
                @update-setting="updateSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
  </SettingsCard>

  <!-- OpenVR Foveated Settings -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="openvrfoveated_settings" v-if="showOpenVrSettings"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="compact"
                :current_preset_idx="current_preset_idx" :settingDisabled="openVrFoveatedSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="openVrFoveatedEnabled ? 'openvrModEnabled' : 'openvrModDisabled'"
                :search="search" header-icon="exclude"
                @update-setting="updateOpenVrFoveatedSetting"
                @set-busy="setBusy"
                @make-toast="makeToast">
    <template #footer v-if="!compact">
      <div style="font-size: small;">
        Visit
        <b-link class="text-rf-orange" target="_blank" href="https://github.com/fholger/openvr_foveated#readme">
          github.com/fholger/openvr_foveated
        </b-link>
        for detailed information.
        <br />
        Leave Sharpening: Off and use the VRToolkit for advanced sharpening instead! Can not be used in
        parallel with FSR.
        <template v-if="openVrFsrEnabled">
          <div class="mt-2">You need to disable Open VR FSR to use this Mod.</div>
        </template>
      </div>
    </template>
  </SettingsCard>
  <!-- OpenVR Foveated HotKey Settings - Hidden -->
  <SettingsCard :preset="preset" :idx="idx" settings-key="openvrfoveated_hk_settings" v-if="false"
                :fixed-width="fixedWidth" :frozen="frozen" :compact="true"
                :current_preset_idx="current_preset_idx" :settingDisabled="openVrFoveatedSettingDisabled"
                :previous-preset-name="previousPresetName"
                :view_mode="viewMode" :class="openVrFoveatedEnabled ? 'openvrModEnabled' : 'openvrModDisabled'"
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
      <p>Make sure to edit <b>Config_DX11.ini</b>. The widget will update your <i>Config_DX11_VR.ini</i>
         automatically.</p>
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
        <b-button variant="danger" @click="deleteConfig" class="mr-2">Delete Settings</b-button>
        <b-button variant="secondary" @click="abortConfig">Abort</b-button>
      </div>
    </template>
  </b-modal>
</div>
</template>

<script>
import SettingsCard from "@/components/settings/SettingsCard";
import {getEelJsonObject} from "@/main";

export default {
  name: "GraphicsArea",
  data: function () {
    return {
      showPerformance: true, showAllReshade: false,
      abortResolutionUpdate: false, showOpenVrSettings: true, showVideoSettings: true,
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
    updateOpenVrFsrSetting: function (setting, value) {
      if (setting.key === 'enabled' && value === true) {
        if (this.openVrFoveatedEnabled) {
          this.showOpenVrSettings = false
          // Disable Foveated
          this.preset['openvrfoveated_settings'].options.forEach(o => {
            if (o.key === 'enabled') { this.$emit('update-setting', o, false, false); o.value = false }
          })
          this.$nextTick(() => {this.showOpenVrSettings = true})
        }
      }
      this.$emit('update-setting', setting, value)
    },
    updateOpenVrFoveatedSetting: function (setting, value) {
      if (setting.key === 'enabled' && value === true) {
        if (this.openVrFsrEnabled) {
          this.showOpenVrSettings = false
          // Disable FSR
          this.preset['openvrfsr_settings'].options.forEach(o => {
            if (o.key === 'enabled') { this.$emit('update-setting', o, false, false); o.value = false }
          })
          this.$nextTick(() => {this.showOpenVrSettings = true})
        }
      }
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
    _getSetSettingsOption(settings_key, option_key, setValue=null) {
      let result = null
      this.preset[settings_key].options.forEach(o => {
        if (o.key === option_key) {
          if (setValue !== null) { o.value = setValue }
          result = o.value
        }
      })
      return result
    },
    reshadeSettingDisabled(setting) {
      if (setting.key === 'use_reshade') { return false }
      return !this.reshadeEnabled
    },
    claritySettingDisabled(setting) {
      if (setting.key === 'use_clarity') { return false }
      return !this.clarityEnabled
    },
    videoSettingsDisabled(setting) {
      if (setting.key === 'UseFXAA') { return this.msaaEnabled }
      return true
    },
    openVrFsrSettingDisabled(setting) {
      if (setting.key === 'enabled') { return false }
      return !this.openVrFsrEnabled
    },
    openVrFoveatedSettingDisabled(setting) {
      if (setting.key === 'enabled') { return false }
      return !this.openVrFoveatedEnabled
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
    msaaEnabled: function() {
      if (this.preset === undefined) { return false }
      return this._getSetSettingsOption('video_settings', 'MSAA')
    },
    openVrFsrEnabled: function () {
      if (this.preset === undefined) { return false }
      return this._getSetSettingsOption('openvrfsr_settings', 'enabled')
    },
    openVrFoveatedEnabled: function () {
      if (this.preset === undefined) { return false }
      return this._getSetSettingsOption('openvrfoveated_settings', 'enabled')
    },
    reshadeEnabled: function () {
      if (this.preset === undefined) { return false }
      return this._getSetSettingsOption('reshade_settings', 'use_reshade')
    },
    clarityEnabled: function () {
      if (this.preset === undefined) { return false }
      return this._getSetSettingsOption('reshade_clarity_fx_settings', 'use_clarity')
    },
    // Display Reshade Setting Details if setting active
    sharpeningFas: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getSetSettingsOption('reshade_settings', 'VRT_SHARPENING_MODE') === 1;
    },
    sharpeningCas: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getSetSettingsOption('reshade_settings', 'VRT_SHARPENING_MODE') === 2;
    },
    applyLUT: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getSetSettingsOption('reshade_settings', 'VRT_COLOR_CORRECTION_MODE') === 1;
    },
    colorCorrection: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getSetSettingsOption('reshade_settings', 'VRT_COLOR_CORRECTION_MODE') === 2;
    },
    antiAliasing: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getSetSettingsOption('reshade_settings', 'VRT_ANTIALIASING_MODE') === 1;
    },
    clarity: function () {
      if (this.preset === undefined) { return false } if (this.showAllReshade) { return true }
      return this._getSetSettingsOption('reshade_clarity_fx_settings', 'use_clarity');
    },
  },
  created() {
    // Show detailed VRToolKit settings if there are settings differences
    if (this.previousPresetName !== '') { this.showAllReshade = true }
  }
}
</script>

<style>
  .video-indicator { line-height: 0.98; }
  /* .reshadeEnabled > div.setting-card { background-color: rgba(234, 234, 234, 0.13) !important; } */
  .reshadeDisabled > div.setting-card { background-color: rgba(56, 56, 56, 0.13) !important; }
  /* .openvrModEnabled > div.setting-card { background-color: rgba(234, 234, 234, 0.15) !important; } */
  .openvrModDisabled > div.setting-card { background-color: rgba(56, 56, 56, 0.13) !important; }
</style>