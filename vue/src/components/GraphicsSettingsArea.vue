<template>
<div v-if="current_preset_idx === idx">
  <!-- Video Settings -->
  <b-card class="mt-2 setting-card" id="video" bg-variant="dark" text-variant="white">
    <template #header>
      <h6 class="mb-0"><span class="title">{{ preset.video_settings.title }}</span></h6>
    </template>
    <Setting v-for="setting in preset.video_settings.options" :key="setting.key"
             :setting="setting" variant="rf-orange" class="mr-3 mb-3" group_id="video"
             :show_performance="showPerformance" :disabled="settingDisabled(setting)"
             v-on:setting-changed="updateSetting" ref="vfx">
    </Setting>

    <!-- Footer -->
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
  </b-card>

  <!-- Display Settings -->
  <b-card class="mt-2 setting-card" id="graphic"
          bg-variant="dark" text-variant="white">
    <template #header>
      <h6 class="mb-0">
        <span class="title">{{ preset.graphic_options.title }}</span>
      </h6>
    </template>
    <template v-if="!viewMode">
      <!-- View Mode Grid -->
      <Setting v-for="setting in preset.graphic_options.options" :key="setting.key"
               :setting="setting" variant="rf-orange" class="mr-3 mb-3" :fixWidth="true"
               group_id="graphic" :show_performance="showPerformance"
               v-on:setting-changed="updateSetting">
      </Setting>
    </template>
    <template v-else>
      <!-- View Mode List -->
      <b-list-group class="text-left">
        <b-list-group-item class="bg-transparent" v-for="setting in preset.graphic_options.options"
                           :key="setting.key">
          <Setting :setting="setting" variant="rf-orange" :fixWidth="true" group_id="graphic"
                   :show_performance="showPerformance"
                   v-on:setting-changed="updateSetting">
          </Setting>
        </b-list-group-item>
      </b-list-group>
    </template>
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
  </b-card>

  <!-- Advanced Display Settings -->
  <b-card class="mt-2 setting-card" id="advanced" bg-variant="dark" text-variant="white">
    <template #header>
      <h6 class="mb-0"><span class="title">{{ preset.advanced_graphic_options.title }}</span></h6>
    </template>
    <Setting v-for="setting in preset.advanced_graphic_options.options" :key="setting.key"
             :setting="setting" variant="rf-orange" group_id="advanced" class="mr-3 mb-3" :fixWidth="true"
             :show_performance="showPerformance"
             v-on:setting-changed="updateSetting">
    </Setting>
  </b-card>

  <b-modal id="video-modal" centered hide-header-close no-close-on-backdrop no-close-on-esc>
    <template #modal-title>
      <b-icon icon="display-fill" variant="primary"></b-icon><span class="ml-2">Video Setup</span>
    </template>
    <div class="d-block">
      <p>rFactor Video Setup application launched. Check your task bar if the window does not appear
      in front of you.</p>
      <p>Window, Resolution and Refresh Rate settings will be saved to
        <i>{{ preset.name }}</i> once you finished or close rFactor's Video Setup dialog.
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
        <b-button variant="warning" @click="deleteConfig">Delete Settings</b-button>
        <b-button variant="secondary" @click="abortConfig">Abort</b-button>
      </div>
    </template>
  </b-modal>
</div>
</template>

<script>
import Setting from "./Setting.vue"
import {getEelJsonObject} from "@/main";

export default {
  name: "GraphicsSettingsArea",
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
        this.makeToast('Could not launch rF Config.exe', 'danger')
        return
      }
      if (this.abortResolutionUpdate) { this.abortResolutionUpdate = false; return }
      this.$bvModal.hide('video-modal')
      await this.updateResolutionSettings()
    }
  },
  components: {
      Setting
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