<template>
  <div class="areas">
    <v-container :class="$vuetify.display.smAndDown ? 'pa-0' : ''">
      <h1 class="lc-visually-hidden">Dashboard</h1>

      <!-- Loading. Three skeletons rather than one, so the placeholder has the
           same shape as the grid it is standing in for and the layout does not
           jump when the data lands. -->
      <div v-if="isLoading" class="lc-card-grid" aria-hidden="true">
        <v-skeleton-loader
          v-for="n in 3"
          :key="n"
          type="article, actions"
        ></v-skeleton-loader>
      </div>

      <!-- One section per group. The API has always returned areas ordered by
           group__group_order, area_name; this view used to flatten that into a
           single grid and throw the grouping away. -->
      <template v-else-if="sections.length">
        <AreaGroupSection
          v-for="(section, index) in sections"
          :key="section.group.id ?? 'ungrouped'"
          :group="section.group"
          :areas="section.areas"
          :is-first="index === 0"
          :is-last="index === lastMovableIndex"
          :is-only-group="realGroupCount <= 1"
          :other-groups="otherGroups(section.group.id)"
          @edit-area="updateArea"
          @remove-area="deleteArea"
          @move="moveGroup"
          @remove="deleteGroup"
        />
      </template>

      <!-- Previously an empty screen with no explanation. -->
      <v-empty-state
        v-else
        icon="mdi-home-heart"
        title="No areas yet"
        text="Areas are the rooms and spaces you keep track of. Add one from the menu to get started."
      ></v-empty-state>
    </v-container>
  </div>
</template>

<script setup>
import { computed, watch } from "vue";
import AreaGroupSection from "@/components/AreaGroupSection.vue";
import { useAreas } from "@/composables/areasComposable";
import { useAreaGroups } from "@/composables/areaGroupsComposable";
import { useDashboardStore } from "@/stores/dashboard";

const { areas, isLoading: areasLoading, editArea, removeArea } = useAreas();
const {
  areagroups,
  isLoading: groupsLoading,
  editAreaGroup,
  removeAreaGroup,
} = useAreaGroups();
const dashboard = useDashboardStore();

// Both queries feed the sections, and they resolve independently. Waiting for
// both avoids a frame where the groups have not arrived and every area falls
// into the "No group" bucket.
const isLoading = computed(() => areasLoading.value || groupsLoading.value);

// A synthetic bucket, not a real group. AreaOut.group is Optional -- it matches
// a nullable column -- so an area can arrive with no group even though the
// delete endpoint now always reassigns. Without this it would simply vanish
// from the dashboard, which is worse than showing it plainly.
const UNGROUPED = {
  id: null,
  group_name: "No group",
  group_color: "outline",
  group_order: Number.MAX_SAFE_INTEGER,
};

const sortedGroups = computed(() =>
  [...(areagroups.value ?? [])].sort(
    (a, b) =>
      (a.group_order ?? 0) - (b.group_order ?? 0) ||
      a.group_name.localeCompare(b.group_name)
  )
);

const realGroupCount = computed(() => sortedGroups.value.length);

const sections = computed(() => {
  const byGroup = new Map();
  for (const area of areas.value ?? []) {
    const key = area.group?.id ?? null;
    if (!byGroup.has(key)) byGroup.set(key, []);
    byGroup.get(key).push(area);
  }

  // Every group gets a section, including empty ones: a group you just created
  // that renders as nothing looks broken rather than empty.
  const out = sortedGroups.value.map(group => ({
    group,
    areas: byGroup.get(group.id) ?? [],
  }));

  const orphans = byGroup.get(null);
  if (orphans?.length) out.push({ group: UNGROUPED, areas: orphans });

  return out;
});

// "Move down" must stop at the last REAL group; the ungrouped bucket is not
// reorderable because it is not a row in the database.
const lastMovableIndex = computed(() => {
  const realSections = sections.value.filter(s => s.group.id !== null);
  return realSections.length - 1;
});

const otherGroups = groupId =>
  sortedGroups.value.filter(g => g.id !== groupId);

// Collapsed ids outlive the groups they name, and Postgres reuses ids, so a
// stale entry could silently fold a future group.
watch(
  sortedGroups,
  groups => dashboard.prune(groups.map(g => g.id)),
  { immediate: true }
);

const updateArea = async updatedArea => {
  await editArea(updatedArea);
};

const deleteArea = async deletedArea => {
  await removeArea(deletedArea);
};

/**
 * Move a group one place up or down.
 *
 * This renumbers the affected rows 1..N rather than swapping two group_order
 * values, because a swap cannot reorder anything in an existing install: the
 * add form hardcoded group_order=1 on EVERY group it ever created, so they all
 * tie and exchanging two 1s is a no-op. Renumbering also repairs that legacy
 * state permanently the first time anyone reorders.
 *
 * Only rows whose order actually changes are written, so after that first
 * repair a move costs the same two writes a swap would have.
 */
const moveGroup = async (group, direction) => {
  const ordered = [...sortedGroups.value];
  const at = ordered.findIndex(g => g.id === group.id);
  const to = at + direction;
  if (at === -1 || to < 0 || to >= ordered.length) return;

  ordered.splice(to, 0, ordered.splice(at, 1)[0]);

  for (const [index, g] of ordered.entries()) {
    const desired = index + 1;
    if (g.group_order === desired) continue;
    await editAreaGroup({
      id: g.id,
      group_name: g.group_name,
      group_color: g.group_color,
      group_order: desired,
    });
  }
};

/**
 * @param payload `{ id, reassign_to }`
 * @param done called once the mutation settles, so the dialog can stop
 *   spinning whether it succeeded or not.
 */
const deleteGroup = async (payload, done) => {
  try {
    await removeAreaGroup(payload);
  } catch {
    // handleApiError has already surfaced it -- including the 400 the API
    // returns when this is the last group.
  } finally {
    done?.();
  }
};
</script>
