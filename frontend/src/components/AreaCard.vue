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
      :class="`bg-${groupColor}`"
      aria-hidden="true"
    ></div>

    <div class="lc-area-card__body">
      <div class="d-flex align-center ga-3">
        <v-avatar
          size="44"
          class="lc-area-card__icon flex-shrink-0"
          :class="`text-${groupColor}`"
          aria-hidden="true"
        >
          <v-icon :icon="props.area.area_icon" size="24"></v-icon>
        </v-avatar>

        <div class="flex-grow-1 min-width-0">
          <h2 class="text-h6 lc-area-card__title">{{ props.area.area_name }}</h2>
          <p class="text-caption text-medium-emphasis mb-0">
            {{ groupName }}
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
        <div class="lc-area-card__panel">
          <!-- Both dialogs were hand-rolled copies of the same stock markup:
               a v-container/v-row/v-col grid inside a width="720" surface,
               color="blue-darken-1" buttons, and -- on the delete -- "Close"
               and "Delete" BOTH rendered as primary-darken-1 text, so the
               irreversible action looked exactly like the way out. They use the
               shared shells now. -->
          <LcFormDialog
            v-model="editcard"
            title="Edit area"
            icon="mdi-note-edit-outline"
            submit-label="Save changes"
            submit-icon="mdi-content-save-outline"
            :schema="editSchema"
            :initial-values="{ area_name: props.area.area_name }"
            @submit="callEditArea"
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

            <fieldset class="lc-fieldset lc-form-group">
              <legend class="lc-form-group__legend text-body-2">What</legend>

              <!-- Was a plain v-model with `required` and no schema, so an
                   empty area name saved happily. -->
              <Field name="area_name" v-slot="{ field, errorMessage }">
                <v-text-field
                  v-bind="field"
                  label="Area name"
                  prepend-inner-icon="mdi-format-title"
                  :error-messages="errorMessage"
                ></v-text-field>
              </Field>

              <v-select
                v-model="editForm.group_id"
                label="Area group"
                prepend-inner-icon="mdi-shape-outline"
                :items="areagroups"
                item-title="group_name"
                item-value="id"
              ></v-select>
            </fieldset>

            <v-divider class="my-4"></v-divider>

            <fieldset class="lc-fieldset">
              <!-- Each chip now carries a name derived from its own MDI id, so
                   the list cannot drift out of sync with the icons it
                   describes. -->
              <legend class="lc-form-group__legend text-body-2">Area icon</legend>
              <v-chip-group
                v-model="editForm.area_icon"
                selected-class="text-primary"
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
            </fieldset>
          </LcFormDialog>

          <LcConfirmDialog
            v-model="deletecard"
            title="Delete this area?"
            icon="mdi-delete-forever-outline"
            confirm-label="Delete area"
            confirm-icon="mdi-delete-forever-outline"
            @confirm="callDeleteArea(props.area)"
          >
            <template v-slot:activator="{ props: activatorProps }">
              <v-btn
                v-bind="activatorProps"
                icon="mdi-delete-forever-outline"
                color="filthy"
                :aria-label="`Delete ${props.area.area_name}`"
              >
                <v-icon icon="mdi-delete-forever-outline"></v-icon>
                <v-tooltip activator="parent" location="top">Delete</v-tooltip>
              </v-btn>
            </template>

            Deleting <strong>{{ props.area.area_name }}</strong> also deletes
            the
            <strong>{{ props.area.totalCount }}</strong>
            {{ props.area.totalCount === 1 ? "chore" : "chores" }} in it. This
            cannot be undone.
          </LcConfirmDialog>
        </div>
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
import { Field } from "vee-validate";
import * as yup from "yup";
import { useAreaGroups } from "@/composables/areaGroupsComposable";
import { useChoreStore } from "@/stores/chores";
import { useRouter } from "vue-router";
import { useOptions } from "@/composables/optionsComposable";
import { iconLabel } from "@/utils/labels";
import LcFormDialog from "@/components/LcFormDialog.vue";
import LcConfirmDialog from "@/components/LcConfirmDialog.vue";

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

// See ChoreCard: AreaOut.group is Optional now, so it has to be read as such.
const groupColor = computed(() => props.area.group?.group_color || "outline");
const groupName = computed(() => props.area.group?.group_name || "no group");
const editForm = ref({
  id: props.area.id || 0,
  area_name: props.area.area_name || "",
  group_id: props.area.group?.id || null,
  area_icon: props.area.area_icon || "",
});

// area_name is a vee-validate field now, so the dialog cannot save an empty
// name -- it previously carried `required` (which does nothing on v-text-field
// without a schema) and no validation at all.
const editSchema = yup.object({
  area_name: yup.string().required("Give the area a name"),
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
// `values` carries the validated area_name; the chip pickers are plain v-models
// on editForm, so the two are merged here.
//
// NOTE: no pending state. The save goes out as an emit that DashView turns into
// a mutation, so this component never sees the promise -- unlike the add forms,
// which hold their own mutation and stay open until it resolves. Wiring that
// through would mean changing who owns the mutation, which is a bigger change
// than this PR is making.
const callEditArea = async values => {
  editcard.value = false;
  emit("editArea", { ...editForm.value, area_name: values.area_name });
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
    `${props.area.area_name}, ${groupName.value}, ` +
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

/* The settings panel is now just the two dialog activators, so it needs a row
   rather than the v-container/v-row/v-col scaffolding that used to hold them. */
.lc-area-card__panel {
  display: flex;
  align-items: center;
  gap: var(--lc-space-1);
  padding: var(--lc-space-2) var(--lc-space-3);
  background: rgb(var(--v-theme-surface-variant));
}

.lc-form-group__legend {
  color: rgb(var(--v-theme-on-surface));
  margin-bottom: var(--lc-space-2);
}

.lc-form-group {
  display: flex;
  flex-direction: column;
  gap: var(--lc-space-1);
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
}
</style>
