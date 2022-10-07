<template>
  <div v-cloak id="dev_presets">
    <b-button variant="danger" @click="createDevGfxPresets">Queue Dev Presets</b-button>
  </div>
</template>

<script>
export default {
  name: "DevPresets",
  data: function () {
    return {
      a: true,
      devPresets: [],
      devPresetSettings: {
        video_settings: {
          'MSAA': [
            {value: 4, name: 'MSAA-4x'},
            {value: 8, name: 'MSAA-8x'}
          ],
          'EPostProcessingSettings': [
            {value: 1, name: 'PostProcessing-Off'},
            {value: 3, name: 'PostProcessing-Medium'},
            {value: 4, name: 'PostProcessing-High'},
            {value: 5, name: 'PostProcessing-Ultra'},
          ]
        },
        graphic_options: {
          'Track Detail': [
            {value: 0, name: 'TrackDetail-Low'},
            {value: 1, name: 'TrackDetail-Medium'},
            {value: 2, name: 'TrackDetail-High'},
            {value: 3, name: 'TrackDetail-Full'},
          ],
          'Texture Detail': [
            {value: 0, name: 'TextureDetail-Low'},
            {value: 3, name: 'TextureDetail-Full'},
          ],
          'Special FX': [
            {value: 0, name: 'SpecialFx-Off'},
            {value: 4, name: 'SpecialFx-Ultra'},
          ],
          'Shadows': [
            {value: 0, name: 'Shadows-Off'},
            {value: 1, name: 'Shadows-Low'},
            {value: 2, name: 'Shadows-Medium'},
            {value: 3, name: 'Shadows-High'},
            {value: 4, name: 'Shadows-Ultra'}
          ],
          'Rain FX Quality': [
            {value: 1, name: 'RainFxQuality-Off'},
            {value: 3, name: 'RainFxQuality-Medium'},
            {value: 4, name: 'RainFxQuality-High'},
            {value: 5, name: 'RainFxQuality-Ultra'}
          ]
        },
      }
    }
  },
  props: {preset: Object},
  methods: {
    createDevGfxPresets: function () {
      this.devPresets = []

      // Iterate every Setting and create a preset per setting
      for (let setting_app_key in this.devPresetSettings) {
        let settings = this.devPresetSettings[setting_app_key]
        for (let option_key in settings) {
          let options = settings[option_key]
          for (let i = 0; i < options.length; i++) {
            let option = options[i]
            this.createDevGfxPreset(setting_app_key, option_key, option)
          }
        }
      }
    },
    createDevGfxPreset: function (settingAppKey, optionKey, option) {
      // Create a copy of the current gfxPreset
      let presetCopy = JSON.parse(JSON.stringify(this.preset))
      presetCopy.name = option.name

      // Alter the setting
      presetCopy[settingAppKey].options.forEach(settingOption => {
        if (settingOption.key === optionKey) {
          settingOption.value = option.value
        }
      })
      this.devPresets.push(presetCopy)
    }
  },
}
</script>

<style scoped>

</style>