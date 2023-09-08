<template>
  <div>
    <table class="min-w-full">
      <thead>
        <tr>
          <th class="px-6 py-3 bg-gray-50 text-left text-xs leading-4 font-medium text-gray-500 uppercase tracking-wider">
            Area Name
          </th>
          <th class="px-6 py-3 bg-gray-50 text-left text-xs leading-4 font-medium text-gray-500 uppercase tracking-wider">
            BG Color
          </th>
          <th class="px-6 py-3 bg-gray-50 text-left text-xs leading-4 font-medium text-gray-500 uppercase tracking-wider">
            Text Color
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td class="px-6 py-4 whitespace-no-wrap border-b border-gray-200">
            {{ item.area_name }}
          </td>
          <td class="px-6 py-4 whitespace-no-wrap border-b border-gray-200">
            {{ item.area_bgcolor }}
          </td>
          <td class="px-6 py-4 whitespace-no-wrap border-b border-gray-200">
            {{ item.area_textcolor }}
          </td>
        </tr>
      </tbody>
    </table>
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
