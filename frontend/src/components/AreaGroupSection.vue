<template>
  <!-- One dashboard section per area group.
       ─────────────────────────────────────────────────────────────────────
       AreaGroup existed to group areas logically and never did: /areas already
       orders by group__group_order, area_name, and DashView flattened that into
       a single grid, discarding the structure entirely. The group survived only
       as a stripe colour and a subtitle.

       This is also the only place a group can be managed. Rename, recolour,
       reorder and delete all live on the header, so management sits on the
       thing being managed rather than behind a settings screen nobody visits. -->
  <section class="lc-group" :aria-labelledby="headingId">
    <div class="lc-group__header">
      <v-btn
        class="lc-group__toggle"
        variant="text"
        :aria-expanded="expanded ? 'true' : 'false'"
        :aria-label="`${expanded ? 'Collapse' : 'Expand'} ${group.group_name}`"
        @click="dashboard.toggleGroup(group.id)"
      >
        <v-icon
          :icon="expanded ? 'mdi-chevron-down' : 'mdi-chevron-right'"
          size="20"
          aria-hidden="true"
        ></v-icon>
        <v-icon
          icon="mdi-circle"
          size="12"
          class="ml-1 mr-2"
          :color="group.group_color"
          aria-hidden="true"
        ></v-icon>
        <h2 :id="headingId" class="lc-group__name text-subtitle-1 font-weight-medium">
          {{ group.group_name }}
        </h2>
      </v-btn>

      <!-- The aggregate is the point of grouping: it answers "how is upstairs
           doing" without reading four cards. Spoken as a sentence, shown as a
           number. -->
      <span class="lc-group__count text-caption text-medium-emphasis" aria-hidden="true">
        {{ dueCount }} / {{ totalCount }} due
      </span>
      <span class="lc-visually-hidden">
        {{ dueCount }} of {{ totalCount }} chores due in {{ group.group_name }}
      </span>

      <v-spacer></v-spacer>

      <v-menu>
        <template v-slot:activator="{ props: activatorProps }">
          <v-btn
            v-bind="activatorProps"
            icon="mdi-dots-vertical"
            size="small"
            variant="text"
            :aria-label="`Manage ${group.group_name}`"
          >
            <v-icon icon="mdi-dots-vertical"></v-icon>
          </v-btn>
        </template>
        <v-list density="compact">
          <v-list-item prepend-icon="mdi-pencil-outline" @click="editOpen = true">
            <v-list-item-title>Edit group</v-list-item-title>
          </v-list-item>
          <v-list-item
            prepend-icon="mdi-arrow-up"
            :disabled="isFirst"
            @click="emit('move', group, -1)"
          >
            <v-list-item-title>Move up</v-list-item-title>
          </v-list-item>
          <v-list-item
            prepend-icon="mdi-arrow-down"
            :disabled="isLast"
            @click="emit('move', group, 1)"
          >
            <v-list-item-title>Move down</v-list-item-title>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item
            prepend-icon="mdi-delete-forever-outline"
            base-color="filthy"
            :disabled="isOnlyGroup"
            @click="openDelete"
          >
            <v-list-item-title>Delete group</v-list-item-title>
            <v-list-item-subtitle v-if="isOnlyGroup">
              The last group cannot be deleted
            </v-list-item-subtitle>
          </v-list-item>
        </v-list>
      </v-menu>
    </div>

    <div v-if="!expanded" class="lc-group__folded">
      <!-- A collapsed group still says how it is doing, or folding one away
           would mean losing sight of it entirely. -->
      <v-progress-linear
        :model-value="dirtiness"
        :color="dirtBand.color"
        height="6"
        rounded
        :aria-label="`${group.group_name}: ${dirtiness} percent dirty, ${dirtBand.label}`"
      ></v-progress-linear>
    </div>

    <v-expand-transition>
      <div v-if="expanded">
        <div v-if="areas.length" class="lc-card-grid">
          <AreaCard
            v-for="area in areas"
            :key="area.id"
            :area="area"
            @edit-area="(a) => emit('editArea', a)"
            @remove-area="(a) => emit('removeArea', a)"
          />
        </div>

        <!-- A group you just created renders as nothing without this, which
             looks broken rather than empty. -->
        <p v-else class="lc-group__empty text-body-2 text-medium-emphasis">
          No areas in this group yet.
        </p>
      </div>
    </v-expand-transition>

    <AreaGroupForm
      v-model="editOpen"
      :group="group"
      @saved="editOpen = false"
    />

    <LcConfirmDialog
      v-model="deleteOpen"
      title="Delete this group?"
      icon="mdi-delete-forever-outline"
      confirm-label="Delete group"
      confirm-icon="mdi-delete-forever-outline"
      :busy="deleting"
      @confirm="confirmDelete"
    >
      <template v-if="areas.length">
        <p class="mb-3">
          <strong>{{ group.group_name }}</strong> holds
          {{ areas.length }} {{ areas.length === 1 ? "area" : "areas" }}. They
          will move to the group you pick — nothing is deleted with it.
        </p>
        <!-- The API defaults to the lowest-ordered remaining group, but
             defaulting silently is how the old behaviour moved people's areas
             without telling them. -->
        <v-select
          v-model="reassignTo"
          label="Move its areas to"
          :items="otherGroups"
          item-title="group_name"
          item-value="id"
          hide-details
        ></v-select>
      </template>
      <template v-else>
        <strong>{{ group.group_name }}</strong> is empty, so nothing moves.
      </template>
    </LcConfirmDialog>
  </section>
