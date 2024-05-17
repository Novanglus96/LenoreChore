<template>
  <v-card
    :color="localchore.active ? localchore.area.group.group_color: 'grey'"
    border
    elevation="3"
  >
    <v-card-item :title="localchore.chore_name">
      <template v-slot:subtitle>
        <v-icon
          :icon="localchore.area.area_icon"
          size="18"
          class="me-1 pb-1"
        ></v-icon>

        {{ localchore.area.area_name }}
      </template>
    </v-card-item>

    <v-card-text class="py-0">
      <v-row align="center" no-gutters v-if="localchore.active">
        <v-col
          class="text-h9"
          cols="6"
        >
          <v-progress-linear
            v-model="localchore.dirtiness"
            :color="getDirtyColor(localchore.dirtiness)"
            height="25"
            striped
          >
            <template v-slot:default="{ value }">
              <strong>{{ Math.ceil(value) }}% Dirty</strong>
            </template>
          </v-progress-linear>
        </v-col>

        <v-col cols="6" class="text-right" v-if="localchore.active">
          <span :class="localchore.isOverdue ? 'text-red' : ''">Due in <strong class="text-accent">{{ localchore.duedays }}</strong> day(s)</span>
        </v-col>
      </v-row>
    </v-card-text>

    <div class="d-flex py-3 justify-space-between">
      <v-list-item
        density="compact"
        :prepend-icon="localchore.isAssigned ? 'mdi-radiobox-marked' : 'mdi-radiobox-blank'"
      >
        <v-list-item-subtitle>{{ localchore.assignee ? localchore.assignee.fullname : "Unassigned" }}</v-list-item-subtitle>
      </v-list-item>

      <v-list-item
        density="compact"
      >
        <v-rating
          v-model="localchore.effort"
          :readonly="!expand"
          length="3"
          size="20"
          @update:modelValue="changeDetected()"
        ></v-rating>
      </v-list-item>
    </div>

    <v-expand-transition>
      <div v-if="expand">
        <v-container theme="dark" class="bg-secondary">
          <v-row dense class="bg-secondary">
            <v-col>
              <v-text-field
                v-model="localchore.chore_name"
                label="Chore Name"
                @update:modelValue="changeDetected()"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row dense class="bg-secondary">
            <v-col>
              <VueDatePicker v-model="localchore.lastCompleted" timezone="America/New_York" model-type="yyyy-MM-dd" :enable-time-picker="false" auto-apply format="yyyy-MM-dd" @update:modelValue="changeDetected(true)"></VueDatePicker>
            </v-col>
            <v-col>
              <VueDatePicker v-model="localchore.nextDue" timezone="America/New_York" model-type="yyyy-MM-dd" :enable-time-picker="false" auto-apply format="yyyy-MM-dd" @update:modelValue="changeDetected(true)"></VueDatePicker>
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
                  v-model="localchore.intervalNumber"
                  @update:modelValue="changeDetected()"
                ></v-select>
            </v-col>
            <v-col>
                <v-select
                    label="Unit(s)*"
                    required
                    :items="units"
                    v-model="localchore.unit"
                    @update:modelValue="changeDetected()"
                ></v-select>
            </v-col>
          </v-row>
          <v-row dense>
            <v-col>
              <v-checkbox
                v-model="localchore.active_months"
                label="Jan"
                color="accent"
                hide-details
                :value="1"
                @update:modelValue="changeDetected()"
              ></v-checkbox>
            </v-col>
            <v-col>
              <v-checkbox
                v-model="localchore.active_months"
                label="Feb"
                color="accent"
                hide-details
                :value="2"
                @update:modelValue="changeDetected()"
              ></v-checkbox>
            </v-col>
            <v-col>
              <v-checkbox
                v-model="localchore.active_months"
                label="Mar"
                color="accent"
                hide-details
                :value="3"
                @update:modelValue="changeDetected()"
              ></v-checkbox>
            </v-col>
            <v-col>
              <v-checkbox
                v-model="localchore.active_months"
                label="Apr"
                color="accent"
                hide-details
                :value="4"
                @update:modelValue="changeDetected()"
              ></v-checkbox>
            </v-col>
          </v-row>
          <v-row dense>
            <v-col>
              <v-checkbox
                v-model="localchore.active_months"
                label="May"
                color="accent"
                hide-details
                :value="5"
                @update:modelValue="changeDetected()"
              ></v-checkbox>
            </v-col>
            <v-col>
              <v-checkbox
                v-model="localchore.active_months"
                label="Jun"
                color="accent"
                hide-details
                :value="6"
                @update:modelValue="changeDetected()"
              ></v-checkbox>
            </v-col>
            <v-col>
              <v-checkbox
                v-model="localchore.active_months"
                label="Jul"
                color="accent"
                hide-details
                :value="7"
                @update:modelValue="changeDetected()"
              ></v-checkbox>
            </v-col>
            <v-col>
              <v-checkbox
                v-model="localchore.active_months"
                label="Aug"
                color="accent"
                hide-details
                :value="8"
                @update:modelValue="changeDetected()"
              ></v-checkbox>
            </v-col>
          </v-row>
          <v-row dense>
            <v-col>
              <v-checkbox
                v-model="localchore.active_months"
                label="Sep"
                color="accent"
                hide-details
                :value="9"
                @update:modelValue="changeDetected()"
              ></v-checkbox>
            </v-col>
            <v-col>
              <v-checkbox
                v-model="localchore.active_months"
                label="Oct"
                color="accent"
                hide-details
                :value="10"
                @update:modelValue="changeDetected()"
              ></v-checkbox>
            </v-col>
            <v-col>
              <v-checkbox
                v-model="localchore.active_months"
                label="Nov"
                color="accent"
                hide-details
                :value="11"
                @update:modelValue="changeDetected()"
              ></v-checkbox>
            </v-col>
            <v-col>
              <v-checkbox
                v-model="localchore.active_months"
                label="Dec"
                color="accent"
                hide-details
                :value="12"
                @update:modelValue="changeDetected()"
              ></v-checkbox>
            </v-col>
          </v-row>
          <v-row dense>
            <v-col>
              <v-btn @click="callSaveChore(localchore)" icon="mdi-content-save-outline" :disabled="!saveEnabled"></v-btn>
              <v-btn @click="callResetChore()" icon="mdi-arrow-u-left-top-bold" :disabled="!saveEnabled"></v-btn>
              <v-dialog
                v-model="deleteDialog"
                persistent(localchore)
                width="auto"
              >
                <template v-slot:activator="{ props }">
                  <v-btn icon="mdi-delete-forever-outline" v-bind="props"></v-btn>
                </template>
                <v-card>
                  <v-card-title class="text-h5">
                    Delete this Chore?
                  </v-card-title>
                  <v-card-text>Are you sure you want to delete <span class="text-secondary">{{ localchore.chore_name }}</span> from <span class="text-secondary">{{ localchore.area.area_name }}</span>?</v-card-text>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn
                      color="primary-darken-1"
                      variant="text"
                      @click="deleteDialog = !deleteDialog"
                    >
                      Close
                    </v-btn>
                    <v-btn
                      color="primary-darken-1"
                      variant="text"
                      @click="callDeleteChore(localchore)"
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
      <div v-if="localchore.history">
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
                    v-for="item in localchore.last_three_history_items"
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
      <v-btn @click="callCompleteChore(localchore.id, getID)" icon="mdi-check" :disabled="!localchore.active || expand"></v-btn>
      <v-dialog
        v-model="snooze"
        scrollable
        max-width="300px"
      >
        <template v-slot:activator="{ props }">
          <v-btn
            v-bind="props"
            icon="mdi-alarm-snooze"
            :disabled="!localchore.active || expand"
          ></v-btn>
        </template>
        <v-card>
          <v-card-title>Snooze Chore</v-card-title>
          <v-divider></v-divider>
          <v-card-text style="height: 500px;">
            <VueDatePicker v-model="localchore.nextDue" timezone="America/New_York" model-type="yyyy-MM-dd" :enable-time-picker="false" auto-apply format="yyyy-MM-dd"></VueDatePicker>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-btn
              color="blue darken-1"
              text
              @click="snooze = !snooze"
            >
              Close
            </v-btn>
            <v-btn
              color="blue darken-1"
              text
              @click="callSnoozeChore(localchore.id, localchore.nextDue)"
            >
              Save
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      <v-btn @click="callClaimChore(localchore.id, localchore.assignee_id)" icon="mdi-clipboard-account-outline" :disabled="!localchore.active || expand" :color="localchore.isAssigned ? 'red' : 'white'"></v-btn>
      <v-btn @click="callToggleChore(localchore.id, !localchore.active)" icon="mdi-circle-off-outline" :color="localchore.active ? 'red' : 'white'" :disabled="expand"></v-btn>
      <v-btn @click="expand = !expand" :icon="expand ? 'mdi-chevron-up' : 'mdi-chevron-down'" :disabled="saveEnabled"></v-btn>
      <v-btn @click="localchore.history = !localchore.history" icon="mdi-clipboard-text-clock-outline" :color="!localchore.history ? 'white' : 'grey'" :disabled="expand"></v-btn>
    </v-card-actions>
  </v-card>
