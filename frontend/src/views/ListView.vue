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
            <ChoreCard v-for="chore in chores" :chore="chore" :key="chore.id" @edit-chore="updateChore" @remove-chore="deleteChore"/>
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
const { chores, isLoading, editChore, removeChore } = useChores();

const updateChore = async (updatedChore) => {
  try {
    await editChore(updatedChore)
    chorestore.showSnackbar('Chore updated', 'success')
  } catch {
    chorestore.showSnackbar('Chore not updated', 'error')
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
