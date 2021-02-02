<template>
  <div id="graphics" v-cloak>
    <template v-if="presets.length > 0">
      <b-overlay :show="isBusy" variant="light">
        <b-input-group>
          <!-- Switch View Mode -->
          <b-input-group-prepend>
            <b-button @click="viewMode = !viewMode ? 1 : 0">
              <b-icon :icon="viewMode ? 'grid-fill' : 'list'"></b-icon>
            </b-button>
            <b-input-group-text class="info-field">Presets</b-input-group-text>

            <!-- Preset Folder Select -->
            <b-button v-b-popover.hover.bottom="'Customize Presets save location'"
                      squared variant="rf-yellow" id="preset-folder">
              <b-icon icon="folder-fill"></b-icon>
            </b-button>

            <!-- Folder Select Popover -->
            <b-popover target="preset-folder" triggers="click">
              <h5>Preset Save Location</h5>
              <p>Paste a path in the Format <i>C:\Dir\MyDir</i></p>
              <b-form-input size="sm" v-model="userPresetsDir"
                            placeholder="Paste a custom folder location">
              </b-form-input>
              <div class="text-right mt-1">
                <b-button @click="setPresetsDir" size="sm" variant="primary"
                          aria-label="Save">
                  Save
                </b-button>
                <b-button @click="$root.$emit('bv::hide::popover', 'preset-folder')"
                          size="sm" aria-label="Close">
                  Close
                </b-button>
              </div>
            </b-popover>
          </b-input-group-prepend>

          <!-- Preset Selection-->
          <b-dropdown :text="currentPresetName" variant="rf-blue">
            <b-dropdown-item v-for="preset in presets" :key="preset.name"
                             @click="selectPreset(preset)">
              {{ preset.name }}
            </b-dropdown-item>
          </b-dropdown>

          <!-- New Preset Name -->
          <b-form-input v-model="newPresetName" :state="presetFileNameState"
                        type="text" placeholder="[New Preset Name]" id="preset-name-input"
                        v-b-popover.hover.bottom="'Enter a name for a new Preset and click the + button'">
          </b-form-input>

          <b-input-group-append>
            <!-- Add/Export/Del Preset Buttons -->
            <b-button :disabled="!addButtonState" variant="success" @click="createPreset">
              <b-icon icon="plus"></b-icon>
            </b-button>
            <b-button variant="rf-blue" @click="getPresets"
                      v-b-popover.hover.bottom="'Refresh Presets if you updated a setting in-game'">
              <b-icon icon="arrow-repeat"></b-icon>
            </b-button>
            <b-button variants="secondary" @click="exportCurrentPreset"
                      v-b-popover.hover.bottom="'Export current Preset to your documents dir to be able to share it!'">
              <b-icon icon="file-earmark-arrow-up-fill"></b-icon>
            </b-button>
            <b-button :disabled="!deleteButtonState" variant="rf-red" id="delete-preset-btn">
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

          <!-- New Preset Name invalid feedback -->
          <b-form-invalid-feedback id="preset-name-input-feedback">
            Enter a valid Windows file name
          </b-form-invalid-feedback>
        </b-input-group>

        <!-- editable Preset Description -->
        <b-form-textarea id="preset-textarea" v-model="presetDesc" class="mt-2 bg-dark text-white"
                         placeholder="Enter a description for your preset ..."
                         rows="2" spellcheck="false" style="border: none;">
        </b-form-textarea>

        <!-- Preset deviates from current rF2 settings message -->
        <b-alert :show="previousPresetName !== ''" dismissible variant="warning" class="mt-3">
          The previously selected Preset <i>{{ previousPresetName }}</i> has different settings than the actual
          rFactor 2 settings on disk.
        </b-alert>

        <!-- Settings area -->
        <div :id="settingsAreaId">
          <div v-for="(preset, idx) in presets" :key="preset.name">
            <GraphicsSettingsArea :preset="preset" :idx="idx" :current_preset_idx="selectedPresetIdx"
                                  :view_mode="viewMode" v-on:update-setting="updateSetting">
            </GraphicsSettingsArea>
          </div>
        </div>
      </b-overlay>
    </template>
  </div>
</template>

<script>
import {getEelJsonObject, isValid, settingsAreaId, sleep} from "@/main";
import GraphicsSettingsArea from "@/components/GraphicsSettingsArea";

