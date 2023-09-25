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
                    v-model="chore.dirtiness"
                    :color="chore.dirtycolor"
                    height="25"
                  >
                    <template v-slot:default="{ value }">
                      <strong>{{ Math.ceil(value) }}%</strong>
                    </template>
                  </v-progress-linear>
                </v-col>

                <v-col cols="6" class="text-right">
                  <span :class="chore.isOverdue ? 'text-red' : ''">Due in {{ chore.duedays }} day(s)</span>
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
                  :readonly="!chore.expand"
                  length="3"
                  size="20"
                ></v-rating>
              </v-list-item>
            </div>

            <v-expand-transition>
              <div v-if="chore.expand">
                <v-container>
                  <v-row dense>
                    <v-col>
                      <v-text-field
                        label="Last Completed"
                        required
                        v-model="chore.lastCompleted"
                      ></v-text-field>
                    </v-col>
                    <v-col>
                      <v-text-field
                        label="Next Due"
                        required
                        v-model="chore.nextDue"
                      ></v-text-field>
                    </v-col>
                  </v-row>
                  <v-row dense>
                    <v-col>
                      Repeats
                    </v-col>
                  </v-row>
                  <v-row dense>
                    <v-col>
                       <v-select
                          label="Interval*"
                          required
                          :items="intervals"
                          v-model="chore.intervalNumber"   
                        ></v-select>
                    </v-col>
                    <v-col>
                        <v-select
                            label="Unit(s)*"
                            required
                            :items="units"
                            v-model="chore.unit"   
                        ></v-select>
                    </v-col>
                  </v-row>
                  <v-row dense>
                    <v-col>
                      <v-checkbox
                        v-model="chore.m_jan"
                        label="Jan"
                        color="white"
                        hide-details
                        :model-value="true"
                      ></v-checkbox>
                    </v-col>
                    <v-col>
                      <v-checkbox
                        v-model="chore.m_feb"
                        label="Feb"
                        color="white"
                        hide-details
                        :model-value="true"
                      ></v-checkbox>
                    </v-col>
                    <v-col>
                      <v-checkbox
                        v-model="chore.m_mar"
                        label="Mar"
                        color="white"
                        hide-details
                        :model-value="true"
                      ></v-checkbox>
                    </v-col>
                    <v-col>
                      <v-checkbox
                        v-model="chore.m_apr"
                        label="Apr"
                        color="white"
                        hide-details
                        :model-value="true"
                      ></v-checkbox>
                    </v-col>
                  </v-row>
                  <v-row dense>
                    <v-col>
                      <v-checkbox
                        v-model="chore.m_may"
                        label="May"
                        color="white"
                        hide-details
                        :model-value="true"
                      ></v-checkbox>
                    </v-col>
                    <v-col>
                      <v-checkbox
                        v-model="chore.m_jun"
                        label="Jun"
                        color="white"
                        hide-details
                        :model-value="true"
                      ></v-checkbox>
                    </v-col>
                    <v-col>
                      <v-checkbox
                        v-model="chore.m_jul"
                        label="Jul"
                        color="white"
                        hide-details
                        :model-value="true"
                      ></v-checkbox>
                    </v-col>
                    <v-col>
                      <v-checkbox
                        v-model="chore.m_aug"
                        label="Aug"
                        color="white"
                        hide-details
                        :model-value="true"
                      ></v-checkbox>
                    </v-col>
                  </v-row>
                  <v-row dense>
                    <v-col>
                      <v-checkbox
                        v-model="chore.m_sep"
                        label="Sep"
                        color="white"
                        hide-details
                        :model-value="true"
                      ></v-checkbox>
                    </v-col>
                    <v-col>
                      <v-checkbox
                        v-model="chore.m_oct"
                        label="Oct"
                        color="white"
                        hide-details
                        :model-value="true"
                      ></v-checkbox>
                    </v-col>
                    <v-col>
                      <v-checkbox
                        v-model="chore.m_nov"
                        label="Nov"
                        color="white"
                        hide-details
                        :model-value="true"
                      ></v-checkbox>
                    </v-col>
                    <v-col>
                      <v-checkbox
                        v-model="chore.m_dec"
                        label="Dec"
                        color="white"
                        hide-details
                        :model-value="true"
                      ></v-checkbox>
                    </v-col>
                  </v-row>
                  <v-row dense>
                    <v-col>
                      <v-btn @click="chorestore.saveChore(chore.id)" icon="mdi-content-save-outline"></v-btn>
                      <v-btn @click="chorestore.deleteChore(chore.id)" icon="mdi-delete-forever-outline"></v-btn>
                    </v-col>
                  </v-row>
                </v-container>
              </div>
            </v-expand-transition>

            <v-divider :thickness="2"></v-divider>

            <v-card-actions>
              <v-btn @click="chorestore.completeChore(chore.id)" icon="mdi-check"></v-btn>
              <v-btn @click="chorestore.snoozeChore(chore.id)" icon="mdi-alarm-snooze"></v-btn>
              <v-btn @click="chorestore.claimChore(chore.id)" icon="mdi-clipboard-account-outline"></v-btn>
              <v-btn @click="chorestore.toggleChore(chore.id)" icon="mdi-circle-off-outline"></v-btn>
              <v-btn @click="chore.expand = !chore.expand" :icon="chore.expand ? 'mdi-chevron-up' : 'mdi-chevron-down'"></v-btn>
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
  const units = computed(() => {
    return chorestore.units;
  });
  const intervals = computed(() => {
    return chorestore.intervals;
  });
</script>