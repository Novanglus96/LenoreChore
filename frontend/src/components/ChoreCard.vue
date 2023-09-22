<template>
  <v-container>
    <v-row dense v-for="chore in getChores" :key="chore.id">
        <v-col cols="12" >
          <v-card
          color="primary"
          :theme="chore.isAssigned ? 'light' : 'dark'"
          >
            <v-card-item :title="chore.chore_name">
              <template v-slot:subtitle>
                <v-icon
                  :icon="chore.areaicon"
                  size="18"
                  class="me-1 pb-1"
                ></v-icon>

                {{ chore.area }}
              </template>
            </v-card-item>

            <v-card-text class="py-0">
              <v-row align="center" no-gutters>
                <v-col
                  class="text-h9"
                  cols="6"
                >
                  <v-progress-linear
                    v-model="chore.cleanliness"
                    color="blue-grey"
                    height="25"
                  >
                    <template v-slot:default="{ value }">
                      <strong>{{ Math.ceil(value) }}%</strong>
                    </template>
                  </v-progress-linear>
                </v-col>

                <v-col cols="6" class="text-right">
                  Due in {{ chore.duedays }} day(s)
                </v-col>
              </v-row>
            </v-card-text>

            <div class="d-flex py-3 justify-space-between">
              <v-list-item
                density="compact"
                :prepend-icon="chore.assignee_icon"
              >
                <v-list-item-subtitle>{{ chore.assignee }}</v-list-item-subtitle>
              </v-list-item>

              <v-list-item
                density="compact"
              >
                <v-rating
                  v-model="chore.effort"
                  readonly
                  length="3"
                  size="20"
                ></v-rating>
              </v-list-item>
            </div>

            <v-expand-transition>
              <div v-if="chore.expand">
                
                <v-list class="bg-transparent">
                  <v-list-item title="Last Completed" :subtitle="chore.lastCompleted">

                  </v-list-item>
                  <v-list-item title="Next Due" :subtitle="chore.nextDue">
                  </v-list-item>
                  <v-list-item title="Repeats Every" :subtitle="chore.repeat">
                  </v-list-item>
                </v-list>
              </div>
            </v-expand-transition>

            <v-divider :thickness="2"></v-divider>

            <v-card-actions>
              <v-btn icon="mdi-check"></v-btn>
              <v-btn icon="mdi-alarm-snooze"></v-btn>
              <v-btn icon="mdi-clipboard-account-outline"></v-btn>
              <v-btn icon="mdi-pencil-outline"></v-btn>
              <v-btn @click="chore.expand = !chore.expand" :icon="chore.expand ? 'mdi-chevron-up' : 'mdi-chevron-down'">
              </v-btn>
              
            </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
<script setup>
  import { computed } from 'vue';
  import { useChoreStore } from '@/stores/chores';

  const chorestore = useChoreStore();
  const getChores = computed(() => {
    return chorestore.getChores;
  });
</script>