<template>
  <div id="main" class="position-relative" v-cloak>
    <b-navbar class="text-left pl-0 pr-0" type="dark">
      <b-navbar-brand href="#" @click="navActive=0" class="r-icon-brand position-relative"
                      v-b-popover.bottomleft.hover="'DashBoard'">
        <b-img width="32px" key="1" src="@/assets/rfW_logo_white.svg"
               :class="navActive === 0 ? 'r-icon top' : 'r-icon top inv'"></b-img>
        <b-img width="32px" key="2" src="@/assets/rfW_logo.svg"
               :class="navActive !== 0 ? 'r-icon bottom' : 'r-icon bottom inv'"></b-img>
      </b-navbar-brand>
      <b-nav>
        <b-nav-item-dropdown text="Settings"
                             :toggle-class="[1,2,3].indexOf(navActive) !== -1 ? 'used pl-0' : 'pl-0'">
          <b-dropdown-item>
            <b-nav-item :active="navActive === 1" @click="navActive=1" link-classes="pl-0">
              Graphics Settings
            </b-nav-item>
          </b-dropdown-item>
          <b-dropdown-item>
            <b-nav-item :active="navActive === 2" @click="navActive=2" link-classes="pl-0">
              Control Settings
            </b-nav-item>
          </b-dropdown-item>
          <b-dropdown-item>
            <b-nav-item :active="navActive === 3" @click="navActive=3" link-classes="pl-0">
              Generic Settings
            </b-nav-item>
          </b-dropdown-item>
          <b-dropdown-item>
            <b-nav-item :active="navActive === 10" @click="navActive=10" link-classes="pl-0">
              Session Settings
            </b-nav-item>
          </b-dropdown-item>
        </b-nav-item-dropdown>

        <b-nav-item :active="navActive === 4" @click="navActive=4" link-classes="pl-0">
          Headlights
        </b-nav-item>
        <b-nav-item :active="navActive === 5" @click="navActive=5" link-classes="pl-0">
          Replays
        </b-nav-item>
        <b-nav-item :active="navActive === 6" @click="navActive=6" link-classes="pl-0">
          Server Browser
        </b-nav-item>
        <b-nav-item :active="navActive === 13" @click="navActive=13" link-classes="pl-0">
          FuelCalc
        </b-nav-item>
        <b-nav-item :active="navActive === 11" @click="navActive=11" link-classes="pl-0">
          Chat
        </b-nav-item>
        <b-nav-item :active="navActive === 9" @click="navActive=9" link-classes="pl-0">
          Benchmark
        </b-nav-item>
      </b-nav>

      <!-- Right aligned nav items -->
      <b-navbar-nav class="ml-auto">
        <b-nav-form v-if="navSearchEnabled" @submit.prevent>
          <b-form-input v-model="search" debounce="800" type="search"
                        size="sm" placeholder="Search..."
                        class="search-bar mr-sm-2 text-white"/>
        </b-nav-form>
        <b-nav-item id="vr-nav" right @click="launchSteamVr" v-b-popover.auto.hover="'Launch SteamVR'">
          <div class="vr-nav-container">
            <div class="vr-nav-font"><b>VR</b></div>
            <div class="vr-nav-icon">
              <b-icon icon="square-fill"></b-icon>
            </div>
          </div>
        </b-nav-item>
        <b-nav-item id="preferences-nav" right :active="navActive === 12" @click="navActive=12">
          <b-iconstack>
            <b-icon stacked icon="square-fill"></b-icon>
            <b-icon stacked icon="gear-fill" scale="0.75" class="gear-icon"></b-icon>
          </b-iconstack>
        </b-nav-item>
        <b-nav-item id="wiki-nav" right :active="navActive === 7" @click="navActive=7">
          <b-icon icon="question-square-fill"></b-icon>
        </b-nav-item>
      </b-navbar-nav>
    </b-navbar>

    <!-- Graphics Preset Handler -->
    <PresetHandler ref="gfx" @make-toast="makeToast" @error="setError" id-ref="gfx"
                   :preset-type="0" @presets-ready="setDashGfxHandler" @set-busy="setBusy"/>

    <!-- Game Settings Handler -->
    <PresetHandler ref="gen" @make-toast="makeToast" @error="setError" id-ref="gen"
                   :preset-type="1" @set-busy="setBusy"/>

    <!-- Controls Settings Handler -->
    <PresetHandler ref="con" @make-toast="makeToast" @error="setError" id-ref="con"
                   :preset-type="2" @set-busy="setBusy"/>

    <!-- Session Settings Handler -->
    <PresetHandler ref="ses" @make-toast="makeToast" @error="setError" id-ref="ses" ignore-deviations
                   :preset-type="3" @set-busy="setBusy"/>

    <!-- Dashboard -->
    <keep-alive>
      <DashBoard ref="dash" :gfx-handler="$refs.gfx" :prefs="$refs.preferences" v-if="navActive === 0 && gfxReady"
                 :refresh-favs="refreshDashFavs" @favs-updated="refreshDashFavs = false"
                 :rfactor-version="rfactorVersion"
                 @make-toast="makeToast" @error="setError" @set-busy="setBusy" @nav="navigate"/>
    </keep-alive>

    <!-- Graphic Settings-->
    <template v-if="navActive === 1">
      <b-overlay :show="$refs.gfx.isBusy" variant="dark" rounded>
        <GraphicsPresetArea id-ref="gfx" fixed-width
                            @make-toast="makeToast"
                            @set-busy="setBusy"
                            :gfx-handler="$refs.gfx"
                            :search="search"/>
      </b-overlay>
    </template>

    <!-- Control Settings-->
    <template v-if="navActive === 2">
      <b-overlay :show="$refs.con.isBusy" variant="dark" rounded>
        <ControlsPresetArea id-ref="con" fixed-width
                            @make-toast="makeToast"
                            @set-busy="setBusy"
                            :con-handler="$refs.con"
                            :search="search"/>
      </b-overlay>
    </template>
    <template v-if="this.preferences">
      <keep-alive>
        <ControllerDeviceList
            :visible="navActive === 2 || (navActive === 0 && this.$refs.preferences.dashboardModules.indexOf('cont') !== -1)"/>
      </keep-alive>
    </template>

    <!-- Generic Settings-->
    <template v-if="navActive === 3">
      <b-overlay :show="$refs.gen.isBusy" variant="dark" rounded>
        <PresetUi ref="genUi" id-ref="gen" display-name="Settings"
                  :presets="$refs.gen.presets"
                  :previous-preset-name="$refs.gen.previousPresetName"
                  :selected-preset-idx="$refs.gen.selectedPresetIdx"
                  :preset-dir="$refs.gen.userPresetsDir"
                  @save-preset="$refs.gen.savePreset"
                  @refresh="$refs.gen.getPresets"
                  @update-presets-dir="$refs.gen.setPresetsDir"
                  @export-current="$refs.gen.exportPreset"
                  @select-preset="$refs.gen.selectPreset"
                  @create-preset="$refs.gen.createPreset"
                  @delete-preset="$refs.gen.deletePreset"
                  @update-setting="$refs.gen.updateSetting"
                  @update-desc="$refs.gen.updateDesc"
                  @update-view-mode="$refs.gen.viewMode=$event"
                  @make-toast="makeToast"/>

        <div>
          <div v-for="(genPreset, idx) in $refs.gen.presets" :key="genPreset.name">
            <SettingsCard :preset="genPreset" :idx="idx" :search="search" fixed-width
                          settings-key="game_options" header-icon="card-heading"
                          :current_preset_idx="$refs.gen.selectedPresetIdx"
                          :previous-preset-name="$refs.gen.previousPresetName"
                          :view_mode="$refs.gen.viewMode"
                          @update-setting="$refs.gen.updateSetting"
                          @set-busy="setBusy"
                          @make-toast="makeToast"/>
            <SettingsCard :preset="genPreset" :idx="idx" :search="search" fixed-width
                          settings-key="misc_options" header-icon="card-text"
                          :current_preset_idx="$refs.gen.selectedPresetIdx"
                          :previous-preset-name="$refs.gen.previousPresetName"
                          :view_mode="$refs.gen.viewMode"
                          @update-setting="$refs.gen.updateSetting"
                          @set-busy="setBusy"
                          @make-toast="makeToast"/>
          </div>
        </div>
      </b-overlay>
    </template>

    <!-- Headlights -->
    <rf2Headlights ref="headlights" v-if="navActive === 4"
                   @make-toast="makeToast"/>

    <!-- Replays -->
    <ReplayArea ref="replays" v-if="navActive === 5" @make-toast="makeToast" @set-busy="setBusy"
                :rfactor-version="rfactorVersion" :gfx-handler="$refs.gfx"/>

    <!-- Server Browser -->
    <keep-alive>
      <ServerBrowser ref="serverBrowser" v-if="navActive === 6" @launch="stopSlideShow"
                     @make-toast="makeToast" @set-busy="setBusy" :rfactor-version="rfactorVersion"
                     @fav-updated="refreshDashFavs = true"/>
    </keep-alive>

    <!-- Fuel Calc -->
    <FuelCalc v-if="navActive === 13" @make-toast="makeToast"></FuelCalc>

    <!-- ChatPage -->
    <keep-alive>
      <ChatPage :visible="navActive === 11" :live="live" @make-toast="makeToast" @set-busy="setBusy"/>
    </keep-alive>

    <!-- Wiki -->
    <AppWiki v-if="navActive === 7" @nav="navigate"/>

    <!-- Log -->
    <AppLog v-if="navActive === 8" @nav="navigate"/>

    <!-- Benchmark -->
    <template v-if="navActive === 9">
      <b-overlay :show="$refs.ses.isBusy" variant="dark" rounded>
        <BenchMark ref="Benchmark" @make-toast="makeToast" @set-busy="setBusy"
                   :gfx-handler="$refs.gfx" :ses-handler="$refs.ses"/>
      </b-overlay>
    </template>

    <!-- Session Settings and Content Selection -->
    <SessionPresetArea v-if="navActive === 10" fixed-width
                       @content-launched="navActive = 0" :ses-handler="$refs.ses" :search="search"
                       @make-toast="makeToast" @set-busy="setBusy"/>

    <!-- App Preferences -->
    <keep-alive>
      <PreferencesPage :visible="navActive === 12" ref="preferences"/>
    </keep-alive>

    <!-- rFactor Actions -->
    <b-container fluid class="mt-3 p-0">
      <b-row cols="2" class="m-0">
        <b-col class="text-left p-0">
          <LaunchRfactorBtn display-live choose-content @make-toast="makeToast" @launch="rfactorLaunched"
                            @update-live="live = $event"
                            @show-content="navActive = 10"/>
        </b-col>
        <b-col class="text-right p-0">
          <b-button size="sm" variant="rf-secondary" class="ml-2"
                    v-b-popover.auto.hover="'Open rF2 vehicle setups folder'"
                    @click="openSetupFolder">
            <b-icon icon="folder"></b-icon>
          </b-button>
          <b-button size="sm" variant="rf-secondary" class="ml-2" v-b-popover.auto.hover="'Run rF2 ModMgr.exe'"
                    @click="runModMgr">
            <b-icon icon="archive-fill"></b-icon>
          </b-button>
          <b-button size="sm" class="ml-2" variant="rf-secondary" id="restore-btn"
                    v-b-popover.auto.hover="'Restore your original settings'">
            <b-icon icon="arrow-counterclockwise"></b-icon>
          </b-button>
        </b-col>
      </b-row>
    </b-container>

    <RfactorOverlay v-if="showRfOverlay" :live="live" :rf2-status="rf2Status"
                    :quit-busy="quitBusy" @quit-rfactor="quitRfactor"/>

    <!-- Restore Popover -->
    <b-popover target="restore-btn" triggers="click">
      <p>Do you really want to restore all of your original settings?</p>
      <span class="text-muted">This will restore your original files when you first launched this app.
        player.JSON, Controller.JSON, Config_DX11.ini</span>
      <div class="text-right mt-3">
        <b-button @click="restoreSettings" size="sm" variant="warning"
                  aria-label="Restore" class="mr-2">
          Restore
        </b-button>
        <b-button @click="$root.$emit('bv::hide::popover', 'restore-btn')"
                  size="sm" aria-label="Close">
          Close
        </b-button>
      </div>
    </b-popover>
  </div>
