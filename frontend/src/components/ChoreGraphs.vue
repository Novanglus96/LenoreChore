<template>
  <div style="height: 400px">
    <Bar id="my-chart-id" :options="chartOptions" :data="chartData" />
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
import { useChoreStore } from "@/stores/chores";

const chorestore = useChoreStore();

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
);

const chartData = {
  labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
  datasets: chorestore.weeklytotals,
};

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
