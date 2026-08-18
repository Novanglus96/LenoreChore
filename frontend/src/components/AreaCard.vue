<template>
  <v-card
    class="lc-area-card lc-lift"
    :class="{ 'lc-area-card--idle': !expandcard }"
    tag="article"
    :aria-label="cardLabel"
    :rounded="$vuetify.display.smAndDown ? 0 : 'lg'"
    :elevation="0"
    border
  >
    <!-- Group colour as identity, not as a surface. See ChoreCard. -->
    <div
      class="lc-area-card__stripe"
      :class="`bg-${props.area.group.group_color}`"
      aria-hidden="true"
    ></div>

    <div class="lc-area-card__body">
      <div class="d-flex align-center ga-3">
        <v-avatar
          size="44"
          class="lc-area-card__icon flex-shrink-0"
          :class="`text-${props.area.group.group_color}`"
          aria-hidden="true"
        >
          <v-icon :icon="props.area.area_icon" size="24"></v-icon>
        </v-avatar>

        <div class="flex-grow-1 min-width-0">
          <h2 class="text-h6 lc-area-card__title">{{ props.area.area_name }}</h2>
          <p class="text-caption text-medium-emphasis mb-0">
            {{ props.area.group.group_name }}
          </p>
        </div>

        <!-- The count is the headline number for an area, so it reads as one
             rather than as a sentence. The full phrasing is kept for screen
             readers, where "3 / 8" alone would be ambiguous. -->
        <div class="text-right flex-shrink-0">
          <div class="text-h6 font-weight-medium lh-1" aria-hidden="true">
            {{ props.area.dueCount }}<span class="text-medium-emphasis text-body-2">
              / {{ props.area.totalCount }}</span
            >
          </div>
          <div class="text-caption text-medium-emphasis" aria-hidden="true">
            due
          </div>
          <span class="lc-visually-hidden">
            {{ props.area.dueCount }} of {{ props.area.totalCount }} chores due
          </span>
        </div>
      </div>

      <div class="mt-3">
        <v-progress-linear
          v-if="!options?.vacation_mode"
          :model-value="dirtiness"
          :color="dirtBand.color"
          height="22"
          rounded
          :striped="dirtiness > 0"
          :aria-label="`${Math.ceil(dirtiness)} percent dirty, ${dirtBand.label}`"
        >
          <span class="text-caption font-weight-medium">
            {{ Math.ceil(dirtiness) }}% · {{ dirtBand.label }}
          </span>
        </v-progress-linear>

        <v-alert
          v-else
          type="info"
          density="compact"
          icon="mdi-island"
          text="Vacation mode — chores are paused."
        ></v-alert>
      </div>
    </div>
    <v-expand-transition>
      <div v-if="expandcard">
        <v-container>
          <v-row dense>
            <v-col>
              <!-- The activator slot destructured `props`, shadowing this
                   component's own `props` which the template uses throughout.
                   It happened to work, but any reference to props.area inside
                   the slot would have silently resolved to the activator
                   bindings instead. -->
              <v-dialog
                v-model="editcard"
                persistent
                :fullscreen="$vuetify.display.smAndDown"
                max-width="720"
              >
                <template v-slot:activator="{ props: activatorProps }">
                  <v-btn
                    v-bind="activatorProps"
                    icon="mdi-note-edit-outline"
                    :aria-label="`Edit ${props.area.area_name}`"
                  >
                    <v-icon icon="mdi-note-edit-outline"></v-icon>
                    <v-tooltip activator="parent" location="top">Edit</v-tooltip>
                  </v-btn>
                </template>
                <v-card>
                  <v-card-title>
                    <span class="text-h5">Edit Area</span>
                  </v-card-title>
                  <v-card-text>
                    <v-container>
                      <v-row>
                        <v-col cols="12" sm="6" md="4">
                          <v-text-field
                            label="Area name*"
                            required
                            v-model="editForm.area_name"
                          ></v-text-field>
                        </v-col>
                        <v-col cols="12">
                          <!-- Twenty chips, each previously containing only an
                               icon: identical, nameless options to a screen
                               reader, and the group itself had no label. Each
                               chip now carries a name derived from its own MDI
                               id, so the list cannot drift out of sync with
                               the icons it describes. -->
                          <div
                            id="area-icon-label"
                            class="text-body-2 mb-1"
                          >
                            Area icon
                          </div>
                          <v-chip-group
                            v-model="editForm.area_icon"
                            selected-class="text-primary"
                            aria-labelledby="area-icon-label"
                            column
                            mandatory
                          >
                            <v-chip
                              v-for="icon in chorestore.areaicons"
                              :key="icon"
                              :value="icon"
                              :aria-label="iconLabel(icon)"
                              :title="iconLabel(icon)"
                            >
                              <v-icon :icon="icon" aria-hidden="true"></v-icon>
                            </v-chip>
                          </v-chip-group>
                        </v-col>
                      </v-row>
                      <v-row>
                        <v-col cols="12" sm="6" md="4">
                          <v-select
                            label="Area Group"
                            :items="areagroups"
                            item-title="group_name"
                            item-value="id"
                            v-model="editForm.group_id"
                          >
                          </v-select>
                        </v-col>
                      </v-row>
                    </v-container>
                    <small>*indicates required field</small>
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn
                      color="blue-darken-1"
                      variant="text"
                      @click="editcard = false"
                    >
                      Close
                    </v-btn>
                    <v-btn
                      color="blue-darken-1"
                      variant="text"
                      @click="callEditArea(editForm)"
                    >
                      Save
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
              <v-dialog v-model="deletecard" persistent max-width="420">
                <template v-slot:activator="{ props: activatorProps }">
                  <v-btn
                    v-bind="activatorProps"
                    icon="mdi-delete-forever-outline"
                    color="filthy"
                    :aria-label="`Delete ${props.area.area_name}`"
                  >
                    <v-icon icon="mdi-delete-forever-outline"></v-icon>
                    <v-tooltip activator="parent" location="top">
                      Delete
                    </v-tooltip>
                  </v-btn>
                </template>
                <v-card>
                  <v-card-title class="text-h5">
                    Delete this Area?
                  </v-card-title>
                  <v-card-text
                    >Are you sure you want to delete
                    <span class="text-secondary">{{
                      props.area.area_name
                    }}</span
                    >? This will also delete
                    <span class="text-secondary">{{
                      props.area.totalCount
                    }}</span>
                    chores!</v-card-text
                  >
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn
                      color="primary-darken-1"
                      variant="text"
                      @click="deletecard = false"
                    >
                      Close
                    </v-btn>
                    <v-btn
                      color="primary-darken-1"
                      variant="text"
                      @click="callDeleteArea(area)"
                    >
                      Delete
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </v-col>
          </v-row>
        </v-container>
      </div>
    </v-expand-transition>
    <v-divider></v-divider>

    <v-card-actions class="lc-area-card__actions">
      <v-btn
        variant="tonal"
        size="small"
        prepend-icon="mdi-format-list-checks"
        :aria-label="`See chores in ${props.area.area_name}`"
        @click="setArea(props.area.id)"
      >
        See chores
      </v-btn>

      <v-spacer></v-spacer>

      <v-btn
        :icon="expandcard ? 'mdi-chevron-up' : 'mdi-chevron-down'"
        :aria-label="`${expandcard ? 'Close' : 'Open'} settings for ${props.area.area_name}`"
        :aria-expanded="expandcard ? 'true' : 'false'"
        @click="expandcard = !expandcard"
      >
        <v-icon
          :icon="expandcard ? 'mdi-chevron-up' : 'mdi-chevron-down'"
        ></v-icon>
        <v-tooltip activator="parent" location="top">
          {{ expandcard ? "Close settings" : "Area settings" }}
        </v-tooltip>
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
// defineProps/defineEmits are compiler macros; importing them warns on build.
import { ref, computed } from "vue";
import { useAreaGroups } from "@/composables/areaGroupsComposable";
import { useChoreStore } from "@/stores/chores";
import { useRouter } from "vue-router";
import { useOptions } from "@/composables/optionsComposable";
import { iconLabel } from "@/utils/labels";

