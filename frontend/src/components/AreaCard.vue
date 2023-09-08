<template>
    <div>
        <div v-for="item in items" :key="item.id" class="p-4 m-auto border-2 rounded-lg bg-slate-800 text-white" >
            <h1 class="text-3xl font-bold">{{ item.area_name }}</h1>
            <p class="mt-5">
            {{ item.area_name }}
            </p>
            <button
            class="bg-indigo-600 hover:bg-indigo-800 mt-4 font-bold py-2 px-4 rounded"
            >
            Click Me
            </button>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      items: [], // Initialize an empty array to hold the fetched data
    };
  },
  mounted() {
    this.fetchData(); // Call the fetchData method when the component is mounted
  },
  methods: {
    fetchData() {
      // Make an Axios GET request to your Django API endpoint
      axios.get('https://chores.danielleandjohn.love/api/areas/')
        .then((response) => {
          this.items = response.data; // Assign the fetched data to the items array
        })
        .catch((error) => {
          console.error('Error fetching data:', error);
        });
    },
  },
};
</script>