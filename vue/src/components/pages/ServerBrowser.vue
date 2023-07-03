<template>
  <div id="server-browser" v-if="!onlyFav || browserReady">
    <!-- Filter -->
    <b-input-group size="sm" v-if="!isBusy && !onlyFav" class="table-bar">
      <b-input-group-prepend>
        <b-input-group-text class="rf-secondary border-0 low-round-left">
          <b-icon icon="filter" aria-hidden="true"></b-icon>
        </b-input-group-text>

        <b-button @click="$bvModal.show(addModalId)" variant="rf-secondary" size="sm" class="border-0">
          <b-icon class="mr-1 ml-1" icon="plus" aria-hidden="true"></b-icon>
        </b-button>
      </b-input-group-prepend>

      <b-form-input v-model="serverTextFilter" id="filter-server" type="search" debounce="1000"
                    placeholder="Search..." spellcheck="false"
                    :class="serverTextFilter !== '' ? 'filter-warn no-border' : 'no-border'">
      </b-form-input>

      <b-input-group-append>
        <b-button-group>
          <b-button @click="toggleFavs" :variant="filterFavs ? 'dark' : ''" size="sm">
            <b-icon :icon="filterFavs ? 'star-fill' : 'star'" :variant="filterFavs ? 'warning' : 'white'">
            </b-icon>
            <span class="ml-2">Favourites</span>
          </b-button>
          <b-button @click="toggleEmpty" :variant="filterEmpty ? 'dark' : ''" size="sm">
            <b-icon :icon="filterEmpty ? 'people-fill' : 'people'" :variant="filterEmpty ? 'warning' : 'white'">
            </b-icon>
            <span class="ml-2">Players</span>
          </b-button>
          <b-button @click="togglePwd" :variant="filterPwd ? 'dark' : ''" size="sm">
            <b-icon :icon="filterPwd ? 'key-fill' : 'key'" :variant="filterPwd ? 'warning' : 'white'">
            </b-icon>
            <span class="ml-2">Password</span>
          </b-button>
          <b-button @click="toggleVer" :variant="filterVer ? 'dark' : ''" size="sm">
            <b-icon :icon="filterVer ? 'plug-fill' : 'plug'" :variant="filterVer ? 'success' : 'white'">
            </b-icon>
            <span class="ml-2">Version</span>
          </b-button>
          <b-button @click="refreshServerList()" variant="rf-secondary" size="sm" class="border-0">
            <b-icon class="mr-1 ml-1" icon="arrow-clockwise" aria-hidden="true"></b-icon>
          </b-button>
          <b-button @click="resetFilter" variant="rf-secondary" size="sm" class="border-0 low-round-right">
            <b-icon class="mr-2 ml-1" icon="backspace-fill" aria-hidden="true"></b-icon>
            Reset
          </b-button>
        </b-button-group>
      </b-input-group-append>
    </b-input-group>

    <b-progress v-if="isBusy && !onlyFav" :max="maxLoadProgress" variant="dark" height="2.75em"
                class="mt-0 mb-0">
      <b-progress-bar :value="loadProgress">
        <span>Loading: <strong>{{ loadProgress }} / {{ maxLoadProgress }}</strong></span>
      </b-progress-bar>
    </b-progress>

    <!-- Server List -->
    <div v-if="onlyFav" class="text-center bg-dark text-muted  low-round-top table-blocks">
      <b-icon icon="star-fill"/>
      <span class="ml-2 title">Favourites</span>
      <b-link class="ml-2" @click="$bvModal.show(addModalId)">
        <b-icon icon="plus"></b-icon>
        Add custom server
      </b-link>
    </div>
    <b-table :items="computedServerList" :fields="serverFields" table-variant="dark" :busy="isBusy" show-empty
             primary-key="id" class="server-list"
             :thead-class="onlyFav ? 'hidden' : 'text-white'"
             small :striped="!onlyFav" borderless>
      <!-- Name -->
      <template v-slot:cell(server_name)="server">
        <b-link @click="toggleServerDetails(server)" class="text-light">
          <b-icon :icon="server.detailsShowing ? 'caret-down-fill': 'caret-right-fill'" variant="secondary">
          </b-icon>
          <span class="ml-1">{{ server.item.server_name }}</span>
        </b-link>
      </template>

      <!-- Pwd -->
      <template v-slot:cell(password_protected)="server">
        <template v-if="server.item.password_protected">
          <b-icon icon="key-fill" variant="danger"></b-icon>
        </template>
      </template>

      <!-- Players -->
      <template v-slot:cell(player_count)="server">
        <span :class="server.item.player_count > 0 ? '' : 'text-muted'">
          {{ server.item.player_count }} / {{ server.item.max_players }}
          <template v-if="server.item.bot_count > 0">[{{ server.item.bot_count }} AI]</template>
        </span>
      </template>

      <!-- Version -->
      <template v-slot:cell(version)="server">
        <span :class="compareVersion(server.item.version) ? 'text-success' : 'muted'">
          {{ server.item.version.slice(1, 5) }}
        </span>
      </template>

      <!-- Fav -->
      <template v-if="!onlyFav" v-slot:cell(actions)="server">
        <b-link @click="toggleServerFavourite(server.item)">
          <b-icon shift-v="1" variant="warning" :icon="isServerFav(server.item) ? 'star-fill' : 'star'"></b-icon>
        </b-link>
      </template>

      <!-- Details -->
      <template #row-details="server">
        <b-card :title="server.item.server_name" :sub-title="server.item.id"
                bg-variant="dark" text-variant="white" class="text-left m-1">

          <b-card-text>{{ server.item.map_name }}</b-card-text>

          <!-- Player Info -->
          <div class="d-flex flex-wrap mt-3">
            <template v-if="server.item.player_count > 0">
              <div class="d-inline-flex mr-2 mb-2 p-1 pr-2 bg-light text-dark rounded"
                   v-for="name in server.item.players" :key="name">
                <b-icon shift-v="-4" class="align-baseline" icon="person-fill"></b-icon>
                <span class="ml-1">{{ name }}</span>
              </div>
            </template>
            <template v-else>
              <div>
                <b-icon shift-v="-1" icon="emoji-dizzy"></b-icon>
                <span class="ml-2">Server is empty</span></div>
            </template>
          </div>

          <!-- Bot info -->
          <template v-if="server.item.bot_count > 0">
            <div class="d-flex flex-wrap mt-3">
              <div>
                <b-icon shift-v="-1" icon="emoji-neutral"></b-icon>
                <span class="ml-2">{{ server.item.bot_count }} Bots on this server</span>
              </div>
            </div>
          </template>

          <!-- Server info -->
          <div class="d-flex flex-wrap mt-3 text-muted">
            <div class="d-inline-flex mr-3 mb-2">
              <div>
                <div class="float-sm-left"><b>Platform</b></div>
                <div style="clear: both;"><i>{{ server.item.platform === 'w' ? 'Windows' : 'Linux' }}</i></div>
              </div>
            </div>
            <div class="d-inline-flex mr-3 mb-2">
              <div>
                <div class="float-sm-left"><b>Game Port</b></div>
                <div style="clear: both;"><i>{{ server.item.port }}</i></div>
              </div>
            </div>
            <div class="d-inline-flex mr-3 mb-2">
              <div>
                <div class="float-sm-left"><b>Password</b></div>
                <div style="clear: both;">
                  <b-icon :icon="server.item.password_protected ? 'key-fill' : 'x'"
                          :variant="server.item.password_protected ? 'danger' : 'secondary'"></b-icon>
                </div>
              </div>
            </div>
            <div class="d-inline-flex mr-3 mb-2">
              <div>
                <div class="float-sm-left"><b>Max Players</b></div>
                <div style="clear: both;"><i>{{ server.item.max_players }}</i></div>
              </div>
            </div>
            <div class="d-inline-flex mr-3 mb-2">
              <div>
                <div class="float-sm-left"><b>Steam ID</b></div>
                <div style="clear: both;"><i>{{ server.item.steam_id }}</i></div>
              </div>
            </div>
            <div class="d-inline-flex mr-3 mb-2">
              <div>
                <div class="float-sm-left"><b>Stored Password</b></div>
                <div style="clear: both;">
                  <b-icon variant="secondary"
                          :icon="server.item.password !== '' ? 'check-square-fill': 'x-square-fill'"/>
                  <template v-if="server.item.password">
                    <b-link @click="showPwdToggle = !showPwdToggle" class="ml-2">
                      <b-icon variant="warning" :icon="showPwdToggle ? 'eye-slash-fill' : 'eye-fill'"/>
                    </b-link>
                    <template v-if="showPwdToggle">
                      <span class="ml-2">{{ server.item.password }}</span>
                    </template>
                  </template>
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div style="position: absolute; top: 1.25rem; right: 1.25rem;">
            <b-button-group>
              <template v-if="serverCustoms.indexOf(server.item.id) !== -1">
                <b-button class="mr-2" variant="danger" size="sm"
                          @click="addCustomServer(false, server.item)">
                  Remove Custom Server
                </b-button>
              </template>
              <b-button @click="refreshServer(server.item)" class="mr-2" variant="rf-secondary" size="sm">
                <b-icon shift-v="-1" icon="arrow-clockwise"></b-icon>
                <span class="ml-1 mr-1">Refresh Server Data</span>
              </b-button>
              <template v-if="server.item.password_protected">
                <b-button @click="joinPswdProtectedRfactor(server.item)"
                          variant="rf-blue-light" size="sm">
                  <b-icon variant="light" icon="play"></b-icon>
                  <span class="ml-1 mr-1">Join Server</span>
                </b-button>
              </template>
              <template v-else>
                <LaunchRfactorBtn @make-toast="makeToast" btn-size="sm"
                                  @launch="joinServerLaunched" :server="server.item" text="Join Server"/>
              </template>
            </b-button-group>
          </div>
        </b-card>
      </template>

      <!-- No Server Data -->
      <template #empty>
        <div class="text-center">
          <template v-if="isBusy">
            <b-spinner></b-spinner>
            <p>Acquiring server data...</p>
          </template>
          <template v-if="onlyFav">
            <template v-if="serverFavs.length === 0">
              <p>No favourite servers added yet. Use the Server Browser to add some favourites to the app.</p>
            </template>
            <template v-else-if="serverFavs.length !== 0 && serverListData.length === 0">
              <p>No favourite servers online</p>
            </template>
            <template v-else>
              <p>The master server is unavailable or could not access internet connection.</p>
            </template>
          </template>
          <template v-if="!onlyFav">
            <template v-if="serverListData.length === 0">
              <h5>No server data</h5>
              <p>The master server is unavailable or could not access internet connection.</p>
            </template>
            <template v-else-if="serverListData.length > 0">
              <h6>No filtering results!</h6>
              <p>Try to reduce filtering options to see some Servers.</p>
            </template>
          </template>
        </div>
      </template>
    </b-table>
    <div class="bg-dark rounded-bottom low-round-bottom table-blocks mt-0"></div>

    <!-- Join password protected Server -->
    <b-modal :id="pwdModalId" centered>
      <template #modal-title>
        <b-icon icon="play-fill" variant="primary"></b-icon>
        <span class="ml-1">Join {{ selectedServer.server_name }}</span>
      </template>
      <div class="d-block" style="font-size: small">
        <p>This server is password protected.</p>
        <p>If you know the exact password you can enter it here and have this application
          remember it for you.</p>
        <p><b>Note:</b> rFactor 2 will idle in the main menu and not connect to the server if you
          provided an incorrect password.</p>
      </div>

      <b-input-group prepend="Password" class="mt-3">
        <b-form-input type="password" v-model="selectedServer.password"></b-form-input>
        <b-input-group-append>
          <LaunchRfactorBtn @make-toast="makeToast" @launch="joinPswdLaunched" text="Join Server"
                            btn-size="md"
                            :server="selectedServer"/>
        </b-input-group-append>
      </b-input-group>
      <b-form-checkbox v-model="storePwd">Remember</b-form-checkbox>

      <template #modal-footer="{ cancel }">
        <div class="d-block" style="font-size: small">
          <i>Passwords will be stored unencrypted. Do not check the Remember option if you would not
            like to store it.</i>
        </div>
        <div class="d-block text-right">
          <b-button variant="secondary" @click="cancel()">Cancel</b-button>
        </div>
      </template>
    </b-modal>

    <!-- Add Custom Server Modal -->
    <b-modal :id="addModalId" centered>
      <template #modal-title>
        <b-icon icon="play-fill" variant="primary"></b-icon>
        <span class="ml-1">Add Custom Server</span>
      </template>

      <div class="d-block">
        <p>Store a custom server that is not publicly listed.</p>
      </div>

      <b-form @submit.prevent="addCustomServer(true)">
        <b-form-group label="Name" label-cols="2">
          <b-form-input required placeholder="Custom Server Name" type="text" v-model="customServerName"></b-form-input>
        </b-form-group>
        <b-form-group label="Password" label-cols="2">
          <b-form-input placeholder="Enter Server password or leave empty" type="text"
                        v-model="customServerPwd"></b-form-input>
        </b-form-group>
        <b-form-group label="Address" label-cols="2">
          <b-form-input placeholder="xxx.xxx.xxx.xxx [IP address]" type="text" required
                        v-model="customServerIp"></b-form-input>
          <b-form-input placeholder="12345 [Port]" class="mt-3" type="text" v-model="customServerPort" required />
          <b-input-group-append class="mt-3">
            <b-button type="submit" variant="success" block>
              <!-- :disabled="!customServerDataValid()" -->
              Add custom server
            </b-button>
          </b-input-group-append>
        </b-form-group>
      </b-form>

      <template #modal-footer="{ cancel }">
        <div class="d-block text-right">
          <b-button variant="secondary" @click="cancel()">Cancel</b-button>
        </div>
      </template>
    </b-modal>
  </div>
