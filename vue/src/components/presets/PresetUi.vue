<template>
  <div id="preset-ui" v-cloak>
    <template v-if="presets.length > 0">
      <b-input-group>
        <!-- Switch View Mode -->
        <b-input-group-prepend>
          <b-button @click="toggleViewMode" class="rounded-left">
            <b-icon :icon="viewMode ? 'grid-fill' : 'list'"></b-icon>
          </b-button>
          <b-input-group-text class="info-field">{{ displayName }}</b-input-group-text>

          <!-- Preset Folder Select -->
          <b-button v-b-popover.hover.bottom="'Customize Presets save location'"
                    squared variant="secondary" id="preset-folder">
            <b-icon icon="folder-fill"></b-icon>
          </b-button>

          <!-- Folder Select Popover -->
          <b-popover target="preset-folder" triggers="click">
            <h5>Preset Save Location</h5>
            <p>Paste a path in the Format <i>C:\Dir\MyDir</i></p>
            <b-form-input size="sm" v-model="userPresetsDirInput"
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
        <b-dropdown :text="currentPresetName" variant="rf-blue" toggle-class="rounded-0">
          <b-dropdown-item v-for="preset in presets" :key="preset.name"
                           @click="selectPreset(preset)">
            {{ preset.name }}
          </b-dropdown-item>
        </b-dropdown>

        <!-- New Preset Name -->
        <b-form-input v-model="newPresetName" :state="presetFileNameState" class="no-border"
                      type="text" placeholder="[New Preset Name]" :id="'preset-name-input' + _uid"
                      v-b-popover.hover.bottom="'Enter a name for a new Preset and click the + button'">
        </b-form-input>

        <b-input-group-append>
          <!-- Add/Export/Del Preset Buttons -->
          <b-button :disabled="!addButtonState" variant="secondary" @click="createPreset">
            <b-icon icon="plus"></b-icon>
          </b-button>

          <b-button variant="secondary" @click="$emit('refresh')"
                    v-b-popover.hover.bottom="'Refresh Presets if you updated a setting in-game'">
            <b-icon icon="arrow-repeat"></b-icon>
          </b-button>
          <b-button variants="secondary" @click="exportCurrentPreset"
                    v-b-popover.hover.bottom="'Export current Preset to your documents dir to be able to share it!'">
            <b-icon icon="file-earmark-arrow-up-fill"></b-icon>
          </b-button>
          <b-button :disabled="!deleteButtonState" variant="secondary" :id="'delete-preset-btn' + idRef" class="rounded-right">
            <b-icon icon="trash-fill"></b-icon>
          </b-button>

          <!-- Delete Popover -->
          <b-popover :target="'delete-preset-btn' + idRef" triggers="click">
            <p>Do you really want to delete the Preset: {{ currentPresetName }}?</p>
            <div class="text-right">
              <b-button @click="deletePreset" size="sm" variant="danger"
                        aria-label="Delete" class="mr-2">
                Delete
              </b-button>
              <b-button @click="$root.$emit('bv::hide::popover', 'delete-preset-btn' + idRef)"
                        size="sm" aria-label="Close">
                Close
              </b-button>
            </div>
          </b-popover>
        </b-input-group-append>

        <!-- New Preset Name invalid feedback -->
        <b-form-invalid-feedback :id="'preset-name-input' + _uid + '-feedback'">
          Enter a valid Windows file name
        </b-form-invalid-feedback>
      </b-input-group>

      <!-- editable Preset Description -->
      <div class="desc-container">
        <b-form-textarea v-model="presetDesc" class="mt-2 bg-dark text-white desc-textarea"
                         placeholder="Enter a description or notes for your preset ..." debounce="6000"
                         rows="2" spellcheck="false" style="border: none;">
        </b-form-textarea>
        <div class="desc-icon">
          <b-icon class="text-muted" icon="pencil"></b-icon>
        </div>
      </div>

      <!-- Preset deviates from current rF2 settings message -->
      <b-alert :show="previousPresetName !== ''" dismissible variant="warning" class="mt-3">
        <h5><b-icon class="mr-1" icon="exclamation-triangle-fill"></b-icon>Settings difference on disk</h5>
        The previously selected Preset <i>{{ previousPresetName }}</i> has different settings than the current
        rFactor 2 settings on disk.
        <b-link @click="restorePreviousPreset" class="text-rf-orange">
          Click here to select your previous Preset <i>{{ previousPresetName }}</i> and restore it's
          settings.
        </b-link>
      </b-alert>
    </template>
  </div>
</template>

<script>
import {isValid} from "@/main";

export default {
  name: "PresetUi",
  data: function () {
    return {
      newPresetName: '',
      presetDesc: '',
      ignoreDescUpdate: false,
      componentReady: false,
      userPresetsDirInput: '',
      viewMode: 0,
    }
  },
  props: { presets: Object, previousPresetName: String, selectedPresetIdx: Number, idRef: Number,
           presetDir: String, displayName: String },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    restorePreviousPreset: async function () {
      this.presets.forEach(preset => {
        if (preset.name === this.previousPresetName) { this.selectPreset(preset) }
      })
    },
    getSelectedPreset: function () {
      if (this.presets.length === 0) { return {} }
      return this.presets[this.selectedPresetIdx]
    },
    exportCurrentPreset: async function () {
      this.$emit('export-current')
    },
    selectPreset: async function (preset) {
      this.getReady()
      this.$emit('select-preset', preset, true)
      this.presetDesc = preset.desc
    },
    createPreset: async function () {
      this.$emit('create-preset', this.newPresetName)
      this.newPresetName = ''
    },
    deletePreset: async function () {
      this.$emit('delete-preset')
    },
    setPresetsDir: async function () {
      this.$emit('update-presets-dir', this.userPresetsDirInput)
      this.$root.$emit('bv::hide::popover', 'preset-folder')
    },
    updateSetting: async function (setting, value, save = true) {
      this.$emit('update-setting', setting, value, save)
    },
    getReady() {
      // Avoid Preset desc field spamming update events
      this.componentReady = false; setTimeout( this.setReady , 500)
    },
    toggleViewMode() {
      this.viewMode = !this.viewMode ? 1 : 0
      this.$emit('update-view-mode', this.viewMode)
    },
    setReady() { this.componentReady = true; console.log('Comp ready') }
  },
  watch: {
    presetDesc: function (value) { if (this.componentReady) {
      if (this.ignoreDescUpdate) { return }
      this.$emit('update-desc', value)
      console.log('Updating desc:', value)
    }}
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
      if (this.newPresetName.startsWith('Current_Settings')) { return null }
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
    this.userPresetsDirInput = this.presetDir
    this.getReady()
  },
  updated() {
    this.ignoreDescUpdate = true
    this.presetDesc = this.getSelectedPreset().desc
    this.$nextTick(() => {this.ignoreDescUpdate = false  })
  }
}
</script>

<style scoped>
.desc-container { position: relative; }
.desc-textarea { position: relative; }
.desc-icon { position: absolute; z-index: 99; right: .75rem; top: .5rem; font-size: .75rem }
</style>