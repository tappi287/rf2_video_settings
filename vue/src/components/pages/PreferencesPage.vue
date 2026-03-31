<template>
  <div v-cloak v-if="visible" id="settings" class="position-relative mb-5 text-left">
    <b-input-group class="pb-2" size="sm">
      <b-input-group-prepend>
        <div class="pl-0 pr-1 rpl-con position-relative bg-transparent">
          <b-img width=".3rem" class="rpl-icon" src="@/assets/rfW_logo_color.svg"></b-img>
        </div>
        <!-- Title -->
        <b-input-group-text class="bg-transparent no-border title text-white pl-0">
          App Preferences
        </b-input-group-text>
      </b-input-group-prepend>

      <!-- Spacer -->
      <div class="form-control bg-transparent no-border"></div>
    </b-input-group>

    <b-card class="setting-card mb-2" bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h6 class="mb-0 text-center"><span class="title">General</span></h6>
      </template>

      <b-checkbox-group :options="appOptions" v-model="appModules" @change="save" />

      <b-card-text class="mt-3">
        Weather to play audio feedback when using rf2-headlights or certain actions within the app.<br />
        You can prefer the Windows builtin Chromium Edge browser over Google Chrome to render this app.
        Changes apply after an app restart.
      </b-card-text>
    </b-card>

    <b-card class="setting-card mb-2" bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h5 class="mb-0"><span class="title">Autostart</span></h5>
      </template>
      <b-card-text>
        Which applications to automatically launch along with the game. This detects already running applications.
      </b-card-text>

      <b-checkbox-group :options="appAutostartOptions" v-model="appAutostart" @change="save" />
    </b-card>

    <b-card class="setting-card mb-2" bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h6 class="mb-0 text-center"><span class="title">Dashboard</span></h6>
      </template>

      <b-checkbox-group :options="dashboardOptions" v-model="dashboardModules" @change="save" />

      <b-card-text class="mt-3">
        Choose what you would like to see on your dashboard. There is no need to disable the Image Slideshow for
        performance reasons. It will stop once rF2 is running. App restart required.
      </b-card-text>

    </b-card>

    <b-card class="setting-card mb-2" bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h5 class="mb-0"><span class="title">Steam Web API Key</span></h5>
      </template>
      <b-card-text>
        Stored Steam Web API Key can be reset here. Enter it in the Server Browser.
      </b-card-text>

      <template v-if="steamWebApiKey !== ''">
        <b-button variant="danger" @click="resetSteamWebApiKey">Delete stored Key</b-button>
      </template>
      <template v-else>
        <span>No key stored.</span>
      </template>
    </b-card>

    <b-card class="setting-card" bg-variant="dark" text-variant="white">
      <template #header>
        <h6 class="mb-0 text-center"><span class="title">rFactor 2 Location</span></h6>
      </template>
      <RfLocation />
    </b-card>
  </div>
</template>

<script>
import {getEelJsonObject} from "@/main";
import RfLocation from "@/components/RfLocation.vue";

export default {
  name: "PreferencesPage",
  components: {RfLocation},
  props: {visible: Boolean},
  data: function () {
    return {
      dashboardModules: ['img', 'favs', 'cont'],
      dashboardOptions: [
          {text: 'Play Image Slideshow', value: 'img'},
          {text: 'Show Server Favourites', value: 'favs'},
          {text: 'Show Controller Devices', value: 'cont'}
      ],
      steamWebApiKey: '',
      appAutostart: [],
      appAutostartOptions: [
          {text: 'OpenKneeboard', value: 'kneeboard'},
          {text: 'CrewChiefV4', value: 'crew_chief'},
          {text: 'SimHub', value: 'sim_hub'},
      ],
      appModules: ['audio', 'edge_preferred'],
      appOptions: [
        {text: 'Enable Audio', value: 'audio'},
        {text: 'Prefer Edge Browser', value: 'edge_preferred'}
      ]
    }
  },
  methods: {
    async save () {
      let appPref = {}
      appPref['dashboardModules'] = this.dashboardModules
      appPref['appModules'] = this.appModules
      appPref['autostart'] = this.appAutostart
      appPref['steam_webapi_key'] = this.steamWebApiKey

      await getEelJsonObject(window.eel.save_app_preferences(appPref)())
    },
    async load () {
      const r = await getEelJsonObject(window.eel.load_app_preferences()())
      if (r.result) {
        const appPref = r.preferences
        if ('dashboardModules' in appPref) {
          this.dashboardModules = appPref['dashboardModules']
        }
        if ('appModules' in appPref) {
          this.appModules = appPref['appModules']
        }
        if ('autostart' in appPref) {
          this.appAutostart = appPref['autostart']
        }
        if ('steam_webapi_key' in appPref && appPref['steam_webapi_key']) {
          this.steamWebApiKey = appPref['steam_webapi_key']
        }
      }
    },
    async resetSteamWebApiKey () {
      this.steamWebApiKey = ''
      await this.save()
    }
  },
  async created() {
    await this.load()
  }
}
</script>

<style scoped>
  .rpl-icon { width: 2.075rem; }
  .rpl-con { margin-top: .1rem; }
</style>