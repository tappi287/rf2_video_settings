<script>

export default {
  name: "ResultDisplay",
  props: {driver: Object},
  data: function () {
    return {
      driverFields: [
        {key: "num", label: "#", sortable: true, class: 'text-left'},
        {key: "p", label: "Position", class: 'text-left'},
        {key: "laptime_formatted", label: "Lap Time", sortable: true, class: 'text-left'},
        {key: "s1", label: "S1", sortable: true, class: 'text-left'},
        {key: "s2", label: "S2", sortable: true, class: 'text-left'},
        {key: "s3", label: "S3", sortable: true, class: 'text-left'},
        {key: "pit", label: "Pit", class: 'text-right'},
        {key: "topspeed", label: "Top Speed", class: 'text-right'},
        {key: "fcompound", label: "Fronts", class: 'text-right'},
        {key: "rcompound", label: "Rears", class: 'text-right'},
      ],
      selectedRow: null,
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
    isFastestLap(entry) {
      return entry.laptime_formatted === this.driver.fastest_lap_formatted;
    },
    isPurpleLap(entry) {
      return entry.laptime_formatted === this.driver.purple_lap_formatted
    },
    isPurpleSector(sectorTime, sectorNum) {
      if (sectorNum === 1) {
        return sectorTime === this.driver.purple_s1
      } else if (sectorNum === 2) {
        return sectorTime === this.driver.purple_s2
      } else if (sectorNum === 3) {
        return sectorTime === this.driver.purple_s3
      }
      return false
    },
    isFastestSector(sectorTime, sectorNum) {
      if (sectorNum === 1) {
        return sectorTime === this.driver.s1_fastest_formatted
      } else if (sectorNum === 2) {
        return sectorTime === this.driver.s2_fastest_formatted
      } else if (sectorNum === 3) {
        return sectorTime === this.driver.s3_fastest_formatted
      }
      return false
    },
    getLapClass(entry) {
      if (!entry.valid) { return "text-warning" }
      if (this.isPurpleLap(entry)) { return "text-purple" }
      if (this.isFastestLap(entry)) { return "text-success" }
      return ""
    },
    getLapTitle(entry) {
      if (!entry.valid) { return "Invalid Lap! Displayed time is estimated and not precise." }
      return null
    },
    getSectorClass(sectorTime, sectorNum) {
      if (this.isPurpleSector(sectorTime, sectorNum)) { return "text-purple" }
      if (this.isFastestSector(sectorTime, sectorNum)) { return "text-success" }
      return ""
    }
  }
}
</script>

<template>
  <div>
    <b-table :items="driver.laps" :fields="driverFields"
             sort-by="num" no-sort-reset sort-icon-left
             class="p-4"
             table-variant="dark" small borderless hover
             thead-class="text-white">
      <template #cell(laptime_formatted)="row">
        <span :title="getLapTitle(row.item)" :class="getLapClass(row.item)">{{ row.item.laptime_formatted }}</span>
      </template>
      <template #cell(s1)="row">
        <span :class="getSectorClass(row.item.s1, 1)">{{ row.item.s1 }}</span>
      </template>
      <template #cell(s2)="row">
        <span :class="getSectorClass(row.item.s2, 2)">{{ row.item.s2 }}</span>
      </template>
      <template #cell(s3)="row">
        <span :class="getSectorClass(row.item.s3, 3)">{{ row.item.s3 }}</span>
      </template>
      <template #cell(pit)="row">
        {{ row.item.pit ? 'In Pit' : '-' }}
      </template>
    </b-table>

    <!-- Possible Best -->
    <div class="text-left p-0 m-0">
      Possible Best: <span class="text-rf-orange">{{ driver.possible_best_formatted }}</span>
    </div>

  </div>
</template>

<style scoped>
.text-purple {
  color: #e400da;
}
</style>