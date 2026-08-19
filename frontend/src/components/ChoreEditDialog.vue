<template>
  <!-- Editing a chore.
       ─────────────────────────────────────────────────────────────────────
       This was an inline panel that expanded the card in place, and it had
       every problem the add forms had before LcFormDialog was written -- plus
       two of its own.

       On a phone the panel pushed the card's own title off the top of the
       viewport, so you were editing something you could no longer see, and
       Save sat below the month picker with nothing pinning it. Worse, the
       chevron that closed the panel was disabled the moment anything changed:
       type one character and the way out went dead, leaving Save (which
       commits) or an `mdi-arrow-u-left-top-bold` icon that reads as "discard"
       to nobody. Opening the panel also disabled four buttons in the card's
       action bar with no explanation of why.

       A dialog answers all of it: fullscreen on a phone with the chore's name
       in the toolbar, a pinned action bar, Cancel always live, and a card
       behind it that never changes shape. It also picks up the validation the
       inline panel never had -- an empty chore name saved happily, while the
       add form and the area editor both refused it. -->
  <LcFormDialog
    v-model="model"
    :title="`Edit ${chore.chore_name}`"
    icon="mdi-pencil-outline"
    submit-label="Save changes"
    submit-icon="mdi-content-save-outline"
    :schema="schema"
    :initial-values="initialValues"
    @submit="submit"
    @cancel="close"
  >
    <!-- The guard that holds a remote update back is on the card, which owns
         the draft; this says so. The wording names both buttons in the action
         bar rather than a "reset" that no longer exists. -->
    <v-alert
      v-if="remoteUpdatePending"
      type="warning"
      variant="tonal"
      density="compact"
      role="status"
      aria-live="polite"
      class="mb-4"
      text="Someone else changed this chore while you were editing. Saving keeps
            your version; cancelling keeps theirs."
    ></v-alert>

    <fieldset class="lc-fieldset lc-form-group">
      <legend class="lc-form-group__legend text-body-2">What</legend>

      <Field name="chore_name" v-slot="{ componentField, errorMessage }">
        <v-text-field
          v-bind="componentField"
          label="Chore name"
          prepend-inner-icon="mdi-format-title"
          :error-messages="errorMessage"
          @update:modelValue="touch()"
        ></v-text-field>
      </Field>
    </fieldset>

    <v-divider class="my-4"></v-divider>

    <!-- Two date pickers sat side by side with no labels at all, so which one
         was "last completed" and which was "next due" came down to
         remembering the order. VueDatePicker renders no element carrying the
         id its `uid` prop implies, so a <label for> would point at nothing --
         labelling the group is what actually reaches the control, the same way
         the snooze dialog does it. -->
    <fieldset class="lc-fieldset lc-form-group">
      <legend class="lc-form-group__legend text-body-2">Dates</legend>

      <div class="lc-date-field">
        <div :id="lastDoneLabelId" class="text-body-2 mb-1">Last completed</div>
        <div role="group" :aria-labelledby="lastDoneLabelId">
          <VueDatePicker
            v-model="draft.lastCompleted"
            :timezone="userTimezone"
            model-type="yyyy-MM-dd"
            :enable-time-picker="false"
            auto-apply
            teleport
            format="yyyy-MM-dd"
            @update:modelValue="touch()"
          ></VueDatePicker>
        </div>
      </div>

      <div class="lc-date-field">
        <div :id="nextDueLabelId" class="text-body-2 mb-1">Next due</div>
        <div role="group" :aria-labelledby="nextDueLabelId">
          <VueDatePicker
            v-model="draft.nextDue"
            :timezone="userTimezone"
            model-type="yyyy-MM-dd"
            :enable-time-picker="false"
            auto-apply
            teleport
            format="yyyy-MM-dd"
            @update:modelValue="touch()"
          ></VueDatePicker>
        </div>
      </div>
    </fieldset>

    <v-divider class="my-4"></v-divider>

    <fieldset class="lc-fieldset lc-form-group">
      <!-- "Repeats" was a bare v-col with a word in it, styled as body text
           and tied to nothing. Same fieldset/legend the add form uses, so the
           two read alike. -->
      <legend class="lc-form-group__legend text-body-2">How often</legend>

      <div class="lc-form-row">
        <Field name="intervalNumber" v-slot="{ componentField, errorMessage }">
          <v-select
            v-bind="componentField"
            label="Every"
            :items="intervals"
            :error-messages="errorMessage"
            @update:modelValue="touch()"
          ></v-select>
        </Field>

        <Field name="unit" v-slot="{ componentField, errorMessage }">
          <v-select
            v-bind="componentField"
            label="Unit"
            :items="units"
            :error-messages="errorMessage"
            @update:modelValue="touch()"
          ></v-select>
        </Field>
      </div>
    </fieldset>

    <v-divider class="my-4"></v-divider>

    <LcMonthPicker v-model="draft.active_months" @update:modelValue="touch()" />

    <v-divider class="my-4"></v-divider>

    <!-- The stars lived on the collapsed card as a control that did nothing
         until the editor was open (`:readonly="!expand"`), which is a mode
         with no visible cue. They are a form field, so they live in the form,
         and they carry the same wording the add form gives them. -->
    <fieldset class="lc-fieldset lc-form-group">
      <legend class="lc-form-group__legend text-body-2">How much work</legend>
      <div class="d-flex align-center ga-3">
        <v-rating
          v-model="draft.effort"
          length="3"
          size="24"
          density="compact"
          active-color="accent"
          :item-aria-label="'Effort level {0} of 3'"
          @update:modelValue="touch()"
        ></v-rating>
        <span class="text-body-2 text-medium-emphasis">
          {{ effortLabel(draft.effort) }}
        </span>
      </div>
    </fieldset>
  </LcFormDialog>
