<template>
  <div v-if="!isLoading" style="height: 400px">
    <v-container fluid class="bg-secondary"
      ><v-row
        ><v-col cols="3" class="text-right"
          ><v-btn
            icon="mdi-arrow-left"
            size="sm"
            color="primary"
            @click="increaseWeek"
          ></v-btn></v-col
        ><v-col cols="6" class="text-center font-weight-bold text-h6"
          ><v-btn @click="historystore.graph.week = 0">{{
            weeklyTotals.title
          }}</v-btn></v-col
        ><v-col cols="3" class="text-left"
          ><v-btn
            icon="mdi-arrow-right"
            size="sm"
            color="primary"
            @click="decreaseWeek"
            :disabled="!historystore.graph.week"
          ></v-btn></v-col></v-row
    ></v-container>
    <Bar id="my-chart-id" :options="chartOptions" :data="weeklyTotals" :plugins="chartPlugins" />
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
import { useHistoryItemsStore } from "@/stores/historyitems";
import { useThemeStore } from "@/stores/theme";
import { computed } from "vue";

const historystore = useHistoryItemsStore();
const themeStore = useThemeStore();
const { weeklyTotals, isLoading } = useWeeklyTotals();

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
);

const chartPlugins = computed(() => {
  if (!themeStore.isDark) return [];
  return [{
    id: "lightBackground",
    beforeDraw: (chart) => {
      const ctx = chart.canvas.getContext("2d");
      ctx.save();
      ctx.globalCompositeOperation = "destination-over";
      ctx.fillStyle = "#EEEEEE";
      ctx.fillRect(0, 0, chart.width, chart.height);
      ctx.restore();
    },
  }];
});

const chartOptions = computed(() => {
  const textColor = themeStore.isDark ? "#333333" : undefined;
  const gridColor = themeStore.isDark ? "rgba(0,0,0,0.1)" : undefined;
  return {
    responsive: true,
    indexAxis: "x",
    plugins: {
      legend: {
        position: "bottom",
        labels: { color: textColor },
      },
    },
    scales: {
      x: {
        ticks: { color: textColor },
        grid: { color: gridColor },
      },
      y: {
        ticks: { color: textColor },
        grid: { color: gridColor },
      },
    },
    maintainAspectRatio: false,
  };
});

const increaseWeek = () => {
  historystore.graph.week += 1;
};
const decreaseWeek = () => {
  if (historystore.graph.week > 0) {
    historystore.graph.week -= 1;
  }
};
</script>
