<template>
  <div class="setting" v-if="!settingHidden">
    <b-input-group size="sm" class="setting-field">
      <b-input-group-prepend>
        <b-input-group-text class="info-field fixed-width-name" :id="nameId">
          {{ setting.name }}
          <b-icon v-if="settingDesc !== ''" icon="info-square" class="ml-2 mr-1"
                      v-b-popover.hover.topright="settingDesc">
          </b-icon>
        </b-input-group-text>
      </b-input-group-prepend>
      <b-input-group-append>
        <!-- Dropdown Menu -->
        <template v-if="inputType === 'value'">
          <b-dropdown :text="currentSettingName" :variant="variant" :id="elemId"
                      class="setting-item fixed-width-setting" :disabled="disabled">
            <b-dropdown-item v-for="s in setting.settings" :key="s.value"
                             @click="selectSetting(s)">
              {{ s.name }}<template v-if="showPerformance && s.perf !== undefined"> {{ s.perf }}</template>
              <b-icon v-if="s.desc !== undefined" icon="info-square"
                      class="ml-2" v-b-popover.hover.topright="s.desc">
              </b-icon>
            </b-dropdown-item>
          </b-dropdown>
        </template>
        <!-- Spinner Menu -->
        <template v-if="inputType === 'range'">
          <div :id="elemId" class="fixed-width-setting">
            <b-form-spinbutton v-model="rangeValue" :min="rangeMin" :max="rangeMax" :step="rangeStep" inline
                               :class="'spinner-setting btn-' + variant"
                               @change="spinnerSettingUpdated" :formatter-fn="spinnerDisplay">
            </b-form-spinbutton>
          </div>
        </template>
      </b-input-group-append>
    </b-input-group>
  </div>
</template>

<script>

export default {
  name: 'Setting',
  data: function () {
    return {
      currentSettingValue: {},
      elemId: 'setting' + this._uid, // _uid is a unique identifier for each vue component
      nameId: 'name' + this._uid,
      settingDesc: '',
      inputType: 'value',
      rangeMin: 0,
      rangeMax: 1,
      rangeStep: 1,
      rangeDisp: undefined,
      rangeValue: 0,
      spinnerTimeout: null,
      spinnerDebounceRate: 2000,
    }
  },
  props: {
    setting: Object, variant: String, fixWidth: Boolean, show_performance: Boolean,
    disabled: Boolean, groupId: String
  },
  methods: {
    selectSetting: function (s) {
      this.currentSettingValue = s.value
      console.log('Emitting setting update', this.setting.key, s.value)
      this.$emit('setting-changed', this.setting, s.value)
    },
    spinnerSettingUpdated: function () {
      clearTimeout(this.spinnerTimeout)
      this.spinnerTimeout = setTimeout(this.spinnerDebouncedUpdate, this.spinnerDebounceRate)
      this.currentSettingValue = this.rangeValue
    },
    spinnerDebouncedUpdate: function () {
      this.spinnerTimeout = null
      this.$emit('setting-changed', this.setting, this.rangeValue)
    },
    spinnerDisplay: function (value) {
      if (this.rangeDisp === 'floatpercent') { return String(Math.round(value * 100)) + '%' }
      return value
    },
    iterateSettings: function (func) {
      if (this.setting === undefined) { return }
      for (let i=0; i <= this.setting.settings.length; i++) {
        let setting = this.setting.settings[i]
        if (setting === undefined) { continue }
        func(this, setting)
      }
    },
    getMaxWidth: function (elements) {
      let maxWidth = 0
      for (let i in elements) {
        if (elements[i].clientWidth !== undefined) {
          maxWidth = Math.max(maxWidth, parseInt(elements[i].clientWidth))
        }
      }
      return maxWidth
    },
    setFixedWidth: function () {
      // Iterate all elements of this setting group_id and set width to widest element found
      const nameElem = document.querySelectorAll('#' + this.groupId + ' .fixed-width-name')
      const settElem = document.querySelectorAll('#' + this.groupId + ' .fixed-width-setting')

      let nameMaxWidth = this.getMaxWidth(nameElem); let settMaxWidth = this.getMaxWidth(settElem)

      let e = document.getElementById(this.nameId)
      if (e !== null) { e.style.width = String(nameMaxWidth) + 'px' }
      let s = document.getElementById(this.elemId)
      if (s !== null) { s.style.width = String(settMaxWidth) + 'px' }
    },
  },
  created: function () {
    // Set description
    this.settingDesc = this.setting.desc || ''

    // Check Setting Type
    if (this.setting.settings[0].settingType !== undefined) {
      if (this.setting.settings[0].settingType === 'range') {
        this.inputType = 'range'
        this.rangeMin = this.setting.settings[0].min
        this.rangeMax = this.setting.settings[0].max
        this.rangeStep = this.setting.settings[0].step
        this.rangeDisp = this.setting.settings[0].display
        this.rangeValue = this.setting.value
        this.settingDesc = this.setting.desc || this.setting.settings[0].desc || ''
      }
    }
  },
  mounted () {
    if (this.variant === undefined) { this.variant = 'secondary'}
    this.currentSettingValue = this.setting.value
    if (this.fixWidth) {
      // Access after rendering finished
      setTimeout(() => {
        this.setFixedWidth()
      }, 0)
    }
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
    showPerformance: function () {
      if (this.show_performance !== undefined) { return this.show_performance }
      return false
    },
    settingHidden: function () {
      if (this.setting === undefined) { return true }
      return this.setting['hidden'] || false
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style>
.setting { display: inline-block }
.setting-item { min-width: 7.0rem; font-weight: lighter; }
.spinner-setting { width: 100% !important; }
</style>
