<template>
  <div id="app">
    <!-- Other content in your App.vue file -->
    <DataTable />
    <DataCard />
  </div>
</template>

<script>
import DataTable from './components/AreaTable.vue'; // Adjust the path to your component
import DataCard from './components/AreaCard.vue';

export default {
  components: {
    DataTable, // Register the DataTable component for use in your template
    DataCard,
  },
};
</script>

