<template>
  <v-card :color="props.area.group.group_color" border elevation="3">
    <v-card-title class="text-h5">
      <v-icon :icon="props.area.area_icon" size="25" class="me-1 pb-1"></v-icon
      >{{ props.area.area_name }}
    </v-card-title>
    <v-card-subtitle>{{ props.area.group.group_name }}</v-card-subtitle>
    <v-card-text class="py-0">
      <v-row align="center" no-gutters>
        <v-col class="text-h9" cols="6">
          <v-progress-linear
            v-model="dirtiness"
            :color="getDirtyColor(dirtiness)"
            height="25"
            striped
          >
            <template v-slot:default="{ value }">
              <strong>{{ Math.ceil(value) }}%</strong>
            </template>
          </v-progress-linear>
        </v-col>
        <v-col class="text-h9 text-center" cols="6">
          <strong class="text-accent">{{ props.area.dueCount }}</strong> of
          <strong class="text-accent">{{ props.area.totalCount }}</strong>
          Chore(s) Due
        </v-col>
      </v-row>
    </v-card-text>
    <v-expand-transition>
      <div v-if="expandcard">
        <v-container>
          <v-row dense>
            <v-col>
              <v-dialog v-model="editcard" persistent width="1024">
                <template v-slot:activator="{ props }">
                  <v-btn icon="mdi-note-edit-outline" v-bind="props"></v-btn>
                </template>
                <v-card>
                  <v-card-title>
                    <span class="text-h5">Edit Area</span>
                  </v-card-title>
                  <v-card-text>
                    <v-container>
                      <v-row>
                        <v-col cols="12" sm="6" md="4">
                          <v-text-field
                            label="Area name*"
                            required
                            v-model="editForm.area_name"
                          ></v-text-field>
                        </v-col>
                        <v-col cols="12" sm="6" md="4">
                          <v-chip-group
                            v-model="editForm.area_icon"
                            selected-class="text-deep-purple-accent-4"
                            mandatory
                          >
                            <v-chip
                              v-for="icon in chorestore.areaicons"
                              :key="icon"
                              :value="icon"
                            >
                              <v-icon>{{ icon }}</v-icon>
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
                            v-model="editForm.group_id"
                          >
                          </v-select>
                        </v-col>
                      </v-row>
                    </v-container>
                    <small>*indicates required field</small>
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn
                      color="blue-darken-1"
                      variant="text"
                      @click="editcard = false"
                    >
                      Close
                    </v-btn>
                    <v-btn
                      color="blue-darken-1"
                      variant="text"
                      @click="callEditArea(editForm)"
                    >
                      Save
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
              <v-dialog v-model="deletecard" persistent width="auto">
                <template v-slot:activator="{ props }">
                  <v-btn
                    icon="mdi-delete-forever-outline"
                    v-bind="props"
                  ></v-btn>
                </template>
                <v-card>
                  <v-card-title class="text-h5">
                    Delete this Area?
                  </v-card-title>
                  <v-card-text
                    >Are you sure you want to delete
                    <span class="text-secondary">{{
                      props.area.area_name
                    }}</span
                    >? This will also delete
                    <span class="text-secondary">{{
                      props.area.totalCount
                    }}</span>
                    chores!</v-card-text
                  >
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn
                      color="primary-darken-1"
                      variant="text"
                      @click="deletecard = false"
                    >
                      Close
                    </v-btn>
                    <v-btn
                      color="primary-darken-1"
                      variant="text"
                      @click="callDeleteArea(area)"
                    >
                      Delete
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </v-col>
          </v-row>
        </v-container>
      </div>
    </v-expand-transition>
    <v-card-actions>
      <v-btn
        class="ms-2"
        variant="outlined"
        size="small"
        :to="listLink(props.area.id)"
      >
        See Chores
      </v-btn>
      <v-btn
        @click="expandcard = !expandcard"
        :icon="expandcard ? 'mdi-chevron-up' : 'mdi-chevron-down'"
      ></v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { defineProps, defineEmits, ref } from "vue";
import { useAreaGroups } from "@/composables/areaGroupsComposable";
import { useChoreStore } from "@/stores/chores";

const expandcard = ref(false);
const editcard = ref(false);
const deletecard = ref(false);
const chorestore = useChoreStore();
const emit = defineEmits(["editArea", "removeArea"]);
const props = defineProps({
  area: Array,
});
const dirtiness = ref(props.area.dirtiness || 0);
const editForm = ref({
  id: props.area.id || 0,
  area_name: props.area.area_name || "",
  group_id: props.area.group.id || 0,
  area_icon: props.area.area_icon || "",
});
const listLink = areaName => {
  return "/list/" + areaName;
};

const { areagroups } = useAreaGroups();

const callDeleteArea = async deletedArea => {
  deletecard.value = false;
  emit("removeArea", deletedArea);
};
const callEditArea = async editArea => {
  editcard.value = false;
  emit("editArea", editArea);
};
const getDirtyColor = dirtiness => {
  const chorestore = useChoreStore();
  let dirtycolor = "error";
  if (dirtiness <= chorestore.med_thresh) {
    dirtycolor = "success";
  } else if (
    dirtiness > chorestore.med_thresh &&
    dirtiness <= chorestore.high_thresh
  ) {
    dirtycolor = "warning";
  } else if (dirtiness > chorestore.high_thresh) {
    dirtycolor = "error";
  }

  return dirtycolor;
};
</script>
