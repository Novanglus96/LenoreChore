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

                  <v-card-actions>
                    <v-btn
                      class="ms-2"
                      variant="outlined"
                      size="small"
                      to="/list"
                    >
                      See Chores
                    </v-btn>
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

  const chorestore = useChoreStore();
  const getAreas = computed(() => {
    return chorestore.getAreas;
  });

</script>