</template>

<script>
import DashBoard from "@/components/pages/DashBoard";
import PresetUi from "@/components/presets/PresetUi";
import ServerBrowser from "@/components/pages/ServerBrowser";
import PresetHandler from "@/components/presets/PresetHandler";
import SettingsCard from "@/components/settings/SettingsCard";
import AppWiki from "@/components/Wiki";
import LaunchRfactorBtn from "@/components/LaunchRfactorBtn";
import rf2Headlights from "@/components/pages/rf2Headlights";
import ReplayArea from "@/components/pages/ReplayArea";
import AppLog from "@/components/Log";
import {getEelJsonObject, sleep} from "@/main";
import BenchMark from "@/components/benchmark/Benchmark";
import GraphicsPresetArea from "@/components/presets/GraphicsPresetArea";
import ControlsPresetArea from "@/components/presets/ControlsPresetArea";
import SessionPresetArea from "@/components/presets/SessionPresetArea";
import ChatPage from "@/components/pages/ChatPage";
import ControllerDeviceList from "@/components/ControllerDeviceList";
import RfactorOverlay from "@/components/RfactorOverlay";
import PreferencesPage from "@/components/pages/PreferencesPage";
import FuelCalc from "@/components/pages/FuelCalc.vue";

export default {
  name: 'MainPage',
  data: function () {
    return {
      navActive: 0,
      searchActive: [1, 2, 3],
      search: '',
      live: false,  // rFactor 2 running
      wasLive: true, // rFactor 2 was running before
      rf2Status: '',  // Desc of current rF2 status eg. loading/quitting
      firstServerBrowserVisit: true,
      gfxReady: false,
      isBusy: false,
      quitBusy: false,
      refreshDashFavs: false,
      contentModal: false,
      preferences: undefined,
    }
  },
  props: {rfactorVersion: String},
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000, noAutoHide = false) {
      this.$bvToast.toast(message, {
        title: title,
        autoHideDelay: delay,
        appendToast: append,
        variant: category,
        solid: true,
        noAutoHide: noAutoHide,
      })
      this.$eventHub.$emit('play-audio', 'audioSelect')
    },
    navigate(target = 0) {
      // Hack to re-draw if requested
      if (target === -1) {
        const currentNav = this.navActive
        this.navActive = 0
        this.$nextTick(() => {
          this.navigate(currentNav)
        })
        return
      }
      this.navActive = target
    },
    updateRfactorLiveState: function (event) {
      this.live = event.detail
      if (this.live) {
        this.stopSlideShow();
        this.wasLive = true
      }
      if (!this.live && this.wasLive) {
        this.wasLive = false;
        this.returnedFromLive()
      }
      this.setBusy(this.live)
    },
    updateRfactorStatus: function (event) {
      let status = ''
      if (event.detail !== undefined) {
        status = event.detail
      }
      this.rf2Status = status
    },
    setBusy: function (busy) {
      this.isBusy = busy
    },
    quitRfactor: async function () {
      this.quitBusy = true
      const r = await getEelJsonObject(window.eel.quit_rfactor()())
      if (r.result) {
        this.makeToast('Rfactor 2 is quitting.', 'success', 'rFactor 2 Control')
      } else if (!r.result) {
        this.makeToast('Could not connect to an rFactor 2 instance to request a game exit.',
            'warning', 'rFactor 2 Control')
      }
      this.quitBusy = false
    },
    setDashGfxHandler: function () {
      this.gfxReady = true
      this.$nextTick(() => {
        if (this.$refs.dash !== undefined) {
          this.$refs.dash.gfxPresetsReady = true
        }
      })
    },
    _refreshPresets: async function () {
      this.setBusy(true)

      // Restore pre-replay Preset
      await getEelJsonObject(window.eel.restore_pre_replay_preset()())
      await sleep(200)

      // Refresh settings
      if (this.$refs.gfx !== undefined) {
        await this.$refs.gfx.getPresets()
      }
      if (this.$refs.con !== undefined) {
        await this.$refs.con.getPresets()
      }
      if (this.$refs.gen !== undefined) {
        await this.$refs.gen.getPresets()
      }
      if (this.$refs.ses !== undefined) {
        await this.$refs.ses.getPresets()
      }
      if (this.$refs.Benchmark !== undefined) {
        await this.$refs.Benchmark.refresh()
      }

      this.setBusy(false)
    },
    returnedFromLive: async function () {
      this.makeToast('Rfactor 2 closed. Refreshing settings in 5 seconds.', 'success', 'rFactor 2 Control')

      // Add a timeout to let rF release its resources
      await sleep(5000)
      await this._refreshPresets()
    },
    importPreset: async function (importPreset) {
      if (importPreset.CHAT !== undefined) {
        // Import rF player.json to Graphics
        await this.$refs.gfx.importPlayerJson(importPreset)
        // Import rF player.json to Settings
        await this.$refs.gen.importPlayerJson(importPreset)
        return
      }
      if (importPreset.preset_type === undefined) {
        this.makeToast('The file you dropped did not contain the expected data.', 'warning',
            'Preset Import')
      }
      switch (importPreset.preset_type) {
        case 0:
          // Graphics
          await this.$refs.gfx.importPreset(importPreset)
          break
        case 1:
          // Settings
          await this.$refs.gen.importPreset(importPreset)
          break
        case 2:
          // Controls
          await this.$refs.con.importPreset(importPreset)
          break
        case 3:
          // Session
          await this.$refs.ses.importPreset(importPreset)
          break
        default:
          this.makeToast('The type of preset you dropped is not supported or from a newer version than ' +
              'your version of the app.', 'warning', 'Preset Import')
      }
      console.log(importPreset.preset_type)
    },
    setError: async function (error) {
      this.$emit('error', error)
    },
    rfactorLaunched: async function () {
      await this.stopSlideShow()
      if (this.$refs.ses !== undefined) {
        await this.$refs.ses.update()
      }
    },
    launchSteamVr: async function () {
      let r = await getEelJsonObject(window.eel.run_steamvr()())
      if (r !== undefined && r.result) {
        this.makeToast(r.msg, 'success', 'SteamVR Launch')
      } else if (r !== undefined && !r.result) {
        this.makeToast(r.msg, 'danger', 'SteamVR Launch')
      }
    },
    stopSlideShow: async function () {
      if (this.$refs.dash !== undefined) {
        await this.$refs.dash.$refs.slider.stop()
      }
    },
    openSetupFolder: async function () {
      await window.eel.open_setup_folder()()
    },
    runModMgr: async function () {
      await window.eel.run_mod_mgr()()
    },
    restoreSettings: async function () {
      const r = await getEelJsonObject(window.eel.restore_backup()())
      if (r.result) {
        this.makeToast(r.msg, 'warning', 'Re-Store')
        await this.$refs.gfx.getPresets()
        await this.$refs.con.getPresets()
        await this.$refs.gen.getPresets()
        await this.$refs.ses.getPresets()
      }
      if (!r.result) {
        this.makeToast(r.msg, 'danger', 'Re-Store Original Settings')
      }
      this.$root.$emit('bv::hide::popover', 'restore-btn')
    },
  },
  computed: {
    navSearchEnabled() {
      return this.searchActive.indexOf(this.navActive) !== -1;
    },
    showRfOverlay() {
      return this.live || this.isBusy || this.quitBusy;
    }
  },
  created() {
    this.$eventHub.$on('navigate', this.navigate)
    // Wait for Preferences ref
    const interval = setInterval(() => {
      if (this.$refs.preferences) {
        this.preferences = this.$refs.preferences
        clearInterval(interval)
      }
    }, 50)
  },
  beforeDestroy() {
    this.$eventHub.$off('navigate', this.navigate)
  },
  components: {
    FuelCalc,
    PreferencesPage,
    RfactorOverlay,
    ControllerDeviceList,
    ChatPage,
    SessionPresetArea,
    GraphicsPresetArea,
    ControlsPresetArea,
    BenchMark,
    ReplayArea,
    rf2Headlights,
    LaunchRfactorBtn,
    SettingsCard,
    DashBoard,
    ServerBrowser,
    PresetHandler,
    PresetUi,
    AppWiki,
    AppLog
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#main {
  width: 97%;
  margin: 0 auto 0 auto;
}

