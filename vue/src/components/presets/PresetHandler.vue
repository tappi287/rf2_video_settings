<template>
  <div style="display: none"></div>
</template>

<script>
import {getEelJsonObject, sleep} from "@/main";

function sortPresets (receivedPresets) {
  // First received preset from API is "Current Preset"
  // Sort the rest by name
  let sortedPresets = receivedPresets.slice(1)
  sortedPresets.sort((a, b) => {
      let fa = a.name.toLowerCase(),
          fb = b.name.toLowerCase()
      if (fa < fb) { return -1 }
      if (fa > fb) { return 1 }
      return 0
  })

  // Insert "Current Preset" at index 0
  sortedPresets.splice(0, 0, receivedPresets[0])

  return sortedPresets
}

export default {
  name: "PresetHandler",
  data: function () {
    return {
      presets: [],
      selectedPresetIdx: 0,
      userPresetsDir: '',
      previousPresetName: '',
      viewMode: 0,
      error: '',
    }
  },
  props: { presetType: Number, idRef: String, ignoreDeviations: Boolean },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) {this.$emit('set-busy', busy) },
    getPresetTypeName: function (pType) {
      if (pType === 0) { return 'Graphics Settings'}
      if (pType === 1) { return 'Generic Settings'}
      if (pType === 2) { return 'Control Settings'}
      if (pType === 3) { return 'Session Settings'}
      return 'Settings'
    },
    getPresetsDirLocation: async function () {
      this.userPresetsDir = await window.eel.get_user_presets_dir_web()()
    },
    _addPreset: function (newPreset) {
      this.presets.push(newPreset)
      this.presets = sortPresets(this.presets)
    },
    getPresets: async function () {
      this.setBusy(true)
      const r = await getEelJsonObject(window.eel.get_presets(this.presetType)())

      if (!r.result) {
        this.$emit('error', r.msg)
        return
      }
      this.presets = []

      this.presets = sortPresets(r.presets)
      let appSelectedPresetIdx = -1
      if (r.preset_changed !== null && !this.ignoreDeviations) {
        this.previousPresetName = r.preset_changed
        this.makeToast('Detected settings deviations to previously selected Preset ' + this.previousPresetName +
            ' on disk. Pointing you to the "Current Preset" reflecting the actual settings on disk.',
            'secondary',this.getPresetTypeName(this.presetType), true, 15000)
        // Force re-draw of Presets
        this.$eventHub.$emit('navigate', -1)
      }

      for (let i = 0; i <= this.presets.length; i++) {
        let preset = this.presets[i]
        if (preset === undefined) {
          continue
        }
        if (preset.name === r.selected_preset) {
          console.log('Found selected Preset:', i, preset.name)
          appSelectedPresetIdx = i
        }
        console.log('Refreshed Settings for', preset.name)
      }
      if (this.presets[appSelectedPresetIdx] !== undefined) {
        await this.selectPreset(this.presets[appSelectedPresetIdx], false)
      }
      this.setBusy(false)
      this.$nextTick(() => { this.$emit('presets-ready') })
    },
    getSelectedPreset: function () {
      if (this.presets.length === 0) { return {} }
      return this.presets[this.selectedPresetIdx]
    },
    savePreset: async function (preset) {
      this.setBusy(true)
      const r = await getEelJsonObject(window.eel.save_preset(preset)())
      this.previousPresetName = ''
      if (!r.result) {
        this.makeToast(r.msg, 'danger')
        console.error('Error writing preset to rFactor 2!', r.msg)
        console.log(r)
      } else {
        console.log('Saved Preset:', preset.name)
      }
      this.setBusy(false)
    },
    exportPreset: async function () {
      this.setBusy(true)
      const r = await getEelJsonObject(window.eel.export_preset(this.getSelectedPreset())())
      this.previousPresetName = ''
      if (!r.result) {
        console.log(r, r.result)
        this.makeToast(r.msg, 'danger')
        console.error('Error writing preset to rFactor 2!', r.msg)
      }
      this.setBusy(false)
    },
    importPlayerJson: async function (importData) {
      if (importData === undefined) { return }
      this.setBusy(true)

      let r = await getEelJsonObject(window.eel.import_player_json(importData, this.presetType)())
      if (r !== undefined && r.result) {
        this._addPreset(r.preset)
        this.makeToast(r.msg, 'success', 'Player.JSON Import')
      } else {
        this.makeToast('Data could not be imported ' + r.msg, 'danger', 'Error')
      }

      this.setBusy(false)
    },
    importPreset: async function (importPreset) {
      if (importPreset === undefined) {
        return
      }
      this.setBusy(true)
      // Avoid doubled preset names
      for (let i = 0; i <= this.presets.length; i++) {
        let preset = this.presets[i]
        if (preset === undefined) {
          continue
        }
        if (preset.name === importPreset.name) {
          importPreset.name = importPreset.name + '_imp'
        }
      }

      let r = await getEelJsonObject(window.eel.import_preset(importPreset)())
      if (r !== undefined && r.result) {
        this._addPreset(r.preset)
        this.makeToast('Preset ' + importPreset.name + ' imported.')
      } else {
        this.makeToast('Preset ' + importPreset.name + ' could not be imported.',
            'danger', 'Error')
      }

      this.setBusy(false)
    },
    selectPreset: async function (preset, save = false) {
      this.setBusy(true)
      this.selectedPresetIdx = this.presets.indexOf(preset)
      let p = this.getSelectedPreset()
      await window.eel.select_preset(p.name, this.presetType)
      if (save) {
        await this.savePreset(p)
        await sleep(150)
      }
      this.setBusy(false)
    },
    createPreset: async function (newPresetName = 'New Preset') {
      this.setBusy(true)

      let preset = {}

      // Clone properties of the currently selected preset
      const keys = Object.keys(this.getSelectedPreset())
      keys.forEach(key => {
        const options = JSON.stringify(this.getSelectedPreset()[key])
        preset[key] = JSON.parse(options)
      })

      preset['name'] = newPresetName
      preset['desc'] = ''

      this._addPreset(preset)
      console.log('Created preset:', preset)

      await this.selectPreset(preset, false)

      await this.savePreset(this.getSelectedPreset())
      await sleep(150)
      this.setBusy(false)
    },
    deletePreset: async function () {
      this.setBusy(true)
      const preset = this.getSelectedPreset()
      const index = this.presets.indexOf(preset);

      if (index > -1) {
        console.log('Deleting Preset -', index)
        const r = await getEelJsonObject(window.eel.delete_preset(preset.name, this.presetType)())
        if (!r.result) {
          this.makeToast('Could not delete Preset', 'danger', 'Error')
          this.$root.$emit('bv::hide::popover', 'delete-preset-btn' + this.idRef)
          this.setBusy(false)
          return
        }
        this.presets.splice(index, 1)
        this.selectedPresetIdx = 0
      }
      this.$root.$emit('bv::hide::popover', 'delete-preset-btn' + this.idRef)
      this.setBusy(false)
    },
    setPresetsDir: async function (newUserPresetsDir) {
      const r = await getEelJsonObject(window.eel.set_user_presets_dir(newUserPresetsDir)())

      if (r !== undefined && r.result) {
        this.makeToast('Updated User Presets directory to: ' + this.userPresetsDir, 'success')
        await this.getPresetsDirLocation()
        await this.getPresets()
      } else {
        this.makeToast('Could not update User Preset Directory. Provided path does not exists or ' +
            'is not accessible.', 'danger')
        await this.getPresetsDirLocation()
      }
    },
    updateDesc: function (newDesc) {
      if (newDesc === undefined || newDesc === null) { return }
      this.getSelectedPreset().desc = newDesc
      this.savePreset(this.getSelectedPreset())
    },
    updateViewMode: function (viewMode) {
      this.viewMode = viewMode
    },
    updateSetting: async function (setting, value, save = true) {
      this.setBusy(true)
      setting.value = value
      console.log('Updated', setting.name, 'to', setting.value)
      if (save) { await this.savePreset(this.getSelectedPreset()) }
      this.setBusy(false)
    },
    update: async function () { await this.savePreset(this.getSelectedPreset()) },
    emitCurrentGfxPreset: async function () {
      if (this.presetType !== 0) { return }
      this.$eventHub.$emit('currentGfxPreset', this.getSelectedPreset())
    }
  },
  created() {
    this.getPresets()
    this.getPresetsDirLocation()
    this.$eventHub.$on('getCurrentGfxPreset', this.emitCurrentGfxPreset)
  },
  destroyed() {
    this.$eventHub.$off('getCurrentGfxPreset', this.emitCurrentGfxPreset)
  }
}
</script>

<style scoped>

</style>