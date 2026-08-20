<template>
  <v-card class="lc-graphs" :elevation="0" border>
    <!-- Was a bg-secondary bar wrapping a 3/6/3 column split. Now a normal
         card header on the themed surface, matching everything else. -->
    <div class="lc-graphs__header">
      <v-btn
        icon="mdi-chevron-left"
        variant="text"
        density="comfortable"
        aria-label="Show the previous week"
        @click="increaseWeek"
      >
        <v-icon icon="mdi-chevron-left"></v-icon>
        <v-tooltip activator="parent" location="bottom">Previous week</v-tooltip>
      </v-btn>

      <!-- Was a bare v-btn showing the date range with no indication that
           pressing it does anything, let alone what. -->
      <v-btn
        variant="text"
        class="lc-graphs__title"
        :disabled="!historystore.graph.week"
        :aria-label="`Showing ${weeklyTotals?.title}. Jump back to this week.`"
        @click="historystore.graph.week = 0"
      >
        {{ weeklyTotals?.title }}
      </v-btn>

      <v-btn
        icon="mdi-chevron-right"
        variant="text"
        density="comfortable"
        aria-label="Show the next week"
        :disabled="!historystore.graph.week"
        @click="decreaseWeek"
      >
        <v-icon icon="mdi-chevron-right"></v-icon>
        <v-tooltip activator="parent" location="bottom">Next week</v-tooltip>
      </v-btn>
    </div>

    <v-divider></v-divider>

    <div class="lc-graphs__canvas">
      <v-skeleton-loader v-if="isLoading" type="image"></v-skeleton-loader>
      <Bar
        v-else
        id="my-chart-id"
        :options="chartOptions"
        :data="chartData"
      />
    </div>

    <!-- A canvas is opaque to assistive tech. The same numbers, as text. -->
    <v-divider></v-divider>
    <div class="lc-visually-hidden">
      <h3>{{ weeklyTotals?.title }} — chores completed</h3>
      <ul>
        <li v-for="(label, i) in chartData.labels" :key="label">
          {{ label }}:
          <template v-for="ds in chartData.datasets" :key="ds.label">
            {{ ds.label }} {{ ds.data[i] }}.
          </template>
        </li>
      </ul>
    </div>
  </v-card>
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

// Hand Chart.js a plain, non-reactive clone of the query data. Passing the
// reactive (readonly) proxy directly causes Chart.js to throw on teardown when
// it tries to splice listener arrays off the dataset ("target is readonly").
const chartData = computed(() => {
  if (!weeklyTotals.value) return { labels: [], datasets: [] };
  return JSON.parse(JSON.stringify(weeklyTotals.value));
});


// The chart used to be made READABLE IN DARK MODE by painting an #EEEEEE
// rectangle behind it and switching the text to #333333 -- i.e. forcing a light
// chart, which sat on the dark page as a glaring white box. Chart.js takes
// colours as plain strings, so the honest fix is to feed it the theme's own
// values and let it be dark when the app is dark.
const chartOptions = computed(() => {
  const dark = themeStore.isDark;
  const textColor = dark ? "#BFCACE" : "#3F4B4F";
  const gridColor = dark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.08)";
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

<style scoped>
.lc-graphs {
  background: rgb(var(--v-theme-surface));
}

.lc-graphs__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--lc-space-2);
  padding: var(--lc-space-2);
}

.lc-graphs__title {
  flex: 1 1 auto;
  min-width: 0;
  font-weight: 600;
}

/* Was a hard-coded 400px on the wrapping div, which on a short phone left the
   chart taller than the viewport and on a large screen wasted the space. The
   aspect ratio keeps it proportional, with a floor and ceiling so it stays
   readable at both extremes. */
.lc-graphs__canvas {
  position: relative;
  padding: var(--lc-space-3);
  height: clamp(240px, 45dvh, 460px);
}

.lc-graphs__canvas > canvas {
  max-height: 100%;
}
</style>
