<template>
  <canvas ref="chartElement"></canvas>
</template>

<script>
import Chart from 'chart.js/auto'
import zoomPlugin from 'chartjs-plugin-zoom';

Chart.register(zoomPlugin);

// Chart Colors
const fontColor = '#afafaf'
const gridColor = 'rgba(0,0,0,0.15)'


export default {
  name: "BenchChart",
  data: function () {
    return {
      chart: null,
      chartOptions: {
        // Performance for large data set
        animation: false,
        parsing: true,
        responsive: true,
        // Do not render data points when not hovering
        radius: 0,
        color: fontColor,
        // Tooltip will popup in-between points
        interaction: {
          intersect: false,
          mode: 'nearest',
        },
        scales: {
          x: {
            title: { display: true, text: 'Recording Time in Seconds', color: fontColor },
            min: 0, max: this.chartData.xAxisSize,
            ticks: { color: fontColor },
            grid: { color: gridColor },
          },
          y: {
            title: { display: false, text: 'Frame time in Milliseconds', color: fontColor },
            min: 0, max: this.chartData.yAxisSize,
            ticks: {
              stepSize: 15,
              color: function(context) {
                if (context.tick.value === 90) {
                  return 'rgba(125,213,165,0.5)'
                } else if (context.tick.value === 45) {
                  return 'rgba(141,9,9,0.75)'
                } else if (context.tick.value === 120) {
                  return 'rgba(0,234,110,0.5)'
                }

                return fontColor;
              }
            },
            grid: {
              color: function(context) {
                if (context.tick.value === 90) {
                  return 'rgba(125,213,165,0.3)'
                } else if (context.tick.value === 45) {
                  return 'rgba(141,9,9,0.3)'
                } else if (context.tick.value === 120) {
                  return 'rgba(0,234,110,0.3)'
                }

                return gridColor;
              },
            },
          },
        },
        elements: { line: { tension: 0 } },
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: this.title !== '',
            text: this.title,
            color: fontColor
          },
          /*
          decimation: {
            enabled: true, algorithm: 'lttb', samples: 100,
          },*/
          zoom: {
            limits: {
              x: { min: 20.0 },
            },
            pan: {
              enabled: true,
              mode: 'x',
            },
            zoom: {
              wheel: {
                enabled: true, speed: 0.25,
              },
              pinch: {
                enabled: true
              },
              mode: 'x',
            }
          }
        },
      }
    }
  },
  methods: {
    refresh: function () {
      this.chart.options.plugins.title.display = this.title !== ''
      this.chart.options.plugins.title.text = this.title
      this.chart.options.scales.y.max = this.chartData.yAxisSize
      this.chart.data = this.chartData
      this.chart.update()
      this.chart.resetZoom()
      console.log('Updated Chart')
    },
  },
  props: {chartData: Object, title: String},
  mounted() {
    const ctx = this.$refs.chartElement
    this.chart = new Chart(ctx,
        {type: 'line', data: this.chartData, options: this.chartOptions}
    )
    console.log('Creating Chart')
  }
}
</script>

<style scoped>

</style>