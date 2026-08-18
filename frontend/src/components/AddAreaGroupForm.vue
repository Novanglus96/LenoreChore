<template>
  <v-dialog v-model="dialog" persistent :fullscreen="$vuetify.display.smAndDown" width="1024">
    <template v-slot:activator="{ props }">
      <v-list-item key="1" v-bind="props">
        <template v-slot:prepend>
          <v-icon icon="mdi-plus-circle"></v-icon>
        </template>
        <v-list-item-title>Add Area Group</v-list-item-title>
      </v-list-item>
    </template>
    <v-card>
      <v-card-title>
        <span class="text-h5">Add Area Group</span>
      </v-card-title>
      <v-card-text>
        <Form @submit="submitForm" :validation-schema="schema" v-slot="{ errors }">
          <v-container>
            <v-row>
              <v-col cols="12" sm="6" md="4">
                <Field name="group_name" v-slot="{ field }">
                  <v-text-field
                    v-bind="field"
                    label="Group name*"
                    :error-messages="errors.group_name"
                  ></v-text-field>
                </Field>
              </v-col>
              <v-col cols="12">
                <!-- The group had no label, so the chips announced with nothing
                     saying what they were for. The names were also Color1..6,
                     which told nobody anything; these match the hues those
                     theme keys actually carry now. -->
                <div id="add-group-colour-label" class="text-body-2 mb-1">
                  Group colour
                </div>
                <v-chip-group
                  v-model="formData.group_color"
                  selected-class="text-primary"
                  aria-labelledby="add-group-colour-label"
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
import { useAreaGroups } from "@/composables/areaGroupsComposable";
import { AREA_GROUP_COLORS } from "@/utils/labels";

// Shared, because the VALUES are persisted -- AreaGroup.group_color stores the
// literal "area1".."area6" and Vuetify resolves it as a theme colour at render
// time. Keeping the list in one place stops a future edit renaming a value.
const colors = ref(AREA_GROUP_COLORS);

const schema = yup.object({
  group_name: yup.string().required("Group name is required"),
});

const dialog = ref(false);
const formData = ref({
  group_color: "area1",
  group_order: 1,
});

const { addAreaGroup } = useAreaGroups();

const submitForm = (values) => {
  addAreaGroup({ ...formData.value, group_name: values.group_name });
  dialog.value = false;
};

const closeDialog = () => {
  dialog.value = false;
};
</script>
