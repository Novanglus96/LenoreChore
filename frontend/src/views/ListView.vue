<template>
  <div class="chores">
      <v-container>
        <v-row dense v-if="!isLoading">
          <v-col cols="12">
            <v-row dense>
              <v-col cols="8">
                <v-select
                  v-model="areafilter"
                  label="Area"
                  :items="areas"
                  item-title="area_name"
                  item-value="id"
                  @select="applyFilter(areafilter, dayfilter, assigneefilter, showDisabled)"
                  density="compact"
                >
                </v-select>
              </v-col>
              <v-col cols="4">
                <v-checkbox label="Disabled?" v-model="showDisabled" @change="applyFilter(areafilter, dayfilter, assigneefilter, showDisabled)"></v-checkbox>
              </v-col>
            </v-row>
            <v-row dense>
              <v-col>
                <v-select
                  v-model="dayfilter"
                  label="TimeFrame"
                  :items="chorestore.getDayFilter"
                  item-title="name"
                  item-value="days"
                  @select="applyFilter(areafilter, dayfilter, assigneefilter, showDisabled)"
                  density="compact"
                >
                </v-select>
              </v-col>
              <v-col>
                <v-select
                  v-model="assigneefilter"
                  label="Assignee"
                  :items="users"
                  item-title="fullname"
                  item-value="value"
                  @select="applyFilter(areafilter, dayfilter, assigneefilter, showDisabled)"
                  density="compact"
                >
                </v-select>
              </v-col>
            </v-row>
            <ChoreCard v-for="chore in chores" :chore="chore" :key="chore.id" @edit-chore="updateChore" @remove-chore="deleteChore" @complete-chore="completeChore" @snooze-chore="snoozeChore" @claim-chore="claimChore" @toggle-activation="toggleChore"/>
          </v-col>
        </v-row>
        <v-row dense v-else>
          <v-col cols="12">
            <v-skeleton-loader type="card" color="primary"></v-skeleton-loader>
          </v-col>
        </v-row>
      </v-container>
  </div>
</template>

<script setup>
import ChoreCard from '@/components/ChoreCard.vue'
import { useChores } from '@/composables/choresComposasble';
import { useChoreStore } from '@/stores/chores'
import { useAreas } from '@/composables/areasComposable';
import { useUsers } from '@/composables/usersComposable'
import { useHistoryItems } from '@/composables/historyItemsComposable'
import { ref } from 'vue'
import { useRoute } from 'vue-router';

const route = useRoute();
const areafilter = ref(route.params.areaName);
const dayfilter = ref(-99);
const assigneefilter = ref(0);
const showDisabled = ref(false);
const chorestore = useChoreStore();
const { areas } = useAreas();
const { users } = useUsers();
const { chores, isLoading, editChore, removeChore, snooze, complete, toggle, claim } = useChores();
const { addHistoryItem } = useHistoryItems();

const updateChore = async (updatedChore) => {
  try {
    await editChore(updatedChore)
    chorestore.showSnackbar('Chore updated', 'success')
  } catch {
    chorestore.showSnackbar('Chore not updated', 'error')
  }
}

const completeChore = async (chore_id, user_id) => {
  let today = new Date();
  let formattedDate = today.toISOString().split('T')[0];
  let choredata = {
    id: chore_id,
    lastCompleted: formattedDate
  }
  let historydata = {
    completed_date: formattedDate,
    completed_by: user_id,
    chore_id: chore_id
  }
  try {
    await complete(choredata)
    await addHistoryItem(historydata)
    chorestore.showSnackbar('Chore completed', 'success')
  } catch {
    chorestore.showSnackbar('Chore not completed', 'error')
  }
}

const snoozeChore = async (chore_id, next_due) => {
  let data = {
    id: chore_id,
    nextDue: next_due
  }
  try {
    await snooze(data)
    chorestore.showSnackbar('Chore snoozed', 'success')
  } catch {
    chorestore.showSnackbar('Chore not snoozed', 'error')
  }

}

const claimChore = async (chore_id, user_id) => {
  let data = {
    id: chore_id,
    assignee_id: user_id
  }
  try {
    await claim(data)
    chorestore.showSnackbar('Chore claimed/unclaimed', 'success')
  } catch {
    chorestore.showSnackbar('Chore not claimed/unclaimed', 'error')
  }
}

const toggleChore = async (chore_id, active) => {
  let data = {
    id: chore_id,
    active: active
  }
  try {
    await toggle(data)
    chorestore.showSnackbar('Chore toggled', 'success')
  } catch {
    chorestore.showSnackbar('Chore not toggled', 'error')
  }
}

const deleteChore = async (deletedChore) => {
  try {
    await removeChore(deletedChore)
    chorestore.showSnackbar('Chore deleted', 'success')
  } catch {
    chorestore.showSnackbar('Chore not deleted', 'error')
  }
}

</script>
