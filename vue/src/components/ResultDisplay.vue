<script>
import {getEelJsonObject, sleep} from "@/main";
import ResultDriver from "@/components/ResultDriver.vue";

export default {
  name: "ResultDisplay",
  props: {resultFile: String},
  components: {ResultDriver},
  data: function () {
    return {
      raceResultFields: [
        // {key: "expandRow", label: "", sortable: false, class: 'text-left'},
        {key: 'position', label: 'P', sortable: true, class: 'text-left'},
        {key: 'name', label: 'Name', class: 'text-left'},
        {key: 'fastest_lap_formatted', label: 'Best Lap', sortable: true, class: 'text-left'},
        {key: 'car_class', label: 'Class', class: 'text-right'},
        {key: 'class_position', label: 'P', class: 'text-left'},
        {key: 'car_number', label: '#', class: 'text-right'},
        {key: 'car_type', label: 'Car', class: 'text-right'},
        {key: 'pace', label: 'Pace', class: 'text-right secondary-info'},
        {key: 'consistency', label: 'Con', sortable: true, class: 'text-right secondary-info'},
        {key: 'finish_delta_laps_formatted', label: '', class: 'text-right secondary-info'},
        {key: 'finish_time_formatted', label: 'Time', class: 'text-right'},
      ],
      incidentFields: [
          {key: 'et', label: 'Time', sortable: true, class: 'text-left'},
          {key: 'drivers', label: 'Drivers', sortable: true, class: 'text-left'},
          {key: 'text', label: 'Text', sortable: false, class: 'text-right'}
      ],
      incidentFilter: null,
      incidentHideDoubles: true,
      resultData: {}
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) {
      this.isBusy = busy;
      this.$emit('set-busy', busy)
    },
    getResults: async function () {
      this.setBusy(true)
      const r = await getEelJsonObject(window.eel.get_result_file(this.resultFile)())
      if (r.result) {
        this.resultData = r.data
      }
      if (!r.result) {
        this.makeToast(r.msg, 'danger', 'Get Results Error')
      }
      this.setBusy(false)
    },
    getLapDots(entry) {
      return [entry.purple_s1 !== "", entry.purple_s2 !== "", entry.purple_s3 !== ""]
    },
    isPurpleLap(entry) {
      if (entry.fastest_lap_formatted === entry.purple_lap_formatted) { return "text-purple" }
      return ""
    },
    async jumpToIncident(drivers, time) {
      // Play
      await this.replayPlaybackCommand(4)
      // Focus driver while in normal playback Speed so camera swings to focused vehicle in time
      await getEelJsonObject(window.eel.focus_driver(drivers[0])())
      // Goto Time
      await getEelJsonObject(window.eel.replay_time_command(time)())
      // Give camera some time to swing to vehicle
      await sleep(1200)
      // Slow-mo
      await this.replayPlaybackCommand(7)

      // Back to realtime after 2 seconds
      await sleep(2000)
      await this.replayPlaybackCommand(8)
    },
    async replayPlaybackCommand(command) {
      await getEelJsonObject(window.eel.replay_playback_command(command)())
    },
    setDriverFilter(value) {
      let hideIncidentDoubles = this.incidentHideDoubles
      this.incidentHideDoubles = false
      this.incidentFilter = value
      this.incidentHideDoubles = hideIncidentDoubles
    }
  },
  computed: {
    raceResultItems() {
      if (this.resultData.drivers === undefined) {
        return []
      }
      let resultItems = []
      for (const driver of this.resultData.drivers) {
        const item = driver
        // Use delta for non-leading cars
        if (driver.class_position !== 1) {
          item.finish_time_formatted = driver.finish_delta_formatted
        }

        // Add to results
        resultItems.push(
            item
        )
      }
      return resultItems
    },
    incidentItems () {
      if (this.resultData.entries === undefined) { return []; }
      let incidentItems = []
      let prevIncident = {}

      for (const entry of this.resultData.entries) {
        if (prevIncident?.drivers?.length === 2 && entry.drivers.length === 2 && this.incidentHideDoubles) {
          if (entry.drivers.indexOf(prevIncident.drivers[0]) !== -1) {
            if (entry.drivers.indexOf(prevIncident.drivers[1]) !== -1) {
              continue
            }
          }
        }

        incidentItems.push(entry)
        prevIncident = entry
      }
      return incidentItems
    }
  },
  mounted() {
    this.getResults()
  }
}
</script>

