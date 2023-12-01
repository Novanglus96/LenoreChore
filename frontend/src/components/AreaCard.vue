<template>
      <v-container>
        <v-row dense>
          <v-col cols="12" v-for="(area, index) in areas" :key="index">
            <v-card
              :color="area.group.group_color"
            >
                  <v-card-title class="text-h5">
                    <v-icon
                  :icon="area.area_icon"
                  size="25"
                  class="me-1 pb-1"
                ></v-icon>{{area.area_name}}
                  </v-card-title>
                  <v-card-subtitle>{{ area.group.group_name }}</v-card-subtitle>
                   <v-card-text class="py-0">
                    <v-row align="center" no-gutters>
                      <v-col
                        class="text-h9"
                        cols="6"
                      >
                        <v-progress-linear
                          v-model="area.dirtiness"
                          :color="getDirtyColor(area)"
                          height="25"
                          striped
                        >
                          <template v-slot:default="{ value }">
                            <strong>{{ Math.ceil(value) }}%</strong>
                          </template>
                        </v-progress-linear>
                      </v-col>
                      <v-col
                        class="text-h9 text-center"
                        cols="6"
                      >
                        <strong class="text-accent">{{ area.dueCount }}</strong> of <strong class="text-accent">{{ area.totalCount }}</strong> Chore(s) Due
                      </v-col>
                    </v-row>
                      </v-card-text>
                  <v-expand-transition>
              <div v-if="expandedCards[index]">
                <v-container>
                  <v-row dense>
                    <v-col>
                      <v-dialog
                        v-model="area.edit"
                        persistent
                        width="1024"
                      >
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
                                <v-col
                                  cols="12"
                                  sm="6"
                                  md="4"
                                >
                                  <v-text-field
                                    label="Area name*"
                                    required
                                    v-model="area.area_name"
                                  ></v-text-field>
                                </v-col>
                                <v-col
                                  cols="12"
                                  sm="6"
                                  md="4"
                                >
                                  <v-chip-group
                                    v-model="area.area_icon"
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
                                <v-col
                                  cols="12"
                                  sm="6"
                                  md="4"
                                >
                                  <v-select
                                      label="Area Group"
                                      :items="areagroups"
                                      item-title="group_name"
                                      item-value="id"
                                      v-model="area.group"
                                      return-object   
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
                              @click="restoreEdit(area)"
                            >
                              Close
                            </v-btn>
                            <v-btn
                              color="blue-darken-1"
                              variant="text"
                              @click="callEditArea(area)"
                            >
                              Save
                            </v-btn>
                          </v-card-actions>
                        </v-card>
                      </v-dialog>
                      <v-dialog
                        v-model="area.delete"
                        persistent
                        width="auto"
                      >
                        <template v-slot:activator="{ props }">
                          <v-btn icon="mdi-delete-forever-outline" v-bind="props"></v-btn>
                        </template>
                        <v-card>
                          <v-card-title class="text-h5">
                            Delete this Area?
                          </v-card-title>
                          <v-card-text>Are you sure you want to delete <span class="text-secondary">{{ area.area_name }}</span>? This will also delete <span class="text-secondary">{{ area.totalCount }}</span> chores!</v-card-text>
                          <v-card-actions>
                            <v-spacer></v-spacer>
                            <v-btn
                              color="primary-darken-1"
                              variant="text"
                              @click="area.delete = false"
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
                      :to="listLink(area.area_name)"
                    >
                      See Chores
                    </v-btn>
                    <v-btn @click="toggleExpand(index)" :icon="area.expand ? 'mdi-chevron-up' : 'mdi-chevron-down'"></v-btn>
                  </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
        <v-snackbar
          v-model="snackbar"
          :color="snackbarColor"
          :timeout="snackbarTimeout"
          content-class="centered-text"
        >
          {{ snackbarText }}
        </v-snackbar>
      </v-container>
</template>

<script setup>
  import { ref } from 'vue';
  import { useAreas } from '@/composables/areasComposable';
  import { useAreaGroups } from '@/composables/areaGroupsComposable';
  import { useChoreStore } from '@/stores/chores'

  const toggleExpand = (index) => {
    // Toggle the expanded state for the clicked card
    expandedCards.value[index] = !expandedCards.value[index];
  };

  const snackbar = ref(false);
  const snackbarText = ref('');
  const snackbarColor = ref('');
  const snackbarTimeout = ref(1500);
  const listLink = (areaName) => {
    return '/list/' + areaName;
  }
  
  const { areas, removeArea, editArea } = useAreas()
  const expandedCards = ref(Array.from({ length: areas.length }, () => false));
  const { areagroups } = useAreaGroups()
  const restoreEdit = async (area) => {
    area.edit = false;
  }
  const callDeleteArea = async (area) => {
    try {
      removeArea(area)
      area.delete = false;
      showSnackbar('Area deleted successfully!', 'success');
    } catch (error) {
      showSnackbar('Area not deleted!', 'error');
    }
  }
  const callEditArea = async (area) => {
    try {
      editArea(area)
      area.edit = false;
      showSnackbar('Area edited successfully!', 'success');
    } catch (error) {
      showSnackbar('Area not edited!', 'error');
    }
  }
  const getDirtyColor = (area) => {
    const chorestore = useChoreStore()
    let dirtycolor = "error"
    if (area.dirtiness <= chorestore.med_thresh ) {
      dirtycolor = 'success'
    }else if (area.dirtiness > chorestore.med_thresh && area.dirtiness <= chorestore.high_thresh){
      dirtycolor = 'warning'
    }else if (area.dirtiness > chorestore.high_thresh){
      dirtycolor = 'error'
    }
    
    return dirtycolor
  }
  const showSnackbar = (text, color) => {
    snackbarText.value = text;
    snackbarColor.value = color;
    snackbar.value = true;
  }
</script>