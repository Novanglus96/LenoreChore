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

      <!-- The round. Only offered when the list has been narrowed to a single
           task, because "complete everything on screen" is a very different
           and much more dangerous button than "complete every Dust". -->
      <div v-if="!isLoading && roundOf" class="lc-round">
        <div class="min-width-0">
          <p class="text-subtitle-2 mb-0">Doing a round of {{ roundOf }}</p>
          <p class="text-caption text-medium-emphasis mb-0">
            {{ chores.length }}
            {{ chores.length === 1 ? "chore" : "chores" }}, across the areas it
            lives in.
          </p>
        </div>
        <v-spacer></v-spacer>
        <v-btn
          variant="flat"
          color="primary"
          prepend-icon="mdi-check-all"
          :loading="completingAll"
          @click="roundDialog = true"
        >
          Complete all
        </v-btn>
      </div>

      <LcConfirmDialog
        v-model="roundDialog"
        :title="`Complete all ${chores?.length ?? 0}?`"
        icon="mdi-check-all"
        confirm-label="Complete them"
        confirm-icon="mdi-check-all"
        confirm-color="primary"
        :busy="completingAll"
        @confirm="completeRound"
      >
        Marks every <strong>{{ roundOf }}</strong> on this list done today and
        rolls each one forward to its next due date. There is no undo.
      </LcConfirmDialog>

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
import LcConfirmDialog from "@/components/LcConfirmDialog.vue";
import { useChores } from "@/composables/choresComposasble";
import { useChoreStore } from "@/stores/chores";
import { useUserStore } from "@/stores/user";

const chorestore = useChoreStore();
const userstore = useUserStore();

const {
  chores,
  isLoading,
  completeAll,
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

// The task filter is what makes a bulk action safe to offer: it means every
// chore on screen is the same job in a different room.
const roundOf = computed(() =>
  chorestore.filters.chore_name && chores.value?.length
    ? chorestore.filters.chore_name
    : null
);

const roundDialog = ref(false);
const completingAll = ref(false);

const completeRound = async () => {
  if (completingAll.value) return;
  const ids = (chores.value ?? []).map(c => c.id);
  if (!ids.length) return;

  completingAll.value = true;
  // The same flag the single completion sets, so emptying the list this way
  // gets the same moment.
  completing = true;
  try {
    await completeAll({
      ids,
      lastCompleted: new Date().toISOString().split("T")[0],
      completed_by_id: userstore.getID,
    });
    roundDialog.value = false;
  } catch {
    // handleApiError has already said so; leave the dialog open.
  } finally {
    completingAll.value = false;
  }
};

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

<style scoped>
.lc-round {
  display: flex;
  align-items: center;
  gap: var(--lc-space-3);
  flex-wrap: wrap;
  padding: var(--lc-space-3) var(--lc-space-4);
  margin-bottom: var(--lc-space-3);
  border: 1px solid rgb(var(--v-theme-outline-variant));
  border-radius: var(--lc-radius-lg);
  background: rgb(var(--v-theme-surface));
}
</style>
