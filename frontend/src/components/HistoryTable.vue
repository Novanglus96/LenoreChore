<template>
  <vue3-datatable
    :rows="historyItems ? historyItems.items : []"
    :columns="columns"
    :loading="isLoading"
    :totalRows="historyItems ? historyItems.total_records : 0"
    :isServerMode="true"
    :pageSize="historystore.pageinfo.page_size"
    :stickyHeader="true"
    noDataContent="No history"
    search=""
    ref="history_table"
    height="600px"
    skin="bh-table-striped bh-table-compact"
    :pageSizeOptions="[5]"
    :showPageSize="false"
    paginationInfo="Showing {0} to {1} of {2} items"
    class="alt-pagination"
    @change="pageChanged"
  >
    <template #completed_by.email="row">
      <span>{{
        row.value.completed_by.fullname == " "
          ? row.value.completed_by.email
          : row.value.completed_by.fullname
      }}</span>
    </template>
  </vue3-datatable>
</template>
<script setup>
import { useHistoryItems } from "@/composables/historyItemsComposable";
import Vue3Datatable from "@bhplugin/vue3-datatable";
import "@bhplugin/vue3-datatable/dist/style.css";
import { ref } from "vue";
import { useHistoryItemsStore } from "@/stores/historyitems";

const historystore = useHistoryItemsStore();
const { historyItems, isLoading } = useHistoryItems();
const columns = ref([
  { field: "id", title: "ID", isUnique: true, hide: true },
  { field: "completed_date", title: "Date", type: "date", width: "120px" },
  { field: "chore.chore_name", title: "Chore", width: "100px" },
  { field: "completed_by.email", title: "Completed By", width: "100px" },
]);
const pageChanged = data => {
  historystore.pageinfo.page = data.current_page;
};
</script>
<style>
.alt-pagination .bh-pagination .bh-page-item {
  background-color: #2196f3;
  color: white;
}
</style>
