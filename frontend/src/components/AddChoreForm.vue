<template>
  <LcFormDialog
    v-model="dialog"
    title="Add chore"
    icon="mdi-plus-circle"
    submit-label="Add chore"
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
        <v-list-item-title>Add Chore</v-list-item-title>
      </v-list-item>
    </template>

    <!-- Four labelled groups instead of an undifferentiated run of rows. The
         only grouping cues before were a bare <b>Effort</b> and a
         <span class="text-h9">Repeat</span> -- and text-h9 is not a Vuetify
         class, so that heading rendered at body size with no styling at all. -->
    <fieldset class="lc-fieldset lc-form-group">
      <legend class="lc-form-group__legend text-body-2">What</legend>

      <Field name="chore_name" v-slot="{ field, errorMessage }">
        <v-text-field
          v-bind="field"
          label="Chore name"
          prepend-inner-icon="mdi-format-title"
          :error-messages="errorMessage"
        ></v-text-field>
      </Field>

      <Field name="area_id" v-slot="{ field, errorMessage }">
        <v-select
          v-bind="field"
          label="Area"
          prepend-inner-icon="mdi-home-outline"
          :items="areas"
          item-title="area_name"
          item-value="id"
          :error-messages="errorMessage"
        ></v-select>
      </Field>
    </fieldset>

    <v-divider class="my-4"></v-divider>

    <fieldset class="lc-fieldset lc-form-group">
      <legend class="lc-form-group__legend text-body-2">How often</legend>

      <!-- The one place two fields genuinely belong on a line: they read as a
           single phrase, "every 3 day(s)". -->
      <div class="lc-form-row">
        <Field name="intervalNumber" v-slot="{ field, errorMessage }">
          <v-select
            v-bind="field"
            label="Every"
            :items="intervals"
            :error-messages="errorMessage"
          ></v-select>
        </Field>

        <Field name="unit" v-slot="{ field, errorMessage }">
          <v-select
            v-bind="field"
            label="Unit"
            :items="units"
            :error-messages="errorMessage"
          ></v-select>
        </Field>
      </div>
    </fieldset>

    <v-divider class="my-4"></v-divider>

    <LcMonthPicker v-model="formData.active_months" />

    <v-divider class="my-4"></v-divider>

    <fieldset class="lc-fieldset lc-form-group">
      <legend class="lc-form-group__legend text-body-2">How much work</legend>
      <div class="d-flex align-center ga-3">
        <v-rating
          v-model="formData.effort"
          length="3"
          size="24"
          density="compact"
          active-color="accent"
          :item-aria-label="'Effort level {0} of 3'"
        ></v-rating>
        <!-- The stars alone never said what one versus three meant. -->
        <span class="text-body-2 text-medium-emphasis">
          {{ effortLabel(formData.effort) }}
        </span>
      </div>
    </fieldset>
  </LcFormDialog>
</template>

<script setup>
import { ref, computed } from "vue";
import { Field } from "vee-validate";
import * as yup from "yup";
import { useChoreStore } from "@/stores/chores";
import { effortLabel } from "@/utils/labels";
import { useAreas } from "@/composables/areasComposable";
import { useChores } from "@/composables/choresComposasble";
import LcFormDialog from "@/components/LcFormDialog.vue";
import LcMonthPicker from "@/components/LcMonthPicker.vue";

const chorestore = useChoreStore();
const dialog = ref(false);
const busy = ref(false);

const DEFAULTS = () => ({
  effort: 1,
  active_months: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
});

const formData = ref(DEFAULTS());

// The asterisks and the "*indicates required field" footnote are gone; the
// schema already says which fields are required, at the field, in words.
const schema = yup.object({
  chore_name: yup.string().required("Give the chore a name"),
  area_id: yup
    .number()
    .required("Pick an area")
    .typeError("Pick an area"),
  intervalNumber: yup
    .number()
    .required("Pick how often it repeats")
    .typeError("Pick how often it repeats"),
  unit: yup.string().required("Pick a unit"),
});

const { areas } = useAreas();
const units = computed(() => chorestore.units);
const intervals = computed(() => chorestore.intervals);

const { addChore } = useChores();

const resetForm = () => {
  formData.value = DEFAULTS();
};

const submitForm = async values => {
  if (busy.value) return;

  // "Some months" with nothing ticked would save a chore that never comes due.
  if (!formData.value.active_months.length) {
    chorestore.showSnackbar("Pick at least one active month", "warning");
    return;
  }

  busy.value = true;
  try {
    await addChore({ ...formData.value, ...values });
    // Only now. A failure leaves the dialog open with everything still typed.
    dialog.value = false;
    resetForm();
  } catch {
    // addChore surfaces the error through handleApiError's snackbar; there is
    // nothing to add here beyond staying open and re-enabling the button.
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

/* Fields stack. The old v-col cols="12" sm="6" md="4" grid put one 330px field
   in the corner of a 1024px dialog and left the rest empty. */
.lc-form-group {
  display: flex;
  flex-direction: column;
  gap: var(--lc-space-1);
}

.lc-form-row {
  display: flex;
  gap: var(--lc-space-3);
}

.lc-form-row > *:first-child {
  flex: 0 0 40%;
}

.lc-form-row > *:last-child {
  flex: 1 1 auto;
  min-width: 0;
}
</style>
