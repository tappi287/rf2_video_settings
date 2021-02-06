<template>
  <div id="graphics" v-cloak>
    <template v-if="gfxPresets.length > 0">
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
              <b-form-input size="sm" v-model="userGfxPresetsDir"
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
            <b-dropdown-item v-for="preset in gfxPresets" :key="preset.name"
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
              <b-icon icon="trash-fill"></b-icon>
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
                         placeholder="Enter a description for your preset ..." debounce="6000"
                         rows="2" spellcheck="false" style="border: none;">
        </b-form-textarea>

        <!-- Preset deviates from current rF2 settings message -->
        <b-alert :show="previousGfxPresetName !== ''" dismissible variant="warning" class="mt-3">
          The previously selected Preset <i>{{ previousGfxPresetName }}</i> has different settings than the actual
          rFactor 2 settings on disk.
        </b-alert>

        <!-- Settings area -->
        <div :id="settingsAreaId">
          <div v-for="(preset, idx) in gfxPresets" :key="preset.name">
            <GraphicsSettingsArea :preset="preset" :idx="idx" :current_preset_idx="selectedGfxPresetIdx"
                                  :view_mode="viewMode" v-on:update-setting="updateSetting">
            </GraphicsSettingsArea>
          </div>
        </div>
      </b-overlay>
    </template>
  </div>
</template>

<script>
import {isValid, settingsAreaId} from "@/main";
import GraphicsSettingsArea from "@/components/GraphicsSettingsArea";

export default {
  name: "Graphics",
  data: function () {
    return {
      newPresetName: '',
      presetDesc: '',
      userGfxPresetsDir: '',
      viewMode: 0,
      settingsAreaId: settingsAreaId,
    }
  },
  props: { gfxPresets: Object, previousGfxPresetName: String, selectedGfxPresetIdx: Number,
    gfxPresetDir: String, isBusy: Boolean},
  methods: {
    getSelectedPreset: function () {
      if (this.gfxPresets.length === 0) { return {} }
      return this.gfxPresets[this.selectedGfxPresetIdx]
    },
    exportCurrentPreset: async function () {
      this.$emit('export-current')
    },
    selectPreset: async function (preset) {
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
      this.$emit('update-presets-dir', this.userGfxPresetsDir)
      this.$root.$emit('bv::hide::popover', 'preset-folder')
    },
    updateSetting: async function (setting, value, save = true) {
      this.$emit('update-setting', setting, value, save)
    }
  },
  components: {
    GraphicsSettingsArea
  },
  watch: {
    presetDesc: function (value) { this.$emit('update-desc', value) }
  },
  computed: {
    currentPresetName: function () {
      if (this.gfxPresets.length === 0) { return 'Unknown' }
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
      return this.getSelectedPreset() !== this.gfxPresets[0]
    },
  },
  created: function () {
    this.userGfxPresetsDir = this.gfxPresetDir
    this.presetDesc = this.getSelectedPreset().desc
  }
}
</script>

<style scoped>

</style>