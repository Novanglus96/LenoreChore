<template>
  <!-- The chores filter.
       ─────────────────────────────────────────────────────────────────────
       Was four naked v-selects in a row: no container, no visible heading, no
       result count, and a reset that was an unlabelled icon at the end of the
       line. Each select took flex: 1 1 200px, so on a wide monitor three
       dropdowns holding four, five and six items each stretched to a third of
       the screen. On a phone they wrapped into a four-row stack that pushed the
       chores themselves below the fold -- the least important thing on the page
       taking the most valuable space on it.

       It is one control now. The two or three questions people actually ask are
       one tap; everything else is behind a badged menu. -->
  <section aria-labelledby="chore-filters-label" class="lc-filters">
    <h2 id="chore-filters-label" class="lc-visually-hidden">Filter chores</h2>

    <div class="lc-filters__bar">
      <!-- Quick filters. "Is anything overdue" and "what's mine" are most of
           the real use, and neither was reachable at all before: the timeframe
           select had no overdue option, and assignee was a full user dropdown. -->
      <div class="lc-filters__quick" role="group" aria-label="Quick filters">
        <v-chip
          :variant="filters.overdue ? 'flat' : 'outlined'"
          :color="filters.overdue ? 'filthy' : undefined"
          :aria-pressed="filters.overdue ? 'true' : 'false'"
          size="small"
          @click="toggleOverdue"
        >
          <v-icon start size="14" icon="mdi-alert-circle-outline" aria-hidden="true"></v-icon>
          Overdue
        </v-chip>

        <v-chip
          v-if="currentUserId"
          :variant="isMine ? 'flat' : 'outlined'"
          :color="isMine ? 'primary' : undefined"
          :aria-pressed="isMine ? 'true' : 'false'"
          size="small"
          @click="toggleMine"
        >
          <v-icon start size="14" icon="mdi-account-outline" aria-hidden="true"></v-icon>
          Mine
        </v-chip>

        <v-chip
          :variant="isDueToday ? 'flat' : 'outlined'"
          :color="isDueToday ? 'primary' : undefined"
          :aria-pressed="isDueToday ? 'true' : 'false'"
          size="small"
          @click="toggleDueToday"
        >
          <v-icon start size="14" icon="mdi-calendar-today" aria-hidden="true"></v-icon>
          Due today
        </v-chip>
      </div>

      <v-divider vertical class="lc-filters__rule d-none d-sm-flex"></v-divider>

      <!-- Everything else. A menu on a pointer, a bottom sheet on a phone --
           dialog-bottom-transition is already the app's global dialog default. -->
      <v-btn
        variant="outlined"
        size="small"
        class="lc-filters__more"
        :aria-expanded="panelOpen ? 'true' : 'false'"
        @click="panelOpen = true"
      >
        <v-icon start icon="mdi-filter-variant" aria-hidden="true"></v-icon>
        Filters
        <v-badge
          v-if="advancedCount"
          :content="advancedCount"
          color="primary"
          inline
        ></v-badge>
      </v-btn>

      <v-menu>
        <template v-slot:activator="{ props: activatorProps }">
          <v-btn v-bind="activatorProps" variant="outlined" size="small">
            <v-icon start icon="mdi-sort" aria-hidden="true"></v-icon>
            {{ activeSort.label }}
            <v-icon end icon="mdi-menu-down" aria-hidden="true"></v-icon>
          </v-btn>
        </template>
        <v-list density="compact">
          <v-list-item
            v-for="option in SORTS"
            :key="option.value"
            :active="filters.sort === option.value"
            @click="filters.sort = option.value"
          >
            <v-list-item-title>{{ option.label }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>

      <v-spacer class="d-none d-sm-block"></v-spacer>

      <!-- Nothing used to say how many chores matched, or that a filter was on
           at all once you had scrolled past the bar. -->
      <span class="lc-filters__count text-caption text-medium-emphasis" aria-hidden="true">
        {{ loading ? "…" : countLabel }}
      </span>
      <span class="lc-visually-hidden" role="status" aria-live="polite">
        {{ loading ? "" : countLabel }}
      </span>
    </div>

    <!-- Active filters as individually removable chips. The old bar had a
         single all-or-nothing reset behind an unlabelled icon. -->
    <div v-if="activeChips.length" class="lc-filters__active">
      <v-chip
        v-for="chip in activeChips"
        :key="chip.key"
        size="small"
        variant="tonal"
        color="primary"
        closable
        :aria-label="`Remove filter: ${chip.label}`"
        :close-label="`Remove filter: ${chip.label}`"
        @click:close="chip.clear()"
      >
        {{ chip.label }}
      </v-chip>

      <v-btn variant="text" size="small" @click="resetFilters">
        Clear all
      </v-btn>
    </div>

    <!-- One set of controls, rendered into a sheet or a menu depending on the
         pointer. Sharing the markup is what stops the two drifting. -->
    <component
      :is="panelComponent"
      v-model="panelOpen"
      :max-width="display.smAndDown.value ? undefined : 420"
    >
      <v-card rounded="lg">
        <v-card-title class="d-flex align-center ga-2 text-subtitle-1 font-weight-medium">
          <v-icon icon="mdi-filter-variant" aria-hidden="true"></v-icon>
          Filter chores
        </v-card-title>
        <v-divider></v-divider>

        <v-card-text class="d-flex flex-column ga-3">
          <!-- Working one task through every room it exists in -- dusting,
               say. Listed first because it is a mode rather than a narrowing:
               it changes what you are looking at, not just how much of it.

               Only names carried by two or more active chores are offered; a
               one-off cannot be worked room by room. -->
          <div>
            <!-- Rendered even when there is nothing to pick. Hiding it made the
                 feature invisible in exactly the situation where someone would
                 go looking for it: a household whose chores all have distinct
                 names cannot tell whether this is missing, broken, or simply
                 not applicable yet. Disabled with a reason instead. -->
            <v-select
              v-model="filters.chore_name"
              label="One task, every area"
              :items="choreNames ?? []"
              item-title="chore_name"
              item-value="chore_name"
              prepend-inner-icon="mdi-repeat-variant"
              density="comfortable"
              hide-details
              clearable
              :disabled="!hasRepeatingTasks"
            >
              <template v-slot:item="{ props: itemProps, item }">
                <v-list-item
                  v-bind="itemProps"
                  :subtitle="`in ${item.raw.area_count} ${
                    item.raw.area_count === 1 ? 'area' : 'areas'
                  }`"
                ></v-list-item>
              </template>
            </v-select>

            <p
              v-if="!hasRepeatingTasks"
              class="text-caption text-medium-emphasis mt-1 mb-0"
            >
              Give the same chore the same name in more than one area — a
              &ldquo;Dust&rdquo; in each room — and it shows up here so you can
              work through all of them at once.
            </p>
          </div>

          <v-divider class="my-1"></v-divider>

          <v-select
            v-model="filters.group_id"
            label="Group"
            :items="areagroups ?? []"
            item-title="group_name"
            item-value="id"
            density="comfortable"
            hide-details
            clearable
          ></v-select>

          <!-- Narrowed by the chosen group. With twenty areas, an unfiltered
               list of every one of them is the thing that makes this control
               unusable. -->
          <v-select
            v-model="filters.area_id"
            :label="filters.group_id ? 'Area in this group' : 'Area'"
            :items="areasInGroup"
            item-title="area_name"
            item-value="id"
            density="comfortable"
            hide-details
            clearable
          ></v-select>

          <v-select
            v-model="filters.assignee_id"
            label="Assignee"
            :items="users"
            item-title="displayName"
            item-value="id"
            density="comfortable"
            hide-details
            clearable
          ></v-select>

          <v-select
            v-model="filters.timeframe"
            label="Due within"
            :items="dayFilter"
            item-title="name"
            item-value="days"
            density="comfortable"
            hide-details
            clearable
          ></v-select>

          <v-checkbox
            v-model="filters.inactive"
            label="Show disabled chores"
            density="compact"
            hide-details
          ></v-checkbox>
        </v-card-text>

        <v-divider></v-divider>
        <v-card-actions>
          <v-btn variant="text" :disabled="!hasActiveFilters" @click="resetFilters">
            Clear all
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn variant="flat" color="primary" @click="panelOpen = false">
            {{ loading ? "Show results" : `Show ${count}` }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </component>
  </section>
</template>

<script setup>
// defineProps is a compiler macro.
import { computed, ref } from "vue";
import { useDisplay } from "vuetify";
// Imported rather than named as strings in :is. Vuetify registers its
// components globally, so strings happen to resolve -- but they resolve at
// render time with no build-time check, so a rename fails silently at runtime.
import { VBottomSheet, VDialog } from "vuetify/components";
import { useChoreStore } from "@/stores/chores";
import { useUserStore } from "@/stores/user";
import { useAreas } from "@/composables/areasComposable";
import { useAreaGroups } from "@/composables/areaGroupsComposable";
import { useUsers } from "@/composables/usersComposable";
import { useChoreNames } from "@/composables/choresComposasble";

const props = defineProps({
  /** How many chores the current filters matched. */
  count: { type: Number, default: 0 },
  loading: { type: Boolean, default: false },
});

const SORTS = [
  { value: "due", label: "Due date" },
  { value: "dirtiest", label: "Dirtiest" },
  { value: "effort", label: "Least effort" },
  { value: "name", label: "Name" },
];

const display = useDisplay();
const chorestore = useChoreStore();
const userstore = useUserStore();
const { areas } = useAreas();
const { areagroups } = useAreaGroups();
const { users: rawUsers } = useUsers();
const { choreNames } = useChoreNames();

// Nothing repeats across areas yet, so there is nothing to filter to. The
// control still renders -- see the template -- but says why it is inert.
const hasRepeatingTasks = computed(() => (choreNames.value ?? []).length > 0);

const filters = chorestore.filters;
const panelOpen = ref(false);

// A sheet rises from the bottom of a phone where a centred dialog fights the
// thumb; dialog-bottom-transition is already the app's global dialog default.
const panelComponent = computed(() =>
  display.smAndDown.value ? VBottomSheet : VDialog
);

const dayFilter = computed(() => chorestore.getDayFilter);
const currentUserId = computed(() => userstore.getID);

const users = computed(() =>
  (rawUsers.value ?? []).map(user => ({
    ...user,
    displayName:
      !user.fullname || user.fullname.trim() === "" ? user.email : user.fullname,
  }))
);

// Areas belonging to the selected group, so choosing a group makes the area
// list answerable rather than a list of everything.
const areasInGroup = computed(() => {
  const all = areas.value ?? [];
  if (!filters.group_id) return all;
  return all.filter(area => area.group?.id === filters.group_id);
});

const activeSort = computed(
  () => SORTS.find(s => s.value === filters.sort) ?? SORTS[0]
);

const isMine = computed(
  () => currentUserId.value != null && filters.assignee_id === currentUserId.value
);
const isDueToday = computed(() => filters.timeframe === 0);

const countLabel = computed(
  () => `${props.count} ${props.count === 1 ? "chore" : "chores"}`
);

const toggleOverdue = () => {
  filters.overdue = !filters.overdue;
};

const toggleMine = () => {
  filters.assignee_id = isMine.value ? null : currentUserId.value;
};

const toggleDueToday = () => {
  filters.timeframe = isDueToday.value ? null : 0;
};

// Only the ones behind the Filters button, so the badge counts what the button
// hides rather than what is already visible as a chip.
const advancedCount = computed(() => {
  let n = 0;
  if (filters.chore_name) n++;
  if (filters.group_id != null) n++;
  if (filters.area_id != null) n++;
  if (filters.assignee_id != null) n++;
  if (filters.timeframe != null) n++;
  if (filters.inactive === true) n++;
  return n;
});

// `sort` is deliberately excluded: sorting is not filtering, and counting it
// would leave "Clear all" permanently enabled.
const hasActiveFilters = computed(
  () => advancedCount.value > 0 || filters.overdue === true
);

const nameOf = (list, id, key) =>
  (list.value ?? []).find(item => item.id === id)?.[key] ?? "";

const activeChips = computed(() => {
  const chips = [];
  if (filters.chore_name) {
    chips.push({
      key: "chore_name",
      label: `Task: ${filters.chore_name}`,
      clear: () => (filters.chore_name = null),
    });
  }
  if (filters.overdue) {
    chips.push({
      key: "overdue",
      label: "Overdue",
      clear: () => (filters.overdue = false),
    });
  }
  if (filters.group_id != null) {
    chips.push({
      key: "group",
      label: `Group: ${nameOf(areagroups, filters.group_id, "group_name")}`,
      clear: () => {
        filters.group_id = null;
        // The area filter may no longer be reachable from the visible list, so
        // leaving it set would filter by something the UI no longer offers.
        filters.area_id = null;
      },
    });
  }
  if (filters.area_id != null) {
    chips.push({
      key: "area",
      label: `Area: ${nameOf(areas, filters.area_id, "area_name")}`,
      clear: () => (filters.area_id = null),
    });
  }
  if (filters.assignee_id != null) {
    const who = isMine.value
      ? "you"
      : users.value.find(u => u.id === filters.assignee_id)?.displayName ?? "";
    chips.push({
      key: "assignee",
      label: `Assignee: ${who}`,
      clear: () => (filters.assignee_id = null),
    });
  }
  if (filters.timeframe != null) {
    const named = dayFilter.value.find(d => d.days === filters.timeframe);
    chips.push({
      key: "timeframe",
      label: named ? named.name : `Due within ${filters.timeframe} days`,
      clear: () => (filters.timeframe = null),
    });
  }
  if (filters.inactive) {
    chips.push({
      key: "inactive",
      label: "Including disabled",
      clear: () => (filters.inactive = false),
    });
  }
  return chips;
});

const resetFilters = () => {
  filters.chore_name = null;
  filters.area_id = null;
  filters.group_id = null;
  filters.timeframe = null;
  filters.assignee_id = null;
  filters.overdue = false;
  filters.inactive = false;
  // sort is not reset: it is a view preference, not a filter, and silently
  // reordering the list on "Clear all" would be a surprise.
};

defineExpose({ hasActiveFilters, resetFilters });
</script>

<style scoped>
.lc-filters {
  /* Sticky under the app bar, so the count and the clear stay reachable in a
     long list instead of scrolling away with the controls. */
  position: sticky;
  top: 0;
  z-index: 2;
  background: rgb(var(--v-theme-background));
  padding-block: var(--lc-space-2);
  margin-bottom: var(--lc-space-2);
}

.lc-filters__bar {
  display: flex;
  align-items: center;
  gap: var(--lc-space-2);
  flex-wrap: wrap;
  background: rgb(var(--v-theme-surface));
  border: 1px solid rgb(var(--v-theme-outline-variant));
  border-radius: var(--lc-radius-pill);
  padding: var(--lc-space-2) var(--lc-space-3);
}

.lc-filters__quick {
  display: flex;
  align-items: center;
  gap: var(--lc-space-2);
  /* On a narrow screen the quick chips scroll rather than wrapping the whole
     bar into a second row. */
  overflow-x: auto;
  scrollbar-width: none;
}

.lc-filters__quick::-webkit-scrollbar {
  display: none;
}

.lc-filters__rule {
  height: 22px;
  align-self: center;
}

.lc-filters__count {
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  margin-inline-start: auto;
}

.lc-filters__active {
  display: flex;
  align-items: center;
  gap: var(--lc-space-2);
  flex-wrap: wrap;
  padding: var(--lc-space-2) var(--lc-space-3) 0;
}

@media (max-width: 599px) {
  .lc-filters__bar {
    border-radius: var(--lc-radius-lg);
    padding: var(--lc-space-2);
  }

  .lc-filters__more {
    flex-shrink: 0;
  }
}
</style>
