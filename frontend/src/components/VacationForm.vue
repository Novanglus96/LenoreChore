<template>
  <v-dialog v-model="show" persistent width="1024">
    <v-card>
      <v-card-title>
        <span class="text-h5">{{
          options.vacation_mode == true
            ? "Disable Vacation Mode"
            : "Enable Vacation Mode"
        }}</span>
      </v-card-title>
      <v-card-text v-if="!options.vacation_mode">
        Enabling vacation mode pauses all chores but preserves due days. When
        back from vacation, disabling vacation mode will unpause chores and set
        the new due date based on the original due days left.</v-card-text
      >
      <v-card-text v-if="options.vacation_mode">
        Disabling vacation mode unpauses all chores and sets the new due date
        based on the due days left when vacation mode was enabled.</v-card-text
      >
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="secondary" variant="text" @click="closeDialog">
          Close
        </v-btn>
        <v-btn color="secondary" variant="text" @click="toggleVacationLocal">
          {{ options.vacation_mode ? "Disable" : "Enable" }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script setup>
import { defineEmits } from "vue";
import { useOptions } from "@/composables/optionsComposable";

const { options, toggleVacation } = useOptions();
const emit = defineEmits(["updateDialog"]);

const toggleVacationLocal = () => {
  toggleVacation();
  emit("updateDialog", false);
};
const closeDialog = () => {
  emit("updateDialog", false);
};
</script>
