<template>
  <v-dialog v-model="dialog" persistent :fullscreen="$vuetify.display.smAndDown" width="1024">
    <template v-slot:activator="{ props }">
      <v-list-item key="2" v-bind="props">
        <template v-slot:prepend>
          <v-icon icon="mdi-plus-circle"></v-icon>
        </template>
        <v-list-item-title>Add Chore</v-list-item-title>
      </v-list-item>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Add Chore</span>
      </v-card-title>
      <v-card-text>
        <Form @submit="submitForm" :validation-schema="schema" v-slot="{ errors }">
          <v-container>
            <v-row>
              <v-col cols="12" sm="6" md="4">
                <Field name="chore_name" v-slot="{ field }">
                  <v-text-field
                    v-bind="field"
                    label="Chore name*"
                    :error-messages="errors.chore_name"
                  ></v-text-field>
                </Field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <Field name="area_id" v-slot="{ field }">
                  <v-select
                    v-bind="field"
                    label="Area*"
                    :items="areas"
                    item-title="area_name"
                    item-value="id"
                    :error-messages="errors.area_id"
                  >
                  </v-select>
                </Field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" sm="6" md="4">
                <span class="text-h9">Repeat</span>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" sm="6" md="4">
                <Field name="intervalNumber" v-slot="{ field }">
                  <v-select
                    v-bind="field"
                    label="Interval*"
                    :items="intervals"
                    :error-messages="errors.intervalNumber"
                  >
                  </v-select>
                </Field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <Field name="unit" v-slot="{ field }">
                  <v-select
                    v-bind="field"
                    label="Unit(s)*"
                    :items="units"
                    :error-messages="errors.unit"
                  >
                  </v-select>
                </Field>
              </v-col>
            </v-row>
            <!-- Was a loose heading plus twelve hand-written v-checkbox
                 blocks: each announced alone, with nothing tying it to "which
                 months does this chore run in". Same fix as ChoreCard, sharing
                 the same MONTHS list so the two cannot diverge. -->
            <v-row dense>
              <v-col cols="12">
                <fieldset class="lc-fieldset">
                  <legend class="text-body-2 mb-1">Active months</legend>
                  <div class="lc-months__grid">
                    <v-checkbox
                      v-for="month in months"
                      :key="month.value"
                      v-model="formData.active_months"
                      :label="month.label"
                      :value="month.value"
                      color="primary"
                      density="compact"
                      hide-details
                    ></v-checkbox>
                  </div>
                </fieldset>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12" sm="6" md="4">
                <b>Effort </b>
                <v-rating
                  label="Effort"
                  v-model="formData.effort"
                  length="3"
                  size="20"
                ></v-rating>
              </v-col>
            </v-row>
          </v-container>
          <small>*indicates required field</small>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="blue-darken-1" variant="text" @click="closeDialog">
              Close
            </v-btn>
            <v-btn color="blue-darken-1" variant="text" type="submit">
              Save
            </v-btn>
          </v-card-actions>
        </Form>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed } from "vue";
import { Form, Field } from "vee-validate";
import * as yup from "yup";
import { useChoreStore } from "@/stores/chores";
import { MONTHS as months } from "@/utils/labels";
import { useAreas } from "@/composables/areasComposable";
import { useChores } from "@/composables/choresComposasble";

const chorestore = useChoreStore();
const dialog = ref(false);
const formData = ref({
  effort: 1,
  active_months: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
});

const schema = yup.object({
  chore_name: yup.string().required("Chore name is required"),
  area_id: yup.number().required("Area is required").typeError("Area is required"),
  intervalNumber: yup.number().required("Interval is required").typeError("Interval is required"),
  unit: yup.string().required("Unit is required"),
});

const { areas } = useAreas();
const units = computed(() => chorestore.units);
const intervals = computed(() => chorestore.intervals);

const { addChore } = useChores();

const submitForm = (values) => {
  addChore({ ...formData.value, ...values });
  dialog.value = false;
};

const closeDialog = () => {
  dialog.value = false;
};
</script>
