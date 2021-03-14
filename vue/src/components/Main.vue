<template>
  <div id="main" class="position-relative" v-cloak>
    <b-navbar class="text-left pl-0 pr-0" type="dark">
      <b-navbar-brand @click="navActive=0">
        <b-img width="32px" src="@/assets/app_icon.webp"></b-img>
      </b-navbar-brand>
      <b-nav>
        <b-nav-item :active="navActive === 0" @click="navActive=0" link-classes="pl-0">
          Dashboard
        </b-nav-item>
        <b-nav-item :active="navActive === 1" @click="navActive=1" link-classes="pl-0">
          Graphics
        </b-nav-item>
        <b-nav-item :active="navActive === 2" @click="navActive=2" link-classes="pl-0">
          Controls
        </b-nav-item>
        <b-nav-item :active="navActive === 3" @click="navActive=3" link-classes="pl-0">
          Settings
        </b-nav-item>
        <b-nav-item :active="navActive === 4" @click="navActive=4" link-classes="pl-0">
          Headlights
        </b-nav-item>
        <b-nav-item :active="navActive === 5" @click="navActive=5" link-classes="pl-0">
          Server Browser
        </b-nav-item>
      </b-nav>

      <!-- Right aligned nav items -->
      <b-navbar-nav class="ml-auto">
        <b-nav-form v-if="navSearchEnabled" @submit.prevent>
          <b-form-input v-model="search" debounce="800" type="search"
                        size="sm" placeholder="Search..."
                        class="search-bar mr-sm-2 text-white"/>
        </b-nav-form>
        <b-nav-item id="wiki-nav" right :active="navActive === 6" @click="navActive=6">
          <b-icon icon="question-square-fill"></b-icon>
        </b-nav-item>
      </b-navbar-nav>
    </b-navbar>

    <!-- Graphics Preset Handler -->
    <PresetHandler ref="gfx" @make-toast="makeToast" @error="setError" id-ref="gfx"
                   :preset-type="0" @presets-ready="setDashGfxHandler" @set-busy="setBusy" />

    <!-- Controls Settings Handler -->
    <PresetHandler ref="con" @make-toast="makeToast" @error="setError" id-ref="con"
                   :preset-type="2" @set-busy="setBusy" />

    <!-- Game Settings Handler -->
    <PresetHandler ref="gen" @make-toast="makeToast" @error="setError" id-ref="gen"
                   :preset-type="1" @set-busy="setBusy" />

    <!-- Dashboard -->
    <keep-alive>
      <Dashboard ref="dash" :gfx-handler="$refs.gfx" v-if="navActive === 0 && gfxReady"
                 :refresh-favs="refreshDashFavs" @favs-updated="refreshDashFavs = false"
                 @make-toast="makeToast" @error="setError" @set-busy="setBusy"></Dashboard>
    </keep-alive>

    <!-- Graphic Settings-->
    <template  v-if="navActive === 1">
      <b-overlay :show="$refs.gfx.isBusy" variant="dark" rounded>
        <PresetUi ref="gfxUi" id-ref="gfx" display-name="Graphics"
                  :presets="$refs.gfx.presets"
                  :previous-preset-name="$refs.gfx.previousPresetName"
                  :selected-preset-idx="$refs.gfx.selectedPresetIdx"
                  :preset-dir="$refs.gfx.userPresetsDir"
                  @save-preset="$refs.gfx.savePreset"
                  @refresh="$refs.gfx.getPresets"
                  @update-presets-dir="$refs.gfx.setPresetsDir"
                  @export-current="$refs.gfx.exportPreset"
                  @select-preset="$refs.gfx.selectPreset"
                  @create-preset="$refs.gfx.createPreset"
                  @delete-preset="$refs.gfx.deletePreset"
                  @update-setting="$refs.gfx.updateSetting"
                  @update-desc="$refs.gfx.updateDesc"
                  @update-view-mode="$refs.gfx.viewMode=$event"
                  @make-toast="makeToast" />

        <div>
          <div v-for="(gfxPreset, idx) in $refs.gfx.presets" :key="gfxPreset.name">
            <GraphicsArea :preset="gfxPreset" :idx="idx" :search="search"
                          :current_preset_idx="$refs.gfx.selectedPresetIdx"
                          :view_mode="$refs.gfx.viewMode"
                          @update-setting="$refs.gfx.updateSetting"
                          @set-busy="setBusy"
                          @make-toast="makeToast" />
          </div>
        </div>
      </b-overlay>
    </template>

    <!-- Control Settings-->
    <template  v-if="navActive === 2">
      <b-overlay :show="$refs.con.isBusy" variant="dark" rounded>
        <PresetUi ref="conUi" id-ref="con" display-name="Controls"
                  :presets="$refs.con.presets"
                  :previous-preset-name="$refs.con.previousPresetName"
                  :selected-preset-idx="$refs.con.selectedPresetIdx"
                  :preset-dir="$refs.con.userPresetsDir"
                  @save-preset="$refs.con.savePreset"
                  @refresh="$refs.con.getPresets"
                  @update-presets-dir="$refs.con.setPresetsDir"
                  @export-current="$refs.con.exportPreset"
                  @select-preset="$refs.con.selectPreset"
                  @create-preset="$refs.con.createPreset"
                  @delete-preset="$refs.con.deletePreset"
                  @update-setting="$refs.con.updateSetting"
                  @update-desc="$refs.con.updateDesc"
                  @update-view-mode="$refs.con.viewMode=$event"
                  @make-toast="makeToast" />

        <div>
          <div v-for="(conPreset, idx) in $refs.con.presets" :key="conPreset.name">
            <GenericSettingsArea :preset="conPreset" :idx="idx" :search="search"
                                 settings-key="freelook_settings"
                                 :current_preset_idx="$refs.con.selectedPresetIdx"
                                 :view_mode="$refs.con.viewMode"
                                 @update-setting="$refs.con.updateSetting"
                                 @set-busy="setBusy"
                                 @make-toast="makeToast"/>
            <GenericSettingsArea :preset="conPreset" :idx="idx" :search="search"
                                 settings-key="gamepad_mouse_settings"
                                 :current_preset_idx="$refs.con.selectedPresetIdx"
                                 :view_mode="$refs.con.viewMode"
                                 @update-setting="$refs.con.updateSetting"
                                 @set-busy="setBusy"
                                 @make-toast="makeToast"/>
            <GenericSettingsArea :preset="conPreset" :idx="idx" :search="search"
                                 settings-key="general_steering_settings"
                                 :current_preset_idx="$refs.con.selectedPresetIdx"
                                 :view_mode="$refs.con.viewMode"
                                 @update-setting="$refs.con.updateSetting"
                                 @set-busy="setBusy"
                                 @make-toast="makeToast"/>
          </div>
        </div>
      </b-overlay>
    </template>

    <!-- Generic Settings-->
    <template  v-if="navActive === 3">
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
                  @make-toast="makeToast" />

        <div>
          <div v-for="(genPreset, idx) in $refs.gen.presets" :key="genPreset.name">
            <GenericSettingsArea :preset="genPreset" :idx="idx" :search="search"
                                 settings-key="game_options"
                                 :current_preset_idx="$refs.gen.selectedPresetIdx"
                                 :view_mode="$refs.gen.viewMode"
                                 @update-setting="$refs.gen.updateSetting"
                                 @set-busy="setBusy"
                                 @make-toast="makeToast"/>
          </div>
        </div>
      </b-overlay>
    </template>

    <!-- Headlights -->
    <Headlights ref="headlights" v-if="navActive === 4" @make-toast="makeToast"></Headlights>

    <!-- Server Browser -->
    <keep-alive>
      <ServerBrowser ref="serverBrowser" v-if="navActive === 5" @launch="stopSlideShow"
               @make-toast="makeToast" @set-busy="setBusy"
               @fav-updated="refreshDashFavs = true"/>
    </keep-alive>

    <!-- Wiki -->
    <template  v-if="navActive === 6">
      <Wiki></Wiki>
    </template>

    <!-- rFactor Actions -->
    <b-container fluid class="mt-3 p-0">
      <b-row>
        <b-col cols="8" class="text-left">
          <LaunchRfactorBtn @make-toast="makeToast" @launch="stopSlideShow"></LaunchRfactorBtn>
        </b-col>
        <b-col cols="4" class="text-right">
          <b-button size="sm" variant="secondary" class="ml-2" v-b-popover.auto.hover="'Open rF2 vehicle setups folder'"
                    @click="openSetupFolder">
            <b-icon icon="folder"></b-icon>
          </b-button>
          <b-button size="sm" variant="secondary" class="ml-2" v-b-popover.auto.hover="'Run rF2 ModMgr.exe'"
                    @click="runModMgr">
            <b-icon icon="archive-fill"></b-icon>
          </b-button>
          <b-button size="sm" class="ml-2" variant="secondary" id="restore-btn"
                    v-b-popover.auto.hover="'Restore your original settings'">
              <b-icon icon="arrow-counterclockwise" class="text-white"></b-icon>
          </b-button>
        </b-col>
      </b-row>
    </b-container>

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
    <b-overlay no-wrap variant="transparent" :show="isBusy" blur="1px"></b-overlay>
  </div>
