<template>
<div v-cloak id="benchmark-app" class="position-relative mb-5">
  <!-- Introduction -->
  <b-button block @click="setNav('benchmark')" class="mt-2"
            :variant="navModel.benchmark ? 'rf-orange' : 'dark'">
    <b-icon icon="clock-history"></b-icon><span class="ml-2"><b>Benchmark</b></span>
  </b-button>
  <b-collapse v-model="navModel.benchmark" accordion="bench-accordion" role="tabpanel">
    <b-card class="mt-2 setting-card" bg-variant="dark" text-variant="white">
      <b-card-text class="text-left">You can run automated Benchmarks here. Choose the desired content, session settings and graphics
      settings. The app will:
        <ul class="mt-2">
          <li>Launch the Game</li>
          <li>Switch to the selected
            <b-link class="text-rf-orange" @click="navModel.content=true">Content and Session Settings</b-link>
          </li>
          <li>Start a Race Session</li>
          <li>Turn on AI Control(make sure you have mapped this to a keyboard button).</li>
          <li>Record frame times for Benchmark Length seconds</li>
        </ul>
        <h6 class="text-rf-orange">Attention</h6>
        This will start an actual race session. Make sure everyone is <b>in safe distance</b> to your
        Steering Wheel, Bass Shakers and Head Cutter equipment during the benchmark.
      </b-card-text>
      <Setting v-for="setting in settings.options" :key="setting.key"
               :setting="setting" variant="rf-orange" class="mr-3 mb-3"
               @setting-changed="updateSetting"></Setting>
      <div class="mt-2">
        <b-button variant="rf-orange" @click="queueBenchmark"
            v-b-popover.hover.top="'Add current Session and Graphics Preset settings to the benchmark queue.'">
          <b-icon icon="plus" /><span class="ml-2" >Add Benchmark Run</span>
        </b-button>
      </div>
      <b-button-group class="mt-3">
        <b-button variant="rf-blue" @click="start" :disabled="queueLength === 0">
          <b-icon icon="play-btn" /><span class="ml-2">Start Benchmark Queue [{{ queueLength }}]</span>
        </b-button>
        <b-button variant="rf-red" @click="resetBenchmarkQueue" :disabled="queueLength === 0">
          <b-icon icon="trash" />
        </b-button>
      </b-button-group>
    </b-card>
  </b-collapse>

  <!-- Session Settings and Content Selection -->
  <b-button block @click="setNav('content')" class="mt-2"
            :variant="navModel.content ? 'rf-orange' : 'dark'">
    <b-icon icon="receipt"></b-icon><span class="ml-2">Session Settings</span>
  </b-button>
  <b-collapse v-model="navModel.content" accordion="bench-accordion" role="tabpanel">
    <div class="mt-2">
      <SessionSettingArea fixed-width :ses-handler="sesHandler" @make-toast="makeToast" @set-busy="setBusy"/>
    </div>
  </b-collapse>

  <!-- Graphics Presets -->
  <b-button block @click="setNav('graphics')" class="mt-2"
            :variant="navModel.graphics ? 'rf-orange' : 'dark'">
    <b-icon icon="display"></b-icon><span class="ml-2">Graphics Settings</span>
  </b-button>
  <b-collapse v-model="navModel.graphics" accordion="bench-accordion" role="tabpanel">
    <GraphicsPresetArea id-ref="gfxBench" class="mt-2" :gfx-handler="gfxHandler" fixed-width />
  </b-collapse>

  <!-- Results -->
  <b-button block @click="setNav('results')" class="mt-2"
            :variant="navModel.results ? 'rf-orange' : 'dark'">
    <b-icon icon="bar-chart-line"></b-icon><span class="ml-2">Results</span>
  </b-button>
  <b-collapse v-model="navModel.results" accordion="bench-accordion" role="tabpanel">
    <b-collapse :visible="selectedResult != null" @shown="chartCloseBtn=true">
      <!-- Chart Close Button -->
      <div v-if="chartCloseBtn" class="position-absolute" style="width: 100%; z-index: 100;">
        <b-button class="mt-1 mr-1 border-0 bg-dark float-right" size="sm"
                  @click="selectedResult=null; chartCloseBtn=false">
          <b-icon icon="x"></b-icon>
        </b-button>
      </div>

      <!-- Result Chart -->
      <b-card class="mt-2 setting-card position-relative" bg-variant="dark" text-variant="white">
        <BenchChart ref="chart" :chart-data="chartData" :title="currentResultName" />
      </b-card>
    </b-collapse>

    <!-- Result list -->
    <b-card class="mt-2 setting-card" bg-variant="dark" text-variant="white">
      <div v-if="!benchmarkResults.length">
        No result files
      </div>
      <div v-for="r in benchmarkResults" :key="r.id" class="mt-3 mb-3">
        <b-link @click="selectResult(r)"
                :class="selectedResult === r.id ? 'text-rf-orange' : 'text-primary'">
          <h6>{{ r.name }}</h6>
        </b-link>

        Fps 99th: <span class="text-rf-orange">{{ fNum(r.data['fps99']) }}</span>
        Fps 98th: <span class="text-rf-orange">{{ fNum(r.data['fps98']) }}</span>
        Fps Avg: <span class="text-rf-orange">{{ fNum(r.data['fpsmean']) }}</span>
        Fps Median: <span class="text-rf-orange">{{ fNum( r.data['fpsmedian']) }}</span>
        <div class="mt-2">
          <b-button size="sm" variant="danger" :id="'delete-result-btn' + r.id">
            <b-icon icon="x"></b-icon>
          </b-button>
        </div>
        <!-- Delete Popover -->
        <b-popover :target="'delete-result-btn' + r.id" triggers="click">
          <p>Do you really want to delete the Result: {{ r.name }}?</p>
          <div class="text-right">
            <b-button @click="deleteResult(r)" size="sm" variant="danger"
                      aria-label="Delete" class="mr-2">
              Delete
            </b-button>
            <b-button @click="$root.$emit('bv::hide::popover', 'delete-result-btn' + r.id)"
                      size="sm" aria-label="Close">
              Close
            </b-button>
          </div>
        </b-popover>
      </div>
      <b-button class="mt-2" variant="secondary" @click="openResultFolder"
                v-b-popover.hover.auto="'Open result files folder'" size="sm">
        <b-icon icon="folder"></b-icon>
      </b-button>
    </b-card>
  </b-collapse>
