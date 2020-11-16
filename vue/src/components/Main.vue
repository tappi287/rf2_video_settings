<template>
  <div id="main">
    <div>
      <b-button class="float-left mt-4" @click="viewMode = !viewMode ? 1 : 0">
        <b-icon :icon="viewMode ? 'grid-fill' : 'list'"></b-icon>
      </b-button>
    </div>
    <div class="title">
      <b-img src="@/assets/app_icon.webp" width="128" alt="rFactor 2 logo" class="m-3"></b-img>
      <h4><i>rFactor 2 Graphic Settings Widget</i></h4>
    </div>
    <p></p>
    <template v-if="presets.length > 0">
      <b-overlay :show="isBusy" variant="light">
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
        <b-form-input v-model="newPresetName" :state="presetFileNameState"
                      type="text" placeholder="[New Preset Name]" id="preset-name-input"
                      v-b-popover.hover.top="'Enter a name for a new Preset and click the + button'">
        </b-form-input>

        <b-input-group-append>
          <!-- Add/Del Preset Buttons -->
          <b-button :disabled="!addButtonState" variant="success" @click="createPreset">
            <b-icon icon="plus"></b-icon>
          </b-button>
          <b-button variant="rf-blue" @click="getPresets"
                    v-b-popover.hover.top="'Refresh Presets if you updated a setting in-game'">
            <b-icon icon="arrow-repeat"></b-icon>
          </b-button>
          <b-button :disabled="!deleteButtonState" variant="danger" id="delete-preset-btn">
            <b-icon icon="x-circle-fill"></b-icon>
          </b-button>

          <!-- Delete Popover -->
          <b-popover target="delete-preset-btn" triggers="click">
            <p>Do you really want to delete the Preset: {{ currentPresetName }}?</p>
            <div class="text-right">
              <b-button @click="deletePreset" size="sm" variant="danger"
                        aria-label="Delete">
                Delete
              </b-button>
              <b-button @click="$root.$emit('bv::hide::popover', 'delete-preset-btn')"
                        size="sm" aria-label="Close">
                Close
              </b-button>
            </div>
          </b-popover>

        </b-input-group-append>
        <b-form-invalid-feedback id="preset-name-input-feedback">
          Enter a valid Windows file name
        </b-form-invalid-feedback>
      </b-input-group>

      <div v-for="(preset, idx) in presets" :key="preset.name">
        <!-- Video Settings -->
        <b-card v-if="selectedPresetIdx === idx" class="mt-3"
                bg-variant="secondary" text-variant="white">
          <template #header>
            <h6 class="mb-0">{{ preset.video_settings.title }}</h6>
          </template>
          <!-- View Mode Grid-->
          <Setting v-for="setting in preset.video_settings.options" :key="setting.key"
                   :setting="setting" variant="rf-orange" class="mr-3"
                   v-on:setting-changed="updateSetting">
          </Setting>
          <!-- Footer -->
          <template #footer>Use the in-game menu to change resolutions and window mode.</template>
        </b-card>
        <!-- Display Settings -->
        <b-card v-if="selectedPresetIdx === idx" class="mt-3"
                bg-variant="secondary" text-variant="white">
          <template #header>
            <h6 class="mb-0">{{ preset.graphic_options.title }}</h6>
          </template>
          <template v-if="!viewMode">
            <Setting v-for="setting in preset.graphic_options.options" :key="setting.key"
                     :setting="setting" variant="rf-orange" class="mr-3 mb-3" :fixWidth="true"
                     v-on:setting-changed="updateSetting">
            </Setting>
          </template>
          <template v-else>
            <b-list-group class="text-left">
              <b-list-group-item class="bg-transparent" v-for="setting in preset.graphic_options.options" :key="setting.key">
                <Setting :setting="setting" variant="rf-orange" :fixWidth="true"
                         v-on:setting-changed="updateSetting">
                </Setting>
              </b-list-group-item>
            </b-list-group>
          </template>
        </b-card>
        <!-- Advanced Display Settings -->
        <b-card v-if="selectedPresetIdx === idx" class="mt-3"
                bg-variant="secondary" text-variant="white">
          <template #header>
            <h6 class="mb-0">{{ preset.advanced_graphic_options.title }}</h6>
          </template>
          <Setting v-for="setting in preset.advanced_graphic_options.options" :key="setting.key"
                   :setting="setting" variant="rf-orange"
                   v-on:setting-changed="updateSetting">
          </Setting>
          <template #footer>More settings available soon.</template>
        </b-card>
      </div>
      </b-overlay>
    </template>
  </div>
