<template>
  <div>
    <b-collapse :visible="selectedResultId != null" @shown="chartCloseBtn=true">
      <!-- Chart Close Button -->
      <div v-if="chartCloseBtn" class="position-absolute" style="width: 100%; z-index: 100;">
        <b-button class="mt-1 mr-1 border-0 bg-dark float-right" size="sm"
                  @click="selectedResultId=null; chartCloseBtn=false">
          <b-icon icon="x"></b-icon>
        </b-button>
      </div>

      <!-- Result Chart -->
      <b-card class="mt-2 setting-card position-relative" bg-variant="dark" text-variant="white">
        <BenchChart ref="chart" :chart-data="chartData" :title="currentResultName" />
        <template #footer>
          <span>Use
            <b-link target="_blank" href="https://github.com/CXWorld/CapFrameX/releases/latest"
                    class="text-rf-orange">
              CapFrameX
            </b-link>
            to analyse the
            <b-link @click="openResultFolder" class="text-rf-orange"
                    v-b-popover.hover.auto="'Open result files folder'">
              <b-icon icon="folder"></b-icon><span class="ml-1">results</span>
            </b-link>
            in Detail.
          </span>
        </template>
      </b-card>

      <!-- Result Settings -->
      <b-card class="mt-2 setting-card" bg-variant="dark" text-variant="white" footer-class="d-none"
              v-if="currentResult.settings !== undefined">
        <div class="setting mr-3 mb-3 input-group-text info-field fixed-width-name"
             v-for="s in currentResult.settings" :key="s">
          {{ s.name }}: {{ s.value }}
        </div>
      </b-card>

      <!-- Result Graphics Settings -->
      <template v-if="currentResult.gfxPreset !== undefined">
        <b-button block class="mt-2" variant="secondary" @click="setNav('gfxResult')">
          <b-icon icon="display"></b-icon><span class="ml-2">{{ currentResult.gfxPreset.name }}</span>
        </b-button>
        <b-collapse v-model="navModel.gfxResult">
          <GraphicsArea :search="search" :preset="currentResult.gfxPreset" fixed-width compact frozen
              :idx="0" :current_preset_idx="0" :view_mode="0" @set-busy="setBusy" @make-toast="makeToast" />
        </b-collapse>
      </template>

      <!-- Result Session Preset -->
      <template v-if="currentResult.sesPreset !== undefined">
        <b-button block class="mt-2" variant="secondary" @click="setNav('sesResult')">
          <b-icon icon="receipt"></b-icon><span class="ml-2">{{ currentResult.sesPreset.name }}</span>
        </b-button>
        <b-collapse v-model="navModel.sesResult">
          <SessionArea :search="search" :preset="currentResult.sesPreset" fixed-width compact frozen
              :idx="0" :current_preset_idx="0" :view_mode="0" @set-busy="setBusy" @make-toast="makeToast" />
        </b-collapse>
      </template>
    </b-collapse>

    <!-- Result list -->
    <b-card no-body class="mt-2 setting-card" bg-variant="dark" text-variant="white">
      <div v-if="!benchmarkResults.length">
        No result files
      </div>
      <b-list-group flush>
        <b-list-group-item v-for="r in benchmarkResults" :key="r.id" class="bg-dark text-light text-left"
                           :active="selectedResultId === r.id" active-class="rf-orange"
                           button @click="selectResult(r)">
          <b-button size="sm" variant="danger" :id="'delete-result-btn' + r.id" class="float-right">
            <b-icon icon="x"></b-icon>
          </b-button>
          <h6 :class="selectedResultId === r.id ? 'text-rf-orange' : 'text-primary'">{{ r.name }}</h6>

          Fps Avg: <span class="text-rf-orange">{{ fNum(r.data['fpsmean']) }}</span>
          Fps Median: <span class="text-rf-orange">{{ fNum( r.data['fpsmedian']) }}</span>
          Fps 99th Percentile: <span class="text-rf-orange">{{ fNum(r.data['fps99']) }}</span>
          Fps 98th Percentile: <span class="text-rf-orange">{{ fNum(r.data['fps98']) }}</span>

          <!-- Delete Popover -->
          <b-popover :target="'delete-result-btn' + r.id" triggers="hover">
            <p>Do you really want to delete the Result: {{ r.name }}?</p>
            <div class="text-right">
              <b-button @click="deleteResult(r)" size="sm" variant="danger"
                        aria-label="Delete" class="mr-2">
                Delete
              </b-button>
            </div>
          </b-popover>
        </b-list-group-item>
      </b-list-group>
    </b-card>
  </div>
</template>

<script>
import GraphicsArea from "@/components/GraphicsArea";
import SessionArea from "@/components/SessionArea";
import BenchChart from "@/components/BenchChart";
import {getEelJsonObject} from "@/main";