</div>
</template>

<script>

import {getEelJsonObject} from "@/main";
import BenchChart from "@/components/BenchChart";
import Setting from "@/components/Setting";
import GraphicsPresetArea from "@/components/GraphicsPresetArea";
import SessionSettingArea from "@/components/SessionSettingArea";
export default {
  name: "Benchmark",
  components: {
    SessionSettingArea,
    GraphicsPresetArea,
    Setting,
    BenchChart,
  },
  data: function () {
    return {
      navModel: {content: true, graphics: true, results: true, benchmark: true},
      settings: {},
      benchmarkPresetName: '',
      benchmarkResults: [],
      queueLength: 0,
      nonePreset: {name: 'None', isNonePreset: true},
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
      selectedResult: null,
    }
  },
  props: { gfxHandler: Object, sesHandler: Object },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    fNum: function (num) { return parseFloat(Number.parseFloat(num).toFixed(2)) },
    setBusy: function (busy) {this.$emit('set-busy', busy) },
    setNav: function (nav) { this.navModel[nav] = !this.navModel[nav] },
    refresh: async function() { await this.getResults() },
    resetBenchmarkQueue: async function() {
      await getEelJsonObject(window.eel.reset_benchmark_queue()())
      this.queueLength = 0
    },
    queueBenchmark: async function() {
      this.setBusy(true)
      const gfxPreset = this.gfxHandler.getSelectedPreset()
      const sesPreset = this.sesHandler.getSelectedPreset()

      const r = await getEelJsonObject(window.eel.queue_benchmark_run([gfxPreset, sesPreset], this.settings)())

      if (!r.result) {
        this.makeToast(r.msg, 'danger')
        console.error('Error queuing Benchmark run!', r.msg)
        console.log(r)
      } else {
        this.queueLength += 1
        console.log('Queue Benchmark run with Presets:', gfxPreset.name, sesPreset.name)
      }
      this.setBusy(false)
    },
    selectResult: function (r) {
      this.setBusy(true)
      this.selectedResult = r.id
      this.updateChartData(r)
      this.$nextTick(() => { this.$refs.chart.refresh() })
      this.setBusy(false)
    },
    getResults: async function () {
      this.benchmarkResults = await getEelJsonObject(window.eel.get_benchmark_results()())
    },
    deleteResult: async function(r) {
      await window.eel.delete_benchmark_result(r.name)()
      await this.getResults()
      this.$root.$emit('bv::hide::popover', 'delete-result-btn' + r.id)
    },
    start: async function () {
      this.setBusy(true)
      this.queueLength = 0
      // Save Session and Content Settings
      await this.sesHandler.update()
      // Save Benchmark settings
      await this.saveSettings()
      // Trigger a Benchmark Run
      await window.eel.start_benchmark()()
      this.setBusy(false)
    },
    getSettings: async function () {
      this.setBusy(true)
      const r = await getEelJsonObject(window.eel.get_benchmark_settings()())
      if (!r.result) {
        this.makeToast(r.msg, 'danger')
        console.error('Error getting Benchmark Settings!', r.msg)
        console.log(r)
        return
      }
      this.settings = r.benchmark_settings
      this.setBusy(false)
    },
    saveSettings: async function () {
      this.setBusy(true)
      const r = await getEelJsonObject(window.eel.save_benchmark_settings(this.settings)())

      if (!r.result) {
        this.makeToast(r.msg, 'danger')
        console.error('Error writing Benchmark Settings!', r.msg)
        console.log(r)
      } else {
        console.log('Saved Benchmark settings.')
      }
      this.setBusy(false)
    },
    openResultFolder: async function() {
      await window.eel.open_result_folder()()
    },
    updateSetting: async function(setting, value) {
      this.settings.options.forEach(s => { if (s.key === setting.key) { s.value = value }})
      setting.value = value
      await this.saveSettings()
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
    currentPresetName() {
      if (this.benchmarkPresetName === '') { return this.nonePreset.name }
      return this.benchmarkPresetName
    },
    currentResult () {
      let result = null
      this.benchmarkResults.forEach(r => {
        if (r.id === this.selectedResult) { result = r }
      })
      return result
    },
    currentResultName () {
      let result = this.currentResult
      if (result === null) { return '' }
      return result.name
    }
  },
  async created() {
    this.setNav('results') // Display results
    await this.getResults()
    await this.getSettings()
  },
  mounted() {
    this.navModel.benchmark = true
  }
}
</script>

<style scoped>

</style>