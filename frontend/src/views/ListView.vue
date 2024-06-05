<template>
  <div class="chores">
    <v-container>
      <v-row dense>
        <v-col cols="12">
          <v-row dense>
            <v-col cols="8">
              <v-select
                v-model="chorestore.filters.area_id"
                label="Area"
                :items="areas"
                item-title="area_name"
                item-value="id"
                density="compact"
                clearable
              >
              </v-select>
            </v-col>
            <v-col cols="4">
              <v-checkbox
                label="Disabled?"
                v-model="chorestore.filters.inactive"
              ></v-checkbox>
            </v-col>
          </v-row>
          <v-row dense>
            <v-col>
              <v-select
                v-model="chorestore.filters.timeframe"
                label="TimeFrame"
                :items="chorestore.getDayFilter"
                item-title="name"
                item-value="days"
                density="compact"
                clearable
              >
              </v-select>
            </v-col>
            <v-col>
              <v-select
                v-model="chorestore.filters.assignee_id"
                label="Assignee"
                :items="computedUsers"
                item-title="displayName"
                item-value="id"
                density="compact"
                clearable
              >
              </v-select>
            </v-col>
          </v-row>
          <v-row dense v-if="!isLoading"
            ><v-col>
              <ChoreCard
                v-for="chore in chores"
                :chore="chore"
                :key="chore.id"
                @edit-chore="updateChore"
                @remove-chore="deleteChore"
                @complete-chore="completeChore"
                @snooze-chore="snoozeChore"
                @claim-chore="claimChore"
                @toggle-activation="toggleChore"
              /> </v-col
          ></v-row>
          <v-row dense v-else>
            <v-col cols="12">
              <v-skeleton-loader
                type="card"
                color="primary"
              ></v-skeleton-loader>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import ChoreCard from "@/components/ChoreCard.vue";
import { useChores } from "@/composables/choresComposasble";
import { useChoreStore } from "@/stores/chores";
import { useAreas } from "@/composables/areasComposable";
import { useUsers } from "@/composables/usersComposable";
import { computed } from "vue";

const chorestore = useChoreStore();
const { areas } = useAreas();
const { users } = useUsers();
const {
  chores,
  isLoading,
  editChore,
  removeChore,
  snooze,
  complete,
  toggle,
  claim,
} = useChores();

const updateChore = async updatedChore => {
  await editChore(updatedChore);
};

const completeChore = async (chore_id, user_id) => {
  let today = new Date();
  let formattedDate = today.toISOString().split("T")[0];
  let choredata = {
    id: chore_id,
    lastCompleted: formattedDate,
    completed_by_id: user_id,
  };
  await complete(choredata);
};

const snoozeChore = async (chore_id, next_due) => {
  let data = {
    id: chore_id,
    nextDue: next_due,
  };
  await snooze(data);
};

const claimChore = async (chore_id, user_id) => {
  let data = {
    id: chore_id,
    assignee_id: user_id,
  };
  await claim(data);
};

const toggleChore = async (chore_id, active) => {
  let data = {
    id: chore_id,
    active: active,
  };
  await toggle(data);
};

const deleteChore = async deletedChore => {
  await removeChore(deletedChore);
};

const computedUsers = computed(() => {
  if (!users.value) {
    return [];
  }
  return users.value.map(item => ({
    ...item,
    displayName:
      !item.fullname || item.fullname.trim() === ""
        ? item.email
        : item.fullname,
  }));
});
</script>
