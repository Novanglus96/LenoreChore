<template>
  <div class="chores">
    <v-container :class="$vuetify.display.smAndDown ? 'px-2 pt-2' : ''">
      <h1 class="lc-visually-hidden">Chores</h1>

      <!-- The whole filter is one component now. This view used to inline four
           v-selects, a checkbox and a reset button, plus the reset logic and
           the assignee name-mapping. -->
      <ChoreFilterBar
        ref="filterBar"
        :count="chores?.length ?? 0"
        :loading="isLoading"
      />

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
           actions. -->
      <v-empty-state
        v-else-if="hasActiveFilters"
        icon="mdi-filter-remove-outline"
        title="Nothing matches those filters"
        text="Try widening the search — or clear the filters to see everything."
      >
        <template v-slot:actions>
          <v-btn
            variant="tonal"
            prepend-icon="mdi-filter-off"
            @click="clearFilters"
          >
            Clear filters
          </v-btn>
        </template>
      </v-empty-state>

      <!-- The last one. Celebrated only when a completion is what emptied the
           list: arriving at an already-empty list is not an achievement, and
           cheering it would cheapen the times it is. -->
      <v-empty-state
        v-else
        :class="{ 'lc-cleared': justCleared }"
        icon="mdi-party-popper"
        :title="justCleared ? 'That was the last one' : 'Nothing needs doing'"
        :text="
          justCleared
            ? 'The whole list is clear. Go and enjoy it.'
            : 'Every chore is done and dusted. Enjoy it while it lasts.'
        "
      ></v-empty-state>
    </v-container>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import ChoreCard from "@/components/ChoreCard.vue";
import ChoreFilterBar from "@/components/ChoreFilterBar.vue";
import { useChores } from "@/composables/choresComposasble";

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

// The bar owns what "filtered" means, so the empty state and its action ask it
// rather than keeping a second copy of the rule that drifts from the first.
const filterBar = ref(null);
const hasActiveFilters = computed(
  () => filterBar.value?.hasActiveFilters ?? false
);
const clearFilters = () => filterBar.value?.resetFilters();

// True only when a completion is what took the list to zero.
const justCleared = ref(false);
// Not a ref: nothing renders from it, and it is read inside a watcher that
// runs before the awaited mutation settles.
let completing = false;

watch(
  () => chores.value?.length ?? 0,
  (now, before) => {
    // The parent's optimistic update removes the chore the instant the
    // mutation starts, so this fires well before the request resolves.
    if (completing && now === 0 && before > 0) justCleared.value = true;
    if (now > 0) justCleared.value = false;
    if (now === 0) completing = false;
  }
);

const updateChore = async updatedChore => {
  await editChore(updatedChore);
};

const completeChore = async (chore_id, user_id) => {
  // Set before the call: the optimistic removal happens synchronously inside
  // the mutation, so setting it afterwards would always be too late.
  completing = true;
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
</script>
