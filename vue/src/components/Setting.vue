<template>
  <div class="setting mr-3 mt-3" v-if="setting !== undefined">
    <b-input-group size="sm">
      <b-input-group-prepend>
        <b-input-group-text>{{ setting.name }}</b-input-group-text>
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
    setting: Object, variant: String
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
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.setting { display: inline-block }
.setting-item {min-width: 7.0rem;}
</style>
