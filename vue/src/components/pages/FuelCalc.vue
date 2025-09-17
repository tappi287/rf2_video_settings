<script>
import lmwLogoUrl from "@/assets/rfW_logo_color.svg"
import defaultFuelCalcTrackPresets from "@/fuelData.js"
import {divMod, getEelJsonObject, isValid, paddedNum} from "@/main.js";

export default {
  name: "FuelCalc",
  data: function () {
    return {
      resultPresets: [
        12, 16, 24, 30, 80, 100, 120
      ],
      trackPresets: JSON.parse(JSON.stringify(defaultFuelCalcTrackPresets)),
      newTrackPresetName: "",
      selectedPreset: 0,
      lapMinutes: 1,
      lapSeconds: 23,
      lapThousands: 456,
      fuelConsumption: 2.5,
      raceHours: 1,
      raceMinutes: 30,
      raceLaps: 0,
      extraLaps: 1,
      logoUrl: lmwLogoUrl,
      isDev: true,
      saveTimerId: null
    }
  },
  methods: {
    makeToast(message, category = 'secondary', title = 'Update', append = true, delay = 8000) {
      this.$emit('make-toast', message, category, title, append, delay)
    },
    setBusy: function (busy) {
      this.$emit('set-busy', busy)
    },
    setLapTime(lapTime) {
      const _r1 = divMod(lapTime * 1000, 1000)
      let s = _r1[0]
      let ms = _r1[1]
      const _r2 = divMod(s, 60)
      let m = _r2[0]
      s = _r2[1]
      const _r3 = divMod(m, 60)
      m = _r3[1]

      this.lapMinutes = m
      this.lapSeconds = s
      this.lapThousands = ms
    },
    selectTrackPreset(idx) {
      this.selectedPreset = parseInt(idx)
      this.setLapTime(this.trackPresets[idx].lapTime)
      this.fuelConsumption = this.trackPresets[idx].consumption
      this.raceDurationUpdate()
    },
    async raceLapsUpdate() {
      const duration = this.currentLapTime * this.raceLaps
      const _r = divMod(duration, 60)
      const _r2 = divMod(_r[0], 60)
      this.raceHours = _r2[0]
      this.raceMinutes = _r2[1]
    },
    async raceDurationUpdate() {
      this.raceLaps = Math.ceil(this.currentRaceDuration / this.currentLapTime)
    },
    calculateFuel(lapTime, duration, fuel, extraLaps) {
      /* Simple fuel estimation by number of laps for given fuel consumption per lap */
      const laps = Math.ceil(duration / lapTime) + extraLaps
      const fuelAmount = Math.round(laps * fuel)
      return [fuelAmount, laps]
    },
    presetCalc(r) {
      return this.calculateFuel(
          parseFloat(this.currentLapTime),
          r * 60,
          parseFloat(this.fuelConsumption),
          parseFloat(this.extraLaps)
      )
    },
    paddedNum(num, padding, padString = "0") {
      return paddedNum(num, padding, padString)
    },
    async lapTimeUpdate() {
      await this.raceDurationUpdate()
      await this.saveUserPresets()
    },
    async fuelConsumptionUpdate() {
      console.log("Fuel calc update")
      await this.saveUserPresets()
    },
    async loadUserPresets() {
      const r = await getEelJsonObject(window.eel.get_fuel_calc_presets()())
      if (r !== undefined && r.result) {
        if (r.data.length > 0) {
          let trackPresetData = []

          for (const i in r.data) {
            const p = r.data[i]

            // Read settings from data
            if (p?.settings !== undefined) {
              this.selectedPreset = p.settings.selectedPreset
              this.raceHours = p.settings.raceHours
              this.raceMinutes = p.settings.raceMinutes
              this.extraLaps = p.settings.extraLaps
            } else {
              trackPresetData.push(p)
            }
          }
          this.trackPresets = trackPresetData
        }
      }
    },
    async saveUserPresets() {
      console.log("Saving fuel presets")
      this.setBusy(true)
      let presetData = this.getUpdatedTrackPresets()

      // Store settings in preset data
      presetData.push({
        settings:
            {
              selectedPreset: this.selectedPreset,
              raceHours: this.raceHours,
              raceMinutes: this.raceMinutes,
              extraLaps: this.extraLaps,
            }
      })

      const r = await getEelJsonObject(window.eel.save_fuel_calc_presets(presetData)())
      if (r !== undefined && !r.result) {
        this.makeToast("Error saving presets")
      }
      this.setBusy(false)
    },
    getUpdatedTrackPresets() {
      this.trackPresets[this.selectedPreset].lapTime = this.currentLapTime
      this.trackPresets[this.selectedPreset].consumption = this.fuelConsumption

      return JSON.parse(JSON.stringify(this.trackPresets))
    },
    deleteCurrentPreset() {
      // Reset Presets to default if last preset deleted
      if (this.trackPresets.length === 1) {
        this.trackPresets = JSON.parse(JSON.stringify(defaultFuelCalcTrackPresets))
      } else if (this.trackPresets[this.selectedPreset] !== undefined) {
        this.trackPresets.splice(this.selectedPreset, 1)
      }
      this.selectTrackPreset(0)
      this.saveUserPresets()
    },
    createNewTrackPreset() {
      if (this.newTrackPresetNameState !== true) {
        return;
      }
      let newTrackPreset = {
        name: this.newTrackPresetName, lapTime: this.currentLapTime, consumption: this.fuelConsumption
      }
      this.trackPresets.push(newTrackPreset)
      this.trackPresets.sort((a, b) => {
        const nameA = a.name.toUpperCase(); // ignore upper and lowercase
        const nameB = b.name.toUpperCase(); // ignore upper and lowercase
        if (nameA < nameB) {
          return -1;
        }
        if (nameA > nameB) {
          return 1;
        }

        // names must be equal
        return 0;
      })
      this.saveUserPresets()

      // Select the newly created preset
      for (const idx in this.trackPresets) {
        if (this.trackPresets[idx].name === newTrackPreset.name) {
          this.selectTrackPreset(idx)
          break
        }
      }
    },
  },
  computed: {
    currentTrackPreset() {
      return this.trackPresets[this.selectedPreset]
    },
    currentLapTime() {
      const lapMinInSeconds = this.lapMinutes * 60
      const lapSeconds = this.lapSeconds
      const lapThousandsInSeconds = this.lapThousands / 1000
      return lapMinInSeconds + lapSeconds + lapThousandsInSeconds
    },
    currentRaceDuration() {
      const raceMinutesInSeconds = this.raceMinutes * 60
      const raceHoursInSeconds = this.raceHours * 3600
      return raceMinutesInSeconds + raceHoursInSeconds
    },
    currentRaceDurationMinutes() {
      const raceMinutes = this.raceMinutes
      const raceHoursInMinutes = this.raceHours * 60
      return raceMinutes + raceHoursInMinutes
    },
    currentFuelCalculation() {
      const fuelResult = this.calculateFuel(
          this.currentLapTime,
          this.currentRaceDuration,
          this.fuelConsumption,
          this.extraLaps
      )
      const fuelAmount = fuelResult[0]
      const estimatedLaps = fuelResult[1]

      return [fuelAmount, estimatedLaps]
    },
    newTrackPresetNameState() {
      if (this.newTrackPresetName === '') {
        return null
      }
      if (this.newTrackPresetName.length >= 20) {
        return false
      }
      return isValid(this.newTrackPresetName)
    },
    newTrackPresetNameValidationHint() {
      if (this.newTrackPresetName.length >= 20) {
        return "Name must not be longer than 20 characters"
      }
      if (!isValid(this.newTrackPresetName)) {
        return "Name contains invalid characters"
      }
      return ""
    },
  },
  async created() {
    await this.loadUserPresets()
    await this.raceDurationUpdate()
    this.selectTrackPreset(this.selectedPreset)
  }
}
</script>

