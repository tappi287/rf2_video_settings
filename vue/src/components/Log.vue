<template>
  <div v-cloak id="log" class="position-relative mb-5 text-left">
    <div class="spacer rounded text-center">
      <h4 class="text-dark">Log</h4>
    </div>

    <div class="mt-1">
      <b-button variant="success" @click="refresh">Refresh</b-button>
      <b-button class="ml-2" variant="secondary" @click="openLogFolder">Open Log Folder</b-button>
    </div>

    <div class="mt-1">
      <pre class="text-white">{{logContent}}</pre>
    </div>
  </div>
</template>

<script>

import {getEelJsonObject} from "@/main";

export default {
  name: "Log",
  data: function () {
    return {
      logContent: '',
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    refresh: async function () {
      const r = await getEelJsonObject(window.eel.get_log()())
      if (r.result) {
        this.makeToast('Refresh log from file.', 'success', 'App Log')
        this.logContent = r.log
      } else if (!r.result) {
        this.makeToast('Error obtaining log content! ' + r.msg, 'danger', 'App Log')
      }
    },
    openLogFolder: async function() {
      await window.eel.open_log_folder()()
    },
  },
  created() {
    this.refresh()
  },
  components: {
  },
}
</script>

<style scoped>
h1, h2, h3, h4, h5 { font-family: Inter, "Segoe UI", system-ui, sans-serif; }
.spacer { width: 100%; height: 1.75rem; background: #efefef; }
</style>

<style>

</style>