<template>
  <div v-if="visible">
    <!-- Input -->
    <b-input-group size="sm" class="mt-2 table-bar">
      <b-input-group-prepend>
        <b-input-group-text class="rf-secondary border-0 low-round-left">
          <b-icon :icon="icon" :variant="currentProviderActive ? 'success' : 'dark'"
                  aria-hidden="true"></b-icon>
        </b-input-group-text>
      </b-input-group-prepend>

      <template v-if="providerName==='Twitch'">
        <b-form-input v-model="currentSettings.channel" type="search" debounce="1000"
                      :placeholder="'Enter Twitch Channel Name / Nickname..'"
                      :disabled="!currentSettings.enabled"
                      @keydown.enter="activateProvider"
                      @change="saveSettings"
                      spellcheck="false" class="no-border w-40"
                      v-b-popover.auto.hover="'Enter your Twitch Channel Name without URL e.g. myusername ' +
                                              '(not twitch.tv/myusername)'">
        </b-form-input>
      </template>
      <template v-else>
        <b-form-input :placeholder="youtubeLiveTitle" class="no-border bg-white w-40" :disabled="true" />
      </template>

      <!-- Prefix Input -->
      <b-form-input v-model="currentSettings.prefix" @change="saveSettings" debounce="1000"
                    id="prefix-input" class="no-border" placeholder="Prefix" :formatter="prefixFormatter"
                    v-b-popover.auto.hover="'Prefix new messages with this word e.g. Tw -> [Tw] User: message'"/>

      <b-input-group-append>
        <!-- Active indicator -->
        <b-input-group-append class="pl-2 bg-white">
          <span class="ml-2">
            <b-icon :icon="currentProviderActive ? 'circle-fill' : 'circle-fill'"
                    :variant="currentProviderActive ? 'success' : 'light'"
                    class="p-0 m-1" shift-v="-3"/>
          </span>
        </b-input-group-append>

        <!-- Enable StartUp -->
        <b-form-checkbox v-model="currentSettings.startup"
                         @change="saveSettings" :disabled="!isEnabled"
                         class="text-dark bg-white enable-box" switch size="lg">
          Start with app
        </b-form-checkbox>

        <!-- Start Stop Buttons -->
        <b-button-group>
          <b-button variant="rf-secondary" size="sm" :disabled="!isEnabled || currentProviderActive"
                    @click="activateProvider" class="pr-3">
            <b-icon class="mr-2 ml-1" icon="play-circle-fill" shift-v="0.75" aria-hidden="true"></b-icon>
            Start
          </b-button>
          <b-button variant="rf-secondary" size="sm" :disabled="!isEnabled || !currentProviderActive"
                    @click="deactivateProvider" class="pr-3">
            <b-icon class="mr-2 ml-1" icon="stop-circle-fill" shift-v="0.75" aria-hidden="true"></b-icon>
            Stop
          </b-button>
        </b-button-group>
      </b-input-group-append>
    </b-input-group>

    <!-- Chat -->
    <b-card class="mt-0 setting-card" bg-variant="dark" text-variant="white">
      <template #header>
        <div class="position-relative">
          <b-icon :icon="icon"/>
          <span class="ml-2">{{ providerName }} Chat</span>
        </div>
      </template>
      <b-card-text></b-card-text>

      <b-card-text class="text-left small mb-3" v-if="!showYtConnect">
        <p class="m-0 p-0" v-for="(message, idx) in chat" :key="idx">{{ message }}</p>

        <!-- Twitch Active -->
        <p class="m-0 p-0" v-if="chat.length === 0 && currentProviderActive">
          <i>No messages received in this session.</i>
        </p>

        <!-- Twitch Inactive -->
        <p class="m-0 mt-2 p-0 text-center" v-if="!currentProviderActive && isTwitch">
          Enter your user/channel name and click Start.
          Chat messages will be forwarded to your rF2 in-game message window.
        </p>

        <!-- YouTube not connected -->
        <p class="m-0 mt-2 p-0 text-center" v-if="showYtConnect">
          Connect your YouTube account with the button below to obtain messages from your live stream.
        </p>

        <!-- YouTube Inactive -->
        <p class="m-0 mt-2 p-0 text-center" v-if="showYtDisconnect && !currentProviderActive">
          Click Start to begin receiving messages from your YouTube live stream.
        </p>
      </b-card-text>

      <b-card-text class="text-center" v-if="isYouTube">
        <template v-if="showYtConnect">
          <b-button @click="acquireYouTubeCredentials" size="sm" variant="rf-orange">
            Connect YouTube Account
          </b-button>
          <div class="mt-2">
            <span class="small">Connecting to YouTube requires you to agree to these
              <b-link class="text-rf-orange"
                      href="https://github.com/tappi287/rf2_video_settings/blob/master/Terms.md" target="_blank">
                Terms and Conditions</b-link>.
            </span>
          </div>

        </template>
        <b-button @click="removeYouTubeCredentials" size="sm" variant="secondary" v-if="showYtDisconnect">
          Remove YouTube Account
        </b-button>
      </b-card-text>
    </b-card>
  </div>