<template>
  <div id="fuel-calc">
    <b-input-group size="sm">
      <b-input-group-prepend>
        <div class="pl-0 pr-1 lmu-con position-relative bg-transparent">
          <b-img width=".3rem" class="lmu-icon" :src="logoUrl"></b-img>
        </div>
        <!-- Title -->
        <b-input-group-text class="bg-transparent no-border title text-white pl-0">
          Fuel Calculator
        </b-input-group-text>
      </b-input-group-prepend>
    </b-input-group>
    <b-card class="setting-card mt-2 mb-2 text-left p-3" bg-variant="dark" text-variant="white" footer-class="p-2">
      <template #header>
        <b-row>
          <b-col sm="4">
            <b-icon shift-v="-2" icon="calculator-fill"></b-icon>
            <span class="ml-2 align-middle">Presets</span>
          </b-col>
          <b-col sm="8">
            <b-input-group size="sm">
              <b-input-group-prepend>
                <b-dropdown size="sm" :text="currentTrackPreset.name" variant="rf-orange-light">
                  <b-dropdown-item size="sm" v-for="(p, idx) in trackPresets" :key="idx"
                                   @click="selectTrackPreset(idx);saveUserPresets()">
                    {{ p.name }}
                  </b-dropdown-item>
                </b-dropdown>
              </b-input-group-prepend>

              <b-input class="track-preset-input" :state="newTrackPresetNameState" id="track-preset-name"
                       type="text" v-model="newTrackPresetName" placeholder="Enter new preset name..."/>
              <b-popover target="track-preset-name" placement="top" triggers="manual"
                         :show="newTrackPresetNameState===false">
                {{ newTrackPresetNameValidationHint }}
              </b-popover>

              <b-input-group-append>
                <b-button size="sm" @click="createNewTrackPreset" variant="rf-secondary">
                  <b-icon icon="plus-circle"></b-icon>
                </b-button>
                <b-button size="sm" @click="deleteCurrentPreset" variant="danger">
                  <b-icon icon="trash-fill"></b-icon>
                </b-button>
              </b-input-group-append>
            </b-input-group>
          </b-col>
        </b-row>
      </template>

      <!-- Lap Time -->
      <b-row class="mt-4 mb-4">
        <b-col sm="4">
          <b-icon shift-v="-3" icon="speedometer"></b-icon>
          <label class="ml-2 m-0 p-0 align-middle" for="inline-form-custom-select-pref">Average lap time</label>
        </b-col>
        <b-col sm="8">
          <b-form inline @change="lapTimeUpdate" debounce="1200" @submit.prevent>
            <b-form-input id="inline-form-custom-lap-minute" class="mr-sm-2" size="sm"
                          type="number" min="0" max="15" number v-model="lapMinutes"/>
            :
            <b-form-input id="inline-form-custom-lap-seconds" class="mr-sm-2 ml-sm-2" size="sm"
                          type="number" min="0" max="59" number v-model="lapSeconds"/>
            .
            <b-form-input id="inline-form-custom-lap-thousands" class="mr-sm-2 ml-sm-2" size="sm"
                          type="number" min="0" max="999" number v-model="lapThousands"/>
            <span class="text-monospace small text-muted align-middle">({{ currentLapTime }}s)</span>
          </b-form>
        </b-col>
      </b-row>

      <!-- Fuel Consumption -->
      <b-row class="mt-4 mb-4">
        <b-col sm="4">
          <b-icon shift-v="-3" icon="funnel"></b-icon>
          <span class="ml-2 align-middle">Average fuel consumption</span>
        </b-col>
        <b-col sm="8">
          <b-form inline @change="fuelConsumptionUpdate" debounce="1200" @submit.prevent>
            <b-form-input id="inline-form-fuel-consume" type="number" size="sm" class="mr-sm-2"
                          number v-model="fuelConsumption" min="0.0" max="99.0" step="0.1"/>
            <span class="align-middle">l</span>
          </b-form>
        </b-col>
      </b-row>

      <!-- Race Duration -->
      <b-row class="mt-4 mb-4">
        <b-col sm="4">
          <b-icon shift-v="-3" icon="clock"></b-icon>
          <span class="ml-2 align-middle">Race Duration</span>
        </b-col>
        <b-col sm="8">
          <b-form inline @change="raceDurationUpdate();saveUserPresets()" @submit.prevent>
            <b-form-input id="inline-form-custom-lap-minute" class="mr-sm-2" size="sm"
                          type="number" min="0" max="999" number v-model="raceHours"/>
            h
            <b-form-input id="inline-form-custom-lap-seconds" class="mr-sm-2 ml-sm-2" size="sm"
                          type="number" min="0" max="59" number v-model="raceMinutes"/>
            min
            <span class="ml-4 text-monospace small text-muted align-middle">({{ currentRaceDuration }}s)</span>
          </b-form>
        </b-col>
      </b-row>
      <b-row>
        <b-col sm="4"/>
        <b-col sm="8">
          <b-form inline @change="raceLapsUpdate();saveUserPresets()" @submit.prevent>
            <b-form-input id="inline-form-custom-lap-minute" class="mr-sm-2" size="sm"
                          type="number" min="0" max="9999" number v-model="raceLaps"/>
            laps
          </b-form>
        </b-col>
      </b-row>

      <!-- Extra Laps -->
      <b-row class="mt-4 mb-4">
        <b-col sm="4">
          <b-icon shift-v="-3" icon="plus-circle-dotted"></b-icon>
          <span class="ml-2 align-middle">Out/in laps</span>
        </b-col>
        <b-col sm="8">
          <b-form inline @submit.prevent @change="saveUserPresets">
            <b-form-input id="inline-form-fuel-consume" type="number" size="sm" class="mr-sm-2" @submit.prevent
                          number v-model="extraLaps" min="0" max="99"/>
          </b-form>
        </b-col>
      </b-row>

      <template #footer>
        <!-- Result -->
        <b-row class="mt-4 mb-2">
          <b-col sm="4">
            <b-icon shift-v="-3" icon="receipt"></b-icon>
            <span class="ml-2 align-middle">Results</span>
          </b-col>
          <b-col sm="8" class="text-monospace text-left">
            <span class="mr-4">{{ paddedNum(currentRaceDurationMinutes, 3) }} mins</span>
            <span class="mr-4">{{ paddedNum(currentFuelCalculation[0], 3, " ") }} l</span>
            <span class="mr-4">{{ paddedNum(currentFuelCalculation[1], 3, "0") }} laps</span>
          </b-col>
        </b-row>
        <!-- Preset Results -->
        <b-row v-for="(r, idx) in resultPresets" :key="idx"
               class="text-muted">
          <b-col sm="4"/>
          <b-col sm="8" class="text-monospace text-left">
            <span class="mr-4">{{ paddedNum(r, 3) }} mins</span>
            <span class="mr-4">{{ paddedNum(presetCalc(r)[0], 3, " ") }} l</span>
            <span class="mr-4">{{ paddedNum(presetCalc(r)[1], 3, "0") }} laps</span>
          </b-col>
        </b-row>
      </template>
    </b-card>
  </div>
</template>

<style scoped>
.lmu-icon {
  width: 2.075rem;
}

.lmu-con {
  margin-top: .1rem;
}

.track-preset-input {
  max-width: 30%;
}
</style>