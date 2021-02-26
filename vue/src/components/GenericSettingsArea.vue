<template>
<div v-if="current_preset_idx === idx">
  <!-- Generic Settings -->
  <b-card class="mt-2 setting-card" :id="groupId"
          bg-variant="dark" text-variant="white">
    <template #header>
      <h6 class="mb-0">
        <span class="title">{{ preset[settingsKey].title }}</span>
      </h6>
    </template>
    <template v-if="!viewMode">
      <!-- View Mode Grid -->
      <Setting v-for="setting in searchedOptions" :key="setting.key"
               :setting="setting" variant="rf-orange" class="mr-3 mb-3" :fixWidth="true"
               :show_performance="showPerformance"
               :disabled="settingDisabledLocal(setting)"
               :group-id="groupId"
               @setting-changed="updateSetting">
      </Setting>
    </template>
    <template v-else>
      <!-- View Mode List -->
      <b-list-group class="text-left">
        <b-list-group-item class="bg-transparent" v-for="setting in searchedOptions"
                           :key="setting.key">
          <Setting :setting="setting" variant="rf-orange" :fixWidth="true"
                   :show_performance="showPerformance"
                   :disabled="settingDisabledLocal(setting)"
                   :group-id="groupId"
                   @setting-changed="updateSetting">
          </Setting>
        </b-list-group-item>
      </b-list-group>
    </template>
    <template #footer>
      <slot name="footer"></slot>
    </template>
  </b-card>
</div>
</template>

<script>
import Setting from "./Setting.vue"
/* import {getEelJsonObject} from "@/main"; */

export default {
  name: "GenericSettingsArea",
  props: {preset: Object, idx: Number, current_preset_idx: Number, view_mode: Number, settingsKey: String,
          settingDisabled: Function, showPerformance: Boolean, search: String },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    updateSetting: function (setting, value) {
      this.$emit('update-setting', setting, value)
    },
    settingDisabledLocal: function (setting) {
      if (this.settingDisabled !== undefined) {
        return this.settingDisabled(setting)
      }
      return false
    },
    searchSetting: function (setting) {
      if (this.search === '' || this.search === null || this.search === undefined) { return true }
      let name = ''
      if (setting.name !== null && setting.name !== undefined) { name = setting.name.toLowerCase() }
      let desc = ''
      if (setting.desc !== null && setting.desc !== undefined) { desc = setting.desc.toLowerCase() }
      let value = ''
      if (setting.value !== null && setting.value !== undefined) { value = String(setting.value).toLowerCase() }
      const search = this.search.toLowerCase()
      return name.indexOf(search) !== -1 || desc.indexOf(search) !== -1 || value.indexOf(search) !== -1
    },
  },
  components: {
      Setting
  },
  computed: {
    viewMode: function () {
      if (this.view_mode !== undefined) { return this.view_mode }
      return 0
    },
    groupId: function () {
      return 'setting-area-' + this._uid
    },
    searchedOptions: function () {
      let settings = []
      this.preset[this.settingsKey].options.forEach(setting => {
        let r1 = this.searchSetting(setting)
        let r2 = false

        setting.settings.forEach(s => { r2 = r2 || this.searchSetting(s) })
        if (r1 || r2) { settings.push(setting) }
      })
      return settings
    },
  },
}
</script>

<style scoped>

</style>