export default {
  name: "Graphics",
  data: function () {
    return {
      presets: [],
      selectedPresetIdx: 0,
      newPresetName: '',
      presetDesc: '',
      userPresetsDir: '',
      isBusy: false,
      viewMode: 0,
      previousPresetName: '',
      error: '',
      settingsAreaId: settingsAreaId,
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    getPresetsDirLocation: async function () {
      this.userPresetsDir = await window.eel.get_user_presets_dir_web()()
    },
    getPresets: async function () {
      this.isBusy = true
      this.presets = []
      const preset_data = await getEelJsonObject(window.eel.get_presets()())

      if (preset_data === undefined || preset_data === null) {
        this.$emit('error', 'Error obtaining presets.')
        return
      }

      this.presets = preset_data.presets
      let appSelectedPresetIdx = -1
      let changeMsg = ''
      let msgDelay = 3000
      if (preset_data.preset_changed !== null) {
        this.previousPresetName = preset_data.preset_changed
        changeMsg = 'Detected settings deviations to previously selected Preset ' + this.previousPresetName +
            ' on disk. Pointing you to the "Current Preset" reflecting the actual settings on disk.'
        msgDelay = 15000
      }

      for (let i = 0; i <= this.presets.length; i++) {
        let preset = this.presets[i]
        if (preset === undefined) { continue }
        if (preset.name === preset_data.selected_preset) {
          appSelectedPresetIdx = i
        }
        console.log('Refreshed Settings for', preset.name)
      }
      if (this.presets[appSelectedPresetIdx] !== undefined) {
        await this.selectPreset(this.presets[appSelectedPresetIdx], false)
      }
      if (changeMsg !== '') {
       this.makeToast('Presets loaded. ' + changeMsg, 'secondary',
           'Graphics Preset', true, msgDelay)
       await sleep(100)
      }
      this.isBusy = false
    },
    getSelectedPreset: function () {
      return this.presets[this.selectedPresetIdx]
    },
    _savePreset: async function (preset) {
      const r = await getEelJsonObject(window.eel.save_preset(preset)())
      this.previousPresetName = ''
      if (!r.result) {
        this.makeToast(r.msg, 'danger')
        console.error('Error writing preset to rFactor 2!', r.msg)
      }
      console.log('Saved Preset:', preset.name)
      return r
    },
    _exportPreset: async function (preset) {
      const r = await getEelJsonObject(window.eel.export_preset(preset)())
      this.previousPresetName = ''
      console.log(r)
      console.log(r.result)
      if (!r.result) {
        this.makeToast(r.msg, 'danger')
        console.error('Error writing preset to rFactor 2!', r.msg)
      }
      return r
    },
    exportCurrentPreset: async function () {
      this.isBusy = true
      await this._exportPreset(this.getSelectedPreset())
      this.isBusy = false
    },
    importPreset: async function(importPreset) {
      if (importPreset === undefined) { return }
      this.isBusy = true
      // Avoid doubled preset names
      for (let i = 0; i <= this.presets.length; i++) {
        let preset = this.presets[i]
        if (preset === undefined) { continue }
        if (preset.name === importPreset.name) {
          importPreset.name = importPreset.name + '_imp'
        }
      }

      let r = await getEelJsonObject(window.eel.import_preset(importPreset)())
      if (r !== undefined && r.result) {
        this.presets.push(r.preset)
        this.makeToast('Preset ' + importPreset.name + ' imported.')
      } else {
        this.makeToast('Preset ' + importPreset.name + ' could not be imported.',
            'danger', 'Error')
      }

      this.isBusy = false
    },
    selectPreset: async function (preset, save = true) {
      this.isBusy = true
      this.selectedPresetIdx = this.presets.indexOf(preset)
      let p = this.getSelectedPreset()
      await window.eel.select_preset(p.name)
      if (save) {
        await this._savePreset(p)
        await sleep(150)
      }
      this.presetDesc = p.desc
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
    },
    setPresetsDir: async function () {
      let r = await getEelJsonObject(window.eel.set_user_presets_dir(this.userPresetsDir)())
      this.$root.$emit('bv::hide::popover', 'preset-folder')

      if (r !== undefined && r.result) {
        this.makeToast('Updated User Presets directory to: ' + this.userPresetsDir, 'success')
        await this.getPresetsDirLocation()
        await this.getPresets()
      } else {
        this.makeToast('Could not update User Preset Directory. Provided path does not exists or ' +
            'is not accessible.', 'danger')
      }
    },
    updateSetting: async function (setting, value) {
      this.isBusy = true
      setting.value = value
      console.log('Updated', setting.name, 'to', setting.value)
      await this._savePreset(this.getSelectedPreset())
      this.isBusy = false
    }
  },
  components: {
    GraphicsSettingsArea
  },
  watch: {
    presetDesc: function (value) { this.getSelectedPreset().desc = value }
  },
  computed: {
    currentPresetName: function () {
      if (this.presets.length === 0) { return 'Unknown' }
      return this.getSelectedPreset().name
    },
    presetFileNameState: function () {
      if (this.newPresetName === '') {
        return null
      }
      return isValid(this.newPresetName)
    },
    addButtonState: function () {
      return !!(this.newPresetName !== '' && this.presetFileNameState)
    },
    deleteButtonState: function () {
      return this.getSelectedPreset() !== this.presets[0]
    },
  },
  created: function () {
    this.getPresets()
    this.getPresetsDirLocation()
  }
}
</script>

<style scoped>

</style>