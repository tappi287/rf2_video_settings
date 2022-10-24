<template>
  <div v-cloak id="chat" v-if="visible" class="position-relative mb-2">
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
                    :disabled="!currentProvider.enabled"
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
                         @change="saveSettings" :disabled="!currentProvider.enabled"
                         class="text-dark bg-white enable-box" switch size="lg">
          Start with app
        </b-form-checkbox>

        <!-- Start Stop Buttons -->
        <b-button-group>
          <b-button variant="rf-secondary" size="sm" :disabled="!currentProvider.enabled"
                    @click="activateProvider">
            <b-icon class="mr-2 ml-1" icon="play-circle-fill" shift-v="0.75" aria-hidden="true"></b-icon>
            Start
          </b-button>
          <b-button variant="rf-secondary" size="sm" :disabled="!currentProvider.enabled"
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
        <!-- Twitch -->
        <p class="m-0 mt-2 p-0 text-center" v-if="!currentProviderActive && isTwitch">
          Enter your <b>user/channel name</b> and click Start.
          Chat messages will be forwarded to your rF2 in-game message window.
        </p>
        <!-- YouTube -->
        <p class="m-0 mt-2 p-0 text-center" v-if="!currentProviderActive && isYouTube">
          Enter your YouTube <b>Channel-Id</b> that you can find at
          <b-link href="https://www.youtube.com/account_advanced" target="_blank">youtube.com/account_advanced</b-link>
          and click Start.
          Chat messages will be forwarded to your rF2 in-game message window.
        </p>
      </b-card-text>
    </b-card>

    <ChatPlugin></ChatPlugin>
  </div>
</template>

<script>
import {getEelJsonObject} from "@/main";
import ChatPlugin from "@/components/pages/ChatPlugin";
import {LiveChat} from 'youtube-chat'
const tmi = require('tmi.js');

const twitch = 0;
const youtube = 1;

export default {
  name: "ChatPage.vue",
  components: {ChatPlugin},
  data: function () {
    return {
      providers: [
        {
          name: "Twitch",
          enabled: true,
          settings: {channel: "", startup: false},
          chat: [],
          icon: "twitch", client: undefined
        },
        {
          name: "YouTube",
          enabled: true,
          settings: {channel: "", startup: false},
          chat: [],
          icon: "youtube", client: undefined
        }
      ],
      twitchUrl: "",
      youtubeUrl: "",
      currentProviderIdx: 0,
      chatLength: 8
    }
  },
  props: {live: Boolean, visible: Boolean},
  methods: {
    chooseProvider(idx) {
      this.currentProviderIdx = idx;
    },
    activateProvider() {
      if (this.currentProviderIdx === twitch) {
        this.activateTmi()
      } else if (this.currentProviderIdx === youtube) {
        this.activateYT()
      }
      this.saveSettings()
    },
    deactivateProvider() {
      if (this.currentProviderIdx === twitch) {
        this.deactivateTmi()
      } else if (this.currentProviderIdx === youtube) {
        this.deactivateYT()
      }
    },
    addChatMessage(chatMsgArray, message) {
      this.postMessage(message)
      return [...chatMsgArray.slice(-this.chatLength), message]
    },
    addYTChatMessage(chatMsgArray, chatItem) {
      const msg = chatItem.author.name + ': ' + chatItem.message.text
      return this.addChatMessage(chatMsgArray, msg)
    },
    addTmiChatMessage(chatMsgArray, tags, message) {
      const msg = `${tags['display-name']}: ${message}`
      return this.addChatMessage(chatMsgArray, msg)
    },
    activateTmi() {
      if (this.providers[twitch].settings.channel === "") { return }

      this.providers[twitch].client = new tmi.Client({channels: [this.providers[twitch].settings.channel]})
      this.providers[twitch].client.connect()
      this.providers[twitch].chat = []
      this.providers[twitch].client.on('message', (channel, tags, message) => {
        this.providers[twitch].chat = this.addTmiChatMessage(this.providers[twitch].chat, tags, message)
      });
    },
    deactivateTmi() {
      if (this.providers[twitch].client !== undefined) {
        this.providers[twitch].client.disconnect()
        this.providers[twitch].client = undefined
      }
    },
    async activateYT() {
      if (this.providers[youtube].settings.channel === "") { return }

      this.providers[youtube].client = new LiveChat({channelId: this.providers[youtube].settings.channel})
      this.providers[youtube].chat = []

      this.providers[youtube].client.on("error", (err) => {
        this.$emit('make-toast', err, "warning", "YouTube Live Chat", false, 4000)
      })
      this.providers[youtube].client.on("chat", (chatItem) => {
        this.addYTChatMessage(this.providers[youtube].chat, chatItem)
      })

      const ok = await this.providers[youtube].client.start()
      if (!ok) {
        this.$emit('make-toast', "Could not start fetching YouTube Live Chat.", "" +
            "danger", "YouTube", false, 4000)
        await this.deactivateYT()
      }
    },
    async deactivateYT() {
      if (this.providers[youtube].client !== undefined) {
        await this.providers[youtube].client.stop()
        this.providers[youtube].client = undefined
      }
    },
    startUp() {
      for (let idx in this.providers) {
        if (idx === twitch) {
          if (this.providers[idx].settings.startup) { this.activateTmi() }
        } else if (idx === youtube) {
          if (this.providers[idx].settings.startup) { this.activateYT() }
        }
      }
    },
    async postMessage(message) {
      await window.eel.post_chat_message(message)()
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
    }
  },
  computed: {
    currentProvider() {
      return this.providers[this.currentProviderIdx]
    },
    currentProviderName() {
      return this.currentProvider.name
    },
    isYouTube() {
      return this.currentProviderIdx === youtube
    },
    isTwitch() {
      return this.currentProviderIdx === twitch
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