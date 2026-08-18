<template>
  <v-dialog v-model="dialog" persistent :fullscreen="$vuetify.display.smAndDown" width="1024">
    <template v-slot:activator="{ props: activatorProps }">
      <v-list-item key="1" v-bind="activatorProps">
        <template v-slot:prepend>
          <v-icon icon="mdi-plus-circle"></v-icon>
        </template>
        <v-list-item-title>Add Area</v-list-item-title>
      </v-list-item>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Add Area</span>
      </v-card-title>
      <v-card-text>
        <Form @submit="submitForm" :validation-schema="schema" v-slot="{ errors }">
          <v-container>
            <v-row>
              <v-col cols="12" sm="6" md="4">
                <Field name="area_name" v-slot="{ field }">
                  <v-text-field
                    v-bind="field"
                    label="Area name*"
                    :error-messages="errors.area_name"
                  ></v-text-field>
                </Field>
              </v-col>
              <v-col cols="12">
                <!-- Same fix as AreaCard's editor: twenty chips containing only
                     an icon are identical, nameless options to a screen reader,
                     and the group had no label of its own. Note the LINTER
                     REPORTS THIS FILE CLEAN -- its anchor-has-content rule is
                     mapped onto VBtn, and v-chip has no equivalent rule. -->
                <div id="add-area-icon-label" class="text-body-2 mb-1">
                  Area icon
                </div>
                <v-chip-group
                  v-model="formData.area_icon"
                  selected-class="text-primary"
                  aria-labelledby="add-area-icon-label"
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
                  v-model="formData.group_id"
                >
                </v-select>
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
import { ref } from "vue";
import { Form, Field } from "vee-validate";
import * as yup from "yup";
import { useAreas } from "@/composables/areasComposable";
import { useAreaGroups } from "@/composables/areaGroupsComposable";
import { iconLabel } from "@/utils/labels";
import { useChoreStore } from "@/stores/chores";

const chorestore = useChoreStore();
const dialog = ref(false);
const formData = ref({
  area_icon: "mdi-home",
  group_id: 1,
});

const schema = yup.object({
  area_name: yup.string().required("Area name is required"),
});

const { addArea } = useAreas();
const { areagroups } = useAreaGroups();

const submitForm = (values) => {
  addArea({ ...formData.value, area_name: values.area_name });
  dialog.value = false;
};

const closeDialog = () => {
  dialog.value = false;
};
</script>
