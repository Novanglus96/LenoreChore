<template>
  <v-data-table-server
    :headers="headers"
    :items="historyItems ? historyItems.items : []"
    :items-length="historyItems ? historyItems.total_records : 0"
    :loading="isLoading"
    :items-per-page="historystore.pageinfo.page_size"
    :items-per-page-options="[{ value: 15, title: '15' }]"
    density="comfortable"
    fixed-header
    hover
    class="lc-history"
    no-data-text="Nothing completed yet."
    @update:options="pageChanged"
  >
    <template #item.completed_date="{ item }">
      <span class="lc-history__date">{{ item.completed_date }}</span>
    </template>

    <template #item.completed_by="{ item }">
      <!-- completed_by is Optional on HistoryItemOut: it goes null when the
           user who completed a chore is later deleted (SET_NULL). This used to
           read item.completed_by.fullname?.trim() -- the ?. guarded `fullname`,
           not `completed_by`, so a deleted household member threw
           "Cannot read properties of null" and took the whole table with it.
           The v1.4.1 hotfix fixed the backend half of exactly this; the
           frontend half was never done. -->
      <v-chip v-if="completedBy(item)" size="small" variant="tonal">
        {{ completedBy(item) }}
      </v-chip>
      <span v-else class="text-medium-emphasis text-caption">
        Deleted member
      </span>
    </template>
  </v-data-table-server>
</template>

<script setup>
import { useHistoryItems } from "@/composables/historyItemsComposable";
import { useHistoryItemsStore } from "@/stores/historyitems";

const historystore = useHistoryItemsStore();
const { historyItems, isLoading } = useHistoryItems();

const headers = [
  { title: "Date", key: "completed_date", width: "130px", sortable: false },
  { title: "Chore", key: "chore.chore_name", sortable: false },
  { title: "Completed by", key: "completed_by", width: "180px", sortable: false },
];

/**
 * The completer's display name, or null when there is no completer.
 * Optional-chained at every level, because both the user AND the name can be
 * absent independently.
 */
const completedBy = item => {
  const user = item?.completed_by;
  if (!user) return null;
  const full = user.fullname?.trim();
  return full || user.email || null;
};

const pageChanged = ({ page }) => {
  historystore.pageinfo.page = page;
};
</script>

<style scoped>
/* Was height="600px". A fixed pixel height leaves dead space on a tall screen
   and forces a second, nested scrollbar on a phone whose viewport is shorter
   than that. dvh tracks the mobile URL bar showing and hiding, which vh does
   not. */
.lc-history {
  --lc-history-max: min(70dvh, 720px);
}

.lc-history :deep(.v-table__wrapper) {
  max-height: var(--lc-history-max);
}

/* Was rgba(0, 0, 0, 0.09) — black at 9%, which is invisible against the dark
   theme's own dark surface. currentColor picks up the theme's text colour, so
   the banding works in both. */
.lc-history :deep(tbody tr:nth-child(odd)) {
  background-color: rgba(var(--v-theme-on-surface), 0.04);
}

.lc-history__date {
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
</style>
