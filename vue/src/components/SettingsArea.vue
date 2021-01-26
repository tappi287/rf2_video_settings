<template>
<div v-if="current_preset_idx === idx">
  <!-- Video Settings -->
  <b-card class="mt-3" id="video" bg-variant="dark" text-variant="white">
    <template #header>
      <h6 class="mb-0"><span class="title">{{ preset.video_settings.title }}</span></h6>
    </template>
    <Setting v-for="setting in preset.video_settings.options" :key="setting.key"
             :setting="setting" variant="rf-orange" class="mr-3" group_id="video"
             :show_performance="showPerformance"
             v-on:setting-changed="updateSetting">
    </Setting>
    <!-- Footer -->
    <template #footer>
    <span class="small font-weight-lighter">
      Use the in-game menu to change screen resolution and window mode for now
    </span>
    </template>
  </b-card>

  <!-- Display Settings -->
  <b-card class="mt-3" id="graphic"
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
  <b-card class="mt-3" id="advanced" bg-variant="dark" text-variant="white">
    <template #header>
      <h6 class="mb-0"><span class="title">{{ preset.advanced_graphic_options.title }}</span></h6>
    </template>
    <Setting v-for="setting in preset.advanced_graphic_options.options" :key="setting.key"
             :setting="setting" variant="rf-orange" group_id="advanced" class="mr-3 mb-3" :fixWidth="true"
             :show_performance="showPerformance"
             v-on:setting-changed="updateSetting">
    </Setting>
    <template #footer><span class="small font-weight-lighter">More settings available soon</span></template>
  </b-card>
</div>
</template>

<script>
import Setting from "./Setting.vue"

export default {
  name: "SettingsArea",
  data: function () {
    return {
      showPerformance: true,
    }
  },
  methods: {
    updateSetting: function (setting, value) {
      console.log('Setting Area forwarding setting update:', setting.name, value)
      this.$emit('update-setting', setting, value)
    },
  },
  props: {preset: Object, idx: Number, current_preset_idx: Number, view_mode: Number},
  components: {
      Setting
  },
  computed: {
    viewMode: function () {
      if (this.view_mode !== undefined) { return this.view_mode }
      return 0
    }
  }
}
</script>

<style scoped>

</style>