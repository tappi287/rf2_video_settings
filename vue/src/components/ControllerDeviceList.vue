<template>
  <div v-if="visible">
    <b-card class="mt-2 setting-card" header-class="m-0 p-2"
            bg-variant="dark" text-variant="white">
      <template #header>
          <b-icon icon="controller"></b-icon>
          <span :class="'ml-2'">Controller Devices</span>
      </template>
      <p class="small">
        Select Controller Devices here that need to be connected when you start the Sim. The app will warn you
        if a device is not connected.
      </p>
      <b-list-group class="text-left">
        <b-list-group-item class="bg-transparent p-0 m-2" v-for="(c, idx) in controller" :key="idx">
          <!-- Device Connected Indicator -->
          <b-iconstack font-scale="1.5" v-b-popover.hover.auto="deviceInfoText(c.guid)">
            <b-icon stacked icon="circle" scale="1" shift-v="-2.0"
                    :variant="c.connected ? 'white' : 'dark'" />
            <b-icon stacked :icon="c.connected ? 'plug-fill' : 'dash'" :variant="c.connected ? 'white' : 'dark'"
                    shift-v="-2.15" shift-h="0.05" scale="0.65" />
          </b-iconstack>
          <!-- Device Watched Checkbox -->
          <b-checkbox :checked="c.watched" switch inline @change="toggled($event, c.name)" class="ml-3">
            <span class="ml-1 device-name">{{ c.name }}</span>
          </b-checkbox>
        </b-list-group-item>
      </b-list-group>
    </b-card>
  </div>
</template>

<script>
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
                   {'name': 'Sim Pedals', 'guid': '000023', 'connected': true, 'watched': true}]
    }
  },
  props: {visible: Boolean},
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) {
      this.$emit('set-busy', busy)
    },
    deviceInfoText: function (guid) {
      let msg = ""

      this.controller.forEach( (device) => {
        if (device.guid === guid) {
          if (device.connected && device.watched) {
            msg = "Device is connected and watched."
          } else if (device.connected && !device.watched) {
            msg = "Device is connected but not watched. You will not be notified upon rF2 launch."
          } else if (!device.connected && device.watched) {
            msg = "Device is not connected. App will warn you about this upon rF2 launch."
          } else if (!device.connected && !device.watched) {
            msg = "Device is not connected and not watched. You will not be notified upon rF2 launch."
          }
        }
      })
      return msg
    },
    toggled (event, name) {
      this.controller.forEach( (device) => {
        if (device.name === name) {
          device.watched = Boolean(event)
        }
      })
    },
    receiveControllerDeviceEvent (event) {
      const connectedDevices = JSON.parse(event.detail)
      let deviceIdList = []
      this.controller.forEach( (device) => { deviceIdList.push(device.guid) })

      // Update/Extend device list
      connectedDevices.forEach( (connectedDevice) => {
        if (deviceIdList.indexOf(connectedDevice.guid) !== -1) {
          this.controller.push({
            name: connectedDevice.name, guid: connectedDevice.guid, connected: true, watched: false
          })
        }
      })

      // Update device connected state
      this.controller.forEach( (device) => {
        connectedDevices.forEach( (connectedDevice) => {
          if (connectedDevice.name === device.name) { device.connected = true }
        })
      })
    },
  },
  created() {
    window.addEventListener('controller-device-event', this.receiveControllerDeviceEvent)
  },
  destroyed() {
    window.removeEventListener('controller-device-event', this.receiveControllerDeviceEvent)
  },
}
</script>

<style scoped>
.device-name { font-family: "Ubuntu", sans-serif; }
</style>