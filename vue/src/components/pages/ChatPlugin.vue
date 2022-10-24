<template>
  <div id="chat-plugin">
    <b-card class="mt-2 setting-card" bg-variant="dark" text-variant="white">
      <!-- Title -->
      <template #header>
        <div class="position-relative">
          <b-icon icon="chat-left-text-fill"/>
          <span class="ml-2">Chat Transceiver Plugin</span>
        </div>
      </template>
      <p class="text-center small">
        rFactor 2 plugin that forwards messages to your in-game message window.
        Convenient and performance friendly in VR.
      </p>
      <p>
        <b-link class="text-rf-orange" target="_blank" href="https://github.com/tappi287/rf2_chat_transceiver">
          rF2ChatTransceiver Plugin @ Github
        </b-link>
      </p>
      <div class="m-3 mt-4">
        <b-button-group>
          <b-button variant="rf-orange-light" :disabled="pluginInstalled" @click="installPlugin">
            Install Plugin
          </b-button>
          <b-button variant="rf-secondary" :disabled="!pluginInstalled" @click="uninstallPlugin">
            Remove Plugin <template v-if="pluginInstalled">v{{ pluginVersion }}</template>
          </b-button>
        </b-button-group>
      </div>

    </b-card>
  </div>
</template>

<script>
import {getEelJsonObject} from "@/main";

export default {
  name: "ChatPlugin",
  data: function () {
    return {
      pluginVersion_v: undefined,
    }
  },
  methods: {
    async installPlugin() {
      await window.eel.install_plugin()()
      await this.getPluginVersion()
    },
    async uninstallPlugin() {
      await window.eel.uninstall_plugin()()
      await this.getPluginVersion()
    },
    async getPluginVersion() {
      const r = await getEelJsonObject(window.eel.get_plugin_version()())
      if (!r.result) {
        this.pluginVersion_v = ''
        return
      }
      this.pluginVersion_v = r.version
    }
  },
  computed: {
    pluginVersion() {
      if (this.pluginVersion_v === undefined) { this.getPluginVersion() }
      return this.pluginVersion_v
    },
    pluginInstalled() {
      return this.pluginVersion_v !== undefined && this.pluginVersion !== "";
    }
  },
  async created() {
    await this.getPluginVersion()
  }
}
</script>

<style scoped>

</style>