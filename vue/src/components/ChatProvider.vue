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

      <!-- Channel Name -->
      <b-form-input v-model="currentSettings.channel" type="search" debounce="1000"
                    :placeholder="channelPlaceholder"
                    :disabled="!currentSettings.enabled"
                    @keydown.enter="activateProvider"
                    @change="saveSettings"
                    spellcheck="false" class="no-border w-40"
                    v-b-popover.auto.hover="channelPopOverText">
      </b-form-input>

      <!-- Prefix Input -->
      <b-form-input v-model="currentSettings.prefix" @change="saveSettings" debounce="1000"
                    id="prefix-input" class="no-border" placeholder="Prefix" :formatter="prefixFormatter"
                    v-b-popover.auto.hover="'Prefix new messages with this word e.g. Tw -> [Tw] User: message'"/>

      <b-input-group-append>
        <!-- Live indicator -->
        <b-input-group-append class="pl-2 bg-white">
          <span class="ml-2">
            <b-icon :icon="liveIndicator ? 'circle-fill' : 'circle-fill'"
                    :variant="liveIndicator ? 'success' : 'light'"
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
          <span v-if="youtubeLiveTitle === ''" class="ml-2">{{ providerName }} Chat</span>
          <span v-if="isYouTube && youtubeLiveTitle" class="ml-2">{{youtubeLiveTitle}}</span>
        </div>
      </template>
      <b-card-text></b-card-text>

      <b-card-text class="text-left small mb-3">
        <!-- Chat messages -->
        <p class="m-0 p-0" v-for="(message, idx) in chat" :key="idx">{{ message }}</p>

        <!-- Provider Active -->
        <p class="m-0 p-0" v-if="chat.length === 0 && currentProviderActive">
          <i>No messages received in this session.</i>
        </p>

        <!-- Twitch Inactive -->
        <p class="m-0 mt-2 p-0 text-center" v-if="!currentProviderActive && isTwitch">
          Enter your user/channel name and click Start.<br />
          Chat messages will be forwarded to your rF2 in-game message window.
        </p>

        <!-- YouTube Inactive -->
        <p class="m-0 mt-2 p-0 text-center" v-if="!currentProviderActive && isYouTube">
          Enter your user/channel name and click Start.<br />
          Click Start to begin receiving messages from your YouTube live stream to the rF2 in-game message window.
        </p>
      </b-card-text>
    </b-card>
    <!--
    <div class="mt-2" v-if="isYouTube">
      <span class="small">Using YouTube requires you to agree to these
        <b-link class="text-rf-orange"
                href="https://github.com/tappi287/rf2_video_settings/blob/master/Terms.md" target="_blank">
          Terms and Conditions</b-link>.
      </span>
    </div>
    -->
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
      this.youtubeLiveTitle = event.detail
    },
    youtubeErrors (event) {
      const errors = event.detail
      for (let idx in errors) {
        const error = errors[idx]
        this.$emit('make-toast', error.message, 'danger', error.domain, true, null, true)
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
      if (this.currentSettings.channel === "") { return }
      await getEelJsonObject(window.eel.set_youtube_username(this.currentSettings.channel)())

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
    async startUp() {
      for (let key in this.providerDetails) {
        const value = this.providerDetails[key]

        if (key === 'settings') {
          this.currentSettings = value
        } else {
          this[key] = value
        }
      }

      // Start chat provider
      if (this.currentSettings.startup) { this.activateProvider() }
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
    liveIndicator () {
      if (this.providerName === 'Twitch') { return this.client !== undefined }
      return this.youtubeLiveTitle !== ""
    },
    isTwitch () { return this.providerName === 'Twitch' },
    isYouTube () { return this.providerName === 'YouTube' },
    isEnabled () {
      return this.currentSettings.enabled
    },
    channelPlaceholder () {
      if (this.providerName === 'Twitch') { return 'Enter Twitch Channel Name / Nickname..' }
      return 'Enter your YouTube username'
    },
    channelPopOverText () {
      if (this.providerName === 'Twitch') { return 'Enter your Twitch Channel Name without URL e.g. ' +
          'myusername (not twitch.tv/myusername)' }
      return 'Enter your YouTube username without URL e.g. myusername (not youtube.com/channel/myusername)'
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