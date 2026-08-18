<template>
  <LcFormDialog
    v-model="dialog"
    title="Add area group"
    icon="mdi-plus-circle"
    submit-label="Add group"
    submit-icon="mdi-check"
    :schema="schema"
    :busy="busy"
    @submit="submitForm"
    @cancel="resetForm"
  >
    <template v-slot:activator="{ props }">
      <v-list-item v-bind="props">
        <template v-slot:prepend>
          <v-icon icon="mdi-plus-circle"></v-icon>
        </template>
        <v-list-item-title>Add Area Group</v-list-item-title>
      </v-list-item>
    </template>

    <fieldset class="lc-fieldset lc-form-group">
      <legend class="lc-form-group__legend text-body-2">What</legend>

      <Field name="group_name" v-slot="{ field, errorMessage }">
        <v-text-field
          v-bind="field"
          label="Group name"
          prepend-inner-icon="mdi-format-title"
          :error-messages="errorMessage"
        ></v-text-field>
      </Field>
    </fieldset>

    <v-divider class="my-4"></v-divider>

    <fieldset class="lc-fieldset">
      <!-- The group had no label, so the chips announced with nothing saying
           what they were for. The names were also Color1..6, which told nobody
           anything; these match the hues those theme keys actually carry now. -->
      <legend class="lc-form-group__legend text-body-2">Group colour</legend>
      <v-chip-group
        v-model="formData.group_color"
        selected-class="text-primary"
        mandatory
        column
      >
        <v-chip
          v-for="color in colors"
          :key="color.value"
          :value="color.value"
          :aria-label="color.name"
          filter
        >
          <v-icon
            icon="mdi-circle"
            size="14"
            :color="color.value"
            start
            aria-hidden="true"
          ></v-icon>
          {{ color.name }}
        </v-chip>
      </v-chip-group>
    </fieldset>
  </LcFormDialog>
</template>

<script setup>
import { ref } from "vue";
import { Field } from "vee-validate";
import * as yup from "yup";
import { useAreaGroups } from "@/composables/areaGroupsComposable";
import { AREA_GROUP_COLORS } from "@/utils/labels";
import LcFormDialog from "@/components/LcFormDialog.vue";

// Shared, because the VALUES are persisted -- AreaGroup.group_color stores the
// literal "area1".."area6" and Vuetify resolves it as a theme colour at render
// time. Keeping the list in one place stops a future edit renaming a value.
const colors = ref(AREA_GROUP_COLORS);

const schema = yup.object({
  group_name: yup.string().required("Give the group a name"),
});

const dialog = ref(false);
const busy = ref(false);

const DEFAULTS = () => ({
  group_color: "area1",
  group_order: 1,
});

const formData = ref(DEFAULTS());

const { addAreaGroup } = useAreaGroups();

const resetForm = () => {
  formData.value = DEFAULTS();
};

const submitForm = async values => {
  if (busy.value) return;
  busy.value = true;
  try {
    await addAreaGroup({ ...formData.value, group_name: values.group_name });
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
