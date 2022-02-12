<template>
<div v-cloak id="benchmark-app" class="position-relative mb-5">
  <!-- Benchmark Button or Progress Bar -->
  <template v-if="progressBarEnabled">
    <!-- Progress -->
    <b-progress :max="100" height="2.25rem" variant="dark" @click="setNav('benchmark')" class="mt-2">
      <b-progress-bar :value="benchmarkProgress">
        <div v-if="benchmarkProgress > 25">
          <b-icon icon="clock-history" />
          <span class="ml-2">Remaining Runs: <strong>{{ this.benchmarkProgressSize }}</strong></span>
        </div>
      </b-progress-bar>
    </b-progress>
  </template>
  <template v-else>
    <!-- Benchmark Button -->
    <b-button block @click="setNav('benchmark')" class="mt-2"
              :variant="navModel.benchmark ? 'rf-orange' : 'dark'">
      <b-icon icon="clock-history" /><span class="ml-2"><b>Benchmark</b></span>
    </b-button>
  </template>

  <!-- Benchmark -->
  <b-collapse v-model="navModel.benchmark" accordion="bench-accordion" role="tabpanel">
    <b-card class="mt-2 setting-card" bg-variant="dark" text-variant="white">
      <b-card-text class="text-left">You can run automated Benchmarks here. Choose the desired content, session settings and graphics
      settings. The app will:
        <ul class="mt-2">
          <li>Launch the Game</li>
          <li>Switch to the selected
            <b-link class="text-rf-orange" @click="navModel.content=true">Content and Session Settings</b-link>
          </li>
          <li>Start a Race Session <b>or</b> start a
            <b-link class="text-rf-orange" @click="navModel.replays=true">Replay</b-link>
          </li>
          <li>Turn on AI Control(make sure you have <b>mapped this to a keyboard key</b>).</li>
          <li>Record frame times for Benchmark Length seconds</li>
        </ul>
        <h6 class="text-rf-orange">Attention</h6>
        This will start an actual race session. Make sure everyone is <b>in safe distance</b> to your
        Steering Wheel, Bass Shakers and Head Cutter equipment during the benchmark.
        <p class="mt-2">
          Also make sure to <b>not switch focus</b> between windows.
          The rFactor 2 game executable needs focus to receive keyboard commands send from this app.
        </p>
      </b-card-text>

      <!-- Benchmark Settings -->
      <div class="pt-4 pb-4">
        <SettingItem v-for="setting in settings.options" :key="setting.key"
                 :setting="setting" variant="rf-orange" class="mr-3 mb-3"
                 ref="benchmarkSettings"
                 @setting-changed="updateSetting"/>
        <b-button v-if="showReplayReset"
                  variant="rf-orange" @click="resetReplay" class="setting mr-3"
                  style="top: -0.04rem; position: relative;">
            <b-icon icon="trash" /> Reset Replay
        </b-button>
      </div>

      <!-- Benchmark Queue -->
      <b-button-group>
        <b-button variant="rf-orange" @click="queueBenchmarkRun"
            v-b-popover.hover.top="'Add current Session and Graphics Preset settings to the benchmark queue.'">
          <b-icon icon="plus-circle" /><span class="ml-2 mr-2" >Add</span>
        </b-button>
        <b-dropdown variant="primary" @click="startBenchmarkQueue" :disabled="startButtonDisabled" split right>
          <template #button-content>
            <div class="rounded-right">
              <b-icon icon="play-btn" /><span class="ml-2">Start Benchmark Queue [{{ benchmarkQueue.length }}]</span>
            </div>
          </template>
          <b-dropdown-item v-for="q in benchmarkQueue" :key="q.id">
            <span>{{ q.id }} <span v-for="p in q.presets" :key="p">{{' - ' + p }}</span> - Replay: {{ q.replay }}</span>
            <b-button @click="removeFromBenchmarkQueue(q)" class="ml-3" size="sm"><b-icon icon="trash" /></b-button>
          </b-dropdown-item>
        </b-dropdown>
        <b-button variant="rf-red" @click="resetBenchmarkQueue" :disabled="benchmarkQueue.length === 0">
          <b-icon icon="trash" />
        </b-button>
      </b-button-group>
    </b-card>
  </b-collapse>

  <!-- Replay List -->
  <b-button block @click="setNav('replays')" class="mt-2"
            :variant="navModel.replays ? 'rf-orange' : 'dark'">
    <b-icon icon="bootstrap-reboot"></b-icon>
    <span class="ml-2">Replays</span>
  </b-button>
  <b-collapse v-model="navModel.replays" accordion="bench-accordion" role="tabpanel">
    <b-card no-body class="mt-2 setting-card" bg-variant="dark" text-variant="white">
      <b-card-text class="p-1">Select a Replay to use it for the current Benchmark Run.</b-card-text>
    </b-card>
    <ReplayList ref="replayList" @row-selected="selectReplay" @replays-ready="replayListReady" />
  </b-collapse>

  <!-- Session Settings and Content Selection -->
  <b-button block @click="setNav('content')" class="mt-2"
            :variant="navModel.content ? 'rf-orange' : 'dark'">
    <b-icon icon="receipt"></b-icon><span class="ml-2">Session Settings</span>
  </b-button>
  <b-collapse v-model="navModel.content" accordion="bench-accordion" role="tabpanel">
    <div class="mt-2">
      <SessionPresetArea fixed-width :ses-handler="sesHandler" :hide-apply-webui-settings="true"
                         :search="search" @make-toast="makeToast" @set-busy="setBusy"/>
    </div>
  </b-collapse>

  <!-- Graphics Presets -->
  <b-button block @click="setNav('graphics')" class="mt-2"
            :variant="navModel.graphics ? 'rf-orange' : 'dark'">
    <b-icon icon="display"></b-icon><span class="ml-2">Graphics Settings</span>
  </b-button>
  <b-collapse v-model="navModel.graphics" accordion="bench-accordion" role="tabpanel">
    <GraphicsPresetArea id-ref="gfxBench" class="mt-2" :gfx-handler="gfxHandler" :search="search" fixed-width />
  </b-collapse>

  <!-- Results -->
  <b-button block @click="setNav('results')" class="mt-2"
            :variant="navModel.results ? 'rf-orange' : 'dark'">
    <b-icon icon="bar-chart-line"></b-icon><span class="ml-2">Results</span>
  </b-button>
  <b-collapse v-model="navModel.results" accordion="bench-accordion" role="tabpanel">
    <BenchmarkResultArea ref="resultArea" :search="search" />
  </b-collapse>
