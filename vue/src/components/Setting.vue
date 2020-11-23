<template>
  <div class="setting" v-if="!settingHidden">
    <b-input-group size="sm" class="setting-field">
      <b-input-group-prepend>
        <b-input-group-text class="info-field fixed-width-name" :id="nameId">
          {{ setting.name }}
          <b-icon v-if="settingDesc !== ''" icon="info-square" class="ml-2 mr-1"
                      v-b-popover.hover.left="settingDesc">
          </b-icon>
        </b-input-group-text>
      </b-input-group-prepend>
      <b-input-group-append>
        <!-- Dropdown Menu -->
        <template v-if="inputType === 'value'">
          <b-dropdown :text="currentSettingName" :variant="variant" :id="elemId"
                      class="setting-item fixed-width-setting">
            <b-dropdown-item v-for="s in setting.settings" :key="s.value"
                             @click="selectSetting(s)">
              {{ s.name }}
              <b-icon v-if="s.desc !== undefined" icon="info-square"
                      v-b-popover.hover.left="s.desc">
              </b-icon>
            </b-dropdown-item>
          </b-dropdown>
        </template>
        <!-- Spinner Menu -->
        <template v-if="inputType === 'range'">
          <div :id="elemId" class="fixed-width-setting">
            <b-form-spinbutton v-model="rangeValue" :min="rangeMin" :max="rangeMax" inline
                               :class="'spinner-setting btn-' + variant"
                               @change="spinnerSettingUpdated">
            </b-form-spinbutton>
          </div>
        </template>
      </b-input-group-append>
    </b-input-group>
  </div>
</template>

<script>
import {settingsAreaId} from "@/main";

export default {
  name: 'Setting',
  data: function () {
    return {
      currentSettingValue: {},
      uniqueGroupId: 'settings' + this._uid,  // Id of parent element holding a group of Setting Components
      elemId: 'setting' + this._uid,
      nameId: 'name' + this._uid,
      settingsAreaId: settingsAreaId,
      settingDesc: '',
      inputType: 'value',
      rangeMin: 0,
      rangeMax: 1,
      rangeValue: 0,
    }
  },
  methods: {
    selectSetting: function (s) {
      this.currentSettingValue = s.value
      console.log('Emitting setting update', this.setting.key, s.value)
      this.$emit('setting-changed', this.setting, s.value)
    },
    spinnerSettingUpdated: function () {
      this.currentSettingValue = this.rangeValue
      this.$emit('setting-changed', this.setting, this.rangeValue)
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
      const nameElem = document.querySelectorAll('#' + this.group_id + ' .fixed-width-name')
      const settElem = document.querySelectorAll('#' + this.group_id + ' .fixed-width-setting')

      let nameMaxWidth = this.getMaxWidth(nameElem); let settMaxWidth = this.getMaxWidth(settElem)

      let e = document.getElementById(this.nameId)
      if (e !== null) { e.style.width = String(nameMaxWidth) + 'px' }
      let s = document.getElementById(this.elemId)
      if (s !== null) { s.style.width = String(settMaxWidth) + 'px' }
    },
  },
  props: {
    setting: Object, variant: String, fixWidth: Boolean, group_id: String
  },
  created: function () {
    // Check Setting Type
    if (this.setting.settings[0].settingType !== undefined) {
      if (this.setting.settings[0].settingType === 'range') {
        console.log('Found range')
        this.inputType = 'range'
        this.rangeMin = this.setting.settings[0].min
        this.rangeMax = this.setting.settings[0].max
        this.rangeValue = this.setting.value
        this.settingDesc = this.setting.settings[0].desc || ''
      }
    }
  },
  mounted () {
    if (this.group_id !== undefined) { this.uniqueGroupId = this.group_id }
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
