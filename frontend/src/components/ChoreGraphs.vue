<template>
  <div style="height: 400px" v-if="!isLoading">
    <v-container fluid
      ><v-row
        ><v-col cols="5" class="text-right"
          ><v-btn
            icon="mdi-arrow-left"
            size="sm"
            color="primary"
            @click="increaseWeek"
          ></v-btn></v-col
        ><v-col cols="2" class="text-center font-weight-bold text-h6"
          ><v-btn @click="historystore.graph.week = 0">{{
            weeklyTotals.title
          }}</v-btn></v-col
        ><v-col cols="5" class="text-left"
          ><v-btn
            icon="mdi-arrow-right"
            size="sm"
            color="primary"
            @click="decreaseWeek"
            :disabled="!historystore.graph.week"
          ></v-btn></v-col></v-row
    ></v-container>
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
import { useHistoryItemsStore } from "@/stores/historyitems";

const historystore = useHistoryItemsStore();
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

const increaseWeek = () => {
  historystore.graph.week += 1;
};
const decreaseWeek = () => {
  if (historystore.graph.week > 0) {
    historystore.graph.week -= 1;
  }
};
</script>
