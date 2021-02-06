<template>
  <div id="dashboard" v-cloak class="position-relative mb-3 text-left">
    <b-img class="mr-1 float-left no-pointer" src="@/assets/app_icon.webp"
           width="24" alt="rFactor 2 logo"></b-img>
    <h5 class="title">Hello {{ userName }}</h5>
    <p></p>

    <!-- Shortcuts Play with Preset -->
    <!--<PresetHandler ref="gf" @makeToast="makeToast" @error="setError"
                   @presets-ready="presetsReady = true"/>-->
    <div v-if="gfxPresetsReady" class="text-center mt-4 mb-4">
      <h5 class="mb-3">Graphics Presets</h5>
      <template v-for="(preset, idx) in gfxHandler.presets.slice(1)">
        <b-button :key="idx"
                  :class="gfxHandler.selectedPresetIdx === idx+1 ? 'active mr-2 ml-2' : 'inactive mr-2 ml-2'"
                  @click="gfxHandler.selectPreset(preset, true)"
                  v-b-popover.bottom.hover="preset.desc"
                  :variant="gfxHandler.selectedPresetIdx === idx+1 ? 'rf-orange' : 'rf-blue'">
          {{ preset.name }}
        </b-button>
      </template>
    </div>
    <!-- Shortcut open Setups Directory -->

    <p></p>
    <!-- Server Favourites -->
    <transition name="fade">
        <ServerBrowser ref="serverBrowser" only-favourites
                       @make-toast="makeToast" @error="setError" />
    </transition>
  </div>
</template>

<script>
import ServerBrowser from "@/components/ServerBrowser"
import PresetHandler from "@/components/PresetHandler";
import { userScreenShots } from "@/main"

export default {
  name: "Dashboard",
  data: function () {
    return {
      userName: 'Driver',
      userScreenUrls: userScreenShots,
      serverBrowserReady: false,
      gfxPresetsReady: false,
    }
  },
  props: { gfxHandler: PresetHandler },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setError: async function (error) { this.$emit('error', error) },
  },
  created() {
    // pass
  },
  components: {
    ServerBrowser
  },
}
</script>

<style scoped>
  .title { font-weight: 300; }

  .fade-enter-active, .fade-leave-active {
    transition: opacity 3s, height 3s;
  }
  .fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
    opacity: 0; height: 0;
  }
  .no-pointer { pointer-events:none; }
  .btn-rf-orange, .btn-rf-blue { font-weight: 300; }
  .btn-rf-orange.active, .btn-rf-blue.active { font-weight: 400; }
</style>