</div>
</template>

<script>

import {getEelJsonObject} from "@/main";
import SettingItem from "@/components/settings/Setting";
import GraphicsPresetArea from "@/components/presets/GraphicsPresetArea";
import SessionPresetArea from "@/components/presets/SessionPresetArea";
import ReplayList from "@/components/ReplayList";
import BenchmarkResultArea from "@/components/benchmark/BenchmarkResultArea";
// --- </ Prepare receiving Benchmark Progress Events
window.eel.expose(rfactorBenchmarkProgress, 'benchmark_progress')
async function rfactorBenchmarkProgress (event) {
  const bEvent = new CustomEvent('benchmark-progress-event', {detail: event})
  window.dispatchEvent(bEvent)
}
// --- />

export default {
  name: "BenchMark",
  components: {
    BenchmarkResultArea,
    ReplayList,
    SessionPresetArea,
    GraphicsPresetArea,
    SettingItem,
  },
  data: function () {
    return {
      navModel: {
        content: true, graphics: true, results: true, benchmark: true, replays: true,
        gfxResult: false, sesResult: false },
      settings: {},
      showReplayReset: false,
      firstSelect: true,
      benchmarkPresetName: '',
      benchmarkQueue: [],
      benchmarkProgress: 0, benchmarkProgressSize: 0,
      nonePreset: {name: 'None', isNonePreset: true},
    }
  },
  props: { gfxHandler: Object, sesHandler: Object, search: String },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    fNum: function (num) { return parseFloat(Number.parseFloat(num).toFixed(2)) },
    setBusy: function (busy) {this.$emit('set-busy', busy) },
    setNav: function (nav) { this.navModel[nav] = !this.navModel[nav] },
    refresh: async function() {
      await this.$refs.resultArea.refresh()
      await this.getBenchmarkQueue()
    },
    getReplaySettingRef: function () {
      let setting = undefined
      this.$refs.benchmarkSettings.forEach(s => { if (s.setting.key === 'Replay') { setting = s } })
      return setting
    },
    selectReplay: function (selection) {
      let replay = null
      if (selection.length) {
        replay = selection[0]
      }
      this.updateReplaySetting(replay)
    },
    updateReplaySetting: function(replay) {
      // Hacky settings list update
      const replaySettingCmp = this.getReplaySettingRef()
      const selectedSetting = replaySettingCmp.setting.settings[0]
      if (replay !== null) {
        this.showReplayReset = true
        selectedSetting.value = replay.name
        selectedSetting.name = replay.name

        // Skip message on initial load
        if (this.firstSelect) {
          this.firstSelect = false
        } else {
          this.makeToast('Replay selected: ' + replay.name, 'success',
              'Benchmark', false, 1500)
        }
      } else {
        this.showReplayReset = false
        selectedSetting.value = null
        selectedSetting.name = 'Select a Replay in the Replay List'
      }
      // Trigger a settings update by selecting the only available setting
      replaySettingCmp.selectSetting(selectedSetting)
    },
    resetReplay: function () { this.$refs.replayList.$refs.replayTable.clearSelected() },
    replayListReady: function () {
      this.$nextTick(() => { this.verifyReplaySetting() })
    },
    verifyReplaySetting: function () {
      // Prepare/Restore Replay setting
      let replay = null; let replayRow = null; let replayExists = false
      this.settings.options.forEach(s => { if (s.key === 'Replay') { replay = s.value }})

      // Verify it exists on disk
      for (let i=0; i < this.$refs.replayList.$refs.replayTable.items.length; i++) {
        if (this.$refs.replayList.$refs.replayTable.items[i].name === replay) {
          replayExists = true; replayRow = i
        }
      }
      // Select Row in Replay Table (will trigger a setting update)
      if (replayRow !== null) { this.$refs.replayList.$refs.replayTable.selectRow(replayRow) }

      if (replayExists) {
        console.log('Found and set replay setting:', replay)
      } else if (replay !== null) {
        this.makeToast('The previously selected Replay file could not be found on disk. If you just copied ' +
            'it to the Replay folder: Navigate away from this page and back then select it again: ' + replay,
            'danger', 'Replay Setting', true, 20000)
      }
    },
    resetBenchmarkQueue: async function() {
      await getEelJsonObject(window.eel.reset_benchmark_queue()()); this.benchmarkQueue = []
      await this.getBenchmarkQueue()
    },
    queueBenchmarkRun: async function() {
      this.setBusy(true)
      const gfxPreset = this.gfxHandler.getSelectedPreset()
      const sesPreset = this.sesHandler.getSelectedPreset()

      const r = await getEelJsonObject(window.eel.queue_benchmark_run([gfxPreset, sesPreset], this.settings)())

      if (!r.result) {
        this.makeToast(r.msg, 'danger')
        console.error('Error queuing Benchmark run!', r.msg)
        console.log(r)
      } else {
        await this.getBenchmarkQueue()
      }
      this.setBusy(false)
    },
    removeFromBenchmarkQueue: async function(entry) {
      const r = await getEelJsonObject(window.eel.remove_from_benchmark_queue(entry.id)())
      if (!r.result) {
        this.makeToast(r.msg, 'danger')
        console.error('Queue entry not found in Benchmark Queue', r.msg)
        console.log(r)
      }
      await this.getBenchmarkQueue()
      this.setBusy(false)
    },
    getBenchmarkQueue: async function() {
      const r = await getEelJsonObject(window.eel.get_benchmark_queue()())
      if (!r.result) {
        this.makeToast(r.msg, 'danger')
        this.benchmarkQueue = []
        console.error('Queue entry not found in Benchmark Queue', r.msg)
        console.log(r)
      } else {
        this.benchmarkQueue = r['queue']
      }
    },
    startBenchmarkQueue: async function () {
      this.setBusy(true)
      // Save Session and Content Settings
      await this.sesHandler.update()
      // Save Benchmark settings
      await this.saveSettings()
      // Trigger a Benchmark Run
      await window.eel.start_benchmark()()
      await this.getBenchmarkQueue()
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
    updateSetting: async function(setting, value) {
      this.settings.options.forEach(s => { if (s.key === setting.key) { s.value = value }})
      setting.value = value
      await this.saveSettings()
    },
    updateBenchmarkProgress: async function(event) {
      this.benchmarkProgressSize = event.detail.size
      this.benchmarkProgress = event.detail.progress
    },
  },
  computed: {
    currentPresetName() {
      if (this.benchmarkPresetName === '') { return this.nonePreset.name }
      return this.benchmarkPresetName
    },
    startButtonDisabled () {
      if (this.benchmarkQueue.length === 0) { return true }
      return this.benchmarkProgress !== 0
    },
    progressBarEnabled () {
      return this.benchmarkProgress !== 0
    }
  },
  async created() {
    await this.getSettings()
    await this.getBenchmarkQueue()
  },
  mounted() {
    window.addEventListener('benchmark-progress-event', this.updateBenchmarkProgress)
    this.$nextTick(() => { this.navModel.benchmark = true })
  },
  destroyed() {
    window.removeEventListener('benchmark-progress-event', this.updateBenchmarkProgress)
  }
}
</script>

<style scoped>

</style>