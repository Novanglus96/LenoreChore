<template>
  <Bar
    id="my-chart-id"
    :options="chartOptions"
    :data="chartData"
  />
</template>

<script>
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

export default {
  name: 'BarChart',
  components: { Bar },
  data() {
    return {
      chartData: {
        labels: [ 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [ 
          {
            label: 'John',
            data: [3, 7, 1, 3, 3, 4, 9],
            backgroundColor: 'red'
          },
          {
            label: 'Danielle',
            data: [4, 8, 2, 4, 4, 5, 10],
            backgroundColor: 'blue'
          }
        ]
      },
      chartOptions: {
        responsive: true,
        indexAxis: 'y',
        title: {
          display: true,
          tex: 'Graphs',
        },
        plugins: {
          legend: {
            position: 'right'
          }
        }
      }
    }
  }
}
</script>