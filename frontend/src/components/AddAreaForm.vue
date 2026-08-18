<template>
  <LcFormDialog
    v-model="dialog"
    title="Add area"
    icon="mdi-plus-circle"
    submit-label="Add area"
    submit-icon="mdi-check"
    :schema="schema"
    :busy="busy"
    @submit="submitForm"
    @cancel="resetForm"
  >
    <template v-slot:activator="{ props: activatorProps }">
      <v-list-item v-bind="activatorProps">
        <template v-slot:prepend>
          <v-icon icon="mdi-plus-circle"></v-icon>
        </template>
        <v-list-item-title>Add Area</v-list-item-title>
      </v-list-item>
    </template>

    <fieldset class="lc-fieldset lc-form-group">
      <legend class="lc-form-group__legend text-body-2">What</legend>

      <Field name="area_name" v-slot="{ field, errorMessage }">
        <v-text-field
          v-bind="field"
          label="Area name"
          prepend-inner-icon="mdi-format-title"
          :error-messages="errorMessage"
        ></v-text-field>
      </Field>

      <v-select
        v-model="formData.group_id"
        label="Area group"
        prepend-inner-icon="mdi-shape-outline"
        :items="areagroups"
        item-title="group_name"
        item-value="id"
      ></v-select>
    </fieldset>

    <v-divider class="my-4"></v-divider>

    <fieldset class="lc-fieldset">
      <!-- Twenty chips containing only an icon are identical, nameless options
           to a screen reader, and the group had no label of its own. Note the
           LINTER REPORTS THIS FILE CLEAN -- its anchor-has-content rule is
           mapped onto VBtn, and v-chip has no equivalent rule. -->
      <legend class="lc-form-group__legend text-body-2">Area icon</legend>
      <v-chip-group
        v-model="formData.area_icon"
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
</template>

<script setup>
import { ref } from "vue";
import { Field } from "vee-validate";
import * as yup from "yup";
import { useAreas } from "@/composables/areasComposable";
import { useAreaGroups } from "@/composables/areaGroupsComposable";
import { iconLabel } from "@/utils/labels";
import { useChoreStore } from "@/stores/chores";
import LcFormDialog from "@/components/LcFormDialog.vue";

const chorestore = useChoreStore();
const dialog = ref(false);
const busy = ref(false);

const DEFAULTS = () => ({
  area_icon: "mdi-home",
  group_id: 1,
});

const formData = ref(DEFAULTS());

const schema = yup.object({
  area_name: yup.string().required("Give the area a name"),
});

const { addArea } = useAreas();
const { areagroups } = useAreaGroups();

const resetForm = () => {
  formData.value = DEFAULTS();
};

const submitForm = async values => {
  if (busy.value) return;
  busy.value = true;
  try {
    await addArea({ ...formData.value, area_name: values.area_name });
    dialog.value = false;
    resetForm();
  } catch {
    // Error already surfaced by handleApiError; stay open so the input survives.
  } finally {
    busy.value = false;
  }
};
</script>

<style scoped>
.lc-form-group__legend {
  color: rgb(var(--v-theme-on-surface));
  margin-bottom: var(--lc-space-2);
}

.lc-form-group {
  display: flex;
  flex-direction: column;
  gap: var(--lc-space-1);
}
</style>
