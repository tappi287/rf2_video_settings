<template>
  <div v-cloak id="dev_presets">
    <b-card class="pb-2 mb-2 setting-card" bg-variant="dark" text-variant="white" title="Dev Settings">
      <div class="text-left">
        <b-card-text>
          Use FpsVR for accurate CPU/GPU frame time measurements(Results not accessible via UI).
        </b-card-text>
        <b-card-text>
          Queue a set of predefined Dev GFX Presets iterating most performance heavy options to
          measure their impact. Enabling this will run the benchmark for quite a long time!
          The currently selected GfxPreset will be used as the base Preset.
        </b-card-text>
        <b-card-text>
          <div class="text-center">
            <b-button size="sm" v-b-toggle.collapse-dev-1 class="btn-rf-secondary">Show Settings</b-button>
            <b-button size="sm" class="btn-rf-orange" @click="createDevGfxPresets">Queue Dev Presets</b-button>
          </div>
          <b-collapse class="mb-2" id="collapse-dev-1">

            <div v-for="(settings, name, index) in devPresetSettings" :key="index">
              {{ name }}

              <ul v-for="(options, sName, sIdx) in settings" :key="sIdx">

                <div class="d-flex">
                  <div class="d-inline-flex mr-2">{{ sName }}</div>
                  <b-checkbox class="text-light d-inline-flex" v-model="devSettingsEnabled[sName]" />
                </div>

                <ul v-for="(opt, oIdx) in options" :key="oIdx">
                  <div class="d-flex">
                    <div class="d-inline-flex mr-2">{{ opt.name }} {{ opt.value }}</div>
                    <b-checkbox class="text-light d-inline-flex" v-model="devOptionsEnabled[opt.name]" />
                  </div>
                </ul>

              </ul>

            </div>
          </b-collapse>
        </b-card-text>
      </div>
    </b-card>
  </div>
</template>

<script>
export default {
  name: "DevPresets",
  data: function () {
    return {
      devPresets: [],
      devSettingsEnabled: {},
      devOptionsEnabled: {},
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
    enableSetting: function (event) {
      console.log(event)
    },
    createDevGfxPresets: function () {
      this.devPresets = []

      // Iterate every Setting and create a preset per setting
      for (let setting_app_key in this.devPresetSettings) {
        let settings = this.devPresetSettings[setting_app_key]

        for (let option_key in settings) {
          let options = settings[option_key]
          if (!this.devSettingsEnabled[option_key]) { continue }

          for (let i = 0; i < options.length; i++) {
            let option = options[i]
            if (!this.devOptionsEnabled[option.name]) { continue }
            this.createDevGfxPreset(setting_app_key, option_key, option)
          }
        }
      }
      this.$emit('queue-presets', this.devPresets)
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
  created() {
    for (let setting_app_key in this.devPresetSettings) {
      let settings = this.devPresetSettings[setting_app_key]
      for (let option_key in settings) {
        this.devSettingsEnabled[option_key] = true
        let options = settings[option_key]
        for (let i = 0; i < options.length; i++) {
          let option = options[i]
          this.devOptionsEnabled[option.name] = true
        }
      }
    }
  }
}
</script>

<style scoped>

</style>