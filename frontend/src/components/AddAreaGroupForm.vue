<template>
  <v-dialog v-model="dialog" persistent width="1024">
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
        <v-container>
          <v-row>
            <v-col cols="12" sm="6" md="4">
              <v-text-field
                label="Group name*"
                required
                v-model="formData.group_name"
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="6" md="4">
              <v-chip-group v-model="formData.group_color" mandatory column>
                <v-chip
                  v-for="color in colors"
                  :key="color.name"
                  :value="color.value"
                  filter
                >
                  <v-icon icon="mdi-square" :color="color.value"></v-icon
                  >{{ color.name }}
                </v-chip>
              </v-chip-group>
            </v-col>
          </v-row>
        </v-container>
        <small>*indicates required field</small>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" variant="text" @click="dialog = false">
          Close
        </v-btn>
        <v-btn color="blue-darken-1" variant="text" @click="submitForm">
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script setup>
import { ref } from "vue";
import { useAreaGroups } from "@/composables/areaGroupsComposable";

const colors = ref([
  {
    name: "Color1",
    value: "area1",
  },
  {
    name: "Color2",
    value: "area2",
  },
  {
    name: "Color3",
    value: "area3",
  },
  {
    name: "Color4",
    value: "area4",
  },
  {
    name: "Color5",
    value: "area5",
  },
  {
    name: "Color6",
    value: "area6",
  },
]);
const dialog = ref(false);
const formData = ref({
  group_name: "",
  group_color: "area1",
  group_order: 1,
});

const { addAreaGroup } = useAreaGroups();
const submitForm = async () => {
  addAreaGroup(formData.value);
  dialog.value = false;
};
</script>
