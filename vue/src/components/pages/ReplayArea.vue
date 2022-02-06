<template>
  <div id="replays">
    <b-input-group>
      <b-input-group-prepend>
        <div class="pl-0 pr-1 rpl-con position-relative bg-transparent rounded-left">
          <b-img width=".3rem" class="rpl-icon" src="@/assets/rfW_logo_color.svg"></b-img>
        </div>
        <!-- Title -->
        <b-input-group-text class="bg-transparent no-border section-title text-white pl-0">
          Replay Manager
        </b-input-group-text>
      </b-input-group-prepend>

      <!-- Spacer -->
      <div class="form-control bg-transparent no-border">
        <span v-if="!watchEnabled">Watching replays is not supported with your rFactor version</span>
      </div>

      <!-- Preset Selection -->
      <div class="mt-1">
        <b-input-group size="sm" class="setting-field">
          <b-input-group-prepend>
            <b-input-group-text class="info-field fixed-width-name">
              Replay Graphics Preset
            </b-input-group-text>
          </b-input-group-prepend>
          <b-input-group-append>
              <b-dropdown size="sm" :text="currentPresetName" right
                          class="setting-item fixed-width-setting no-border"
                          v-b-popover.auto.hover="'Select a Graphics Preset you want to use when watching a Replay.'"
                          :variant="currentPresetName !== nonePreset.name ? 'rf-orange' : 'rf-blue'">
                <b-dropdown-item v-for="(preset, idx) in replayPresetList" :key="idx"
                                 @click="setReplayPreset(preset)">
                  {{ preset.name }}
                </b-dropdown-item>
              </b-dropdown>
            </b-input-group-append>
          </b-input-group>
      </div>
    </b-input-group>

    <ReplayList :watch-enabled="watchEnabled" editing />
  </div>
</template>

<script>

import ReplayList from "@/components/ReplayList";
export default {
  name: "ReplayArea",
  components: {ReplayList},
  data: function () {
    return {
      nonePreset: {name: 'None', isNonePreset: true},
      replayPreset: '',
      watchEnabled: false,
      isBusy: false,
    }
  },
  props: { rfactorVersion: String, gfxHandler: Object },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) { this.isBusy = busy; this.$emit('set-busy', busy) },
    getReplayPreset: async function() {
      this.replayPreset = await window.eel.get_replay_preset()()
      if (this.replayPreset === '') { return }
      let presets = this.gfxHandler.presets.slice(1)

      // Check if preset is in Graphics preset list
      let match = false
      presets.forEach(p => { if(this.replayPreset === p.name) { match = true }})
      // Reset Preset if not in current graphics presets
      if (!match) { await this.setReplayPreset(this.nonePreset) }
    },
    setReplayPreset: async function(preset) {
      let name = preset.name
      if (preset.isNonePreset !== undefined) { name = '' }
      await window.eel.set_replay_preset(name)()
      await this.getReplayPreset()
    },

  },
  computed: {
    currentPresetName() {
      if (this.replayPreset === '') { return this.nonePreset.name }
      return this.replayPreset
    },
    replayPresetList() {
      let presets = this.gfxHandler.presets.slice(1)
      presets.unshift(this.nonePreset)
      return presets
    },
  },
  created() {
    if (this.rfactorVersion >= '1.1122') { this.watchEnabled = true }
    this.getReplayPreset()
  }
}
</script>

<style scoped>
.section-title { font-family: Ubuntu, sans-serif; }
.rpl-icon { width: 2.075rem; }
.rpl-con { margin-top: .1rem; }
</style>