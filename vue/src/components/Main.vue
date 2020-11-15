<template>
  <div id="main">
    <div class="title">
      <b-img src="@/assets/rf2_logo.png" width="128" alt="rFactor 2 logo" class="m-3"></b-img>
      <h4><i>rFactor 2 Graphic Settings Widget</i></h4>
    </div>
    <p></p>
    <template v-if="presets.length > 0">
      <!-- Preset Selection-->
      <b-input-group>
        <b-input-group-prepend>
          <b-input-group-text>Presets</b-input-group-text>
        </b-input-group-prepend>

        <b-dropdown :text="currentPresetName" variant="rf-blue">
          <b-dropdown-item v-for="preset in presets" :key="preset.name"
                           @click="selectPreset(preset)">
            {{ preset.name }}
          </b-dropdown-item>
        </b-dropdown>
        <b-form-input v-model="newPresetName" type="text" :placeholder="currentPresetName"
                      v-b-popover.hover.top="'Enter a name for a new Preset and click the + button'">
        </b-form-input>

        <b-input-group-append>
          <b-button variant="success" @click="createPreset"><b-icon icon="plus"></b-icon></b-button>
        </b-input-group-append>
      </b-input-group>

      <div v-for="(preset, idx) in presets" :key="preset.name">
        <!-- Display Settings -->
        <b-card :title="preset.graphic_options.title" v-if="selectedPresetIdx === idx"
                class="bg-dark text-white mt-3">
          <Setting v-for="setting in preset.graphic_options.options" :key="setting.key"
                   :setting="setting" variant="rf-orange"
                   v-on:setting-changed="updateSetting">
          </Setting>
        </b-card>
      </div>
    </template>
  </div>
</template>

<script>
import Setting from "./Setting.vue";
import {getEelJsonObject} from '@/main'
require("@/assets/rf2_logo.png")

export default {
  name: 'Main',
  data: function () {
    return {
      presets: [],
      selectedPresetIdx: 0,
      newPresetName: '',
    }
  },
  methods: {
    getPresets: async function () {
      this.presets = await getEelJsonObject(window.eel.get_presets()())

      for (let i = 0; i <= this.presets.length; i++) {
        let preset = this.presets[i]
        if (preset === undefined) { continue }
        console.log('Refreshed Graphic Settings for', preset.graphic_options.title)
      }
    },
    getSelectedPreset: function () {
      return this.presets[this.selectedPresetIdx]
    },
    updateSetting: function(setting, value) {
      setting.value = value
      console.log('Updated', setting.name, 'to', setting.value)
      window.eel.save_preset(this.getSelectedPreset())
    },
    selectPreset: function (preset) {
      this.selectedPresetIdx = this.presets.indexOf(preset)
    },
    createPreset: function () {
      let preset = {}
      preset['name'] = this.newPresetName
      let graphicOptions = JSON.stringify(this.getSelectedPreset().graphic_options)
      preset['graphic_options'] = JSON.parse(graphicOptions)
      this.presets.push(preset)
      console.log('Created preset:', preset)
      this.selectPreset(preset)
    },
  },
  components: {
    Setting
  },
  computed: {
    currentPresetName: function () {
      if (this.presets.length === 0) { return 'Unknown'}
      return this.getSelectedPreset().name
    }
  },
  created: function() {
    this.getPresets()
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  #main {
    width: 90%;
    margin: 0 auto 0 auto;
  }
  .title {
    font-family: "Ubuntu", sans-serif;
    font-weight: bold;
  }
</style>