</template>

<script>
/*
    # Server info attributes we're interested in
    attributes = ('map_name', 'max_players', 'mod_version', 'version', 'protocol', 'password_protected', 'ping',
                  'platform', 'bot_count', 'player_count', 'protocol', 'server_name', 'server_type', 'steam_id',
                  'ip', 'port', 'players')
 */
import {getEelJsonObject, sleep} from "@/main";
import LaunchRfactorBtn from "@/components/LaunchRfactorBtn";


export default {
  name: "ServerBrowser",
  components: {LaunchRfactorBtn},
  data: function () {
    return {
      isBusy: false,
      browserReady: false,
      loadProgress: 0,
      maxLoadProgress: 1,
      serverTextFilter: null,
      serverFavs: [],
      serverCustoms: [],
      serverListData: [],
      filterEmpty: false,
      filterPwd: false,
      filterFavs: false,
      filterVer: false,
      serverFields: [
        {key: 'server_name', label: 'Name', sortable: true, class: 'text-left'},
        {key: 'password_protected', label: 'Pwd', sortable: true},
        {key: 'map_name', label: 'Track', sortable: true, class: 'text-left'},
        {key: 'player_count', label: 'Players', sortable: true, class: 'text-right secondary-info'},
        {key: 'version', label: 'Version', sortable: true, class: 'text-right secondary-info'},
        {key: 'ping', label: 'Ping', sortable: true, class: 'text-right secondary-info'},
        {key: 'actions', label: '', class: 'text-right'},
      ],
      selectedServer: {},
      serverPassword: '',
      customServerName: '',
      customServerIp: '',
      customServerPort: '',
      customServerPwd: '',
      storePwd: true,
      showPwdToggle: false,
      pwdModalId: 'password-modal' + this._uid,
      addModalId: 'add-modal' + this._uid,
      onlyFav: false,
      isActive: false
    }
  },
  props: {onlyFavourites: Boolean, delay: Number, rfactorVersion: String},
  emits: ['launch', 'make-toast', 'server-browser-ready'],
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      console.log('Making toast', message, category, title, append, delay)
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) {
      this.isBusy = busy; /* this.$emit('set-busy', busy) */
    },
    compareVersion: function (serverVersion) {
      if (this.rfactorVersion !== '' && this.rfactorVersion !== undefined) {
        if (this.rfactorVersion === serverVersion) {
          return true
        }
      }
      return false
    },
    togglePwd() {
      this.filterPwd = !this.filterPwd;
    },
    toggleEmpty() {
      this.filterEmpty = !this.filterEmpty;
    },
    toggleFavs() {
      this.filterFavs = !this.filterFavs;
    },
    toggleVer() {
      this.filterVer = !this.filterVer;
    },
    toggleServerDetails: function (row) {
      row.toggleDetails();
      this.showPwdToggle = false
    },
    isServerFav: function (server_info) {
      return this.serverFavs.indexOf(server_info.id) !== -1
    },
    customServerDataValid() {
      return this.customServerIp !== "" && this.customServerPort !== "" && this.customServerName !== ""
    },
    addCustomServerToFavourites: async function (customServers) {
      // Update Server List
      for (let sid in customServers) {
        let alreadyInList = false

        if (this.serverFavs.indexOf(customServers[sid].id) === -1) {
          this.serverFavs.push(customServers[sid].id)
        }
        if (this.serverCustoms.indexOf(customServers[sid].id) === -1) {
          this.serverCustoms.push(customServers[sid].id)
        }
        for (let idx in this.serverListData) {
          const server = this.serverListData[idx]
          if (server.id === sid) {
            alreadyInList = true
            this.serverListData[idx] = customServers[sid]
          }
        }
        if (!alreadyInList) {
          this.serverListData.push(customServers[sid])
        }
      }
    },
    addCustomServer: async function (add = true, customServerInfo = null) {
      let serverInfo = {
        bot_count: 0, map_name: "", max_players: 0, ping: 0, platform: "w", player_count: 0, players: [],
        protocol: 17, server_type: "1", steam_id: 0, version: "",
        id: this.customServerIp + ':' + this.customServerPort,
        address: [this.customServerIp, this.customServerPort],
        port: this.customServerPort,
        server_name: this.customServerName,
        password_protected: this.customServerPwd !== '',
        password: this.customServerPwd
      }
      if (customServerInfo !== null) {
        serverInfo = customServerInfo
      }
      this.$bvModal.hide(this.addModalId)

      // Add Custom
      if (add) {
        const result = await getEelJsonObject(window.eel.custom_server(serverInfo, true)())
        if ((result !== undefined) && (result.data !== undefined)) {
          // Update Server List
          await this.addCustomServerToFavourites(result.data)

          this.makeToast('Added custom server ' + serverInfo.server_name,
              'success', 'Server Browser', false, 800)
        }
        this.$emit('fav-updated')
        return
      }

      // Remove Custom
      const result = await getEelJsonObject(window.eel.custom_server(serverInfo, false)())
      if ((result !== undefined) && (result.data !== undefined)) {
        this.refreshServerList()

        this.makeToast('Removed custom server ' + serverInfo.server_name,
            'primary', 'Server Browser', false, 800)
      }
      this.$emit('fav-updated')
    },
    toggleServerFavourite: async function (server) {
      this.$emit('fav-updated')

      // Add Favourite
      if (!this.isServerFav(server)) {
        const result = await getEelJsonObject(window.eel.server_favourite(server, true)())
        if ((result !== undefined) && (result.data !== undefined)) {
          this.serverFavs = []
          this.serverFavs = result.data
          this.makeToast('Added server ' + server.server_name + ' to favourites.',
              'success', 'Server Browser', false, 800)
        }
        return
      }

      // Remove Favourite
      const result = await getEelJsonObject(window.eel.server_favourite(server, false)())
      if ((result !== undefined) && (result.data !== undefined)) {
        this.serverFavs = []
        this.serverFavs = result.data
        this.makeToast('Removed server ' + server.server_name + ' from favourites.',
            'success', 'Server Browser', false, 800)
      }
    },
    resetFilter() {
      this.serverTextFilter = ''
      this.filterEmpty = false;
      this.filterPwd = false;
      this.filterFavs = false;
      this.filterVer = false
    },
    filteredList: function () {
      if ((this.serverTextFilter === null || this.serverTextFilter === '') &&
          (!this.filterPwd && !this.filterEmpty && !this.filterFavs && !this.filterVer)) {
        return this.serverListData
      }

      if (!this.onlyFav) {
        this.saveSettings()
      }

      let filterText = ''
      let filteredList = []
      if (this.serverTextFilter !== null) {
        filterText = this.serverTextFilter.toLowerCase()
      }

      this.serverListData.forEach(row => {
        // Button Filter
        if (this.filterEmpty && row.player_count === 0) {
          return
        }
        if (this.filterPwd && row.password_protected) {
          return
        }
        if (this.filterVer && !this.compareVersion(row.version)) {
          return
        }
        if (this.filterFavs && !this.isServerFav(row)) {
          return
        }

        // Text Filter
        if (filterText === '') {
          filteredList.push(row);
          return
        }
        if ((row.server_name.toLowerCase().includes(filterText) || row.map_name.toLowerCase().includes(filterText) ||
            row.version.includes(filterText))) {
          filteredList.push(row)
        }
      })

      return filteredList
    },
    refreshServerList: async function () {
      this.setBusy(true)
      this.isBusy = true
      this.serverListData = []

      try {
        console.log('Calling get server list. Favs:', this.onlyFav)
        const r = await getEelJsonObject(window.eel.get_server_list(this.onlyFav)())
        if (r === undefined || r === null) {
          this.makeToast('Error acquiring server list.', 'danger', 'Server Browser')
        }
      } catch (error) {
        console.error(error)
      }

      // Custom server
      try {
        const r = await getEelJsonObject(window.eel.get_custom_server()())
        await this.addCustomServerToFavourites(r)
        if (r === undefined || r === null) {
          this.makeToast('Error acquiring custom server.', 'danger', 'Server Browser')
        }
      } catch (error) {
        console.error(error)
      }

      this.setBusy(false)
    },
    refreshServer: async function (server) {
      let update_data = null
      try {
        update_data = await getEelJsonObject(window.eel.refresh_server(server.address)())
      } catch (error) {
        console.error(error)
      }

      if (update_data === undefined || update_data === null || update_data.result === false) {
        this.makeToast('Error acquiring server info.' + update_data.msg,
            'danger', 'Server Browser')
        return
      }

      this.serverListData[this.serverListData.indexOf(update_data.result)] = update_data.result
    },
    updateProgress(event) {
      this.loadProgress = event.detail.progress
      this.maxLoadProgress = event.detail.maxProgress
    },
    updateServerListData(event) {
      if (!this.isActive) {
        return
      }
      const newServerListChunk = event.detail
      console.log('Adding server list chunk', newServerListChunk.length)
      newServerListChunk.forEach(entry => {
        this.serverListData.push(entry)
      })
    },
    loadSettings: async function () {
      try {
        const server_fav_data = await getEelJsonObject(window.eel.get_server_favourites()())
        const settings = await getEelJsonObject(window.eel.get_server_browser_settings()())

        if (server_fav_data !== undefined) {
          this.serverFavs = server_fav_data
        }

        if ((settings !== undefined) && (!this.onlyFav)) {
          // Full Server Browser with filtering
          this.filterFavs = settings.filter_fav || false
          this.filterEmpty = settings.filter_empty || false
          this.filterPwd = settings.filter_pwd || false
          this.filterVer = settings.filter_version || false
          this.serverTextFilter = settings.filter_text || ''
          this.storePwd = settings.store_pwd || false
        } else {
          // Only Favourites fixed setting for Dashboard
          this.filterFavs = true
          this.storePwd = settings.store_pwd || false
        }
      } catch (error) {
        console.error(error)
      }
    },
    saveSettings: async function () {
      let settings = {
        filter_fav: this.filterFavs, filter_empty: this.filterEmpty, filter_pwd: this.filterPwd,
        filter_version: this.filterVer, store_pwd: this.storePwd
      }
      if (this.serverTextFilter !== null) {
        settings.filter_text = this.serverTextFilter
      }
      let r = await getEelJsonObject(window.eel.save_server_browser_settings(settings)())
      if (r !== undefined && !r.result) {
        this.makeToast('Error saving Server Browser settings', 'warning')
      }
    },
    joinServerLaunched: function () {
      this.$emit('launch')
    },
    joinPswdProtectedRfactor: function (server) {
      this.selectedServer = server
      this.selectedServer.password_remember = this.storePwd
      this.$bvModal.show(this.pwdModalId)
    },
    joinPswdLaunched: function () {
      this.$emit('launch')
      this.$bvModal.hide(this.pwdModalId)
    },
    asyncCreate: async function () {
      console.log('AsyncCreate called. Favs', this.onlyFavourites)
      this.setBusy(true)
      if (this.delay !== undefined) {
        await sleep(this.delay)
      }
      await this.loadSettings()
      await this.refreshServerList()
      this.$emit('server-browser-ready')
      this.browserReady = true
      this.setBusy(false)
    }
  }
  ,
  mounted() {
    window.addEventListener('update-progress', this.updateProgress)
    window.addEventListener('add-server-list-chunk', this.updateServerListData)
    this.asyncCreate()
  }
  ,
  activated() {
    this.isActive = true
  }
  ,
  deactivated() {
    this.isActive = false
  }
  ,
  created() {
    this.onlyFav = this.onlyFavourites
  }
  ,
  destroyed() {
    if (!this.onlyFav) {
      this.saveSettings()
    }
    console.log('Removing Event listeners')
    window.removeEventListener('update-progress', this.updateProgress)
    window.removeEventListener('add-server-list-chunk', this.updateServerListData)
  }
  ,
  watch: {
    storePwd: function (value) {
      console.log('Remb Pswd:', value)
      this.selectedServer.password_remember = value
    }
    ,
  }
  ,
  computed: {
    computedServerList() {
      if (this.serverListData !== undefined && this.serverListData !== null) {
        return this.filteredList()
      } else {
        return []
      }
    }
  }
}
</script>

<style scoped>

</style>