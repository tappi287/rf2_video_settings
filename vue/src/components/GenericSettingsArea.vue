<template>
<div v-if="current_preset_idx === idx">
  <!-- Generic Settings -->
  <b-card class="mt-2 setting-card" id="graphic"
          bg-variant="dark" text-variant="white">
    <template #header>
      <h6 class="mb-0">
        <span class="title">{{ preset.game_options.title }}</span>
      </h6>
    </template>
    <template v-if="!viewMode">
      <!-- View Mode Grid -->
      <Setting v-for="setting in preset.game_options.options" :key="setting.key"
               :setting="setting" variant="rf-orange" class="mr-3 mb-3" :fixWidth="true"
               group_id="graphic"
               v-on:setting-changed="updateSetting">
      </Setting>
    </template>
    <template v-else>
      <!-- View Mode List -->
      <b-list-group class="text-left">
        <b-list-group-item class="bg-transparent" v-for="setting in preset.game_options.options"
                           :key="setting.key">
          <Setting :setting="setting" variant="rf-orange" :fixWidth="true" group_id="graphic"
                   v-on:setting-changed="updateSetting">
          </Setting>
        </b-list-group-item>
      </b-list-group>
    </template>
    <template #footer>
    </template>
  </b-card>
</div>
</template>

<script>
import Setting from "./Setting.vue"
/* import {getEelJsonObject} from "@/main"; */

export default {
  name: "GenericSettingsArea",
  data: function () {
    return {
      data: false
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