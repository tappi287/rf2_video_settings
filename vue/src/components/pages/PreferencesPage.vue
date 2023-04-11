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

    </b-card>

    <b-card class="setting-card" bg-variant="dark" text-variant="white" footer-class="pt-0">
      <template #header>
        <h6 class="mb-0 text-center"><span class="title">Dashboard</span></h6>
      </template>

      <b-checkbox-group :options="dashboardOptions" v-model="dashboardModules" @change="save" />

      <b-card-text class="mt-3">
        Choose what you would like to see on your dashboard. There is no need to disable the Image Slideshow for
        performance reasons. It will stop once rF2 is running.
      </b-card-text>

    </b-card>
  </div>
</template>

<script>
import {getEelJsonObject} from "@/main";

export default {
  name: "PreferencesPage",
  props: {visible: Boolean},
  data: function () {
    return {
      dashboardModules: ['img', 'favs', 'cont'],
      dashboardOptions: [
          {text: 'Image Slideshow', value: 'img'},
          {text: 'Show Favourites', value: 'favs'},
          {text: 'Show Controller', value: 'cont'}
      ],
      appModules: ['audio'],
      appOptions: [
        {text: 'Enable Audio Feedback', value: 'audio'}
      ]
    }
  },
  methods: {
    async save () {
      let appPref = {}
      appPref['dashboardModules'] = this.dashboardModules
      appPref['appModules'] = this.appModules

      await getEelJsonObject(window.eel.save_app_preferences(appPref)())
    },
    async load () {
      const r = await getEelJsonObject(window.eel.load_app_preferences()())
      if (r.result) {
        const appPref = r.preferences
        if ('dashboardModules' in appPref) {
          this.dashboardModules = appPref['dashboardModules']
          this.appModules = appPref['appModules']
        }
      }
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