</template>

<script>
import Setting from "./Setting.vue";
import {getEelJsonObject} from '@/main'
import {isValid} from "@/main";
import {sleep} from "@/main";

export default {
  name: 'Main',
  data: function () {
    return {
      presets: [],
      selectedPresetIdx: 0,
      newPresetName: '',
      isBusy: false,
      viewMode: 0,
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true) {
      this.$bvToast.toast(message, {
        title: title,
        autoHideDelay: 5000,
        appendToast: append,
        variant: category,
        isBusy: false,
      })
    },
    getPresets: async function () {
      this.isBusy = true
      this.presets = []
      const preset_data = await getEelJsonObject(window.eel.get_presets()())
      this.presets = preset_data.presets

      for (let i = 0; i <= this.presets.length; i++) {
        let preset = this.presets[i]
        if (preset === undefined) { continue }
        console.log('Refreshed Settings for', preset.name)
      }
      if (this.presets[preset_data.selected_preset] !== undefined) {
        await this.selectPreset(this.presets[preset_data.selected_preset], false)
      }
      this.makeToast('Presets loaded.', 'success')
      await sleep(100)
      this.isBusy = false
    },
    getSelectedPreset: function () {
      return this.presets[this.selectedPresetIdx]
    },
    _savePreset: async function (preset) {
      const r = await getEelJsonObject(window.eel.save_preset(preset)())
      if (!r.result) {
        this.makeToast(r.msg, 'danger')
        console.error('Error writing preset to rFactor 2!', r.msg)
      }
      return r
    },
    updateSetting: async function(setting, value) {
      this.isBusy = true
      setting.value = value
      console.log('Updated', setting.name, 'to', setting.value)
      await this._savePreset(this.getSelectedPreset())
      this.isBusy = false
    },
    selectPreset: async function (preset, save = true) {
      this.isBusy = true
      this.selectedPresetIdx = this.presets.indexOf(preset)
      await window.eel.select_preset(this.selectedPresetIdx)
      if (save) {
        await this._savePreset(this.getSelectedPreset())
        await sleep(150)
      }
      this.isBusy = false
    },
    createPreset: async function () {
      this.isBusy = true

      let preset = {}
      preset['name'] = this.newPresetName
      let graphicOptions = JSON.stringify(this.getSelectedPreset().graphic_options)
      let advancedGraphicOptions = JSON.stringify(this.getSelectedPreset().advanced_graphic_options)
      let videoSettings = JSON.stringify(this.getSelectedPreset().video_settings)
      preset['graphic_options'] = JSON.parse(graphicOptions)
      preset['advanced_graphic_options'] = JSON.parse(advancedGraphicOptions)
      preset['video_settings'] = JSON.parse(videoSettings)

      this.presets.push(preset)
      console.log('Created preset:', preset)

      await this.selectPreset(preset, false)
      this.newPresetName = ''

      await this._savePreset(this.getSelectedPreset())
      await sleep(150)
      this.isBusy = false
    },
    deletePreset: async function () {
      this.isBusy = true
      const preset = this.getSelectedPreset()
      const index = this.presets.indexOf(preset);

      if (index > -1) {
        console.log('Deleting Preset -', index)
        await window.eel.delete_preset(preset.name)
        this.presets.splice(index, 1)
        this.selectedPresetIdx = 0
      }
      this.$root.$emit('bv::hide::popover', 'delete-preset-btn')
      this.isBusy = false
    }
  },
  components: {
    Setting
  },
  computed: {
    currentPresetName: function () {
      if (this.presets.length === 0) { return 'Unknown'}
      return this.getSelectedPreset().name
    },
    presetFileNameState: function () {
      if (this.newPresetName === '') { return null }
      return isValid(this.newPresetName)
    },
    addButtonState: function () {
      return !!(this.newPresetName !== '' && this.presetFileNameState)
    },
    deleteButtonState: function () {
      return this.getSelectedPreset() !== this.presets[0]
    },
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
  .fix-width {
    width: 18rem;
  }
</style>
