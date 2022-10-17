<template>
  <div v-cloak id="chat" class="position-relative mb-2">
    <b-input-group size="sm">
      <b-input-group-prepend>
        <div class="pl-0 pr-1 rpl-con position-relative bg-transparent" v-if="false">
          <b-img width=".3rem" class="rpl-icon" src="@/assets/TwitchGlitchPurple.svg"></b-img>
        </div>
        <!-- Title -->
        <b-input-group-text class="bg-transparent no-border title text-white pl-0">
          Chat Transceiver Client
        </b-input-group-text>
      </b-input-group-prepend>

    <!-- Spacer -->
    <div class="form-control bg-transparent no-border">
    </div>
    </b-input-group>

    <!-- Input -->
    <b-input-group size="sm" class="mt-2 table-bar">
      <b-input-group-prepend>
        <b-input-group-text class="rf-secondary border-0 low-round-left">
          <b-icon :icon="currentProvider.icon" :variant="currentProviderActive ? 'success' : 'dark'"
                  aria-hidden="true"></b-icon>
        </b-input-group-text>
      </b-input-group-prepend>

      <b-form-input v-model="currentProvider.settings.channel" type="search" debounce="1000"
                    :placeholder="'Enter ' + currentProviderName + ' Channel Name / Nickname..'"
                    :disabled="!currentProvider.settings.enabled"
                    @keydown.enter="activateProvider"
                    spellcheck="false" class="no-border">
      </b-form-input>

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
        <b-form-checkbox v-model="currentProvider.settings.startup"
                         @change="saveSettings" :disabled="!currentProvider.settings.enabled"
                         class="text-dark bg-white enable-box" switch size="lg">
          Start with app
        </b-form-checkbox>

        <!-- Start Stop Buttons -->
        <b-button-group>
          <b-button variant="rf-secondary" size="sm" :disabled="!currentProvider.settings.enabled"
                    @click="activateProvider">
            <b-icon class="mr-2 ml-1" icon="play-circle-fill" shift-v="0.75" aria-hidden="true"></b-icon>
            Start
          </b-button>
          <b-button variant="rf-secondary" size="sm" :disabled="!currentProvider.settings.enabled"
                    @click="deactivateProvider">
            <b-icon class="mr-2 ml-1" icon="stop-circle-fill" shift-v="0.75" aria-hidden="true"></b-icon>
            Stop
          </b-button>
        </b-button-group>

        <!-- Chat Provider Selection -->
        <b-input-group-text class="info-field fixed-width-name">
          Provider:
        </b-input-group-text>
        <b-dropdown size="sm" :text="currentProviderName" right
                    class="setting-item fixed-width-setting no-border"
                    v-b-popover.auto.hover="'Select a chat provider to configure.'"
                    variant="rf-orange">
          <b-dropdown-item v-for="(provider, idx) in providers" :key="idx"
                           @click="chooseProvider(idx)">
            {{ provider.name }}
          </b-dropdown-item>
        </b-dropdown>
      </b-input-group-append>
    </b-input-group>
    <b-card class="mt-2 setting-card" bg-variant="dark" text-variant="white">
      <template #header>
        <div class="position-relative">
          <b-icon :icon="currentProvider.icon"/>
          <span class="ml-2">{{ currentProviderName }} Chat</span>
        </div>
      </template>
      <b-card-text></b-card-text>
      <b-card-text class="text-left small mb-3">
        <p class="m-0 p-0" v-for="(message, idx) in currentProvider.chat" :key="idx">{{ message }}</p>
        <p class="m-0 p-0" v-if="currentProvider.chat.length === 0 && currentProviderActive">
          <i>No messages received in this session.</i>
        </p>
        <p class="m-0 mt-2 p-0 text-center" v-if="!currentProviderActive">
          Enter your user/channel name and click Start.
          Chat messages will be forwarded to your rF2 in-game message window.
        </p>
      </b-card-text>
    </b-card>

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
          <b-button variant="rf-orange-light">Install Plugin</b-button>
          <b-button variant="rf-secondary">Remove Plugin</b-button>
        </b-button-group>
      </div>

    </b-card>
  </div>
</template>

<script>
import {getEelJsonObject} from "@/main";

const tmi = require('tmi.js');

export default {
  name: "ChatPage.vue",
  data: function () {
    return {
      providers: [
        {
          name: "Twitch",
          settings: {enabled: true, channel: "", startup: false},
          chat: [],
          icon: "twitch", client: undefined
        },
        {
          name: "YouTube",
          settings: {enabled: false, channel: "", startup: false},
          chat: ["YouTube is not implemented yet!"],
          icon: "youtube", client: undefined
        }
      ],
      twitchUrl: "",
      youtubeUrl: "",
      currentProviderIdx: 0,
      chatLength: 4,
    }
  },
  props: {live: Boolean},
  methods: {
    chooseProvider(idx) {
      this.currentProviderIdx = idx;
    },
    addChatMessage(chat_array, tags, message) {
      const msg = `${tags['display-name']}: ${message}`
      return [...chat_array.slice(-this.chatLength), msg]
    },
    activateProvider() {
      if (this.currentProvider.name === "Twitch") {
        this.activateTmi()
      }
      this.saveSettings()
    },
    deactivateProvider() {
      if (this.currentProvider.name === "Twitch") {
        this.deactivateTmi()
      }
    },
    activateTmi() {
      if (this.providers[0].settings.channel === "") {
        return
      }

      this.providers[0].client = new tmi.Client({channels: [this.providers[0].settings.channel]})
      this.providers[0].client.connect()
      this.providers[0].chat = []
      this.providers[0].client.on('message', (channel, tags, message) => {
        this.providers[0].chat = this.addChatMessage(this.providers[0].chat, tags, message)
      });
    },
    deactivateTmi() {
      if (this.providers[0].client !== undefined) {
        this.providers[0].client.disconnect()
        this.providers[0].client = undefined
      }
    },
    startUp() {
      for (let idx in this.providers) {
        if (this.providers[idx].name === "Twitch") {
          if (this.providers[idx].settings.startup) {
            this.activateTmi()
          }
        }
        if (this.providers[idx].name === "YouTube") {
          if (this.providers[idx].settings.startup) {
            console.log("YouTube not implemented")
          }
        }
      }
    },
    async saveSettings() {
      let settings = [];
      for (let idx in this.providers) {
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
    },
  },
  computed: {
    currentProvider() {
      return this.providers[this.currentProviderIdx]
    },
    currentProviderName() {
      return this.currentProvider.name
    },
    currentProviderActive() {
      return this.currentProvider.client !== undefined
    }
  },
  async created() {
    await this.getSettings()
    this.startUp()
  }
}
</script>

<style scoped>
.rpl-icon {
  width: 1.5rem;
}

.enable-box {
  padding-top: 0.3rem;
  padding-right: 0.6rem;
  padding-left: 2.7rem;
}

.rpl-con {
  margin-top: .1rem;
}
</style>