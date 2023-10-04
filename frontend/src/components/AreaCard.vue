<template>
      <v-container>
        <v-row dense>
          <v-col cols="12" v-for="area in getAreas" :key="area.id">
            <v-card
              color="primary"
            >
              <div class="d-flex flex-no-wrap justify-space-between">
                <div>
                  <v-card-title class="text-h5">
                    <v-icon>{{ area.area_icon }}</v-icon>
                    {{ area.area_name }}
                  </v-card-title>

                  <v-card-subtitle>{{ area.dueCount }} Chore(s) Due</v-card-subtitle>
                  <v-expand-transition>
              <div v-if="area.expand">
                <v-container>
                  <v-row dense>
                    <v-col>
                      <v-btn icon="mdi-content-save-outline"></v-btn>
                      <v-btn icon="mdi-delete-forever-outline"></v-btn>
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
      </v-container>
</template>

<script setup>
  import { computed } from 'vue';
  import { useChoreStore } from '@/stores/chores';
  
  const listLink = (areaName) => {
    return '/list/' + areaName;
  }
  const chorestore = useChoreStore();
  const getAreas = computed(() => {
    return chorestore.getAreas;
  });

</script>