</template>

<script>
import {getEelJsonObject} from "@/main";
import tmi from "tmi.js";

// --- </ Prepare receiving YouTube live chat messages
window.eel.expose(youtubeMessagesFunc, 'youtube_messages')
async function youtubeMessagesFunc (event) {
  const youtubeMessageEvent = new CustomEvent('youtube-message-event', {detail: event})
  window.dispatchEvent(youtubeMessageEvent)
}
window.eel.expose(youtubeErrorsFunc, 'youtube_errors')
async function youtubeErrorsFunc (event) {
  const youtubeErrorsEvent = new CustomEvent('youtube-errors-event', {detail: event})
  window.dispatchEvent(youtubeErrorsEvent)
}
window.eel.expose(youtubeLiveFunc, 'youtube_live')
async function youtubeLiveFunc (event) {
  const youtubeLiveEvent = new CustomEvent('youtube-live-event', {detail: event})
  window.dispatchEvent(youtubeLiveEvent)
}
// --- />

export default {
  name: "ChatProvider",
  data: function () {
    return {
      currentSettings: {enabled: true, channel: "", startup: false, prefix: ""},
      name: undefined,
      chat: [],
      icon: "",
      client: undefined,
      chatLength: 8,
      youtubeCredentialsFound: false,
      youtubeLiveTitle: "",
    }
  },
  props: {providerName: String, providerDetails: Object, visible: Boolean},
  methods: {
    setBusy (busy) {
      this.$emit('set-busy', busy)
    },
    prefixFormatter(value) {
      return value.slice(0, 7)
    },
    getPrefix() {
      if (this.currentSettings.prefix === "") { return ""}
      return `[${this.currentSettings.prefix}] `
    },
    activateProvider() {
      if (this.providerName === "Twitch") {
        this.activateTmi()
      } else if (this.providerName === 'YouTube') {
        this.activateYt()
      }
      this.saveSettings()
    },
    deactivateProvider() {
      if (this.providerName === "Twitch") {
        this.deactivateTmi()
      } else if (this.providerName === 'YouTube') {
        this.deactivateYt()
      }
      this.saveSettings()
    },
    youtubeLive (event) {
      const broadcastTitle = event.detail
      if (broadcastTitle === "") {
        this.youtubeLiveTitle = "No active broadcast"
      } else {
        this.youtubeLiveTitle = broadcastTitle
      }
    },
    youtubeErrors (event) {
      this.deactivateYt()

      const errors = event.detail
      for (let idx in errors) {
        const error = errors[idx]
        this.$emit('make-toast', error.message, 'danger', error.domain, true, 0)
      }
    },
    addYtChatMessages(event) {
      const messages = event.detail
      const prefix = this.getPrefix()

      for (let idx in messages) {
        const msg = `${prefix}${messages[idx]}`
        this.postMessage(msg)
        this.chat = [...this.chat.slice(-this.chatLength), msg]
      }
    },
    async activateYt() {
      const r = await getEelJsonObject(window.eel.start_youtube_chat_capture()())
      this.chat = []
      this.client = r.result
    },
    async deactivateYt() {
      window.eel.stop_youtube_chat_capture()()
      this.chat = []
      this.client = undefined
    },
    addTmiChatMessage(chat_array, tags, message) {
      const prefix = this.getPrefix()
      const msg = `${prefix}${tags['display-name']}: ${message}`
      this.postMessage(msg)
      return [...chat_array.slice(-this.chatLength), msg]
    },
    activateTmi() {
      if (this.currentSettings.channel === "") { return }

      this.client = new tmi.Client({channels: [this.currentSettings.channel]})
      this.client.connect()
      this.chat = []
      this.client.on('message', (channel, tags, message) => {
        this.chat = this.addTmiChatMessage(this.chat, tags, message)
      });
    },
    deactivateTmi() {
      if (this.client !== undefined) {
        this.client.disconnect()
        this.client = undefined
      }
    },
    async removeYouTubeCredentials() {
      window.eel.remove_youtube_credentials()()
      this.youtubeCredentialsFound = false
      await this.deactivateYt()
    },
    async loadYouTubeCredentials() {
      const r = await getEelJsonObject(window.eel.load_youtube_credentials()())
      this.youtubeCredentialsFound = r.result
    },
    async acquireYouTubeCredentials() {
      this.setBusy(true)
      const r = await getEelJsonObject(window.eel.acquire_youtube_credentials()())
      this.youtubeCredentialsFound = r.result
      this.setBusy(false)
    },
    async startUp() {
      for (let key in this.providerDetails) {
        const value = this.providerDetails[key]

        if (key === 'settings') {
          this.currentSettings = value
        } else {
          this[key] = value
        }
      }

      // Twitch
      if (this.providerName === "Twitch") {
        if (this.currentSettings.startup) {
          this.activateTmi()
        }
      }

      // YouTube
      if (this.providerName === "YouTube") {
        await this.loadYouTubeCredentials()

        if (this.currentSettings.startup && this.youtubeCredentialsFound) {
          await this.activateYt()
        }
      }
    },
    async postMessage(message) {
      console.log(this.providerName + ' Chat message: ' + message)
      await window.eel.post_chat_message(message)()
    },
    async saveSettings() {
      this.$emit('save-settings', {'settings': this.currentSettings, 'provider': this.providerName })
    }
  },
  computed: {
    currentProviderActive() { return this.client !== undefined },
    isTwitch () { return this.providerName === 'Twitch' },
    isYouTube () { return this.providerName === 'YouTube' },
    isEnabled () {
      if (this.providerName === 'Twitch') { return this.currentSettings.enabled }
      return this.youtubeCredentialsFound
    },
    showYtConnect () {
      if (this.providerName === 'Twitch') { return false }
      return !this.youtubeCredentialsFound
    },
    showYtDisconnect () {
      if (this.providerName === 'Twitch') { return false }
      return this.youtubeCredentialsFound
    }
  },
  async created() {
    if (this.providerName === 'YouTube') {
      window.addEventListener('youtube-message-event', this.addYtChatMessages)
      window.addEventListener('youtube-errors-event', this.youtubeErrors)
      window.addEventListener('youtube-live-event', this.youtubeLive)
    }

    console.log('Created Chat Provider: ' + this.providerName)
    await this.startUp()
  },
  destroyed() {
    if (this.providerName === 'YouTube') {
      window.removeEventListener('youtube-message-event', this.addYtChatMessages)
      window.removeEventListener('youtube-errors-event', this.youtubeErrors)
      window.removeEventListener('youtube-live-event', this.youtubeLive)
    }
    this.deactivateTmi()
    this.deactivateYt()
    console.log('Destroyed Chat Provider: ' + this.providerName)
  },
}
</script>

<style scoped>
.enable-box {
  padding-top: 0.3rem;
  padding-right: 0.6rem;
  padding-left: 2.7rem;
}
.w-40 {
  width: 40%;
}
</style>