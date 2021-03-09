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
        <div :class="settingVariant + ' setting-item fixed-width-setting'">
          <b-icon shift-v="-1" icon="controller" class="text-white" v-b-popover.hover.topright="settingDeviceName"/>
          <span class="ml-2">{{ typeName }} {{ settingValueName }}</span>
          <b-link @click="startListening" class="text-white ml-2">
            <b-icon icon="pencil"></b-icon>
          </b-link>
        </div>
      </b-input-group-append>
    </b-input-group>

    <!-- Controller Assign Modal -->
    <b-modal v-model="listening" centered hide-header-close no-close-on-backdrop no-close-on-esc :id="modalId">
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
import {
  getControllerValueName,
  getMaxWidth,
  getControllerDeviceTypeName,
  getEelJsonObject,
  getRfactorControllerDeviceTypeName
} from "@/main";

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
      eventCaptured: false,
      capturedEvent: null,
      rfValueName: '',
      modalId: 'assign' + this._uid,
    }
  },
  props: {
    setting: Object, variant: String, fixWidth: Boolean, groupId: String, rfJson: Boolean
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    handleControllerEvent: function () {
      if (this.listening && !this.eventCaptured) {
        // Copy/Capture current event
        const eventData = JSON.stringify(currentEvent)
        this.capturedEvent = JSON.parse(eventData)
        this.eventCaptured = true
      }
    },
    handleKeyDownEvent: async function (event) {
      if (this.listening && !this.eventCaptured) {
        this.eventCaptured = true
        this.capturedEvent = {name: 'Keyboard', value: event.keyCode, key: event.key, type: 768}
        if (this.rfJson) {
          const rf_keycode = await getEelJsonObject(
              window.eel.get_rfactor_keycode_from_js_keycode(event.keyCode)()
          )
          this.capturedEvent.value = [0, rf_keycode]
        }
      }
    },
    listenToKeyboard: function (remove = false) {
      // We do not want to capture keyboard events for non-rfactor settings
      if (!this.rfJson) { return }

      // Add or Remove Keydown event listener
      const m = document.getElementById(this.modalId)
      if (m !== null && !remove) {
        console.log('Listening for keyboard events')
        m.addEventListener('keydown', this.handleKeyDownEvent)
      } else if (m !== null && remove) {
        console.log('Removing Keyboard listener')
        m.removeEventListener('keydown', this.handleKeyDownEvent)
      }
    },
    startListening: function () {
      this.eventCaptured = false; this.capturedEvent = null; this.listening = true
      this.$nextTick(() => { this.listenToKeyboard(false) })
    },
    abortListeningController: function () {
      this.listenToKeyboard(true); this.listening = false; this.eventCaptured = false
    },
    confirmAssign: async function () {
      if (this.rfJson) {
        if (!Array.isArray(this.capturedEvent.value)) {
          // Abort non-keyboard settings for rF for now
          this.abortListeningController()
          this.makeToast('Re-mapping rFactor controls to non-keyboard keys is currently not supported!',
              'danger', 'rFactor 2 Control Mapping')
          return
        }
      }
      this.$emit('update-assignment', this.setting, this.capturedEvent)
      this.abortListeningController()
      if (this.rfJson) { await this.getRfactorKeyName() }
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
    getRfactorKeyName: async function() {
      if (!Array.isArray(this.setting.value)) { return }
      this.rfValueName = await getEelJsonObject(window.eel.get_rfactor_key_name(this.setting.value[1])())
    }
  },
  created: function () {
    // Set description
    this.settingDesc = this.setting.desc || ''
    // Forward Controller events
    window.addEventListener('con-event', this.handleControllerEvent)
  },
  destroyed() {
    // Stop forwarding Controller events if this instance gets deleted
    console.log('Removing Controller Event listeners')
    window.removeEventListener('con-event', this.handleControllerEvent)
  },
  mounted () {
    if (this.rfJson) { this.getRfactorKeyName() }

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
    settingVariant: function () {
      if (this.variant === undefined) { return 'secondary' }
      return this.variant
    },
    typeName: function () {
      if (this.rfJson) { return getRfactorControllerDeviceTypeName(this.setting) }
      return getControllerDeviceTypeName(this.setting)
    },
    settingValueName: function () {
      if (this.rfJson) { return this.rfValueName }
      return getControllerValueName(this.setting)
    },
    settingDeviceName: function () {
      if (this.rfJson) {
        if (this.setting.value[0] === 0) { return 'Keyboard'}
        if (this.setting.value[0] > 0) { return 'rF Direct Input Device #' + this.setting.value[0]}
      }
      return this.setting.device_name
    },
    capturedEventDeviceName() {
      if (!this.eventCaptured) { return this.settingDeviceName }
      return this.capturedEvent.name
    },
    capturedValue() {
      if (!this.eventCaptured) { return this.settingValueName }
      return getControllerValueName(this.capturedEvent)
    },
    capturedTypeName() {
      if (!this.eventCaptured) { return this.typeName }
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