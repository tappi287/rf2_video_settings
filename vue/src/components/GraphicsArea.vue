<template>
<div v-if="current_preset_idx === idx">
  <!-- Video Settings -->
  <GenericSettingsArea :preset="preset" :idx="idx" settings-key="video_settings"
                       :current_preset_idx="current_preset_idx"
                       :setting-disabled="settingDisabled"
                       @update-setting="updateSetting"
                       @set-busy="setBusy"
                       @make-toast="makeToast">
    <template #footer>
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
  </GenericSettingsArea>

  <!-- Display Settings -->
  <GenericSettingsArea :preset="preset" :idx="idx" settings-key="graphic_options"
                       :current_preset_idx="current_preset_idx"
                       :show-performance="showPerformance"
                       :view_mode="viewMode"
                       @update-setting="updateSetting"
                       @set-busy="setBusy"
                       @make-toast="makeToast">
    <template #footer>
      <div class="float-right">
        <b-button size="sm" @click="showPerformance = !showPerformance"
                  v-b-popover.lefttop.hover="'Show performance data next to supported settings in ' +
                   'the dropdown menu. ' +
                   'G=relative GPU performance impact | C=relative CPU performance impact'">
          <b-icon :icon="showPerformance ? 'graph-up' : 'graph-down'"></b-icon>
        </b-button>
      </div>
    </template>
  </GenericSettingsArea>

  <!-- Advanced Display Settings -->
  <GenericSettingsArea :preset="preset" :idx="idx" settings-key="advanced_graphic_options"
                       :current_preset_idx="current_preset_idx"
                       :show_performance="showPerformance"
                       :view_mode="viewMode"
                       @update-setting="updateSetting"
                       @set-busy="setBusy"
                       @make-toast="makeToast">
  </GenericSettingsArea>

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
import GenericSettingsArea from "@/components/GenericSettingsArea";
import {getEelJsonObject} from "@/main";

export default {
  name: "GraphicsArea",
  data: function () {
    return {
      showPerformance: true,
      abortResolutionUpdate: false,
    }
  },
  props: {preset: Object, idx: Number, current_preset_idx: Number, view_mode: Number},
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
      GenericSettingsArea
  },
  computed: {
    viewMode: function () {
      if (this.view_mode !== undefined) { return this.view_mode }
      return 0
    },
  }
}
</script>

<style scoped>
.video-indicator {
  padding: .25rem .5rem;
  font-size: 1.275rem;
}
</style>