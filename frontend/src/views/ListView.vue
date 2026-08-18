<template>
  <div class="chores">
    <v-container :class="$vuetify.display.smAndDown ? 'px-0 pt-2' : ''">
      <h1 class="lc-visually-hidden">Chores</h1>

      <!-- Filters are a labelled group, so a screen reader announces what this
           cluster of controls is for rather than reading four loose inputs. -->
      <section aria-labelledby="chore-filters-label" class="mb-3">
        <h2 id="chore-filters-label" class="lc-visually-hidden">Filter chores</h2>
        <div class="lc-filter-bar">
          <v-select
            v-model="chorestore.filters.area_id"
            label="Area"
            :items="areas"
            item-title="area_name"
            item-value="id"
            density="compact"
            hide-details
            clearable
          ></v-select>

          <v-select
            v-model="chorestore.filters.timeframe"
            label="Due within"
            :items="chorestore.getDayFilter"
            item-title="name"
            item-value="days"
            density="compact"
            hide-details
            clearable
          ></v-select>

          <v-select
            v-model="chorestore.filters.assignee_id"
            label="Assignee"
            :items="computedUsers"
            item-title="displayName"
            item-value="id"
            density="compact"
            hide-details
            clearable
          ></v-select>

          <v-checkbox
            v-model="chorestore.filters.inactive"
            label="Show disabled"
            density="compact"
            hide-details
          ></v-checkbox>

          <v-btn
            icon="mdi-filter-off"
            variant="text"
            size="small"
            aria-label="Clear all filters"
            :disabled="!hasActiveFilters"
            @click="resetFilter()"
          >
            <v-icon icon="mdi-filter-off"></v-icon>
            <v-tooltip activator="parent" location="top">
              Clear filters
            </v-tooltip>
          </v-btn>
        </div>
      </section>

      <div v-if="isLoading" class="lc-card-grid" aria-hidden="true">
        <v-skeleton-loader
          v-for="n in 3"
          :key="n"
          type="article, actions"
        ></v-skeleton-loader>
      </div>

      <div v-else-if="chores && chores.length" class="lc-card-grid">
        <ChoreCard
          v-for="chore in chores"
          :chore="chore"
          :key="chore.id"
          @edit-chore="updateChore"
          @remove-chore="deleteChore"
          @complete-chore="completeChore"
          @snooze-chore="snoozeChore"
          @claim-chore="claimChore"
          @toggle-activation="toggleChore"
        />
      </div>

      <!-- Two distinct empty states. "Nothing matches your filters" and "there
           are no chores at all" look identical on screen but need opposite
           actions, and the old view rendered nothing for either. -->
      <v-empty-state
        v-else-if="hasActiveFilters"
        icon="mdi-filter-remove-outline"
        title="Nothing matches those filters"
        text="Try widening the search — or clear the filters to see everything."
      >
        <template v-slot:actions>
          <v-btn variant="tonal" prepend-icon="mdi-filter-off" @click="resetFilter()">
            Clear filters
          </v-btn>
        </template>
      </v-empty-state>

      <v-empty-state
        v-else
        icon="mdi-party-popper"
        title="Nothing needs doing"
        text="Every chore is done and dusted. Enjoy it while it lasts."
      ></v-empty-state>
    </v-container>
  </div>
</template>

<script setup>
import ChoreCard from "@/components/ChoreCard.vue";
import { useChores } from "@/composables/choresComposasble";
import { useChoreStore } from "@/stores/chores";
import { useAreas } from "@/composables/areasComposable";
import { useUsers } from "@/composables/usersComposable";
import { computed } from "vue";

const chorestore = useChoreStore();
const { areas } = useAreas();
const { users } = useUsers();
const {
  chores,
  isLoading,
  editChore,
  removeChore,
  snooze,
  complete,
  toggle,
  claim,
} = useChores();

const updateChore = async updatedChore => {
  await editChore(updatedChore);
};

const completeChore = async (chore_id, user_id) => {
  let today = new Date();
  let formattedDate = today.toISOString().split("T")[0];
  let choredata = {
    id: chore_id,
    lastCompleted: formattedDate,
    completed_by_id: user_id,
  };
  await complete(choredata);
};

const snoozeChore = async (chore_id, next_due) => {
  let data = {
    id: chore_id,
    nextDue: next_due,
  };
  await snooze(data);
};

const claimChore = async (chore_id, user_id) => {
  let data = {
    id: chore_id,
    assignee_id: user_id,
  };
  await claim(data);
};
// Drives both the reset button's disabled state and which empty state shows.
// `inactive` is a boolean whose falsy default is "off", so it is compared
// explicitly rather than lumped in with the null-able ids.
const hasActiveFilters = computed(
  () =>
    chorestore.filters.area_id != null ||
    chorestore.filters.timeframe != null ||
    chorestore.filters.assignee_id != null ||
    chorestore.filters.inactive === true
);

const resetFilter = async () => {
  chorestore.filters.area_id = null;
  chorestore.filters.timeframe = null;
  chorestore.filters.inactive = false;
  chorestore.filters.assignee_id = null;
};
const toggleChore = async (chore_id, active) => {
  let newStatus = 0;
  if (active == 0) {
    newStatus = 1;
  }
  if (active == 1) {
    newStatus = 0;
  }
  if (active == 2) {
    newStatus = 0;
  }
  let data = {
    id: chore_id,
    status: newStatus,
  };
  await toggle(data);
};

const deleteChore = async deletedChore => {
  await removeChore(deletedChore);
};

const computedUsers = computed(() => {
  if (!users.value) {
    return [];
  }
  return users.value.map(item => ({
    ...item,
    displayName:
      !item.fullname || item.fullname.trim() === ""
        ? item.email
        : item.fullname,
  }));
});
</script>

<style scoped>
/* Wraps instead of a fixed 7/4/1 column split, which squeezed the selects on a
   phone and stranded them at a third of the width on a desktop. */
.lc-filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--lc-space-3);
  padding-inline: var(--lc-space-3);
}

.lc-filter-bar > .v-select {
  flex: 1 1 200px;
  min-width: 0;
}

@media (min-width: 600px) {
  .lc-filter-bar {
    padding-inline: 0;
  }
}
</style>
