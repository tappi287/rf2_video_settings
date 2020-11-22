<template>
  <div id="updater" v-if="updatedVersion !== ''" class="mt-2">
    <template v-if="error === ''">
      <p>Update available!</p>
      <template v-if="!updateReady">
        <b-button size="sm" variant="primary" @click="downloadUpdate" :disabled="downloadInProgress">
          <b-spinner small type="grow" v-if="downloadInProgress"></b-spinner>
          Download Version {{ updatedVersion }}
        </b-button>
      </template>
      <template v-else>
        <b-button size="sm" variant="success" @click="runUpdate">
          Run update installer {{ updatedVersion }}
        </b-button>
      </template>
    </template>
    <template v-else>
      <pre>{{ error }}</pre>
    </template>
  </div>
</template>

<script>
import {getEelJsonObject} from '@/main'

export default {
  name: 'Updater',
  data: function () {
    return {
      updatedVersion: '',
      downloadInProgress: false,
      updateReady: false,
      error: '',
    }
  },
  methods: {
    checkUpdate: async function () {
      const r = await getEelJsonObject(window.eel.check_for_updates()())
      if (r === undefined || r === null ) { return }
      if (r.result) {
        this.updatedVersion = r.version
      }
    },
    downloadUpdate: async function () {
      this.downloadInProgress = true
      const r = await getEelJsonObject(window.eel.download_update()())
      this.downloadInProgress = false
      if (r === undefined || r === null ) { return }
      if (r.result) {
        // Offer update run
        this.updateReady = true
      }
    },
    runUpdate: async function () {
      const r = await getEelJsonObject(window.eel.run_update()())
      if (r === undefined || r === null ) { return }
      if (!r.result) {
        this.error = 'Could not execute installer. Navigate to your Downloads directory and try to run it yourself.'
      }
    },
  },
  props: {
    // None yet
  },
  mounted() {
    /*
    Remove Auto-update for now

    setTimeout(() => {
      this.checkUpdate()
    }, 2500)
     */
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
