<template>
  <div style="height: 400px" v-if="!isLoading">
    <Bar id="my-chart-id" :options="chartOptions" :data="weeklyTotals" />
  </div>
</template>
<script setup>
import { Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
import { useWeeklyTotals } from "@/composables/historyItemsComposable";

const { weeklyTotals, isLoading } = useWeeklyTotals();

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
);

const chartOptions = {
  responsive: true,
  indexAxis: "x",
  title: {
    display: true,
    text: "Graphs",
  },
  plugins: {
    legend: {
      position: "bottom",
    },
  },
  maintainAspectRatio: false,
};
</script>
