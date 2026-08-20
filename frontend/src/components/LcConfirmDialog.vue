<template>
  <!-- Destructive confirmations, shared by ChoreCard and AreaCard.
       ─────────────────────────────────────────────────────────────────────
       Both wrote their own, and both got the emphasis backwards: "Close" and
       "Delete" were BOTH color="primary-darken-1" variant="text", so the
       button that destroys data looked exactly like the one that backs out,
       and neither carried the danger colour the app already defines (filthy).

       Deliberately separate from LcFormDialog: a confirmation has no fields,
       no validation and no pending-input to protect, and folding the two
       together would mean a component that is half its props at any one time. -->
  <v-dialog v-model="model" max-width="440">
    <template
      v-if="$slots.activator"
      v-slot:activator="{ props: activatorProps }"
    >
      <slot name="activator" :props="activatorProps"></slot>
    </template>

    <v-card :elevation="8">
      <v-card-title class="d-flex align-center ga-2 text-subtitle-1 font-weight-medium">
        <v-icon
          v-if="icon"
          :icon="icon"
          :color="confirmColor"
          aria-hidden="true"
        ></v-icon>
        {{ title }}
      </v-card-title>

      <v-divider></v-divider>

      <v-card-text class="text-body-2">
        <slot></slot>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-btn variant="text" :disabled="busy" @click="cancel">
          {{ cancelLabel }}
        </v-btn>
        <v-spacer></v-spacer>
        <!-- Filled and in the danger colour: this is the one action on screen
             that cannot be undone, so it should not be mistakable for the one
             that changes nothing. -->
        <v-btn
          variant="flat"
          :color="confirmColor"
          :prepend-icon="confirmIcon"
          :loading="busy"
          @click="confirm"
        >
          {{ confirmLabel }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
// defineProps/defineEmits/defineModel are compiler macros.
const model = defineModel({ type: Boolean, default: false });

defineProps({
  title: { type: String, required: true },
  icon: { type: String, default: "" },
  confirmLabel: { type: String, default: "Delete" },
  confirmIcon: { type: String, default: undefined },
  cancelLabel: { type: String, default: "Cancel" },
  /** A theme colour name. `filthy` is the app's danger band. */
  confirmColor: { type: String, default: "filthy" },
  busy: { type: Boolean, default: false },
});

const emit = defineEmits(["confirm", "cancel"]);

const confirm = () => {
  emit("confirm");
};

const cancel = () => {
  emit("cancel");
  model.value = false;
};
</script>
