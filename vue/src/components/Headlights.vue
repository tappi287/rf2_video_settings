<template>
  <div id="headlights">
    <h5>Headlights</h5>
    <p>{{ message }}</p>
  </div>
</template>

<script>
// --- </ Prepare receiving controller events
let currentEvent = null
const controllerEvent = new Event('con-event')
window.eel.expose(controllerEventFunc, 'controller_event')
function controllerEventFunc (event) { currentEvent = event; window.dispatchEvent(controllerEvent) }
// --- />

export default {
name: "Headlights",
  data: function () {
    return {
      message: ''
    }
  },
  methods: {
    handleControllerEvent: function () {
      console.log('Controller Event:', currentEvent)
      this.message = String(currentEvent)
    },
  },
  created() {
    // Forward Controller events
    window.addEventListener('con-event', this.handleControllerEvent)
  },
  destroyed() {
    // Stop forwarding Controller events if this instance gets deleted
    console.log('Removing Controller Event listeners')
    window.removeEventListener('con-event', this.handleControllerEvent)
  },
}
</script>

<style scoped>

</style>