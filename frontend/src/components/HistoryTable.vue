<template>
  <v-data-table-server
    :headers="headers"
    :items="historyItems ? historyItems.items : []"
    :items-length="historyItems ? historyItems.total_records : 0"
    :loading="isLoading"
    :items-per-page="historystore.pageinfo.page_size"
    :items-per-page-options="[{ value: 15, title: '15' }]"
    density="compact"
    fixed-header
    height="600px"
    no-data-text="No history"
    class="striped-table"
    @update:options="pageChanged"
  >
    <template #item.completed_by="{ item }">
      <span>{{
        item.completed_by.fullname?.trim()
          ? item.completed_by.fullname
          : item.completed_by.email
      }}</span>
    </template>
  </v-data-table-server>
</template>

<script setup>
import { useHistoryItems } from "@/composables/historyItemsComposable";
import { useHistoryItemsStore } from "@/stores/historyitems";

const historystore = useHistoryItemsStore();
const { historyItems, isLoading } = useHistoryItems();

const headers = [
  { title: "Date", key: "completed_date", width: "120px", sortable: false },
  { title: "Chore", key: "chore.chore_name", width: "100px", sortable: false },
  { title: "Completed By", key: "completed_by", width: "100px", sortable: false },
];

const pageChanged = ({ page }) => {
  historystore.pageinfo.page = page;
};
</script>

<style scoped>
.striped-table :deep(tbody tr:nth-child(odd)) {
  background-color: rgba(0, 0, 0, 0.09);
}
</style>
