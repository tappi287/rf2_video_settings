<template>
  <div v-cloak id="wiki" class="position-relative mb-5 text-left">
    <h4>Pin to taskbar</h4>
    <p>If you want to pin this app to your taskbar: type rf2 into your Windows start menu and right click the
      rf2 Settings Widget app entry > Pin to taskbar. If you try to pin the running app, you'll pin
      a shortcut to your web browser.</p>

    <h4 class="mt-4">Import</h4>
    <p>You can import preset JSON files by simply dragging them into the application window!</p>

    <h4 class="mt-4">Server Browser</h4>
    <p>The Server Browser uses Steam's API to query server information. The number of connected players and
    names of the connected players does most likely not reflect the actual number of players.
    The information should be similar to what you see when launching Steam>View>Server</p>

    <h4 class="mt-4">rF2 Notes</h4>
    <p>Start rF2 while a dedicated server is running on the same machine: Change the WebUI Port in player.json
    to something different than the default value. Use this app to start rF2 or create a shortcut to rF2.exe
    and set the StartIn parameter to the rFactor 2 root directory.</p>
    <p></p>
    <span>Start rF2 from command line and join a password protected server: </span>
    <pre class="text-muted">rFactor2.exe +multiplayer +connect=:Password@IP:Port</pre>
    <p></p>
    <span>Server XY won't let you join: Unable to install server mod. Take a look at your:</span>
    <pre class="text-muted mb-0">rFactor 2\UserData\cmpReport.txt</pre>
    <span>If you find messages like component XY missing: try to un- and resubscribe to that Item in the
    Steam Workshop.</span>
    <p></p>
    <span>Your ModMgr.exe is not starting. The registry key for the packages and rFactor directory
    is most likely out of date. Take a look at these Windows registry keys:</span>
    <pre class="text-muted">HKEY_CURRENT_USER\\SOFTWARE\\Image Space Incorporated\\rFactor2 Mod Manager\\--guid--\\Packages Dir</pre>

    <h4 class="mt-4">Credits</h4>
    <b-list-group>
      <b-list-group-item variant="dark">
        <b-link href="https://studio397.com">Studio 397 Dev Guide</b-link>
        <span> - general resource about rFactor 2 development</span>
      </b-list-group-item>
      <b-list-group-item variant="dark">
        <b-link href="https://github.com/ChrisKnott/Eel">Eel</b-link>
        <span> - A little Python library for making simple Electron-like HTML/JS GUI apps</span>
      </b-list-group-item>
      <b-list-group-item variant="dark">
        <b-link href="https://github.com/TonyWhitley/rF2_serverNotify">rF2_serverNotify</b-link>
        <span> - starting point to read rF2 Server information</span>
      </b-list-group-item>
      <b-list-group-item variant="dark">
        <b-link href="https://gitlab.com/grumbel/rfactortools">rfactortools</b-link>
        <span> - interesting source of information to handle various rF specific file types.</span>
      </b-list-group-item>
      <b-list-group-item variant="dark">
        <b-link href="https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/">
          Studio 397 Screenshot Thread</b-link>
        <span> - most of the dashboard shots are taken from there, every author is credited and no images
        are distributed with this app.</span>
      </b-list-group-item>
    </b-list-group>
  </div>
</template>

<script>

export default {
  name: "Wiki",
  data: function () {
    return {
      data: null
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
  },
  components: {
  },
}
</script>

<style scoped>

</style>

<style>

</style>