</template>
<script setup>
import { computed, defineProps, defineEmits, ref, watch, onMounted } from 'vue';
import { useChoreStore } from '@/stores/chores';
import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
import { useUserStore } from '@/stores/user'

const expand = ref(false);
const snooze = ref(false);
const saveEnabled = ref(false);
const deleteDialog = ref(false);
const chorestore = useChoreStore();
const userstore = useUserStore();
const emit = defineEmits(['editChore', 'removeChore', 'snoozeChore', 'completeChore', 'claimChore', 'toggleActivation'])
const props = defineProps({
  chore: Array
})
const localchore = ref(null)

watch(() => props.chore, (updatedChore) => {
  localchore.value = updatedChore
})

onMounted(() => {
  localchore.value = props.chore
  console.log('chore: ', localchore.value)
})

const callResetChore = async () => {
  localchore.value.dirtiness = props.chore.dirtiness
  localchore.value.duedays = props.chore.duedays
  localchore.value.unit = props.chore.unit
  localchore.value.intervalNumber = props.chore.intervalNumber
  localchore.value.active_months = props.chore.active_months.map(month => month.id)
  localchore.value.nextDue = props.chore.nextDue
  localchore.value.lastCompleted = props.chore.lastCompleted
  localchore.value.effort = props.chore.effort
  localchore.value.chore_name = props.chore.chore_name
  saveEnabled.value = false
}
const changeDetected = async (recalcDirty) => {
  if (recalcDirty) {
    localchore.value.dirtiness = calcDirtiness()
    localchore.value.duedays = calcDueDays()
  }
  saveEnabled.value = true
}
const calcDirtiness = () => {
  const millisecondsInADay = 1000 * 60 * 60 * 24;
  const today = new Date();
  const nextDueDate = new Date(localchore.value.nextDue);
  const lastCompleted = new Date(localchore.value.lastCompleted);

  // Calculate the time difference in milliseconds
  const timesincedone = lastCompleted - today;
  const timeperiod = lastCompleted - nextDueDate;

  // Calculate the time difference in days
  const timesincedonedays = Math.ceil(timesincedone / millisecondsInADay);
  const timeperioddays = Math.ceil(timeperiod / millisecondsInADay);

  let dirtiness = 0;

  if (timeperioddays === 0) {
    dirtiness = 0;
  } else {
    dirtiness = Math.round((timesincedonedays / timeperioddays) * 100);
    dirtiness = Math.min(dirtiness, 100); // Ensure dirtiness is at most 100
  }

  return dirtiness;
}
const calcDueDays = () => {
  const today = new Date();
  const nextDueDate = new Date(localchore.value.nextDue);

  // Calculate the difference in milliseconds
  const timeDifference = nextDueDate - today;

  // Convert milliseconds to days
  const millisecondsInADay = 1000 * 60 * 60 * 24;
  const duedays = Math.ceil(timeDifference / millisecondsInADay);

  return duedays;
}
const getID = computed(() => {
  return userstore.getID;
});
const units = computed(() => {
  return chorestore.units;
});
const intervals = computed(() => {
  return chorestore.intervals;
});
const getDirtyColor = (dirtiness) => {
  let color = 'success'
  if (dirtiness <= chorestore.med_thresh) {
    color = 'success'
  } else if (dirtiness > chorestore.med_thresh && dirtiness <= chorestore.high_thresh) {
    color = 'warning'
  } else if (dirtiness > chorestore.high_thresh) {
    color = 'error'
  }
  return color
}
const callSnoozeChore = async (chore_id, next_due) => {
  emit('snoozeChore', chore_id, next_due)
  snooze.value = !snooze.value
}
const callSaveChore = async (saveChore) => {
  saveEnabled.value = false
  expand.value = false
  emit('editChore', saveChore)
}
const callDeleteChore = async (deleteChore) => {
  emit('removeChore', deleteChore)
  deleteDialog.value = !deleteDialog.value
}
const callCompleteChore = async (chore_id, user_id) => {
  emit('completeChore', chore_id, user_id)
}
const callClaimChore = async (chore_id, user_id) => {
  let assignee = null
  if (getID.value == user_id) {
    assignee = null
  } else {
    assignee = getID.value
  }
  emit('claimChore', chore_id, assignee)
}
const callToggleChore = async (chore_id, active) => {
  emit('toggleActivation', chore_id, active)
}
</script>
<style scoped>
.centered-text {
  text-align: center; /* Center-align the text */
}
</style>