export default {
  name: "BenchmarkResultArea",
  components: {BenchChart, SessionArea, GraphicsArea},
  props: {search: String, },
  data: function () {
    return {
      navModel: { gfxResult: false, sesResult: false },
      benchmarkResults: [],
      selectedResultId: null,
      chartCloseBtn: false,
      chartData: {
        labels: [],
        yAxisSize: 15.0,
        datasets: [
          { label: 'Frame time',
            data: {},
            backgroundColor: 'rgba(70,62,166,0.4)',
            borderColor: 'rgba(116,90,196,0.8)'
          },
          { label: 'Frames per second',
            data: {},
            backgroundColor: 'rgba(255,153,0,0.4)',
            borderColor: 'rgba(250,124,86,0.8)'
          }
        ]
      },
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    fNum: function (num) { return parseFloat(Number.parseFloat(num).toFixed(2)) },
    setBusy: function (busy) {this.$emit('set-busy', busy) },
    setNav: function (nav) { this.navModel[nav] = !this.navModel[nav] },
    refresh: async function () { await this.getResults() },
    selectResult: async function (r) {
      this.setBusy(true)

      // Avoid keeping all the data in memory
      await this.clearResultDetails()

      // Select the result
      this.selectedResultId = r.id

      // Expand Result Panes for fixed width rendering
      const gfxTemp = this.navModel.gfxResult; const sesTemp = this.navModel.sesResult
      this.navModel.gfxResult = true; this.navModel.sesResult = true

      // Get detailed chart and preset data
      const details = await this.getResultDetails(r)

      // Update Entry
      r.data = details.data; r.gfxPreset = details.gfxPreset; r.sesPreset = details.sesPreset

      this.updateChartData(r)
      this.$nextTick(() => {
        this.$refs.chart.refresh();
        // Restore Result Panes that finished fixed width rendering
        this.$nextTick(() => { this.navModel.gfxResult = gfxTemp; this.navModel.sesResult = sesTemp })
      })
      this.setBusy(false)
    },
    getResults: async function () {
      this.benchmarkResults = await getEelJsonObject(window.eel.get_benchmark_results()())
    },
    getCurrentResult: function () {
      let result = {}
      this.benchmarkResults.forEach(r => {
        if (r.id === this.selectedResultId) { result = r }
      })
      return result
    },
    clearResultDetails: async function () {
      this.benchmarkResults.forEach(r => {
        const fps98 = r.data['fps98']; const fps99 = r.data['fps99']
        const fpsmean = r.data['fpsmean']; const fpsmedian = r.data['fpsmedian']
        r.data = {}  // Clear
        r.data['fps98'] = fps98; r.data['fps99'] = fps99
        r.data['fpsmean'] = fpsmean; r.data['fpsmedian'] = fpsmedian
        r.data['msBetweenPresents'] = []
        r.data['fps'] = []
        r.gfxPreset = undefined; r.sesPreset = undefined
      })
    },
    getResultDetails: async function (benchmarkResult) {
      const r = await getEelJsonObject(window.eel.get_benchmark_result_details(benchmarkResult.name)())
      if (!r.result) {
        this.makeToast(r.msg, 'danger')
        console.error('Error getting Benchmark Settings!', r.msg)
        console.log(r)
        return {}
      } else {
        return r
      }
    },
    deleteResult: async function(r) {
      await window.eel.delete_benchmark_result(r.name)()
      await this.getResults()
      this.$root.$emit('bv::hide::popover', 'delete-result-btn' + r.id)
    },
    openResultFolder: async function() {
      await window.eel.open_result_folder()()
    },
    updateChartData: function (r) {
      if (r === null) { return {} }
      this.chartData.labels = []            // X-Axis time
      this.chartData.yAxisSize = 60         // Min Y-Axis size
      this.chartData.xAxisSize = 50
      this.chartData.datasets[0].data = []  // Frame times
      this.chartData.datasets[1].data = []  // FPS

      for (let i = 0; i < r.data['TimeInSeconds'].length; i++) {
        // X-Axis Time in s
        const time = r.data['TimeInSeconds'][i]
        const time_label = String(this.fNum(time)) + 's'
        this.chartData.labels.push(time_label)

        // Y-Axis Frame Times
        this.chartData.datasets[0].data.push(r.data['msBetweenPresents'][i])
        this.chartData.datasets[1].data.push(r.data['fps'][i])

        // Set Y-Axis size
        this.chartData.yAxisSize = Number(
            Math.max(r.data['fps'][i], this.chartData.yAxisSize, r.data['msBetweenPresents'][i]).toFixed()
        )
        // Set X-Axis size
        this.chartData.xAxisSize = i

        // Limit number of Data points
        if (i > 15000) { break }
      }
    },
  },
  computed: {
    currentResult () {
      return this.getCurrentResult()
    },
    currentResultName () {
      let result = this.currentResult
      if (result === null) { return '' }
      return result.name
    },
  },
  async created() {
    await this.getResults()
  }
}
</script>

<style scoped>

</style>