<template>
    <v-table>
        <thead>
        <tr>
            <th class="text-left">
            Date
            </th>
            <th class="text-left">
            Area
            </th>
            <th class="text-left">
            Chore
            </th>
            <th class="text-left">
            Completed By
            </th>
        </tr>
        </thead>
        <tbody>
        <tr
            v-for="item in getHistoryItems"
            :key="item.chore.chore_name"
        >
            <td>{{ item.completed_date }}</td>
            <td><v-icon :icon="item.chore.area.area_icon"></v-icon>{{ item.chore.area.area_name }}</td>
            <td>{{ item.chore.chore_name }}</td>
            <td>{{ item.completed_by.fullname }}</td>
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