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
      <div class="float-right">
        <b-button @click="launchConfig" size="sm"
                  v-b-popover.lefttop.hover="'Launch rf Config to change resolution, refresh rate ' +
                   'and window mode.'">
          <b-icon icon="display-fill" />
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
      resolutionSettingsKeys: ['WindowedMode', 'Borderless', 'VideoMode', 'VideoRefresh', 'VSync'],
      enableResolutionSettings: false,
    }
  },
  methods: {
    updateSetting: function (setting, value) {
      if (this.resolutionSettingsKeys.indexOf(setting.key) !== -1) {
        if (!this.enableResolutionSettings) { console.log('Skipping res setting', setting.key); return}
      }
      this.$emit('update-setting', setting, value)
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
        // Disable FXAA
        this.$emit('update-setting', setting, 0, false)
        return true
      }
      // Enabled
      return false
    },
    launchConfig: async function() {
      let r = await getEelJsonObject(window.eel.run_rfactor_config()())
      if (r === undefined || !r.result) {
        this.makeToast('Could not launch rF Config.exe', 'danger')
      }
    }
  },
  props: {preset: Object, idx: Number, current_preset_idx: Number, view_mode: Number},
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

</style>