</template>

<script>
import Dashboard from "@/components/Dashboard";
import PresetUi from "@/components/PresetUi";
import GraphicsArea from "@/components/GraphicsArea";
import ServerBrowser from "@/components/ServerBrowser";
import PresetHandler from "@/components/PresetHandler";
import GenericSettingsArea from "@/components/GenericSettingsArea";
import Wiki from "@/components/Wiki";
import LaunchRfactorBtn from "@/components/LaunchRfactorBtn";
import {getEelJsonObject} from "@/main";
import Headlights from "@/components/Headlights";

export default {
  name: 'Main',
  data: function () {
    return {
      navActive: 0,
      search: '',
      firstServerBrowserVisit: true,
      gfxReady: false,
      isBusy: false,
      refreshDashFavs: false,
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
      })
    },
    setBusy: function (busy) { this.isBusy = busy},
    setDashGfxHandler: function () {
      this.gfxReady = true
      this.$nextTick(() => {
        if (this.$refs.dash !== undefined) { this.$refs.dash.gfxPresetsReady = true }
      })
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
        default:
          this.makeToast('The type of preset you dropped is not supported or from a newer version than' +
              'your version of the app.', 'warning', 'Preset Import')
      }
      console.log(importPreset.preset_type)
    },
    setError: async function (error) { this.$emit('error', error) },
    stopSlideShow() {
      if (this.$refs.dash !== undefined) { this.$refs.dash.$refs.slider.stop() }
    },
    openSetupFolder: async function () { await window.eel.open_setup_folder()() },
    runModMgr: async function () { await window.eel.run_mod_mgr()() },
    restoreSettings: async function () {
      const r = await getEelJsonObject(window.eel.restore_backup()())
      if (r.result) {
        this.makeToast(r.msg, 'warning', 'Re-Store')
        await this.$refs.gfx.getPresets()
        await this.$refs.con.getPresets()
        await this.$refs.gen.getPresets()
      }
      if (!r.result) { this.makeToast(r.msg, 'danger', 'Re-Store Original Settings') }
      this.$root.$emit('bv::hide::popover', 'restore-btn')
    },
  },
  computed: {
    navSearchEnabled() {
      return [0, 4].indexOf(this.navActive) === -1;
    },
  },
  components: {
    Headlights,
    LaunchRfactorBtn,
    GenericSettingsArea,
    Dashboard,
    ServerBrowser,
    PresetHandler,
    PresetUi,
    GraphicsArea,
    Wiki
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#main {
  width: 92%;
  margin: 0 auto 0 auto;
}
#wiki-nav a { padding-right: 0; }
.nav-link.active {
  text-decoration: underline;
  text-decoration-skip-ink: auto;
}
.search-bar {
  background: transparent; border: none;
}
.search-off { opacity: 0.3; }
</style>
