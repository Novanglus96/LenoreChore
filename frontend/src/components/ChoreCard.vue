<template>
  <v-container>
    <v-row dense v-for="chore in getChores" :key="chore.id">
        <v-col cols="12" >
          <v-card
          :color="chore.active ? 'primary' : 'grey'"
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
                  >
                    <template v-slot:default="{ value }">
                      <strong>{{ Math.ceil(value) }}% Dirty</strong>
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
                      <v-btn @click="callSaveChore(chore)" icon="mdi-content-save-outline"></v-btn>
                      <v-btn @click="callDeleteChore(chore)" icon="mdi-delete-forever-outline"></v-btn>
                    </v-col>
                  </v-row>
                </v-container>
              </div>
            </v-expand-transition>

            <v-divider :thickness="2"></v-divider>

            <v-card-actions>
              <v-btn @click="callCompleteChore(chore)" icon="mdi-check" :disabled="!chore.active"></v-btn>
              <v-btn @click="callSnoozeChore(chore)" icon="mdi-alarm-snooze" :disabled="!chore.active"></v-btn>
              <v-btn @click="callClaimChore(chore,getID)" icon="mdi-clipboard-account-outline" :disabled="!chore.active" :color="chore.isAssigned ? 'red' : 'white'"></v-btn>
              <v-btn @click="callToggleChore(chore)" icon="mdi-circle-off-outline" :color="chore.active ? 'red' : 'white'"></v-btn>
              <v-btn @click="chore.expand = !chore.expand" :icon="chore.expand ? 'mdi-chevron-up' : 'mdi-chevron-down'"></v-btn>
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

  const snackbar = ref(false);
  const snackbarText = ref('');
  const snackbarColor = ref('');
  const snackbarTimeout = ref(1500)
  const chorestore = useChoreStore();
  const userstore = useUserStore();
  const getChores = computed(() => {
    return chorestore.getChores;
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
  const callSnoozeChore = async (chore) => {
    try {
      const store = useChoreStore();
      await store.snoozeChore(chore);

      showSnackbar('Chore snoozed successfully!', 'success');
    } catch (error) {
      showSnackbar('Chore not snoozed!', 'error');
    }
  }
  const callSaveChore = async (chore) => {
    try {
      const store = useChoreStore();
      await store.saveChore(chore);

      showSnackbar('Chore saved successfully!', 'success');
    } catch (error) {
      showSnackbar('Chore not saved!', 'error');
    }
  }
  const callDeleteChore = async (chore) => {
    try {
      const store = useChoreStore();
      await store.deleteChore(chore);

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
