<template>
  <v-card
    class="lc-area-card lc-lift"
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

      <LcActionMenu
        :items="menuItems"
        :title="props.area.area_name"
        @select="onMenuSelect"
      >
        <template v-slot:activator="{ props: activatorProps }">
          <v-btn
            v-bind="activatorProps"
            icon="mdi-dots-vertical"
            :aria-label="`More actions for ${props.area.area_name}`"
          >
            <v-icon icon="mdi-dots-vertical"></v-icon>
          </v-btn>
        </template>
      </LcActionMenu>
    </v-card-actions>

    <!-- ── Overlays ────────────────────────────────────────────────────────
         Both used to sit inside a panel the chevron expanded, so reaching
         "Edit area" was: tap chevron, wait for the card to grow, tap an
         unlabelled pencil, then read the dialog. The panel's entire payload
         was these two activators. They are menu items now, which is what the
         group header directly above this card has always used for exactly the
         same job -- two patterns for one thing on one screen. -->
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
      <fieldset class="lc-fieldset lc-form-group">
        <legend class="lc-form-group__legend text-body-2">What</legend>

        <!-- Was a plain v-model with `required` and no schema, so an
             empty area name saved happily. -->
        <Field name="area_name" v-slot="{ componentField, errorMessage }">
          <v-text-field
            v-bind="componentField"
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
      Deleting <strong>{{ props.area.area_name }}</strong> also deletes the
      <strong>{{ props.area.totalCount }}</strong>
      {{ props.area.totalCount === 1 ? "chore" : "chores" }} in it. This cannot
      be undone.
    </LcConfirmDialog>
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
import LcActionMenu from "@/components/LcActionMenu.vue";
import LcFormDialog from "@/components/LcFormDialog.vue";
import LcConfirmDialog from "@/components/LcConfirmDialog.vue";

const { options } = useOptions();
const router = useRouter();
const editcard = ref(false);
const deletecard = ref(false);
const chorestore = useChoreStore();
const emit = defineEmits(["editArea", "removeArea"]);
const props = defineProps({
  area: Object,
});
const dirtiness = computed(() => props.area.dirtiness || 0);

// Built as data so the desktop menu and the mobile bottom sheet cannot drift.
const menuItems = computed(() => [
  { key: "edit", title: "Edit area…", icon: "mdi-note-edit-outline" },
  {
    key: "delete",
    title: "Delete area",
    icon: "mdi-delete-forever-outline",
    color: "filthy",
    dividerBefore: true,
    subtitle: props.area.totalCount
      ? `Also deletes ${props.area.totalCount} ${
          props.area.totalCount === 1 ? "chore" : "chores"
        }`
      : undefined,
  },
]);

const onMenuSelect = key => {
  if (key === "edit") editcard.value = true;
  else if (key === "delete") deletecard.value = true;
};

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
  width: var(--lc-card-stripe);
}

.lc-area-card__body {
  padding: var(--lc-space-4) var(--lc-space-4) var(--lc-space-3)
    calc(var(--lc-space-4) + var(--lc-card-stripe));
}

.lc-area-card__icon {
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

@media (max-width: 599px) {
  .lc-area-card__body {
    padding: var(--lc-space-3) var(--lc-space-3) var(--lc-space-2)
      calc(var(--lc-space-3) + var(--lc-card-stripe));
  }
}
</style>
