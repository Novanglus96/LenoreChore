<template>
  <v-container>
      <v-row dense>
        <v-col cols="12">
          <v-card
          color="red"
          >
            <v-card-item title="Clean sink and counters">
              <template v-slot:subtitle>
                Kitchen
              </template>
            </v-card-item>

            <v-card-text class="py-0">
              <v-row align="center" no-gutters>
                <v-col
                  class="text-h9"
                  cols="6"
                >
                  <v-progress-linear
                    v-model="skill"
                    color="blue-grey"
                    height="25"
                  >
                    <template v-slot:default="{ value }">
                      <strong>{{ Math.ceil(value) }}%</strong>
                    </template>
                  </v-progress-linear>
                </v-col>

                <v-col cols="6" class="text-right">
                  Due in 1 day(s)
                </v-col>
              </v-row>
            </v-card-text>

            <div class="d-flex py-3 justify-space-between">
              <v-list-item
                density="compact"
                prepend-icon="mdi-radiobox-blank"
              >
                <v-list-item-subtitle>Unclaimed</v-list-item-subtitle>
              </v-list-item>

              <v-list-item
                density="compact"
              >
                <v-rating
                  v-model="rating"
                  readonly
                  length="3"
                  size="20"
                ></v-rating>
              </v-list-item>
            </div>

            <v-expand-transition>
              <div v-if="expand">
                
                <v-list class="bg-transparent">
                  <v-list-item title="Last Completed" subtitle="01/12/24">
                  </v-list-item>
                  <v-list-item title="Next Due" subtitle="12/01/24">
                  </v-list-item>
                  <v-list-item title="Repeats Every" subtitle="3 Weeks">
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
              <v-btn @click="expand = !expand" :icon="expand ? 'mdi-chevron-up' : 'mdi-chevron-down'">
              </v-btn>
              
            </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-row dense>
        <v-col cols="12">
          <v-card
          color="primary"
          theme="dark"
          >
            <v-card-item title="Clean Toilet">
              <template v-slot:subtitle>
                Upstairs Bathroom
              </template>
            </v-card-item>

            <v-card-text class="py-0">
              <v-row align="center" no-gutters>
                <v-col
                  class="text-h9"
                  cols="6"
                >
                  <v-progress-linear
                    v-model="skill"
                    color="blue-grey"
                    height="25"
                  >
                    <template v-slot:default="{ value }">
                      <strong>{{ Math.ceil(value) }}%</strong>
                    </template>
                  </v-progress-linear>
                </v-col>

                <v-col cols="6" class="text-right">
                  Due in 1 day(s)
                </v-col>
              </v-row>
            </v-card-text>

            <div class="d-flex py-3 justify-space-between">
              <v-list-item
                density="compact"
                prepend-icon="mdi-radiobox-marked"
              >
                <v-list-item-subtitle>John Adams</v-list-item-subtitle>
              </v-list-item>

              <v-list-item
                density="compact"
              >
                <v-rating
                  v-model="rating"
                  readonly
                  length="3"
                  size="20"
                ></v-rating>
              </v-list-item>
            </div>

            <v-expand-transition>
              <div v-if="expand2">
                
                <v-list class="bg-transparent">
                  <v-list-item title="Last Completed" subtitle="01/12/24">
                  </v-list-item>
                  <v-list-item title="Next Due" subtitle="12/01/24">
                  </v-list-item>
                  <v-list-item title="Repeats Every" subtitle="3 Weeks">
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
              <v-btn @click="expand2 = !expand2" :icon="expand2 ? 'mdi-chevron-up' : 'mdi-chevron-down'">
              </v-btn>
              
            </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-row dense>
        <v-col cols="12">
          <v-card
          color="green"
          >
            <v-card-item title="Change Sheets">
              <template v-slot:subtitle>
                Bedroom
              </template>
            </v-card-item>

            <v-card-text class="py-0">
              <v-row align="center" no-gutters>
                <v-col
                  class="text-h9"
                  cols="6"
                >
                  <v-progress-linear
                    v-model="skill"
                    color="blue-grey"
                    height="25"
                  >
                    <template v-slot:default="{ value }">
                      <strong>{{ Math.ceil(value) }}%</strong>
                    </template>
                  </v-progress-linear>
                </v-col>

                <v-col cols="6" class="text-right">
                  Due in 1 day(s)
                </v-col>
              </v-row>
            </v-card-text>

            <div class="d-flex py-3 justify-space-between">
              <v-list-item
                density="compact"
                prepend-icon="mdi-radiobox-blank"
              >
                <v-list-item-subtitle>Unclaimed</v-list-item-subtitle>
              </v-list-item>

              <v-list-item
                density="compact"
              >
                <v-rating
                  v-model="rating"
                  readonly
                  length="3"
                  size="20"
                ></v-rating>
              </v-list-item>
            </div>

            <v-expand-transition>
              <div v-if="expand3">
                
                <v-list class="bg-transparent">
                  <v-list-item title="Last Completed" subtitle="01/12/24">
                  </v-list-item>
                  <v-list-item title="Next Due" subtitle="12/01/24">
                  </v-list-item>
                  <v-list-item title="Repeats Every" subtitle="3 Weeks">
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
              <v-btn @click="expand3 = !expand3" :icon="expand3 ? 'mdi-chevron-up' : 'mdi-chevron-down'">
              </v-btn>
              
            </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
<script >
  export default {
    data: () => ({
      labels: { 0: 'SU', 1: 'MO', 2: 'TU', 3: 'WED', 4: 'TH', 5: 'FR', 6: 'SA' },
      expand: false,
      expand2: false,
      expand3: false,
      time: 0,
      forecast: [
        { day: 'Tuesday', icon: 'mdi-white-balance-sunny', temp: '24\xB0/12\xB0' },
        { day: 'Wednesday', icon: 'mdi-white-balance-sunny', temp: '22\xB0/14\xB0' },
        { day: 'Thursday', icon: 'mdi-cloud', temp: '25\xB0/15\xB0' },
      ],
      skill: 20,
      rating: 2,
    }),
  }
</script>