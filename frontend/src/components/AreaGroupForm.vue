<template>
  <!-- Rename and recolour an existing group.
       ─────────────────────────────────────────────────────────────────────
       There was no way to do either: AddAreaGroupForm could create a group and
       nothing could ever change it. `editAreaGroup` existed in the composable
       as a dead export, pointed at a URL missing its slash.

       Unlike AreaCard's edit dialog, this owns its mutation rather than
       emitting upward, so it gets a real pending state and closes only on
       success. -->
  <LcFormDialog
    v-model="model"
    title="Edit group"
    icon="mdi-pencil-outline"
    submit-label="Save changes"
    submit-icon="mdi-content-save-outline"
    :schema="schema"
    :initial-values="{ group_name: group.group_name }"
    :busy="busy"
    @submit="submitForm"
  >
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
      <legend class="lc-form-group__legend text-body-2">Group colour</legend>
      <v-chip-group
        v-model="groupColor"
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
// defineProps/defineEmits/defineModel are compiler macros.
import { ref, watch } from "vue";
import { Field } from "vee-validate";
import * as yup from "yup";
import { AREA_GROUP_COLORS } from "@/utils/labels";
import { useAreaGroups } from "@/composables/areaGroupsComposable";
import LcFormDialog from "@/components/LcFormDialog.vue";

const props = defineProps({
  group: { type: Object, required: true },
});

const emit = defineEmits(["saved"]);
const model = defineModel({ type: Boolean, default: false });

const colors = ref(AREA_GROUP_COLORS);
const busy = ref(false);
const groupColor = ref(props.group.group_color);

// The dialog is kept mounted between opens, so without this a second open would
// still show the colour from the first -- or from before someone else's change
// arrived over SSE.
watch(
  () => [model.value, props.group.group_color],
  ([open, color]) => {
    if (open) groupColor.value = color;
  }
);

const schema = yup.object({
  group_name: yup.string().required("Give the group a name"),
});

const { editAreaGroup } = useAreaGroups();

const submitForm = async values => {
  if (busy.value) return;
  busy.value = true;
  try {
    await editAreaGroup({
      id: props.group.id,
      group_name: values.group_name,
      group_color: groupColor.value,
      // Omitted deliberately: the API leaves group_order alone when it is not
      // sent, and reordering is its own operation on the group header. Sending
      // the current value here would make a rename race a concurrent reorder.
    });
    emit("saved");
    model.value = false;
  } catch {
    // handleApiError already surfaced it; stay open with the input intact.
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
