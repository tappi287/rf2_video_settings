<template>
  <div class="setting" v-if="!settingHidden">
    <b-input-group size="sm" class="setting-field">
      <b-input-group-prepend>
        <div v-if="fixWidth" class="fixed-width">
          <b-input-group-text class="info-field">{{ setting.name }}</b-input-group-text>
        </div>
        <template v-else>
          <b-input-group-text class="info-field">{{ setting.name }}</b-input-group-text>
        </template>
      </b-input-group-prepend>
      <b-input-group-append>
        <b-dropdown :text="currentSettingName" :variant="variant" class="setting-item">
          <b-dropdown-item v-for="s in setting.settings" :key="s.value"
                           @click="selectSetting(s)">
            {{ s.name }}
            <b-icon v-if="s.desc !== undefined" icon="info-square"
                    v-b-popover.hover.left="s.desc">
            </b-icon>
          </b-dropdown-item>
        </b-dropdown>
      </b-input-group-append>
    </b-input-group>
  </div>
</template>

<script>
export default {
  name: 'Setting',
  data: function () {
    return {
      currentSettingValue: {}
    }
  },
  methods: {
    selectSetting: function (s) {
      this.currentSettingValue = s.value
      console.log('Emitting setting update', this.setting.key, s.value)
      this.$emit('setting-changed', this.setting, s.value)
    },
    iterateSettings: function (func) {
      if (this.setting === undefined) { return }
      for (let i=0; i <= this.setting.settings.length; i++) {
        let setting = this.setting.settings[i]
        if (setting === undefined) { continue }
        func(this, setting)
      }
    }
  },
  props: {
    setting: Object, variant: String, fixWidth: Boolean
  },
  mounted() {
    if (this.variant === undefined) { this.variant = 'secondary'}
    this.currentSettingValue = this.setting.value
  },
  computed: {
    currentSettingName: function () {
      let name = 'Not Set!'
      if (this.setting === undefined) { return name }
      this.iterateSettings(function (instance, setting) {
        if (instance.currentSettingValue === setting.value) {
          name = setting.name
        }
      })
      return name
    },
    settingHidden: function () {
      if (this.setting === undefined) { return true }
      return this.setting['hidden'] || false
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.setting { display: inline-block }
.setting-item { min-width: 7.0rem; font-weight: lighter; }
.fixed-width { min-width: 10rem; }
</style>
