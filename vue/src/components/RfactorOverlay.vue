<template>
  <div>
    <b-overlay no-wrap fixed class="rf-bg-overlay" z-index="10" variant="transparent" blur="1px" :show="!showBackdrop">
      <template #overlay><div><!-- Hide default Spinner --></div></template>
    </b-overlay>
    <div id="rf-overlay" :class="this.showBackdrop ? '' : 'no-pointer'">
      <div id="rf-overlay-centered" :class="this.showBackdrop ? 'rf-overlay-centered-side' : 'rf-overlay-centered-center'">
        <div class="busy-div p-4 rounded" id="rf-overlay-content">
          <template v-if="!live">
            <div class="d-flex justify-content-center mb-3">
              <b-spinner label="Loading..."></b-spinner>
            </div>
          </template>
          <template v-else>
            <div class="d-flex justify-content-center mb-3">
              <b-button variant="secondary"
                        @click="setBusy(false);proceed()"
                        v-b-popover.top.hover="'If you started to watch a replay with this app: ' +
                         'Please wait a moment so the app can restore the original video settings. ' +
                         'Detecting rFactor not running can take up to a minute.'">
                Proceed
              </b-button>
              <b-button class="ml-2" variant="danger" id="quit-rfactor">Quit rFactor 2</b-button>

              <!-- Quit Popover -->
              <b-popover target="quit-rfactor" triggers="click">
                <template #title>Quit rFactor 2</template>
                <p>Do you really want to request the currently running instance of rFactor 2 to quit?</p>
                <div class="text-right">
                  <b-button variant="danger"
                            @click="quitRfactor(); $root.$emit('bv::hide::popover', 'quit-rfactor')">
                    <b-spinner v-if="quitBusy" class="mr-1"></b-spinner>Quit
                  </b-button>
                  <b-button class="ml-2" variant="secondary"
                            @click="$root.$emit('bv::hide::popover', 'quit-rfactor')">
                    Close
                  </b-button>
                </div>
              </b-popover>
            </div>
            <pre class="text-white" v-if="rf2Status !== ''"><span>{{ rf2Status }}</span></pre>
            <span>rFactor 2 is currently running. Please wait.</span>
          </template>
        </div>
      </div>
    </div>
    <div id="rf-spacer" v-if="this.showBackdrop"></div>
  </div>
</template>

<script>

export default {
  name: "RfactorOverlay",
  data: function () {
    return { showBackdrop: false }
  },
  props: { rf2Status: String, quitBusy: Boolean, live: Boolean },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000, noAutoHide = false) {
      this.$emit('make-toast', message, category, title, append, delay, noAutoHide)
    },
    setBusy (busy) { this.$emit('set-busy', busy) },
    proceed () { this.showBackdrop = !this.showBackdrop },
    quitRfactor () {this.$emit('quit-rfactor') }
  }
}
</script>

<style scoped>
.busy-div { background: rgba(0,0,0, 0.80); }
#rf-overlay {
  position: fixed;
  width: 100%; height: 100%; top: 0; left: 0; overflow: hidden;
  z-index: 500; pointer-events: none;
}
#rf-overlay-centered {
  display: flex;
  min-height: calc(100% - 1.5rem);
  width: auto; max-width: fit-content; pointer-events: none;
}
.rf-overlay-centered-side { align-items: self-end; margin: 0 0 0 calc(100% - 25.85rem); transition: all .2s;}
.rf-overlay-centered-center { align-items: center; margin: 1.75rem auto; transition: all .2s;}
#rf-overlay-content { pointer-events: all; width: 25rem; }
#rf-spacer { height: 9.5rem; }
.no-pointer{ pointer-events: none; }
</style>