<template>
  <b-button-group>
    <b-dropdown variant="primary" size="sm" right split @click="launchRfactor">
      <template #button-content class="rounded-right">
        <b-icon icon="play"></b-icon>
        {{ buttonText }}
        <span class="ml-2" v-if="displayLive">
          <b-icon shift-v="-1" :icon="live ? 'circle-fill' : 'circle'" :variant="live ? 'success' : 'primary'"/>
        </span>
      </template>
      <b-dropdown-item @click="launchRfactor">
        Launch via Steam
      </b-dropdown-item>
      <b-dropdown-item v-b-popover.auto.hover="'Updated Workshop item packages will not be installed or synced.' +
       ' But if you have eg. a dedicated Server running. This is the method to launch rF2 anyway. Make sure you ' +
       'have configured your WebUI ports correctly.'"
                       @click="launchRfactor(1)">
        Launch via Exe
      </b-dropdown-item>
    </b-dropdown>
  </b-button-group>
</template>

<script>
import {getEelJsonObject} from "@/main";
// --- </ Prepare receiving rfactor live events
window.eel.expose(rfactorLiveFunc, 'rfactor_live')
async function rfactorLiveFunc (event) {
  const liveEvent = new CustomEvent('rfactor-live-event', {detail: event})
  window.dispatchEvent(liveEvent)
}
// --- />

export default {
name: "LaunchRfactorBtn",
  props: {text: String, server: Object, displayLive: Boolean},
  data: function () {
    return { live: false }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    updateRfactorState: function (event) {
      this.live = event.detail
    },
    launchRfactor: async function (method) {
      if (typeof (method) !== 'number') { method = 0 }
      let r = await getEelJsonObject(window.eel.run_rfactor(this.serverData, method)())
      if (r !== undefined && r.result) {
        this.makeToast('rFactor2.exe launched. Do not change settings here while the game is running. ' +
            'The game would overwrite those settings anyway upon exit.', 'success', 'rFactor 2 Launch')
        this.$emit('launch')
      } else {
        this.makeToast('Could not launch rFactor2.exe', 'danger', 'rFactor 2 Launch')
        this.$emit('launch-failed')
      }
    },
  },
  computed: {
    serverData: function ()  {
      if (this.server !== undefined) { return this.server }
      // make sure we send Python: None object
      return undefined
    },
    buttonText: function () {
      if (this.text !== undefined) { return this.text }
      return 'Start rFactor 2'
    }
  },
  mounted() {
    if (this.displayLive) {
      window.addEventListener('rfactor-live-event', this.updateRfactorState)
    }
  },
  destroyed() {
    if (this.displayLive) {
      window.removeEventListener('rfactor-live-event', this.updateRfactorState)
    }
  }
}
</script>

<style scoped>

</style>