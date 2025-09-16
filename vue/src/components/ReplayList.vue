<template>
  <div>
    <!-- Filter -->
    <b-input-group size="sm" class="mt-2 table-bar">
      <b-input-group-prepend>
        <b-input-group-text class="rf-secondary border-0 low-round-left">
          <b-icon icon="filter" aria-hidden="true"></b-icon>
        </b-input-group-text>
      </b-input-group-prepend>

      <b-form-input v-model="replayTextFilter" type="search" debounce="1000"
                    placeholder="Search..." spellcheck="false"
                    :class="replayTextFilter !== '' && replayTextFilter !== null ? 'filter-warn no-border' : 'no-border'">
      </b-form-input>

      <b-input-group-append>
        <b-button-group>
          <b-button @click="filterP = !filterP" :variant="!filterP ? 'dark' : ''"
                    v-b-popover.auto.hover="'Filter Practice Sessions'" size="sm">
            <b-icon icon="filter" :variant="filterP ? 'rf-secondary' : 'secondary'"/>
            <span class="ml-2">P</span>
          </b-button>
          <b-button @click="filterW = !filterW" :variant="!filterW ? 'dark' : ''"
                    v-b-popover.auto.hover="'Filter Warm Up Sessions'" size="sm">
            <b-icon icon="filter" :variant="filterW ? 'rf-secondary' : 'info'"/>
            <span class="ml-2">W</span>
          </b-button>
          <b-button @click="filterQ = !filterQ" :variant="!filterQ ? 'dark' : ''"
                    v-b-popover.auto.hover="'Filter Qualifying Sessions'" size="sm">
            <b-icon icon="filter" :variant="filterQ ? 'rf-secondary' : 'primary'"/>
            <span class="ml-2">Q</span>
          </b-button>
          <b-button @click="filterH = !filterH" :variant="!filterH ? 'dark' : ''"
                    v-b-popover.auto.hover="'Filter Hot Laps'" size="sm">
            <b-icon icon="filter" :variant="filterH ? 'rf-secondary' : 'danger'"/>
            <span class="ml-2">H</span>
          </b-button>
          <b-button @click="filterR = !filterR" :variant="!filterR ? 'dark' : ''"
                    v-b-popover.auto.hover="'Filter Race Sessions'" size="sm">
            <b-icon icon="filter" :variant="filterR ? 'rf-secondary' : 'success'"/>
            <span class="ml-2">R</span>
          </b-button>
          <b-button variant="danger" :id="'delete-replays-btn' + _uid" v-if="editing"
                    v-b-popover.auto.hover="'Delete selected Replay files.'" size="sm">
            <b-icon class="mr-2 ml-1" icon="trash-fill" aria-hidden="true"></b-icon>
          </b-button>
          <b-button @click="resetFilter" variant="rf-secondary" size="sm">
              <b-icon class="mr-2 ml-1" icon="backspace-fill" aria-hidden="true"></b-icon>Reset
          </b-button>
        </b-button-group>

        <!-- Delete Popover -->
        <b-popover :target="'delete-replays-btn' + _uid" triggers="click">
          <p>Do you really want to delete the {{ currentSelection.length }} selected Replays from your hard drive?</p>
          <div class="text-right">
            <b-button @click="deleteReplays" size="sm" variant="danger"
                      aria-label="Delete" class="mr-2" v-b-popover.bottom.hover="'Delete selected Replay files.'">
              Delete
            </b-button>
            <b-button @click="$root.$emit('bv::hide::popover', 'delete-replays-btn' + _uid)"
                      size="sm" aria-label="Close">
              Close
            </b-button>
          </div>
        </b-popover>
      </b-input-group-append>
    </b-input-group>

    <b-table :items="computedReplayList" :fields="replayFields" table-variant="dark" small borderless
             primary-key="id" class="server-list" thead-class="text-white"
             ref="replayTable"
             selectable selected-variant="primary"
             :select-mode="editing ? 'range' : 'single'"
             @row-selected="selectRows">
      <!-- Name -->
      <template v-slot:cell(name)="replay">
        <!-- Name Link -->
        <template v-if="editing">
          <b-link  :class="'replay-link text-' + replayTypeText(replay.item).var"
                   :id="'replay-action-btn-' + replay.item.id + _uid"
                   @click="setActionReplay(replay.item)">
            <b-icon shift-v="-0.5" icon="play-circle-fill"></b-icon>
            <span :class="replay.rowSelected ? 'ml-2' : 'ml-2 text-white'">{{ replay.item.name }}</span>
          </b-link>

          <!-- Play/Rename Popover -->
          <b-popover :target="'replay-action-btn-' + replay.item.id + _uid" triggers="click">
            <template #title>
              {{ replay.item.name }}
            </template>
            <div>
              <p>Rename or watch this replay.</p>
              <b-form-input title="Rename" size="sm" class="mb-2" v-model="newReplayName" @submit.prevent></b-form-input>
            </div>
            <div class="text-right">
              <b-button @click="playReplay(replay.item); $root.$emit('bv::hide::popover', 'replay-action-btn-' + replay.item.id + _uid)"
                        size="sm" variant="rf-blue-light"
                        v-if="watchEnabled"
                        aria-label="Watch" class="mr-1">
                Watch
              </b-button>
              <b-button @click="replay.toggleDetails(); $root.$emit('bv::hide::popover', 'replay-action-btn-' + replay.item.id + _uid)"
                        size="sm" variant="rf-blue-light" aria-label="Show Results" class="mr-1">
                Results
              </b-button>
              <b-button @click="renameReplay(replay.item); $root.$emit('bv::hide::popover', 'replay-action-btn-' + replay.item.id + _uid)"
                        size="sm" variant="rf-orange-light"
                        aria-label="Rename" class="mr-1">
                Rename
              </b-button>
              <b-button @click="$root.$emit('bv::hide::popover', 'replay-action-btn-' + replay.item.id + _uid)"
                        size="sm" aria-label="Close" variant="rf-secondary">
                Close
              </b-button>
            </div>
          </b-popover>
        </template>
        <template v-else>
          <b-icon shift-v="-0.5" icon="play-circle-fill" class="mr-2"></b-icon>
          <span :class="'replay-link text-' + replayTypeText(replay.item).var">{{ replay.item.name }}</span>
        </template>
      </template>
      <!-- Replay Type -->
      <template v-slot:cell(type)="replay">
        <span :class="'text-' + replayTypeText(replay.item).var">{{ replayTypeText(replay.item).text }}</span>
      </template>

      <!-- Results -->
      <template #row-details="replay">
        <!-- Results -->
        <ResultDisplay
            :result-file="replay.item.result_file"
            @make-toast="makeToast"
            @set-busy="setBusy"
        >
          <template #top>
            <b-button @click="replay.toggleDetails();"
                      size="sm" variant="rf-blue"
                      aria-label="Close Results" class="mr-2">Close Result Viewer</b-button>
          </template>
        </ResultDisplay>
      </template>
    </b-table>
  </div>
