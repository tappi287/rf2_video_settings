<template>
  <div id="main" v-cloak>
    <div class="text-left mt-3 mb-3">
      <b-button-group class="w-100">
        <b-button variant="dark">
          <b-img src="@/assets/app_icon.webp" width="24" alt="rFactor 2 logo"></b-img>
        </b-button>
        <b-button variant="dark" @click="navActive=1">Graphics</b-button>
        <b-button disabled variant="dark" @click="navActive=2">Controls</b-button>
        <b-button disabled variant="dark" @click="navActive=3">Advanced Settings</b-button>
        <b-button variant="dark" @click="navActive=4">Server Browser</b-button>
      </b-button-group>
    </div>

    <!-- Graphic Settings-->
    <Graphics v-if="navActive === 1" @make-toast="makeToast"></Graphics>

    <!-- Server Browser -->
    <ServerBrowser ref="serverBrowser" v-if="navActive === 4" @make-toast="makeToast"></ServerBrowser>

    <!-- Launch rFactor -->
    <div class="mt-2">
      <b-button size="sm" variant="primary" @click="launchRfactor">
        <b-icon icon="play"></b-icon>Start rFactor 2
      </b-button>
    </div>
  </div>
</template>

<script>
import {getEelJsonObject} from '@/main'
import Graphics from "@/components/Graphics";
import ServerBrowser from "@/components/ServerBrowser";

export default {
  name: 'Main',
  data: function () {
    return {
      navActive: 1,
    }
  },
  methods: {
    updateProgress(progress) { console.log('Server Update Progress:', progress) },
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$bvToast.toast(message, {
        title: title,
        autoHideDelay: delay,
        appendToast: append,
        variant: category,
        solid: true,
        isBusy: false
      })
    },
    launchRfactor: async function () {
      let r = await getEelJsonObject(window.eel.run_rfactor()())
      if (r !== undefined && r.result) {
        this.makeToast('rFactor2.exe launched. This will take some time.', 'success')
      } else {
        this.makeToast('Could not launch rFactor2.exe', 'danger')
      }
    },
  },
  components: {
    ServerBrowser,
    Graphics
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#main {
  width: 92%;
  margin: 0 auto 0 auto;
}
</style>
