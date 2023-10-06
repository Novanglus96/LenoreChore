<template>
  <v-container>
    <v-row dense>
      <v-col cols="12">
        <v-chip-group v-model="filter">
          <v-chip color="primary" key="All" class="ma-2" label value="All" @click="applyFilter('All')"><v-icon start icon="mdi-all-inclusive"></v-icon>All</v-chip>
          <v-chip color="primary" v-for="area in getAreas" :key="area.area_name" class="ma-2" label :value="area.area_name" @click="applyFilter(area.area_name)"><v-icon start :icon="area.area_icon"></v-icon>{{ area.area_name }}</v-chip>
        </v-chip-group>
      </v-col>
    </v-row>
    <v-row dense v-for="chore in getFilteredChores" :key="chore.id">
        <v-col cols="12" >
          <v-card
          :color="chore.active ? chore.area.group.group_color: 'grey'"
          >
            <v-card-item :title="chore.chore_name">
              <template v-slot:subtitle>
                <v-icon
                  :icon="chore.area.area_icon"
                  size="18"
                  class="me-1 pb-1"
                ></v-icon>

                {{ chore.area.area_name }}
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
                    striped
                  >
                    <template v-slot:default="{ value }">
                      <strong>{{ Math.ceil(value) }}% Dirty</strong>
                    </template>
                  </v-progress-linear>
                </v-col>

                <v-col cols="6" class="text-right">
                  <span :class="chore.isOverdue ? 'text-red' : ''">Due in <strong class="text-accent">{{ chore.duedays }}</strong> day(s)</span>
                </v-col>
              </v-row>
            </v-card-text>

            <div class="d-flex py-3 justify-space-between">
              <v-list-item
                density="compact"
                :prepend-icon="chore.isAssigned ? 'mdi-radiobox-marked' : 'mdi-radiobox-blank'"
              >
                <v-list-item-subtitle>{{ chore.isAssigned ? chore.assignee.fullname : "Unassigned" }}</v-list-item-subtitle>
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
                <v-container theme="dark" class="bg-secondary">
                  <v-row dense class="bg-secondary">
                    <v-col>
                      <v-text-field
                        v-model="chore.chore_name"
                        label="Chore Name"
                      ></v-text-field>
                    </v-col>
                  </v-row>
                  <v-row dense class="bg-secondary">
                    <v-col>
                      <v-menu
                        v-model="chore.lastCompletedPicker"
                        :close-on-content-click="false"
                        :nudge-right="40"
                        transition="scale-transition"
                        offset-y
                        min-width="auto"
                      >
                        <template v-slot:activator="{ props }">
                          <v-text-field
                            v-model="chore.lastCompleted"
                            label="Last Completed"
                            prepend-icon="mdi-calendar"
                            readonly
                            v-bind="props"
                          ></v-text-field>
                        </template>
                        <v-date-picker
                          v-model="chore.lastCompleted"
                          hide-actions
                        ></v-date-picker>
                      </v-menu>
                    </v-col>
                    <v-col>
                      <v-menu
                        v-model="chore.nextDuePicker"
                        :close-on-content-click="false"
                        :nudge-right="40"
                        transition="scale-transition"
                        offset-y
                        min-width="auto"
                      >
                        <template v-slot:activator="{ props }">
                          <v-text-field
                            v-model="chore.nextDue"
                            label="Next Due"
                            prepend-icon="mdi-calendar"
                            readonly
                            v-bind="props"
                          ></v-text-field>
                        </template>
                        <v-date-picker
                          v-model="chore.nextDue"
                          hide-actions
                        ></v-date-picker>
                      </v-menu>
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
                      <v-btn @click="callSaveChore(chore)" icon="mdi-content-save-outline"></v-btn>
                      <v-dialog
                        v-model="chore.delete"
                        persistent
                        width="auto"
                      >
                        <template v-slot:activator="{ props }">
                          <v-btn icon="mdi-delete-forever-outline" v-bind="props"></v-btn>
                        </template>
                        <v-card>
                          <v-card-title class="text-h5">
                            Delete this Chore?
                          </v-card-title>
                          <v-card-text>Are you sure you want to delete <span class="text-secondary">{{ chore.chore_name }}</span> from <span class="text-secondary">{{ chore.area.area_name }}</span>?</v-card-text>
                          <v-card-actions>
                            <v-spacer></v-spacer>
                            <v-btn
                              color="primary-darken-1"
                              variant="text"
                              @click="chore.delete = false"
                            >
                              Close
                            </v-btn>
                            <v-btn
                              color="primary-darken-1"
                              variant="text"
                              @click="callDeleteChore(chore)"
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
            <v-expand-transition>
              <div v-if="chore.history">
                <v-container class="bg-secondary" theme="dark">
                  <v-row dense>
                    <v-col>
                      <v-table class="bg-secondary">
                        <thead>
                        <tr>
                            <th class="text-left">
                            Date
                            </th>
                            <th class="text-left">
                            Completed By
                            </th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr
                            v-for="item in chore.last_three_history_items"
                            :key="item.id"
                            :style="{ backgroundColor: secondary }"
                        >
                            <td>{{ item.completed_date }}</td>
                            <td>{{ item.completed_by }}</td>
                        </tr>
                        </tbody>
                    </v-table>
                    </v-col>
                  </v-row>
                </v-container>
              </div>
            </v-expand-transition>

            <v-divider :thickness="2"></v-divider>

            <v-card-actions>
              <v-btn @click="callCompleteChore(chore)" icon="mdi-check" :disabled="!chore.active"></v-btn>
              <v-dialog
                v-model="chore.snoozedialog"
                scrollable
                max-width="300px"
              >
                <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    icon="mdi-alarm-snooze"
                    :disabled="!chore.active"
                  ></v-btn>
                </template>
                <v-card>
                  <v-card-title>Snooze Chore</v-card-title>
                  <v-divider></v-divider>
                  <v-card-text style="height: 500px;">
                    <v-menu
                        v-model="chore.snoozePicker"
                        :close-on-content-click="false"
                        :nudge-right="40"
                        transition="scale-transition"
                        offset-y
                        min-width="auto"
                      >
                        <template v-slot:activator="{ props }">
                          <v-text-field
                            v-model="chore.nextDue"
                            label="Next Due"
                            prepend-icon="mdi-calendar"
                            readonly
                            v-bind="props"
                          ></v-text-field>
                        </template>
                        <v-date-picker
                          v-model="chore.nextDue"
                          hide-actions
                        ></v-date-picker>
                      </v-menu>
                  </v-card-text>
                  <v-divider></v-divider>
                  <v-card-actions>
                    <v-btn
                      color="blue darken-1"
                      text
                      @click="chore.snoozedialog = false"
                    >
                      Close
                    </v-btn>
                    <v-btn
                      color="blue darken-1"
                      text
                      @click="callSnoozeChore(chore)"
                    >
                      Save
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
              <v-btn @click="callClaimChore(chore,getID)" icon="mdi-clipboard-account-outline" :disabled="!chore.active" :color="chore.isAssigned ? 'red' : 'white'"></v-btn>
              <v-btn @click="callToggleChore(chore)" icon="mdi-circle-off-outline" :color="chore.active ? 'red' : 'white'"></v-btn>
              <v-btn @click="callExpandChore(chore)" :icon="chore.expand ? 'mdi-chevron-up' : 'mdi-chevron-down'"></v-btn>
              <v-btn @click="chore.history = !chore.history" icon="mdi-clipboard-text-clock-outline" :color="!chore.history ? 'white' : 'grey'"></v-btn>
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
  import { computed, ref } from 'vue';
  import { useChoreStore } from '@/stores/chores';
  import { useUserStore } from '@/stores/user';
  import { useRoute, useRouter } from 'vue-router';
  import { VDatePicker } from 'vuetify/labs/VDatePicker';

  const route = useRoute();
  const router = useRouter();
  const filter = ref(route.params.areaName);
  const snackbar = ref(false);
  const snackbarText = ref('');
  const snackbarColor = ref('');
  const snackbarTimeout = ref(1500);
  const chorestore = useChoreStore();
  const userstore = useUserStore();
  const getFilteredChores = computed(() => {
    return chorestore.getFilteredChores(filter.value);
  });
  const applyFilter = (areaName) => {
    filter.value = areaName;
    router.push({ name: 'listfilter', params: { areaName }});
  }
  const getAreas = computed(() => {
    return chorestore.getAreas;
  });
  const getID = computed(() => {
    return userstore.getID;
  });
  const units = computed(() => {
    return chorestore.units;
  });
  const intervals = computed(() => {
    return chorestore.intervals;
  });
  const callExpandChore = async (chore) => {
    if (chore.expand) {
      chore.expand = false
      const store = useChoreStore()
      await store.fetchChores()
    } else {
      chore.expand = true
    }
  }
  const callSnoozeChore = async (chore) => {
    try {
      const store = useChoreStore();
      await store.snoozeChore(chore);
      chore.snoozedialog = false
      showSnackbar('Chore snoozed successfully!', 'success');
    } catch (error) {
      showSnackbar('Chore not snoozed!', 'error');
    }
  }
  const callSaveChore = async (chore) => {
    try {
      const store = useChoreStore();
      await store.saveChore(chore);
      chore.expand = false
      showSnackbar('Chore saved successfully!', 'success');
    } catch (error) {
      showSnackbar('Chore not saved!', 'error');
    }
  }
  const callDeleteChore = async (chore) => {
    try {
      const store = useChoreStore();
      await store.deleteChore(chore);
      chore.delete = false;
      showSnackbar('Chore deleted successfully!', 'success');
    } catch (error) {
      showSnackbar('Chore not deleted!', 'error');
    }
  }
  const callCompleteChore = async (chore) => {
    try {
      const store = useChoreStore();
      await store.completeChore(chore);

      showSnackbar('Chore completed successfully!', 'success');
    } catch (error) {
      showSnackbar('Chore not completed!', 'error');
    }
  }
  const callClaimChore = async (chore,user) => {
    try {
      const store = useChoreStore();
      await store.claimChore(chore,user);

      showSnackbar('Chore claimed/unclaimed successfully!', 'success');
    } catch (error) {
      showSnackbar('Chore not claimed/unclaimed!', 'error');
    }
  }
  const callToggleChore = async (chore) => {
    try {
      const store = useChoreStore();
      await store.toggleChore(chore);
      if (chore.active){
        showSnackbar('Chore deactivated successfully!', 'success');
      } else {
        showSnackbar('Chore activated successfully!', 'success');
      }
    } catch (error) {
      if (chore.active){
        showSnackbar('Chore not deactivated!', 'error');
      } else {
        showSnackbar('Chore not activated!', 'error');
      }
    }
  }
  const showSnackbar = (text, color) => {
    snackbarText.value = text;
    snackbarColor.value = color;
    snackbar.value = true;
  }
</script>
<style scoped>
.centered-text {
  text-align: center; /* Center-align the text */
}
</style>
