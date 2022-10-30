<template>
  <div id="chat">
    <b-input-group size="sm" v-if="visible" class="mt-2">
      <b-input-group-prepend>
        <!-- Title -->
        <b-input-group-text class="bg-transparent no-border title text-white pl-0">
          Chat Transceiver Client
        </b-input-group-text>
      </b-input-group-prepend>

    <!-- Spacer -->
    <div class="form-control bg-transparent no-border">
    </div>
    </b-input-group>

    <template v-if="chatSettingsReady">
      <ChatProvider :provider-name="providers[0].name" :provider-details="providers[0]" :visible="visible"
                    @save-settings="saveSettings" @set-busy="setBusy" />
      <ChatProvider :provider-name="providers[1].name" :provider-details="providers[1]" :visible="visible"
                    @save-settings="saveSettings" @set-busy="setBusy" />
    </template>

    <b-card class="mt-2 setting-card" bg-variant="dark" text-variant="white" v-if="visible">
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
import ChatProvider from "@/components/ChatProvider";

export default {
  name: "ChatPage.vue",
  data: function () {
    return {
      providers: [
        {
          name: "Twitch",
          settings: {enabled: true, channel: "", startup: false, prefix: "TW"},
          chat: [],
          icon: "twitch", client: undefined
        },
        {
          name: "YouTube",
          settings: {enabled: true, channel: "", startup: false, prefix: "YT"},
          chat: [],
          icon: "youtube", client: undefined
        }
      ],
      twitchClient: undefined,
      chatLength: 8,
      pluginVersion_v: undefined,
      chatSettingsReady: false
    }
  },
  props: {live: Boolean, visible: Boolean},
  methods: {
    setBusy (busy) {
      this.$emit('set-busy', busy)
    },
    async saveSettings(event) {
      let settings = []

      for (let idx in this.providers) {
        if (this.providers[idx].name === event.provider) { this.providers[idx].settings = event.settings }
        settings.push(this.providers[idx].settings)
      }

      const r = await getEelJsonObject(window.eel.save_chat_settings(settings)())

      if (!r.result) {
        this.$emit('make-toast', r.msg, "danger", "Chat Settings", false, 4000)
        console.error('Error writing Chat Settings!', r.msg)
        console.log(r)
      } else {
        console.log('Saved Chat settings.')
      }
    },
    async getSettings() {
      const r = await getEelJsonObject(window.eel.get_chat_settings()())
      if (!r.result) {
        this.$emit('make-toast', r.msg, "danger", "Chat Settings", false, 4000)
        console.error('Error getting Chat settings!', r.msg)
        console.log(r)
        return
      }
      for (let idx in r.settings) {
        this.providers[idx].settings = r.settings[idx]
      }
      this.chatSettingsReady = true
    },
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
  watch: {
    visible() {
      this.isVisible = this.visible
    }
  },
  async created() {
    await this.getSettings()
    await this.getPluginVersion()
  },
  components: {ChatProvider}
}
</script>

<style scoped>

</style>