const { options } = useOptions();
const router = useRouter();
const expandcard = ref(false);
const editcard = ref(false);
const deletecard = ref(false);
const chorestore = useChoreStore();
const emit = defineEmits(["editArea", "removeArea"]);
const props = defineProps({
  area: Object,
});
const dirtiness = computed(() => props.area.dirtiness || 0);
const editForm = ref({
  id: props.area.id || 0,
  area_name: props.area.area_name || "",
  group_id: props.area.group.id || 0,
  area_icon: props.area.area_icon || "",
});

const { areagroups } = useAreaGroups();

const setArea = async areaID => {
  chorestore.filters.area_id = areaID;
  router.push({ name: "list" });
};

const callDeleteArea = async deletedArea => {
  deletecard.value = false;
  emit("removeArea", deletedArea);
};
const callEditArea = async editArea => {
  editcard.value = false;
  emit("editArea", editArea);
};
// Same bands as ChoreCard: a colour AND a word, so the meaning does not depend
// on being able to tell the hues apart.
const dirtBand = computed(() => {
  const dirt = dirtiness.value;
  const med = options.value?.med_thresh ?? 49;
  const high = options.value?.high_thresh ?? 74;

  if (dirt <= med) return { color: "clean", label: "clean-ish" };
  if (dirt <= high) return { color: "soiled", label: "getting there" };
  return { color: "filthy", label: "filthy" };
});

const cardLabel = computed(
  () =>
    `${props.area.area_name}, ${props.area.group.group_name}, ` +
    `${props.area.dueCount} of ${props.area.totalCount} chores due, ` +
    `${Math.ceil(dirtiness.value)} percent dirty`
);
</script>

<style scoped>
.lc-area-card {
  position: relative;
  overflow: hidden;
  background: rgb(var(--v-theme-surface));
}

.lc-area-card__stripe {
  position: absolute;
  inset-block: 0;
  inset-inline-start: 0;
  width: 4px;
}

.lc-area-card__body {
  padding: var(--lc-space-4) var(--lc-space-4) var(--lc-space-3)
    calc(var(--lc-space-4) + 4px);
}

.lc-area-card__icon {
  background: rgb(var(--v-theme-surface-variant));
}

.lc-area-card__title {
  line-height: 1.25;
  overflow-wrap: anywhere;
}

.lh-1 {
  line-height: 1.1;
}

.min-width-0 {
  min-width: 0;
}

/* No hover lift while the settings panel is open — see ChoreCard. */
.lc-area-card:not(.lc-area-card--idle) {
  transform: none !important;
  box-shadow: none !important;
}

@media (max-width: 599px) {
  .lc-area-card__body {
    padding: var(--lc-space-3) var(--lc-space-3) var(--lc-space-2)
      calc(var(--lc-space-3) + 4px);
  }

  .lc-area-card__actions :deep(.v-btn--icon) {
    min-width: 44px;
    min-height: 44px;
  }
}
</style>
