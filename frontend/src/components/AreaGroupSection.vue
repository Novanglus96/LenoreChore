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

      <!-- No spacer. The header is as wide as the container, so pushing this
           to the far right stranded it a long way from the group it acts on
           once the window got wide. It belongs with the name and the count. -->
      <LcActionMenu
        v-if="isRealGroup"
        :items="menuItems"
        :title="group.group_name"
        @select="onMenuSelect"
      >
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
      </LcActionMenu>
    </div>

    <div v-if="!expanded" class="lc-group__folded">
      <!-- A collapsed group still says how it is doing, or folding one away
           would mean losing sight of it entirely. -->
      <LcDirtBar
        :value="dirtiness"
        :height="6"
        :show-label="false"
        :label="group.group_name"
      />
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
import LcActionMenu from "@/components/LcActionMenu.vue";
import LcDirtBar from "@/components/LcDirtBar.vue";
import LcConfirmDialog from "@/components/LcConfirmDialog.vue";
import { useDashboardStore } from "@/stores/dashboard";
import { weightedDirtiness } from "@/utils/dirt";

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

const editOpen = ref(false);
const deleteOpen = ref(false);
const deleting = ref(false);
const reassignTo = ref(null);

const headingId = computed(() => `group-heading-${props.group.id ?? "none"}`);

// The "No group" bucket is synthetic -- there is no row behind it. Rename,
// reorder and delete all have nothing to act on, and delete would have sent
// DELETE /areagroups/null.
const isRealGroup = computed(() => props.group.id !== null);
const expanded = computed(() => !dashboard.isCollapsed(props.group.id));

const dueCount = computed(() =>
  props.areas.reduce((sum, a) => sum + (a.dueCount || 0), 0)
);
const totalCount = computed(() =>
  props.areas.reduce((sum, a) => sum + (a.totalCount || 0), 0)
);

// The same helper the dashboard's house reads, so a folded group's bar and the
// window standing for it cannot disagree.
const dirtiness = computed(() => weightedDirtiness(props.areas));

// Shared with the cards below, so the group's own actions reach a thumb the
// same way theirs do -- this was a v-menu, which on a phone opened wherever it
// could fit while every card underneath opened a bottom sheet.
const menuItems = computed(() => [
  { key: "edit", title: "Edit group…", icon: "mdi-pencil-outline" },
  {
    key: "up",
    title: "Move up",
    icon: "mdi-arrow-up",
    disabled: props.isFirst,
  },
  {
    key: "down",
    title: "Move down",
    icon: "mdi-arrow-down",
    disabled: props.isLast,
  },
  {
    key: "delete",
    title: "Delete group",
    icon: "mdi-delete-forever-outline",
    color: "filthy",
    dividerBefore: true,
    disabled: props.isOnlyGroup,
    subtitle: props.isOnlyGroup ? "The last group cannot be deleted" : undefined,
  },
]);

const onMenuSelect = key => {
  if (key === "edit") editOpen.value = true;
  else if (key === "up") emit("move", props.group, -1);
  else if (key === "down") emit("move", props.group, 1);
  else if (key === "delete") openDelete();
};

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
}
</style>