</template>

<script setup>
// defineProps/defineEmits are compiler macros.
import { computed, ref } from "vue";
import AreaCard from "@/components/AreaCard.vue";
import AreaGroupForm from "@/components/AreaGroupForm.vue";
import LcConfirmDialog from "@/components/LcConfirmDialog.vue";
import { useDashboardStore } from "@/stores/dashboard";
import { useOptions } from "@/composables/optionsComposable";

const props = defineProps({
  group: { type: Object, required: true },
  areas: { type: Array, default: () => [] },
  isFirst: { type: Boolean, default: false },
  isLast: { type: Boolean, default: false },
  isOnlyGroup: { type: Boolean, default: false },
  /** Every other group, for the delete dialog's destination picker. */
  otherGroups: { type: Array, default: () => [] },
});

const emit = defineEmits(["editArea", "removeArea", "move", "remove"]);

const dashboard = useDashboardStore();
const { options } = useOptions();

const editOpen = ref(false);
const deleteOpen = ref(false);
const deleting = ref(false);
const reassignTo = ref(null);

const headingId = computed(() => `group-heading-${props.group.id}`);
const expanded = computed(() => !dashboard.isCollapsed(props.group.id));

const dueCount = computed(() =>
  props.areas.reduce((sum, a) => sum + (a.dueCount || 0), 0)
);
const totalCount = computed(() =>
  props.areas.reduce((sum, a) => sum + (a.totalCount || 0), 0)
);

// Chore-weighted, not a mean of means: total_dirtiness is the SUM of chore
// dirtiness and totalCount the chore count, so dividing the sums gives the same
// answer an area with all these chores in it would report. Averaging each
// area's percentage would let a one-chore area outvote a twenty-chore one.
const dirtiness = computed(() => {
  const chores = totalCount.value;
  if (!chores) return 0;
  const total = props.areas.reduce(
    (sum, a) => sum + (a.total_dirtiness || 0),
    0
  );
  return Math.min(100, Math.round(total / chores));
});

// Same bands as ChoreCard and AreaCard, and the same reason: a word as well as
// a colour.
const dirtBand = computed(() => {
  const med = options.value?.med_thresh ?? 49;
  const high = options.value?.high_thresh ?? 74;
  if (dirtiness.value <= med) return { color: "clean", label: "clean-ish" };
  if (dirtiness.value <= high) return { color: "soiled", label: "getting there" };
  return { color: "filthy", label: "filthy" };
});

const openDelete = () => {
  // Pre-select the same destination the API would choose, so the field shows
  // what will happen rather than sitting empty.
  reassignTo.value = props.otherGroups[0]?.id ?? null;
  deleteOpen.value = true;
};

const confirmDelete = async () => {
  if (deleting.value) return;
  deleting.value = true;
  try {
    await new Promise(resolve => {
      emit("remove", { id: props.group.id, reassign_to: reassignTo.value }, resolve);
    });
    deleteOpen.value = false;
  } finally {
    deleting.value = false;
  }
};
</script>

<style scoped>
.lc-group + .lc-group {
  margin-top: var(--lc-space-5);
}

.lc-group__header {
  display: flex;
  align-items: center;
  gap: var(--lc-space-2);
  padding-inline: var(--lc-space-2);
  margin-bottom: var(--lc-space-2);
}

/* The whole name+chevron+dot cluster is one control, so the hit area matches
   what reads as clickable rather than being a chevron alone. */
.lc-group__toggle {
  padding-inline: var(--lc-space-2);
  min-width: 0;
  text-transform: none;
  letter-spacing: normal;
}

.lc-group__name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.lc-group__count {
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.lc-group__folded {
  padding: 0 var(--lc-space-4) var(--lc-space-1);
}

.lc-group__empty {
  padding: var(--lc-space-3) var(--lc-space-4);
  margin: 0;
}

@media (max-width: 599px) {
  .lc-group__header {
    padding-inline: var(--lc-space-1);
  }

  .lc-group__header :deep(.v-btn--icon) {
    min-width: 44px;
    min-height: 44px;
  }
}
</style>