</template>

<script setup>
// defineProps/defineEmits/defineModel are compiler macros.
import { computed, ref, watch } from "vue";
import { Field } from "vee-validate";
import * as yup from "yup";
import VueDatePicker from "@vuepic/vue-datepicker";
import { useChoreStore } from "@/stores/chores";
import { effortLabel } from "@/utils/labels";
import LcFormDialog from "@/components/LcFormDialog.vue";
import LcMonthPicker from "@/components/LcMonthPicker.vue";

const model = defineModel({ type: Boolean, default: false });

const props = defineProps({
  chore: { type: Object, required: true },
  /** True when a remote change arrived while this draft was dirty. */
  remoteUpdatePending: { type: Boolean, default: false },
});

const emit = defineEmits(["submit", "dirty", "cancel"]);

const chorestore = useChoreStore();

// Was hardcoded to "America/New_York" on all three pickers before the card was
// last touched, so every date it wrote was read as Eastern regardless of where
// the user actually is. Falls back to the browser's own zone.
const userTimezone =
  Intl.DateTimeFormat().resolvedOptions().timeZone || undefined;

// Unique per instance: a grid of cards mounts many of these, and a repeated id
// makes aria-labelledby point at whichever one rendered first.
const lastDoneLabelId = computed(() => `chore-${props.chore.id}-last-done`);
const nextDueLabelId = computed(() => `chore-${props.chore.id}-next-due`);

// The fields vee-validate owns, versus the ones held as plain state. Dates,
// months and effort are pickers rather than inputs -- there is nothing to
// validate on them beyond what LcMonthPicker already says in place.
const draft = ref(seedDraft());

function seedDraft() {
  return {
    lastCompleted: props.chore.lastCompleted,
    nextDue: props.chore.nextDue,
    active_months: [...(props.chore.active_months ?? [])],
    effort: props.chore.effort,
  };
}

// A snapshot taken when the dialog opens, NOT a computed off props.chore.
// vee-validate treats `initialValues` as reactive and re-seeds any field the
// user has not touched yet, so leaving it live would let a remote change edit
// half the open form out from under whoever is filling it in -- the same class
// of bug the card's watch exists to prevent, arriving through a side door.
const initialValues = ref(seedValues());

function seedValues() {
  return {
    chore_name: props.chore.chore_name,
    intervalNumber: props.chore.intervalNumber,
    unit: props.chore.unit,
  };
}

const schema = yup.object({
  // The inline editor had no schema at all, so "" saved happily.
  chore_name: yup.string().required("Give the chore a name"),
  intervalNumber: yup
    .number()
    .required("Pick how often it repeats")
    .typeError("Pick how often it repeats"),
  unit: yup.string().required("Pick a unit"),
});

const units = computed(() => chorestore.units);
const intervals = computed(() => chorestore.intervals);

// Reseed every time it opens, so an editor closed with Cancel does not come
// back holding the abandoned draft. LcFormDialog remounts its <Form> with
// `initialValues`, which covers the validated half.
watch(model, open => {
  if (!open) return;
  draft.value = seedDraft();
  initialValues.value = seedValues();
});

// Re-seed from a remote change only when the dialog is shut. While it is open
// the card holds updates back, and this would overwrite them anyway.
watch(
  () => props.chore,
  () => {
    if (model.value) return;
    draft.value = seedDraft();
    initialValues.value = seedValues();
  }
);

// `v-bind="componentField"` already carries vee-validate's own onUpdate:modelValue;
// Vue merges same-named handlers into an array rather than replacing, so both
// run. Without this the card's guard would only notice the pickers changing and
// would happily overwrite a half-typed name.
const touch = () => emit("dirty");

const close = () => {
  emit("cancel");
};

/**
 * Dirtiness and days-to-due are derived server-side on read, but the card
 * renders straight from whatever the mutation puts in the cache -- so a chore
 * whose dates just changed would show the OLD bar and the OLD due chip until
 * the next refetch landed. Recomputing them here keeps the optimistic copy
 * honest, exactly as the inline editor did.
 */
const derived = () => {
  const msPerDay = 1000 * 60 * 60 * 24;
  const today = new Date();
  const nextDue = new Date(draft.value.nextDue);
  const lastCompleted = new Date(draft.value.lastCompleted);

  const period = Math.ceil((lastCompleted - nextDue) / msPerDay);
  const elapsed = Math.ceil((lastCompleted - today) / msPerDay);

  return {
    dirtiness: period === 0 ? 0 : Math.min(Math.round((elapsed / period) * 100), 100),
    duedays: Math.ceil((nextDue - today) / msPerDay),
  };
};

const submit = values => {
  if (!draft.value.active_months.length) {
    // Saving none would mean a chore that never comes due. LcMonthPicker says
    // so in place; this is what stops it being saved anyway.
    chorestore.showSnackbar("Pick at least one active month", "warning");
    return;
  }

  emit("submit", {
    ...props.chore,
    ...draft.value,
    ...values,
    ...derived(),
  });
  model.value = false;
};
</script>

<style scoped>
.lc-form-group__legend {
  color: rgb(var(--v-theme-on-surface));
  margin-bottom: var(--lc-space-2);
}

.lc-form-group {
  display: flex;
  flex-direction: column;
  gap: var(--lc-space-1);
}

/* Stacked, not side by side. Two date pickers on one line are ~150px each on a
   phone, which is narrower than the calendar they open. */
.lc-date-field + .lc-date-field {
  margin-top: var(--lc-space-3);
}

.lc-form-row {
  display: flex;
  gap: var(--lc-space-3);
}

.lc-form-row > *:first-child {
  flex: 0 0 40%;
}

.lc-form-row > *:last-child {
  flex: 1 1 auto;
  min-width: 0;
}
</style>
