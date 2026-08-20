<template>
  <!-- "Which months does this chore run in", shared by AddChoreForm and
       ChoreCard's editor.
       ─────────────────────────────────────────────────────────────────────
       Both rendered twelve v-checkboxes in a grid. That is a lot of chrome for
       a setting that is "all year" on nearly every chore, and it dominated the
       form it sat in -- on a phone it was most of the scroll between the first
       field and the Save button.

       The common case is now one control, and the twelve only appear when the
       answer is actually "some months". Shared rather than copied for the same
       reason MONTHS itself is shared: two copies drift. -->
  <fieldset class="lc-fieldset">
    <legend class="lc-months__legend text-body-2 mb-2">{{ legend }}</legend>

    <v-btn-toggle
      v-model="allYear"
      class="lc-months__toggle mb-3"
      density="comfortable"
      color="primary"
      variant="outlined"
      mandatory
      divided
    >
      <v-btn :value="true" size="small">All year</v-btn>
      <v-btn :value="false" size="small">Some months</v-btn>
    </v-btn-toggle>

    <v-expand-transition>
      <div v-if="!allYear">
        <div class="lc-months__grid" role="group" :aria-label="legend">
          <v-checkbox
            v-for="month in MONTHS"
            :key="month.value"
            v-model="selected"
            :label="month.label"
            :value="month.value"
            color="primary"
            density="compact"
            hide-details
          ></v-checkbox>
        </div>

        <!-- Selecting none would silently mean "never runs". Say so rather
             than letting it save quietly. -->
        <p v-if="selected.length === 0" class="text-caption text-warning mb-0 mt-1">
          Pick at least one month, or switch back to All year.
        </p>
      </div>
    </v-expand-transition>
  </fieldset>
</template>

<script setup>
// defineModel is a compiler macro.
import { ref, watch } from "vue";
import { MONTHS } from "@/utils/labels";

const ALL = MONTHS.map(m => m.value);

/**
 * The persisted value: an array of month numbers, 1..12.
 *
 * The default maps MONTHS inline rather than reusing the ALL const above:
 * defineModel is hoisted out of setup(), so it can reference an import but not
 * a local declaration.
 */
const selected = defineModel({
  type: Array,
  default: () => MONTHS.map(m => m.value),
});

const legend = "Active months";

// Derived from the model on mount rather than kept as a second source of
// truth, so an existing chore that runs in all twelve months opens on "All
// year" instead of showing twelve ticked boxes.
const allYear = ref(selected.value.length === ALL.length);

watch(allYear, isAll => {
  if (isAll) {
    selected.value = [...ALL];
  } else if (selected.value.length === ALL.length) {
    // Coming off "All year" with everything ticked would show twelve boxes
    // already checked, which reads as "nothing to do here". Clear them so the
    // control asks the question it just offered to ask.
    selected.value = [];
  }
});

// If every month gets ticked by hand, that IS all year -- keep the toggle
// honest rather than letting the two disagree.
watch(selected, months => {
  if (months.length === ALL.length) allYear.value = true;
});
</script>

<style scoped>
.lc-months__legend {
  color: rgb(var(--v-theme-on-surface));
}

.lc-months__toggle {
  /* v-btn-toggle inherits the pill radius from the global VBtn default, which
     leaves the divided pair looking like two unrelated chips. */
  border-radius: var(--lc-radius-sm);
}
</style>
