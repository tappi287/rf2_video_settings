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
      posterImg: rfWPoster,
      preloadAbort: false,
      imgErrorAttached: false
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

        // Filter invalid and missing images
        await this._filterInvalidImages();
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
    _ensureFluxVisible() {
      // Warten, bis der DOM sichtbar ist (nach Route/Transition)
      this.$nextTick(() => {
        requestAnimationFrame(() => {
          const slider = this.$refs.slider;
          if (slider && typeof slider.resize === 'function') {
            slider.resize();
          }
        });
      });
    },

    // Vorab-Validierung mit Timeout (z.B. 6 Sekunden)
    async _filterInvalidImages(timeoutMs = 6000) {
      if (!Array.isArray(this.vfImages)) return;

      const original = [...this.vfImages];
      const urls = original.map(it => (typeof it === 'string' ? it : it && it.src)).filter(Boolean);

      const okSet = new Set(await this._preloadImages(urls, timeoutMs));
      // Rekonstruiere die Struktur (String oder Objekt), aber nur für valide URLs
      const filtered = original.filter(it => {
        const url = typeof it === 'string' ? it : it && it.src;
        return okSet.has(url);
      });

      this.vfImages = filtered;
    },

    async _preloadImages(urls, timeoutMs) {
      const checks = urls.map(url => this._checkImage(url, timeoutMs).then(() => url).catch(() => null));
      return Promise.all(checks).then(list => list.filter(Boolean));
    },

    _checkImage(url, timeoutMs) {
      return new Promise((resolve, reject) => {
        if (this.preloadAbort) {
          reject(new Error('aborted'));
          return;
        }
        const img = new Image();
        let done = false;
        const finish = (ok) => {
          if (done) return;
          done = true;
          clearTimeout(to);
          img.onload = img.onerror = null;
          ok ? resolve() : reject(new Error('load-error'));
        };
        const to = setTimeout(() => finish(false), timeoutMs);
        img.onload = () => finish(true);
        img.onerror = () => finish(false);
        img.src = url;
      });
    },

    // Laufzeit-Handler: Fehlende <img> erkennen, Bild aus Liste entfernen, weiterspringen
    _attachImageErrorHandler() {
      if (this.imgErrorAttached) return;
      const root = this.$el && this.$el.querySelector('.vue-flux-container');
      if (!root) return;

      this._onImgError = (e) => {
        console.error(`Slider image error: ${e}`);
        const el = e.target;
        if (!el || el.tagName !== 'IMG') return;

        const badSrc = el.currentSrc || el.src;
        const index = this.vfImages.findIndex(it => (typeof it === 'string' ? it : it && it.src) === badSrc);
        if (index === -1) return;

        // Entferne defektes Bild aus Datenquelle
        this.vfImages.splice(index, 1);

        // Slider sanft fortsetzen
        this.$nextTick(() => {
          const slider = this.$refs.slider;
          if (!slider) return;

          if (typeof slider.resize === 'function') slider.resize();
          if (typeof slider.next === 'function') slider.next();
          if (typeof slider.play === 'function') slider.play();
        });
      };

      // useCapture=true, damit IMG-Fehler auch am Container ankommen
      root.addEventListener('error', this._onImgError, true);
      this.imgErrorAttached = true;
    },

    _detachImageErrorHandler() {
      if (!this.imgErrorAttached) return;
      const root = this.$el && this.$el.querySelector('.vue-flux-container');
      if (root && this._onImgError) {
        root.removeEventListener('error', this._onImgError, true);
      }
      this.imgErrorAttached = false;
      this._onImgError = null;
    },
  },
  activated() {
    this.updateFavs();
    this._ensureFluxVisible();
  },
  async mounted() {
    // Sicherstellen, dass der Slider sichtbar ist
    this._ensureFluxVisible();

    // Fehler zur Laufzeit abfangen und Skipping aktivieren
    this._attachImageErrorHandler();

    // Access after rendering finished
    setTimeout(() => {
      this.equalPresetButtonWidth()
    }, 0)
    this._ensureFluxVisible();
  },
  async created() {
    this.setBusy(true)
    await this.setupScreenShots()
    await this.getDriver()
    this.setBusy(false)
    setTimeout( () => {
      this.getRemoteScreenShots()
    }, 500)
  },
  beforeDestroy() {
    this._detachImageErrorHandler()
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