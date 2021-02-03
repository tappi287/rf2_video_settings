<template>
  <div id="dashboard" v-cloak>
    <h5>Hello {{ userName }}</h5>

    <!-- Shortcuts Play with Preset -->

    <!-- Server Favourites -->
    <ServerBrowser ref="serverBrowser" only-favourites
                   @make-toast="makeToast" @error="setError"></ServerBrowser>
    <!-- -->
  </div>
</template>

<script>
import ServerBrowser from "@/components/ServerBrowser";

export default {
  name: "Dashboard",
  data: function () {
    return {
      userName: 'Driver',
    }
  },
  components: {
    ServerBrowser,
  },
}
</script>

<style scoped>

</style>