.nav {
  margin-top: .175rem;
}

.vr-nav-container {
  position: relative;
  width: 1rem;
}

.vr-nav-font {
  position: absolute;
  color: black;
  z-index: 2;
  font-size: 0.875rem;
  left: 0.115rem;
  top: 0.185rem;
}

.vr-nav-icon {
  position: absolute;
}

#vr-nav a {
  padding-right: 0.275rem;
}

#wiki-nav a {
  padding-right: 0;
}

#preferences-nav a {
  padding-right: 0;
}

.gear-icon {
  color: rgba(0.1, 0.1, 0.1, 0.75);
}

.nav-link.active {
  text-decoration: underline;
  text-decoration-skip-ink: auto;
}

.used {
  color: white;
  text-decoration: underline !important;
  text-decoration-skip-ink: auto !important;
}

.search-bar {
  background: transparent;
  border: none;
}

.search-off {
  opacity: 0.3;
}

.r-icon {
  transition: opacity .8s;
}

.r-icon-brand {
  display: inline-block;
  width: 1.725rem;
  height: 2.5rem;
}

.r-icon.bottom {
  position: relative;
  vertical-align: baseline;
}

.r-icon.bottom.inv {
  opacity: 0;
}

.r-icon.top {
  position: absolute;
  z-index: 2;
}

.r-icon.top.inv {
  opacity: 0;
}
</style>
