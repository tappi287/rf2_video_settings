<template>
  <div class="setting">
    <b-input-group size="sm" class="setting-field">
      <b-input-group-prepend>
        <b-input-group-text class="info-field fixed-width-name" :id="nameId">
          {{ setting.name }}
          <b-icon v-if="settingDesc !== ''" icon="info-square" class="ml-2 mr-1"
                  v-b-popover.hover.topright="settingDesc">
          </b-icon>
        </b-input-group-text>
      </b-input-group-prepend>
      <b-input-group-append>
        <div :class="variant + ' setting-item fixed-width-setting'">
          <b-icon shift-v="-1" icon="controller" class="text-white" v-b-popover.hover.topright="setting.device_name"/>
          <span class="ml-2">{{ typeName }} {{ settingValueName }}</span>
          <b-link @click="startListening" class="text-white ml-2">
            <b-icon icon="pencil"></b-icon>
          </b-link>
        </div>
      </b-input-group-append>
    </b-input-group>

    <!-- Controller Assign Modal -->
    <b-modal v-model="listening" centered hide-header-close no-close-on-backdrop no-close-on-esc>
      <template #modal-title>
        <b-icon icon="controller" variant="primary"></b-icon>
        <span class="ml-2">{{ setting.name }}</span>
      </template>
      <div class="d-block">
        <p style="font-size: small;">Press a Controller or Steering Wheel Button or a Keyboard Key to assign</p>
        <div :class="eventCaptured ? '' : 'old-setting'">
          <h5>{{ capturedEventDeviceName }}</h5>
          <p>
            <span>{{ capturedTypeName }}</span>
            <span class="ml-2">{{ capturedValue }}</span>
          </p>
        </div>
      </div>

      <template #modal-footer>
        <div class="d-block text-right">
          <b-button v-if="eventCaptured" @click="confirmAssign" variant="success">Confirm</b-button>
          <b-button class="ml-2" v-if="eventCaptured" @click="startListening" variant="primary">Retry</b-button>
          <b-button class="ml-2" variant="secondary" @click="abortListeningController">Abort</b-button>
        </div>
      </template>
    </b-modal>
  </div>
</template>

<script>
import {getControllerValueName, getMaxWidth, getControllerDeviceTypeName, getEelJsonObject} from "@/main";

// --- </ Prepare receiving controller events
let currentEvent = null
const controllerEvent = new Event('con-event')

window.eel.expose(controllerEventFunc, 'controller_event')

async function controllerEventFunc (event) {
  currentEvent = await getEelJsonObject(event)
  window.dispatchEvent(controllerEvent)
}
// --- />

export default {
  name: "ControllerAssignment",
  data: function () {
    return {
      elemId: 'setting' + this._uid, // _uid is a unique identifier for each vue component
      nameId: 'name' + this._uid,
      settingDesc: '',
      listening: false,
      listeningToSetting: {},
      eventCaptured: false,
      capturedEvent: null,
    }
  },
  props: {
    setting: Object, variant: String, fixWidth: Boolean, groupId: String
  },
  methods: {
    handleControllerEvent: function () {
      if (this.listening && !this.eventCaptured) {
        // Copy/Capture current event
        const eventData = JSON.stringify(currentEvent)
        this.capturedEvent = JSON.parse(eventData)

        console.log('Captured Event:', this.capturedEvent)
        this.eventCaptured = true
      }
    },
    startListening: function () { this.eventCaptured = false; this.capturedEvent = null; this.listening = true },
    abortListeningController: function () { this.listening = false; this.eventCaptured = false },
    confirmAssign: function () {
      this.$emit('update-assignment', this.setting, this.capturedEvent)
      this.abortListeningController()
    },
    setFixedWidth: function () {
      // Iterate all elements of this setting group_id and set width to widest element found
      const nameElem = document.querySelectorAll('#' + this.groupId + ' .fixed-width-name')
      const settElem = document.querySelectorAll('#' + this.groupId + ' .fixed-width-setting')

      let nameMaxWidth = getMaxWidth(nameElem); let settMaxWidth = getMaxWidth(settElem)

      let e = document.getElementById(this.nameId)
      if (e !== null) { e.style.width = String(nameMaxWidth) + 'px' }
      let s = document.getElementById(this.elemId)
      if (s !== null) { s.style.width = String(settMaxWidth) + 'px' }
    },
  },
  created: function () {
    // Set description
    this.settingDesc = this.setting.desc || ''
    console.log('Con Setting', this.setting)

    // Forward Controller events
    window.addEventListener('con-event', this.handleControllerEvent)
  },
  destroyed() {
    // Stop forwarding Controller events if this instance gets deleted
    console.log('Removing Controller Event listeners')
    window.removeEventListener('con-event', this.handleControllerEvent)
  },
  mounted () {
    if (this.variant === undefined) { this.variant = 'secondary'}
    this.currentSettingValue = this.setting.value
    if (this.fixWidth) {
      // Access after rendering finished
      setTimeout(() => {
        this.setFixedWidth()
      }, 0)
    }
  },
  computed: {
    currentSettingName: function () {
      let name = 'Not Set!'
      if (this.setting === undefined) { return name }
      return name
    },
    typeName: function () {
      return getControllerDeviceTypeName(this.setting)
    },
    settingValueName: function () {
      return getControllerValueName(this.setting)
    },
    capturedEventDeviceName() {
      if (!this.eventCaptured) { return this.setting.device_name }
      return this.capturedEvent.name
    },
    capturedValue() {
      if (!this.eventCaptured) { return getControllerValueName(this.setting) }
      return getControllerValueName(this.capturedEvent)
    },
    capturedTypeName() {
      if (!this.eventCaptured) { return getControllerDeviceTypeName(this.setting) }
      return getControllerDeviceTypeName(this.capturedEvent)
    },
  }
}
</script>

<style scoped>
.setting-item {
  vertical-align: bottom;
  font-size: .875rem;
  padding: .25rem .5rem;
  border-radius: 0 0.25rem 0.25rem 0;
}
.old-setting {
  color: #c6c6c6;
}
</style>