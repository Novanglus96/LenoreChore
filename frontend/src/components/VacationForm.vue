<template>
  <!-- Was width="1024" and fullscreen on mobile — an enormous surface for what
       is a two-line confirmation. -->
  <v-dialog v-model="show" max-width="480">
    <v-card>
      <v-card-title class="d-flex align-center ga-2">
        <v-icon icon="mdi-island" aria-hidden="true"></v-icon>
        {{ isOn ? "Disable vacation mode" : "Enable vacation mode" }}
      </v-card-title>

      <v-divider></v-divider>

      <v-card-text>
        <template v-if="!isOn">
          Pauses every chore but keeps its remaining due days. When you turn
          vacation mode off again, each chore resumes with the days it had left.
        </template>
        <template v-else>
          Unpauses every chore and sets each new due date from the days it had
          left when vacation mode started.
        </template>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-spacer></v-spacer>
        <!-- Both buttons used to be color="secondary" variant="text", so the
             action and the escape hatch looked identical. -->
        <v-btn variant="text" @click="closeDialog">Cancel</v-btn>
        <v-btn
          variant="flat"
          color="primary"
          :prepend-icon="isOn ? 'mdi-play' : 'mdi-pause'"
          @click="toggleVacationLocal"
        >
          {{ isOn ? "Resume chores" : "Pause chores" }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
// defineEmits/defineModel are compiler macros; importing them warns on build.
import { computed } from "vue";
import { useOptions } from "@/composables/optionsComposable";

const { options, toggleVacation } = useOptions();
const emit = defineEmits(["updateDialog"]);

// `show` was used by v-model in the template and DECLARED NOWHERE. The dialog
// still opened -- but only because the parent's v-model passes `modelValue`,
// which fell through $attrs onto the root v-dialog. That is an accident, not a
// binding: it breaks silently the moment this component grows a second root
// element or sets inheritAttrs: false. Declared properly now.
const show = defineModel({ type: Boolean, default: false });

// `options` is undefined until its query resolves, and this dialog is mounted
// by AppNavigation on every page. Reading options.vacation_mode directly threw
// during first paint — the same bug fixed in AppNavigation, in the component
// it renders.
const isOn = computed(() => options.value?.vacation_mode === true);

const toggleVacationLocal = () => {
  toggleVacation();
  emit("updateDialog", false);
};
const closeDialog = () => {
  emit("updateDialog", false);
};
</script>