</template>

<script>
import {getEelJsonObject} from "@/main";
import ResultDisplay from "@/components/ResultDisplay.vue";

export default {
  name: "ReplayList",
  components: {ResultDisplay},
  data: function () {
    return {
      replays: [],
      replayFields: [
        { key: 'type', label: 'T', sortable: true, class: 'text-left' },
        { key: 'name', label: 'Name', sortable: true, class: 'text-left' },
        { key: 'size', label: 'Size', sortable: true, class: 'text-right secondary-info' },
        { key: 'date', label: 'Last modified', sortable: true, class: 'text-right secondary-info' },
      ],
      newReplayName: '',
      currentSelection: [],
      replayTextFilter: null,
      filterQ: false, filterR: false, filterP: false, filterH: false, filterW: false,
      isBusy: false,
    }
  },
  props: { watchEnabled: Boolean, editing: Boolean },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) { this.isBusy = busy; this.$emit('set-busy', busy) },
    getReplays: async function() {
      this.setBusy(true)
      const r = await getEelJsonObject(window.eel.get_replays()())
      if (r.result) { this.replays = r.replays }
      if (!r.result) { this.makeToast(r.msg, 'danger', 'Get Replays Error') }
      this.setBusy(false)
    },
    setActionReplay(replay) { this.newReplayName = replay.name },
    renameReplay: async function(replay) {
      this.setBusy(true)
      const r = await getEelJsonObject(window.eel.rename_replay(replay, this.newReplayName)())
      if (r.result) {
        this.makeToast(r.msg, 'success', 'Replay renamed to: ' + this.newReplayName)
        await this.getReplays()
      }
      if (!r.result) { this.makeToast(r.msg, 'danger', 'Replay Rename Error') }
      this.setBusy(false)
    },
    playReplay: async function (replay) {
      const r = await getEelJsonObject(window.eel.play_replay(replay.name)())
      if (r.result) {
        this.makeToast(r.msg, 'success', 'Playing replay')
        this.setBusy(true)
        this.$eventHub.$emit('play-audio', 'audioConfirm')
      }
      if (!r.result) { this.makeToast(r.msg, 'danger', 'Replay Play Error') }
    },
    replayTypeText(replay) {
      if (replay.type === 1) {
        return {text: 'Q', var: 'primary'}
      } else if (replay.type === 2) {
        return {text: 'P', var: 'secondary'}
      } else if (replay.type === 3) {
        return {text: 'R', var: 'success'}
      } else if (replay.type === 4) {
        return {text: 'H', var: 'danger'}
      } else if (replay.type === 5) {
        return {text: 'W', var: 'info'}
      }
      return {text: '', var: ''}
    },
    resetFilter() {
      this.replayTextFilter = ''
      this.filterQ = false; this.filterP = false; this.filterR = false; this.filterH = false; this.filterW = false
    },
    filteredList: function() {
      if ((this.replayTextFilter === null || this.replayTextFilter === '') &&
          (!this.filterQ && !this.filterP && !this.filterR && !this.filterH && !this.filterW)) {
        return this.replays
      }

      let filterText = ''
      let filteredList = []
      if (this.replayTextFilter !== null) { filterText = this.replayTextFilter.toLowerCase() }

      this.replays.forEach(row => {
        // Button Filter
        if (this.filterQ && row.type === 1) { return }
        if (this.filterP && row.type === 2) { return }
        if (this.filterR && row.type === 3) { return }
        if (this.filterH && row.type === 4) { return }
        if (this.filterW && row.type === 5) { return }

        // Text Filter
        if (filterText === '') { filteredList.push(row); return }
        if (row.name.toLowerCase().includes(filterText)) { filteredList.push(row) }
      })

      return filteredList
    },
    selectRows: function (selection) {
      this.currentSelection = selection
      this.$emit('row-selected', selection)
      console.log('Selection:', selection)
    },
    deleteReplays: async function() {
      if (this.currentSelection.length <= 0) { return }
      this.setBusy(true)
      this.$root.$emit('bv::hide::popover', 'delete-replays-btn' + this._uid)
      const r = await getEelJsonObject(window.eel.delete_replays(this.currentSelection)())
      if (r.result) {
        this.makeToast(r.msg, 'success', 'Selected Replays deleted.')
        await this.getReplays()
      }
      if (!r.result) { this.makeToast(r.msg, 'danger', 'Replay Delete Error') }

      this.setBusy(false)
    },
  },
  computed: {
    computedReplayList() {
      if (this.replays !== undefined && this.replays !== null) {
        return this.filteredList()
      } else {
        return []
      }
    },
  },
  async created() {
    await this.getReplays()
    this.$emit('replays-ready')
  }
}
</script>

<style scoped>
.replay-link { cursor: alias; }
.popover.b-popover {
  max-width: 600px !important;
}
</style>