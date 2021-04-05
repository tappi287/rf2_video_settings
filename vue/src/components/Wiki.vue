<template>
  <div v-cloak id="wiki" class="position-relative mb-5 text-left">
    <div class="spacer rounded text-center">
      <h4 class="text-dark">About</h4>
    </div>

    <p class="mt-2">
      <a href="https://www.github.com/tappi287/rf2_video_settings" target="_blank">rf2 Settings Widget v{{ ver }}</a>
      published under MIT license &#169; 2020-2021
      <a href="https://sim-site.netlify.app" target="_blank">Stefan Tapper</a>
    </p>

    <div class="mt-5 spacer rounded text-center">
      <h4 class="text-dark">Wiki</h4>
    </div>

    <h4 class="mt-1">Pin to taskbar</h4>
    <p>If you want to pin this app to your taskbar: type rf2 into your Windows start menu and right click the
      rf2 Settings Widget app entry > Pin to taskbar. If you try to pin the running app, you'll pin
      a shortcut to your web browser.</p>

    <h4 class="mt-5">Report a bug</h4>
    <p>Want to report a bug, request a feature or have a setting you're missing? Head over to GitHub and
      <b-link target="_blank" href="https://github.com/tappi287/rf2_video_settings/issues">create an issue</b-link>.
    </p>

    <h4 class="mt-5">Import</h4>
    <p>You can import preset JSON files, exported from this app, by simply dragging them into the application window!
    This also works for rFactors player.JSON files. Simply drop it on the application and it will import all the
    settings available in this widget(and only those!).</p>
    <i>This is handy if you import someone else's player.JSON and want to make sure you are not overwriting all your
    other settings like your Player Name and Nickname.</i>

    <h4 class="mt-5">Server Browser</h4>
    <p>The Server Browser uses Steam's API to query server information. The number of connected players and
    names of the connected players does most likely not reflect the actual number of players.
    The information should be similar to what you see when launching Steam>View>Server</p>

    <h4 class="mt-5">rF2 Notes</h4>
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

    <h4 class="mt-5">Credits</h4>
    <b-list-group>
      <b-list-group-item variant="dark">
        <b-link target="_blank" href="https://studio397.com">Studio 397 Dev Guide</b-link>
        <span> - general resource about rFactor 2 development</span>
      </b-list-group-item>
      <b-list-group-item variant="dark">
        <b-link target="_blank" href="https://github.com/ChrisKnott/Eel">Eel</b-link>
        <span> - A little Python library for making simple Electron-like HTML/JS GUI apps</span>
      </b-list-group-item>
      <b-list-group-item variant="dark">
        <b-link target="_blank" href="https://github.com/TonyWhitley/rF2_serverNotify">rF2_serverNotify</b-link>
        <span> - starting point to read rF2 Server information</span>
      </b-list-group-item>
      <b-list-group-item variant="dark">
        <b-link target="_blank" href="https://gitlab.com/grumbel/rfactortools">rfactortools</b-link>
        <span> - interesting source of information to handle various rF specific file types.</span>
      </b-list-group-item>
      <b-list-group-item variant="dark">
        <b-link target="_blank" href="https://forum.studio-397.com/index.php?threads/community-screenshots-thread-unedited-screens-only.40609/">
          Studio 397 Screenshot Thread</b-link>
        <span> - most of the dashboard shots are taken from there, every author is credited and no images
        are distributed with this app.</span>
      </b-list-group-item>
      <b-list-group-item variant="dark">
        <b-link target="_blank" href="https://github.com/andybluenoes">
          andybluenoes</b-link>
        <span> - providing feedback and settings research</span>
      </b-list-group-item>
      <b-list-group-item variant="dark">
        <b-link target="_blank" href="https://github.com/fholger/reshade">
          ReShade - Copyright 2014 Patrick Mours. All rights reserved.
        </b-link>
      </b-list-group-item>
    </b-list-group>
    <h4 class="mt-5">ReShade - Copyright 2014 Patrick Mours. All rights reserved.</h4>
    <pre class="text-muted">
      THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
      EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
      OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
      SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
      INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
      TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
      BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
      CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
      ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
      SUCH DAMAGE.
    </pre>
    <p></p>
    <b-button class="mt-4" variant="primary" @click="$emit('nav', 8)">Show App Logs</b-button>
    <b-button class="ml-2 mt-4" variant="danger" @click="testException">Produce Test App Exception</b-button>
    <p></p>
    <b-button-group size="sm">
      <b-button @click="$eventHub.$emit('play-audio', 'audioConfirm')">audioConfirm</b-button>
      <b-button @click="$eventHub.$emit('play-audio', 'audioPing')">audioPing</b-button>
      <b-button @click="$eventHub.$emit('play-audio', 'audioIndicator')">audioIndicator</b-button>
      <b-button @click="$eventHub.$emit('play-audio', 'audioSelect')">audioSelect</b-button>
    </b-button-group>
  </div>
</template>

<script>

import {version} from "../../package.json";

export default {
  name: "Wiki",
  data: function () {
    return {
      ver: version,
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    testException: async function () { await window.eel.test_app_exception() },
  },
  components: {
  },
}
</script>

<style scoped>
h1, h2, h3, h4, h5 { font-family: Inter, "Segoe UI", system-ui, sans-serif; }
.spacer { width: 100%; height: 1.75rem; background: #efefef; }
</style>

<style>

</style>