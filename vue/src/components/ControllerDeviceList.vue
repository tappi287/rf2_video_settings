<template>
  <div v-if="visible">
    <b-card class="mt-2 setting-card no-border" header-class="m-0 p-2 text-center"
            :bg-variant="darkVar" :text-variant="whiteVar">
      <template #header>
          <b-icon icon="controller"></b-icon>
          <span :class="'ml-2'">Controller Devices</span>
      </template>
      <p class="small">
        Click on the Checkboxes to select input devices here that need to be connected when you start rF2.
        The app will warn you if a device is not connected while launching rF2.
      </p>
      <b-list-group class="text-left no-border">
        <b-list-group-item class="bg-transparent p-0 m-2 no-border" v-for="(c, idx) in controller" :key="idx">
          <!-- Device Connected Indicator -->
          <b-iconstack font-scale="1.5">
            <b-icon stacked icon="circle" scale="1" shift-v="-2.0"
                    :variant="c.connected ? whiteVar : mutedVar" />
            <b-icon stacked :icon="c.connected ? 'plug-fill' : 'dash'" :variant="c.connected ? whiteVar : mutedVar"
                    shift-v="-2.15" shift-h="0.05" scale="0.65" />
          </b-iconstack>
          <!-- Device Watched Checkbox -->
          <b-checkbox :checked="c.watched" switch inline @change="toggled($event, c.guid)" class="ml-3"
                      v-b-popover.hover.auto="deviceInfoEnabled(c.watched) + deviceInfoText(c.guid)">
            <span class="ml-1 device-name">{{ c.name }}</span>
          </b-checkbox>
          <!-- Remove device button -->
          <b-link class="small close-btn" v-if="!c.connected" @click="removeDevice(c.guid)">Remove from list</b-link>
        </b-list-group-item>
      </b-list-group>
    </b-card>
  </div>
</template>

<script>
import {getEelJsonObject} from "@/main";

// --- </ Prepare receiving controller device events
window.eel.expose(controllerDeviceEventFunc, 'controller_device_event')
async function controllerDeviceEventFunc (event) {
  const controllerDeviceEvent = new CustomEvent('controller-device-event', {detail: event})
  window.dispatchEvent(controllerDeviceEvent)
}
// --- />

export default {
  name: "ControllerDeviceList",
  data: function () {
    return {
      controller: [{'name': 'Example Device', 'guid': '0000123456789#123456', 'connected': false, 'watched': false},
                   {'name': 'Sim Pedals', 'guid': '000023', 'connected': true, 'watched': true}],
      darkVar: 'dark', whiteVar: 'white', mutedVar: 'dark'
    }
  },
  props: {visible: Boolean, cardStyle: String},
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) {
      this.$emit('set-busy', busy)
    },
    deviceInfoEnabled: function (watched) {
      if (watched) { return ""}
      return 'Enable to get a warning before launch if this device is not connected. '
    },
    deviceInfoText: function (guid) {
      let msg = ""

      this.controller.forEach( (device) => {
        if (device.guid === guid) {
          if (device.connected && device.watched) {
            msg = "Device is connected and monitored."
          } else if (device.connected && !device.watched) {
            msg = "Device is connected but not monitored. You will not be notified upon rF2 launch."
          } else if (!device.connected && device.watched) {
            msg = "Device is monitored but not connected. App will warn you about this upon rF2 launch."
          } else if (!device.connected && !device.watched) {
            msg = "Device is not connected and not monitored. You will not be notified upon rF2 launch."
          }
        }
      })
      return msg
    },
    toggled (event, guid) {
      this.controller.forEach( (device) => {
        if (device.guid === guid) {
          device.watched = Boolean(event)
        }
      })
      this.saveDeviceList()
    },
    async removeDevice (deviceGuid) {
      await getEelJsonObject(window.eel.remove_from_device_list(deviceGuid)())
      await this.getDeviceList()
    },
    async getDeviceList () {
      this.controller = await getEelJsonObject(window.eel.get_device_list()())
      await this.sendUpdateEvent()
    },
    async saveDeviceList () {
      await getEelJsonObject(window.eel.save_device_list(this.controller)())
      await this.sendUpdateEvent()
    },
    receiveControllerDeviceEvent (event) {
      this.controller = JSON.parse(event.detail)
      this.saveDeviceList()
    },
    async sendUpdateEvent () {
      let devicesReady = true
      let msg = []

      this.controller.forEach( (device) => {
        if (device.watched && !device.connected) {
          devicesReady = false
          msg.push(device.name)
        }
      })

      const deviceEvent = {devicesReady: devicesReady, deviceList: msg}
      this.$eventHub.$emit('deviceUpdate', deviceEvent)
    }
  },
  async mounted() {
    await this.getDeviceList()
  },
  async created() {
    if (this.cardStyle === 'bright') { this.darkVar = 'white'; this.whiteVar = 'dark'; this.mutedVar = 'muted'}
    await this.getDeviceList()
    this.$eventHub.$on('requestDeviceUpdate', this.sendUpdateEvent)
    window.addEventListener('controller-device-event', this.receiveControllerDeviceEvent)
  },
  destroyed() {
    this.$eventHub.$off('requestDeviceUpdate', this.sendUpdateEvent)
    window.removeEventListener('controller-device-event', this.receiveControllerDeviceEvent)
  },
}
</script>

<style scoped>
.device-name { font-family: "Ubuntu", sans-serif; }
.close-btn { height: 1.5rem; }
.no-border { border: none; }
</style>