<template>
  <div style="display: none"></div>
</template>

<script>
import {getEelJsonObject, sleep} from "@/main";

export default {
  name: "PresetHandler",
  data: function () {
    return {
      presets: [],
      selectedPresetIdx: 0,
      userPresetsDir: '',
      isBusy: false,
      previousPresetName: '',
      viewMode: 0,
      error: '',
    }
  },
  props: { presetType: Number, idRef: String },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    getPresetsDirLocation: async function () {
      this.userPresetsDir = await window.eel.get_user_presets_dir_web()()
    },
    getPresets: async function () {
      this.isBusy = true
      const r = await getEelJsonObject(window.eel.get_presets(this.presetType)())

      if (!r.result) {
        this.$emit('error', r.msg)
        return
      }
      this.presets = []

      this.presets = r.presets
      let appSelectedPresetIdx = -1
      if (r.preset_changed !== null) {
        this.previousPresetName = r.preset_changed
        this.makeToast('Detected settings deviations to previously selected Preset ' + this.previousPresetName +
            ' on disk. Pointing you to the "Current Preset" reflecting the actual settings on disk.',
            'secondary','Graphics Preset', true, 15000)
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
      this.isBusy = false
      this.$nextTick(() => { this.$emit('presets-ready') })
    },
    getSelectedPreset: function () {
      if (this.presets.length === 0) { return {} }
      return this.presets[this.selectedPresetIdx]
    },
    savePreset: async function (preset) {
      const r = await getEelJsonObject(window.eel.save_preset(preset)())
      this.previousPresetName = ''
      if (!r.result) {
        this.makeToast(r.msg, 'danger')
        console.error('Error writing preset to rFactor 2!', r.msg)
        console.log(r)
      } else {
        console.log('Saved Preset:', preset.name)
      }
    },
    exportPreset: async function () {
      this.isBusy = true
      const r = await getEelJsonObject(window.eel.export_preset(this.getSelectedPreset())())
      this.previousPresetName = ''
      if (!r.result) {
        console.log(r, r.result)
        this.makeToast(r.msg, 'danger')
        console.error('Error writing preset to rFactor 2!', r.msg)
      }
      this.isBusy = false
    },
    importPlayerJson: async function (importData) {
      if (importData === undefined) { return }
      this.isBusy = true

      let r = await getEelJsonObject(window.eel.import_player_json(importData, this.presetType)())
      if (r !== undefined && r.result) {
        this.presets.push(r.preset)
        this.makeToast(r.msg, 'success', 'Player.JSON Import')
      } else {
        this.makeToast('Data could not be imported ' + r.msg, 'danger', 'Error')
      }

      this.isBusy = false
    },
    importPreset: async function (importPreset) {
      if (importPreset === undefined) {
        return
      }
      this.isBusy = true
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
        this.presets.push(r.preset)
        this.makeToast('Preset ' + importPreset.name + ' imported.')
      } else {
        this.makeToast('Preset ' + importPreset.name + ' could not be imported.',
            'danger', 'Error')
      }

      this.isBusy = false
    },
    selectPreset: async function (preset, save = false) {
      this.isBusy = true
      this.selectedPresetIdx = this.presets.indexOf(preset)
      let p = this.getSelectedPreset()
      await window.eel.select_preset(p.name, this.presetType)
      if (save) {
        await this.savePreset(p)
        await sleep(150)
      }
      this.isBusy = false
    },
    createPreset: async function (newPresetName = 'New Preset') {
      this.isBusy = true

      let preset = {}

      // Clone properties of the currently selected preset
      const keys = Object.keys(this.getSelectedPreset())
      keys.forEach(key => {
        const options = JSON.stringify(this.getSelectedPreset()[key])
        preset[key] = JSON.parse(options)
      })

      preset['name'] = newPresetName

      this.presets.push(preset)
      console.log('Created preset:', preset)

      await this.selectPreset(preset, false)

      await this.savePreset(this.getSelectedPreset())
      await sleep(150)
      this.isBusy = false
    },
    deletePreset: async function () {
      this.isBusy = true
      const preset = this.getSelectedPreset()
      const index = this.presets.indexOf(preset);

      if (index > -1) {
        console.log('Deleting Preset -', index)
        const r = await getEelJsonObject(window.eel.delete_preset(preset.name, this.presetType)())
        if (!r.result) {
          this.makeToast('Could not delete Preset', 'danger', 'Error')
          this.$root.$emit('bv::hide::popover', 'delete-preset-btn' + this.idRef)
          this.isBusy = false
          return
        }
        this.presets.splice(index, 1)
        this.selectedPresetIdx = 0
      }
      this.$root.$emit('bv::hide::popover', 'delete-preset-btn' + this.idRef)
      this.isBusy = false
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
    updateSetting: async function (setting, value, save = true) {
      this.isBusy = true
      setting.value = value
      console.log('Updated', setting.name, 'to', setting.value)
      if (save) { await this.savePreset(this.getSelectedPreset()) }
      this.isBusy = false
    }
  },
  created() {
    this.getPresets()
    this.getPresetsDirLocation()
  }
}
</script>

<style scoped>

</style>