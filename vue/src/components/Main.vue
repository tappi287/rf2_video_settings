<template>
  <div id="main" v-cloak>
    <div class="text-left mt-2">
      <div class="float-right" v-if="error !== ''">
        <b-button @click="requestClose" size="sm">Close</b-button>
      </div>
      <h4>
        <b-img src="@/assets/app_icon.webp" width="64" alt="rFactor 2 logo" class="mr-3 logo-style"></b-img>
        <span class="title"><i>rFactor 2 Settings Widget</i></span>
      </h4>
    </div>
    <p></p>
    <template v-if="presets.length > 0">
      <b-overlay :show="isBusy" variant="light">
        <!-- Preset Selection-->
        <b-input-group>
          <b-input-group-prepend>
            <b-button @click="viewMode = !viewMode ? 1 : 0">
              <b-icon :icon="viewMode ? 'grid-fill' : 'list'"></b-icon>
            </b-button>
            <b-input-group-text class="info-field">Presets</b-input-group-text>
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
            <b-button variants="secondary" @click="exportCurrentPreset"
                      v-b-popover.hover.top="'Export current Preset to your documents dir to be able to share it!'">
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
          <b-form-invalid-feedback id="preset-name-input-feedback">
            Enter a valid Windows file name
          </b-form-invalid-feedback>
        </b-input-group>
        <b-form-textarea id="preset-textarea" v-model="presetDesc" class="mt-3"
                         placeholder="Enter a description for your preset ..."
                         rows="2" spellcheck="false">
        </b-form-textarea>
        <b-alert show dismissible variant="warning" class="mt-3" v-if="previousPresetName !== ''">
          The previously selected Preset <i>{{ previousPresetName }}</i> has different settings than the actual
          rFactor 2 settings on disk.
        </b-alert>

        <div v-for="(preset, idx) in presets" :key="preset.name">
          <!-- Video Settings -->
          <b-card v-if="selectedPresetIdx === idx" class="mt-3" id="video"
                  bg-variant="dark" text-variant="white">
            <template #header>
              <h6 class="mb-0"><span class="title">{{ preset.video_settings.title }}</span></h6>
            </template>
            <!-- View Mode Grid-->
            <Setting v-for="setting in preset.video_settings.options" :key="setting.key"
                     :setting="setting" variant="rf-orange" class="mr-3" group_id="video"
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
          <b-card v-if="selectedPresetIdx === idx" class="mt-3" id="graphic"
                  bg-variant="dark" text-variant="white">
            <template #header>
              <h6 class="mb-0"><span class="title">{{ preset.graphic_options.title }}</span></h6>
            </template>
            <template v-if="!viewMode">
              <Setting v-for="setting in preset.graphic_options.options" :key="setting.key"
                       :setting="setting" variant="rf-orange" class="mr-3 mb-3" :fixWidth="true"
                       group_id="graphic"
                       v-on:setting-changed="updateSetting">
              </Setting>
            </template>
            <template v-else>
              <b-list-group class="text-left">
                <b-list-group-item class="bg-transparent" v-for="setting in preset.graphic_options.options"
                                   :key="setting.key">
                  <Setting :setting="setting" variant="rf-orange" :fixWidth="true" group_id="graphic"
                           v-on:setting-changed="updateSetting">
                  </Setting>
                </b-list-group-item>
              </b-list-group>
            </template>
          </b-card>
          <!-- Advanced Display Settings -->
          <b-card v-if="selectedPresetIdx === idx" class="mt-3" id="advanced"
                  bg-variant="dark" text-variant="white">
            <template #header>
              <h6 class="mb-0"><span class="title">{{ preset.advanced_graphic_options.title }}</span></h6>
            </template>
            <Setting v-for="setting in preset.advanced_graphic_options.options" :key="setting.key"
                     :setting="setting" variant="rf-orange" group_id="advanced"
                     v-on:setting-changed="updateSetting">
            </Setting>
            <template #footer><span class="small font-weight-lighter">More settings available soon</span></template>
          </b-card>
        </div>
      </b-overlay>
    </template>
    <template v-if="error !== ''">
      <b-card class="mt-3" bg-variant="dark" text-variant="white">
        <template #header>
          <h6 class="mb-0"><span class="title">Error</span></h6>
        </template>
        <p>Could not detect a rFactor 2 Steam installation with a player.JSON and/or Config_DX11.ini</p>
        <pre>{{ error }}</pre>
        <p>
          Click here to try to re-run this application with administrative privileges:
          <b-button @click="reRunAsAdmin" size="sm">Re-Run</b-button>
        </p>
        <template #footer>
          <span class="small font-weight-lighter">
            Please make sure that a rFactor 2 Steam installation is present on your machine and that you have at least
            once started the game.
          </span>
        </template>
      </b-card>
    </template>
  </div>
</template>

<script>
import Setting from "./Setting.vue";
import {getEelJsonObject, isValid, sleep} from '@/main'

export default {
  name: 'Main',
  data: function () {
    return {
      presets: [],
      selectedPresetIdx: 0,
      newPresetName: '',
      presetDesc: '',
      isBusy: false,
      viewMode: 0,
      previousPresetName: '',
      error: ''
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$bvToast.toast(message, {
        title: title,
        autoHideDelay: delay,
        appendToast: append,
        variant: category,
        solid: true,
        isBusy: false
      })
    },
    requestClose: async function () {
      await window.eel.close_request()
    },
    reRunAsAdmin: async function () {
      await window.eel.re_run_admin()
    },
    getPresets: async function () {
      this.isBusy = true
      this.presets = []
      const preset_data = await getEelJsonObject(window.eel.get_presets()())
      if (preset_data === undefined || preset_data === null) { this.error = 'Error obtaining presets.'; return }
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
      this.makeToast('Presets loaded. ' + changeMsg, 'secondary', 'Start Up', true, msgDelay)
      await sleep(100)
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
      return r
    },
    _exportPreset: async function (preset) {
      const r = await getEelJsonObject(window.eel.export_preset(preset)())
      this.previousPresetName = ''
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
    updateSetting: async function (setting, value) {
      this.isBusy = true
      setting.value = value
      console.log('Updated', setting.name, 'to', setting.value)
      await this._savePreset(this.getSelectedPreset())
      this.isBusy = false
    },
    selectPreset: async function (preset, save = true) {
      this.isBusy = true
      this.selectedPresetIdx = this.presets.indexOf(preset)
      await window.eel.select_preset(this.getSelectedPreset().name)
      if (save) {
        await this._savePreset(this.getSelectedPreset())
        await sleep(150)
      }
      this.presetDesc = this.getSelectedPreset().desc
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
  watch: {
    presetDesc: function (value) { this.getSelectedPreset().desc = value }
  },
  computed: {
    currentPresetName: function () {
      if (this.presets.length === 0) {
        return 'Unknown'
      }
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
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#main {
  width: 90%;
  margin: 0 auto 0 auto;
}

.fix-width {
  width: 18rem;
}
</style>