<template>
  <div>
    <slot name="top">
    </slot>
    <!--
    <b-button-group title="Replay Controls" size="sm" class="text-center text-monospace text-bold mb-4">
      <b-button @click="replayPlaybackCommand(0)" variant="rf-blue" title="Skip to Start">
        |<
      </b-button>
      <b-button @click="replayPlaybackCommand(2)" variant="rf-secondary" title="Fast Reverse" >
        <<<
      </b-button>
      <b-button @click="replayPlaybackCommand(3)" variant="rf-secondary" title="Reverse Scan">
        <<
      </b-button>
      <b-button @click="replayPlaybackCommand(4)" variant="rf-secondary" title="Play Reverse">
        <
      </b-button>
      <b-button @click="replayPlaybackCommand(5)" variant="rf-secondary" title="Reverse Slow-Mo">
        <|
      </b-button>
      <b-button @click="replayPlaybackCommand(6)" variant="rf-secondary" title="Pause">
        ||
      </b-button>
      <b-button @click="replayPlaybackCommand(7)" variant="rf-secondary" title="Slow-mo">
        |>
      </b-button>
      <b-button @click="replayPlaybackCommand(8)" variant="rf-secondary" title="Play">
        >
      </b-button>
      <b-button @click="replayPlaybackCommand(9)" variant="rf-secondary" title="Scan Forward">
        >>
      </b-button>
      <b-button @click="replayPlaybackCommand(10)" variant="rf-secondary" title="Fast Forward">
        >>>
      </b-button>
      <b-button @click="replayPlaybackCommand(1)" variant="rf-blue" title="Skip to End">
        >|
      </b-button>
    </b-button-group>
    -->
    <b-tabs align="left" no-fade>
      <template #tabs-end>
        <li class="nav-item align-self-center xml-title">
          <small>{{resultData?.file_name }}</small>
        </li>
      </template>
      <b-tab title="Session Results" title-link-class="btn-secondary pt-1 pb-1">
        <!-- RESULT -->
        <b-table :items="raceResultItems" :fields="raceResultFields"
                 details-td-class="result-td-details"
                 sort-by="position" no-sort-reset sort-icon-left
                 table-variant="dark" small borderless
                 class="server-list" thead-class="text-white"
                 ref="resultTable" :title="resultData?.file_name"
        >
          <!-- Name -->
          <template #head(name)="headRow">
            <span class="pl-2"><b-icon icon="person-fill" /> {{ headRow.label }}</span>
          </template>
          <template #cell(name)="row">
            <b-button size="sm" @click="row.toggleDetails" title="Show Laptimes"
                      class="text-light m-0 mr-2 no-border no-bg">
              <b-icon :icon="row.detailsShowing ? 'caret-down-fill': 'caret-right-fill'"
                      variant="secondary" shift-v="1"/>
              {{ row.item.name }}
            </b-button>
          </template>
          <!-- Fastest Lap -->
          <template #cell(fastest_lap_formatted)="row">
            <span class="mr-3 text-left">
              <b-icon v-for="(isPurple, idx) in getLapDots(row.item)" :key="idx" icon="circle-fill"
                      scale="0.5" class="lap-dot"
                      :class="isPurple ? 'text-purple' : 'text-dot-secondary'"></b-icon>
            </span>
            <span :class="isPurpleLap(row.item)">{{ row.item.fastest_lap_formatted }}</span>
          </template>
          <!-- Consistency -->
          <template #head(consistency)>
            <span title="Consistency">Con</span>
          </template>
          <template #cell(consistency)="row">
            <span title="Exaggerated lap time consistency, invalid laps are penalized"
                  class="text-monospace small">
              {{ row.item.consistency }}
            </span>
          </template>

          <!-- Race Pace -->
          <template #head(pace)>
            <span title="Race Pace relative to leader">Pace</span>
          </template>
          <template #cell(pace)="row">
            <span title="Race Pace relative to leader" class="text-monospace small">{{ row.item.pace }}</span>
          </template>

          <!-- LAP TIMES -->
          <template #row-details="detail">
            <ResultDriver :driver="detail.item" />
          </template>
        </b-table>
      </b-tab>
      <!-- INCIDENTS -->
      <b-tab title="Incidents" title-link-class="btn-secondary pt-1 pb-1">
        <b-table :items="incidentItems"
                 :fields="incidentFields"
                 :filter="incidentFilter"
                 sort-by="et" no-sort-reset sort-icon-left
                 table-variant="dark" small borderless
                 class="server-list" thead-class="text-white">
          <template #cell(et)="row">
            <b-link class="text-monospace" @click="jumpToIncident(row.item.drivers, row.item.et)"
                    title="Jump to incident in current Replay">
              {{ row.item.et }}
            </b-link>
          </template>
          <!-- A custom formatted header cell for field 'name' -->
          <template #head(drivers)="data">
            <span class="mr-1">{{ data.label }}</span>
            <b-link @click="incidentHideDoubles=!incidentHideDoubles" class="float-right text-success">
              {{ incidentHideDoubles ? 'Show' : 'Hide' }} collision doubles
            </b-link>
            <template v-if="incidentFilter!==null">
              <b-link @click="setDriverFilter(null)" class="float-right text-warning mr-3">
                Clear Filter
              </b-link>
            </template>
          </template>
          <template #cell(drivers)="row">
            <b-link v-for="(d, idx) in row.item.drivers" :key="idx"
                    @click="setDriverFilter(d)" title="Filter by this Driver"
                    class="mr-1 small" :class="d === incidentFilter ? 'text-warning' : ''">
              {{ d }}
            </b-link>
          </template>
          <template #cell(text)="row">
            <span class="small">{{ row.item.text }}</span>
          </template>
        </b-table>
      </b-tab>
    </b-tabs>
  </div>
</template>

<style scoped>
.text-purple {
  color: #e327db;
}
.text-dot-secondary {
  color: #838383;
  opacity: 0.2
}
.lap-dot {
  margin-left: -0.25rem;
}
.result-td-details { padding: 0; margin: 0; border: none; }

.xml-title {margin-left: auto;}
</style>