<template>
  <div id="main" v-cloak>
    <div class="text-left mt-3 mb-3">
      <b-nav>
        <b-nav-item :active="navActive === 0" @click="navActive=0">
          Dashboard
          <!-- <b-img src="@/assets/app_icon.webp" width="24" alt="rFactor 2 logo"></b-img> -->
        </b-nav-item>
        <b-nav-item :active="navActive === 1" @click="navActive=1">
          Graphics
        </b-nav-item>
        <b-nav-item disabled :active="navActive === 2" @click="navActive=2">
          Controls
        </b-nav-item>
        <b-nav-item disabled :active="navActive === 3" @click="navActive=3">
          Advanced Options
        </b-nav-item>
        <b-nav-item :active="navActive === 4" @click="toggleServerBrowser">
          Server Browser
        </b-nav-item>
      </b-nav>
      <!--
      <b-button-group class="w-100">
        <b-button variant="dark" @click="navActive=0">
          <b-img src="@/assets/app_icon.webp" width="24" alt="rFactor 2 logo"></b-img>
        </b-button>
        <b-button variant="dark" @click="navActive=1">Graphics</b-button>
        <b-button disabled variant="dark" @click="navActive=2">Controls</b-button>
        <b-button disabled variant="dark" @click="navActive=3">Advanced Settings</b-button>
        <b-button variant="dark" @click="toggleServerBrowser">Server Browser</b-button>
      </b-button-group>
      -->
    </div>

    <!-- Graphics Preset Handler -->
    <PresetHandler ref="gfx" @makeToast="makeToast" @error="setError"
                   @presets-ready="setDashGfxHandler" />

    <!-- Dashboard -->
    <keep-alive>
      <Dashboard ref="dash" v-if="navActive === 0 && gfxReady" :gfx-handler="$refs.gfx"
                 @makeToast="makeToast" @error="setError"></Dashboard>
    </keep-alive>

    <!-- Graphic Settings-->
    <Graphics ref="graphics" v-if="navActive === 1"
              :gfx-presets="$refs.gfx.presets"
              :previous-gfx-preset-name="$refs.gfx.previousPresetName"
              :selected-gfx-preset-idx="$refs.gfx.selectedPresetIdx"
              :gfx-preset-dir="$refs.gfx.userPresetsDir"
              :is-busy="$refs.gfx.isBusy"
              @save-preset="$refs.gfx.savePreset"
              @update-presets-dir="$refs.gfx.setPresetsDir"
              @export-current="$refs.gfx.exportPreset"
              @select-preset="$refs.gfx.selectPreset"
              @create-preset="$refs.gfx.createPreset"
              @delete-preset="$refs.gfx.deletePreset"
              @update-setting="$refs.gfx.updateSetting"
              @update-desc="$refs.gfx.updateDesc" />

    <!-- Server Browser -->
    <ServerBrowser ref="serverBrowser" v-if="navActive === 4"
                   @make-toast="makeToast" @error="setError"></ServerBrowser>

    <!-- Launch rFactor -->
    <div class="mt-3">
      <b-button size="sm" variant="primary" @click="launchRfactor">
        <b-icon icon="play"></b-icon>Start rFactor 2
      </b-button>
    </div>
  </div>
</template>

<script>
import {getEelJsonObject} from '@/main'
import Dashboard from "@/components/Dashboard";
import Graphics from "@/components/Graphics";
import ServerBrowser from "@/components/ServerBrowser";
import PresetHandler from "@/components/PresetHandler";

export default {
  name: 'Main',
  data: function () {
    return {
      navActive: 0,
      firstServerBrowserVisit: true,
      gfxReady: false
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
        isBusy: false,
      })
    },
    setDashGfxHandler: function () {
      this.gfxReady = true
      this.$nextTick(() => { this.$refs.dash.gfxPresetsReady = true })
    },
    importPreset: async function (importPreset) {
      await this.$refs.gfx.importPreset(importPreset)
    },
    setError: async function (error) { this.$emit('error', error) },
    toggleServerBrowser() {
      this.navActive = 4
      // Refresh full server list on first visit
      this.$nextTick(() => {
        if (this.firstServerBrowserVisit) { this.$refs.serverBrowser.refreshServerList(true) }
        this.firstServerBrowserVisit = false
      })
    },
    launchRfactor: async function () {
      let r = await getEelJsonObject(window.eel.run_rfactor()())
      if (r !== undefined && r.result) {
        this.makeToast('rFactor2.exe launched. This will take some time.', 'success')
      } else {
        this.makeToast('Could not launch rFactor2.exe', 'danger')
      }
    },
  },
  components: {
    Dashboard,
    ServerBrowser,
    Graphics,
    PresetHandler
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#main {
  width: 92%;
  margin: 0 auto 0 auto;
}
.nav-link.active {
  text-decoration: underline;
  text-decoration-skip-ink: auto;
}
</style>
