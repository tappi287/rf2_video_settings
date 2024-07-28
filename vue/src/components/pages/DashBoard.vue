<template>
  <div v-cloak id="dashboard" class="position-relative mb-3 text-left">
    <div class="vue-flux-container">
      <vue-flux class="img-slider" id="img" ref="slider"
          :captions="vfCaptions"
          :images="vfImages"
          :options="vfOptions"
          :transitions="vfTransitions">

        <template v-slot:preloader>
          <flux-preloader/>
        </template>

        <template v-slot:caption>
          <flux-caption v-slot="captionProps" class="img-caption">
            <b-link :href="captionProps.caption.url" target="_blank" class="text-white int-font title">
              {{ captionProps.caption.text }}
            </b-link>
          </flux-caption>
        </template>
      </vue-flux>
    </div>
    <div id="i-overlay">
      <div id="img-gradient" class="low-round"></div>

      <!-- Display over image slider -->
      <div class="p-3" id="top-menu">
        <b-icon icon="house-fill" class="mr-1 float-left no-pointer"></b-icon>
        <h6 class="title int-font mb-0">Hello {{ userName }}</h6>

        <!-- Shortcuts Play with Preset v-if="gfxPresetsReady" -->
        <div class="text-center mb-5" id="gfx-presets">
          <h6 class="title int-font">
            <b-link class="text-white" @click="$emit('nav', 1)">Graphics Presets</b-link>
          </h6>
          <template v-for="(preset, idx) in gfxHandler.presets.slice(1)">
            <b-button :key="idx" squared
                      v-b-popover.bottom.hover="preset.desc"
                      :class="gfxHandler.selectedPresetIdx === idx+1 ? 'low-round active' + cls : 'low-round inactive' + cls"
                      :variant="gfxHandler.selectedPresetIdx === idx+1 ? 'rf-orange' : 'rf-blue'"
                      @click="gfxHandler.selectPreset(preset, true)">
              {{ preset.name }}
            </b-button>
          </template>
        </div>
        <!-- Shortcut open Setups Directory -->
      </div>
    </div>
    <div id="spacer" class="no-pointer"></div>

    <!-- Server Favourites -->
    <transition name="fade">
      <ServerBrowser ref="serverBrowser" only-favourites class="mt-3" :delay="100" :rfactor-version="rfactorVersion"
                     @make-toast="makeToast" @launch="$refs.slider.stop()"
                     @set-busy="setBusy" v-if="showServerFavs" />
    </transition>
  </div>
</template>

<script>
import ServerBrowser from "@/components/pages/ServerBrowser"
import PresetHandler from "@/components/presets/PresetHandler";
import PreferencesPage from "@/components/pages/PreferencesPage";
import { VueFlux, FluxCaption, FluxPreloader } from 'vue-flux';
import {getEelJsonObject, chooseIndex, userScreenShotsUrl, getMaxWidth } from "@/main"
import rfWPoster from "@/assets/rfW_Poster.webp"

let userScreenShots = []

function prepareScreenshots () {
  let imgList = userScreenShots.slice()
  let images = []
  let captions = []

  // Add app poster entry
  images.push(rfWPoster)
  captions.push({text: 'SIM SITE', url: 'https://sim-site.netlify.app'})

  for (let i = 0; i < userScreenShots.length; i++) {
    const randomIdx = chooseIndex(imgList)
    const entry = imgList.splice(randomIdx, 1)[0]
    images.push(entry[0])
    captions.push({text: 'Shot by ' + entry[1], url: entry[2]})
  }

  return {images: images, captions: captions}
}

export default {
  name: "DashBoard",
  data: function () {
    return {
      userName: 'Driver',
      cls: ' mb-3 mr-2 ml-2 preset-button',
      serverBrowserReady: false,
      showServerFavs: true,
      gfxPresetsReady: false,
      vfOptions: { autoplay: true, delay: 12000, allowFullscreen: true },
      vfImages: [],
      vfTransitions: [ 'fade', 'slide', 'swipe', 'fade' ],
      vfCaptions: [],
      posterImg: rfWPoster
    }
  },
  props: {gfxHandler: PresetHandler, prefs: PreferencesPage, refreshFavs: Boolean, rfactorVersion: String },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setupScreenShots: async function() {
      const r = prepareScreenshots()
      this.vfImages = r.images; this.vfCaptions = r.captions
    },
    getRemoteScreenShots: async function() {
      let slideShowActivated = false
      if (this.prefs !== undefined) {
        slideShowActivated = this.prefs.dashboardModules.indexOf('img') !== -1
      }

      if (slideShowActivated) {
        const request = await fetch(userScreenShotsUrl)
        if (request.ok === false) {
          console.error('Error fetching Screenshots: ' + request.status)
          return
        }
        userScreenShots = await request.json()
        await this.setupScreenShots()
      } else {
        this.$refs.slider.stop()
      }
    },
    setBusy: function (busy) {this.$emit('set-busy', busy) },
    getDriver: async function () {
      let r = await getEelJsonObject(window.eel.get_rf_driver()())
      if (r === undefined || !r.result) {
        return
      }
      r.result.options.forEach(setting => {
        if (setting.key === 'Player Nick') {
          this.userName = setting.value
        }
      })
    },
    equalPresetButtonWidth() {
      const elements = document.querySelectorAll('.preset-button')
      const maxWidth = getMaxWidth(elements)
      elements.forEach(e => { e.style.width = String(maxWidth) + 'px' })
    },
    updateFavs: async function () {
      this.showServerFavs = this.prefs.dashboardModules.indexOf('favs') !== -1
      if (this.refreshFavs && this.showServerFavs) {
        // Reset ServerBrowser data
        await this.$refs.serverBrowser.loadSettings()
        await this.$refs.serverBrowser.refreshServerList(true)
      }
      this.$emit('favs-updated')
    },
  },
  activated() {
    this.updateFavs()
  },
  async mounted() {
    // Access after rendering finished
    setTimeout(() => {
      this.equalPresetButtonWidth()
    }, 0)
  },
  async created() {
    this.setBusy(true)
    await this.setupScreenShots()
    await this.getDriver()
    await this.setBusy(false)
    setTimeout( () => {
      this.getRemoteScreenShots()
    }, 500)
  },
  components: {
    ServerBrowser,
    VueFlux,
    FluxCaption,
    FluxPreloader,
  },
}
</script>

<style scoped src="../../assets/dashboard.css">

</style>