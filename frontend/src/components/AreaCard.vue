<template>
      <v-container>
        <v-row dense>
          <v-col cols="12" v-for="area in getAreas" :key="area.id">
            <v-card
              :color="area.group.group_color"
            >
              <div class="d-flex flex-no-wrap justify-space-between">
                <div>
                  <v-card-title class="text-h5">
                    <v-icon>{{ area.area_icon }}</v-icon>
                    {{ area.area_name }}
                  </v-card-title>

                  <v-card-subtitle>{{ area.dueCount }} of {{ area.totalCount }} Chore(s) Due</v-card-subtitle>
                  <v-card-text>{{ area.group.group_name }}</v-card-text>
                  <v-expand-transition>
              <div v-if="area.expand">
                <v-container>
                  <v-row dense>
                    <v-col>
                      <v-btn icon="mdi-content-save-outline"></v-btn>
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
                    <v-btn @click="area.expand = !area.expand" :icon="area.expand ? 'mdi-chevron-up' : 'mdi-chevron-down'"></v-btn>
                  </v-card-actions>
                </div>
                <v-progress-circular
                  :rotate="360"
                  :size="125"
                  :width="15"
                  :model-value="area.dirtiness"
                  :color="area.dirtycolor"
                >
                  {{ area.dirtiness }}% Dirty
                </v-progress-circular>

              </div>
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
  import { computed, ref } from 'vue';
  import { useChoreStore } from '@/stores/chores';

  const snackbar = ref(false);
  const snackbarText = ref('');
  const snackbarColor = ref('');
  const snackbarTimeout = ref(1500);
  const listLink = (areaName) => {
    return '/list/' + areaName;
  }
  const chorestore = useChoreStore();
  const getAreas = computed(() => {
    return chorestore.getAreas;
  });
  const callDeleteArea = async (area) => {
    try {
      const store = useChoreStore();
      await store.deleteArea(area);
      area.delete = false;
      showSnackbar('Area deleted successfully!', 'success');
    } catch (error) {
      showSnackbar('Area not deleted!', 'error');
    }
  }
  const showSnackbar = (text, color) => {
    snackbarText.value = text;
    snackbarColor.value = color;
    snackbar.value = true;
  }
</script>