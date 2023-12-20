<template>
  <v-table>
    <thead>
      <tr class="bg-secondary">
        <th class="text-center text-accent font-weight-bold">Date</th>
        <th class="text-center text-accent font-weight-bold">Area</th>
        <th class="text-center text-accent font-weight-bold">Chore</th>
        <th class="text-center text-accent font-weight-bold">Completed By</th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="(item, index) in getHistoryItems"
        :key="item.chore.chore_name"
        :class="index % 2 === 0 ? 'even-row' : 'odd-row'"
        dense
      >
        <td class="text-center">{{ item.completed_date }}</td>
        <td class="text-center">
          <v-icon :icon="item.chore.area.area_icon"></v-icon>{{
          item.chore.area.area_name }}
        </td>
        <td class="text-center">{{ item.chore.chore_name }}</td>
        <td class="text-center">{{ item.completed_by.fullname }}</td>
      </tr>
    </tbody>
  </v-table>
</template>
<script setup>
  import { computed } from 'vue';
  import { useChoreStore } from '@/stores/chores';

  const chorestore = useChoreStore();
  const getHistoryItems = computed(() => {
    return chorestore.getHistoryItems;
  });

</script>
<style scoped>
  .even-row {
    background-color: #f2f2f2; /* Define the background color for even rows */
  }

  .odd-row {
    background-color: #ffffff; /* Define the background color for odd rows */
  }
</style>