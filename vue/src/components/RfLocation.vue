<template>
  <b-card-text>
    If you have multiple rFactor 2 installation paths or trouble with outdated Steam files. You can enter the
    installation path manually here and restart the app.<br />
    This will disable auto detection of the rFactor installation.
    <b-form-group class="mt-2" :state="rfOverwriteLocationValid"
                  :valid-feedback="'rF2 install detected! ' + rfactorPath"
                  :invalid-feedback="'Could not detect valid rF2 install ' + rfOverwriteLocation">
      <b-input-group>
        <b-form-input v-model="rfOverwriteLocation" :state="rfOverwriteLocationValid"
                      :placeholder="rfactorLocationPlaceholder">
        </b-form-input>
        <b-input-group-append>
          <b-button variant="warning" @click="rfOverwriteLocation=''">Reset</b-button>
        </b-input-group-append>
      </b-input-group>
    </b-form-group>
  </b-card-text>
</template>

<script>
import {getEelJsonObject} from "@/main";

export default {
  name: 'RfLocation',
  data: function () {
    return {
      dragActive: false,
      error: '',
      rfactorVersion: '',
      rfactorPath: '',
      rfOverwriteLocation: null,
      rfOverwriteLocationValid: null,
    }
  },
  methods: {
    getRfVersion: async function () {
      let r = await getEelJsonObject(window.eel.get_rf_version()())
      if (r !== undefined) {
        let version = r.version
        this.rfactorPath = r.location

        version = version.replace('.', '')
        version = version.replace('\n', '')
        this.rfactorVersion = version
      }
    },
    getRfLocationValid: async function () {
      let r = await getEelJsonObject(window.eel.rf_is_valid()())
      if (r !== undefined) {
        this.rfOverwriteLocationValid = r
      }
    }
  },
  watch: {
    rfOverwriteLocation: async function (newValue) {
      let r = await getEelJsonObject(window.eel.overwrite_rf_location(newValue)())
      if (r !== undefined) {
        await this.getRfVersion()  // Update rF location
        await this.getRfLocationValid()  // Update rf install valid state
        this.rfOverwriteLocationValid = r
      }
    },
  },
  computed: {
    rfactorLocationPlaceholder: function () {
      if (this.rfactorPath !== '') {
        return 'Auto detected: ' + this.rfactorPath
      }
      return 'Path eg. D:\\Steam\\steamapps\\common\\rFactor 2\\'
    }
  },
  created() {
    this.getRfVersion()
  }
}
</script>

<style scoped>

</style>