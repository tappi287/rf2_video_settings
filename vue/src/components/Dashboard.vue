<template>
  <div v-cloak id="dashboard" class="position-relative mb-3 text-left">
    <vue-flux class="img-slider rounded" id="img"
        ref="slider"
        :captions="vfCaptions"
        :images="vfImages"
        :options="vfOptions"
        :transitions="vfTransitions"
        @ready="updateHeight">

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
    <div id="img-gradient" class="rounded"></div>

    <!-- Display over image slider -->
    <div class="p-3" id="top-menu">
      <b-icon icon="house-fill" class="mr-1 float-left no-pointer"></b-icon>
      <h6 class="title int-font mb-0">Hello {{ userName }}</h6>

      <!-- Shortcuts Play with Preset -->
      <div v-if="gfxPresetsReady" class="text-center mb-5" style="position: relative; top: -.5rem;">
        <h6 class="title int-font">Graphics Presets</h6>
        <template v-for="(preset, idx) in gfxHandler.presets.slice(1)">
          <b-button :key="idx"
                    v-b-popover.bottom.hover="preset.desc"
                    :class="gfxHandler.selectedPresetIdx === idx+1 ? 'active' + cls : 'inactive' + cls"
                    :variant="gfxHandler.selectedPresetIdx === idx+1 ? 'rf-orange' : 'rf-blue'"
                    @click="gfxHandler.selectPreset(preset, true)">
            {{ preset.name }}
          </b-button>
        </template>
      </div>
      <!-- Shortcut open Setups Directory -->
    </div>

    <div id="spacer" class="no-pointer"></div>

    <!-- Server Favourites -->
    <transition name="fade">
      <ServerBrowser ref="serverBrowser" only-favourites class="mt-3" :delay="100"
                     @server-browser-ready="resize" @make-toast="makeToast" @launch="$refs.slider.stop()"
                     @set-busy="setBusy"/>
    </transition>
  </div>
</template>

<script>
import ServerBrowser from "@/components/ServerBrowser"
import PresetHandler from "@/components/PresetHandler";
import { VueFlux, FluxCaption, FluxPreloader } from 'vue-flux';
import {getEelJsonObject, chooseIndex, userScreenShots, getMaxWidth} from "@/main"
import rfWPoster from "@/assets/rfW_Poster.webp"

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
  name: "Dashboard",
  data: function () {
    return {
      userName: 'Driver',
      cls: ' mb-3 mr-2 ml-2 preset-button',
      serverBrowserReady: false,
      gfxPresetsReady: false,
      vfOptions: { autoplay: true, delay: 12000 },
      vfImages: [],
      vfTransitions: [ 'fade', 'slide', 'swipe', 'fade' ],
      vfCaptions: [],
      resizeTimeout: null,
      resizeDebounceRate: 20,
      posterImg: rfWPoster
    }
  },
  props: {gfxHandler: PresetHandler, refreshFavs: Boolean },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
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
    resize() {
      // Hack to trigger a resize event
      window.resizeBy(-1, 0)
      window.resizeBy(1, 0)
    },
    debounceResize() {
      clearTimeout(this.resizeTimeout)
      this.resizeTimeout = setTimeout(this.updateHeight, this.resizeDebounceRate)
    },
    updateHeight() {
      this.resizeTimeout = null

      this.$nextTick(() => {
        const imgDiv = document.getElementById('img')
        const topMenu = document.getElementById('top-menu')
        if (imgDiv === undefined || imgDiv === null || topMenu === null || topMenu === undefined) { return }
        const imgHeight = imgDiv.offsetHeight
        const menuHeight = topMenu.offsetHeight
        document.getElementById('spacer').style.height = String(imgHeight - menuHeight) + 'px'
      })
    },
    equalPresetButtonWidth() {
      const elements = document.querySelectorAll('.preset-button')
      const maxWidth = getMaxWidth(elements)
      elements.forEach(e => { e.style.width = String(maxWidth) + 'px' })
    },
    updateFavs: async function () {
      if (this.refreshFavs) {
        // Reset ServerBrowser data
        await this.$refs.serverBrowser.loadSettings()
        await this.$refs.serverBrowser.refreshServerList(true)
      }
      this.$emit('favs-updated')
    },
  },
  activated() {
    console.log('Dashboard activated')
    this.resize()
    this.$refs.slider.play()
    this.updateFavs()
  },
  updated() {
    console.log('Dashboard updated')
    this.updateHeight()
  },
  mounted() {
    console.log('Dashboard mounted')
    // Access after rendering finished
    setTimeout(() => {
      this.equalPresetButtonWidth()
    }, 0)
  },
  created() {
    this.setBusy(true)
    const r = prepareScreenshots()
    this.vfImages = r.images; this.vfCaptions = r.captions
    this.getDriver()
    this.setBusy(false)
    window.onresize = this.debounceResize
  },
  components: {
    ServerBrowser,
    VueFlux,
    FluxCaption,
    FluxPreloader,
  },
}
</script>

<style scoped>
.int-font { font-family: Inter, "Segoe UI", system-ui, sans-serif; }
.title {
  font-weight: 200;
  text-shadow: 1px 1px 2px black;
}

.fade-enter-active, .fade-leave-active { transition: opacity 3s, height 3s; }

.fade-enter, .fade-leave-to {opacity: 0; height: 0;}

.btn-rf-orange, .btn-rf-blue { font-weight: 300; }
.btn-rf-orange.active, .btn-rf-blue.active { font-weight: 400; }
.active, .inactive { box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.8), 0 6px 20px 0 rgba(0, 0, 0, 0.75); }

.no-pointer { pointer-events: none; }

#top-menu { z-index: 10; position: relative; }
#spacer { z-index: -10; position: relative; }
.img-slider { position: absolute; z-index: 1; width: 100%; }
.img-caption { position: absolute; width: 100%; bottom: 0; }
.img-caption a { line-height: 1.1rem; width: 100%; font-family: Ubuntu, "Segoe UI", sans-serif; }
#img-gradient {
  position: absolute;
  background: linear-gradient(rgba(0,0,0,0.5) 0%, rgba(0,0,0,0) 100%);
  height: 6rem; width: 100%; z-index: 2;
}
</style>

<style>
.flux-image { border-radius: .25rem; }
.flux-caption {
  background-color: transparent !important;
  background: radial-gradient(circle at 50% 250%, rgba(0,0,0, 0.85) 10%, rgba(0,0,0,0) 30%);
}
</style>