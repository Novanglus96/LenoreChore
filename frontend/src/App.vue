<template>
  <div id="app">
    <!-- Other content in your App.vue file -->
    <!-- 
    <DataTable />
    <DataCard />
    -->
    <StackedLayout />
  </div>
</template>

<script>
// import DataTable from './components/AreaTable.vue'; // Adjust the path to your component
// import DataCard from './components/AreaCard.vue';
import StackedLayout from './components/StackedLayout.vue';

export default {
  name: 'app',
  created () {
    document.title = "Chores";
  },
  components: {
    //DataTable, // Register the DataTable component for use in your template
    //DataCard,
    StackedLayout,
  },
};
</script>

