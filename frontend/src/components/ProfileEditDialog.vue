<template>
  <!-- Editing who you are.
       ─────────────────────────────────────────────────────────────────────
       The profile was the last screen in the app still editing in place. It
       was one long card with a "Save changes" button at the bottom -- and that
       button governed about a third of what was on it. Name, avatar and colour
       needed saving; the reminders switch and its time picker wrote
       immediately on change; the password lived in its own dialog. Three save
       semantics under one button, with nothing saying which was which.

       So the three are separated. This is the part that is genuinely a form,
       and it is now the same form every other edit in the app uses. -->
  <LcFormDialog
    v-model="model"
    title="Edit profile"
    icon="mdi-account-edit-outline"
    submit-label="Save changes"
    submit-icon="mdi-content-save-outline"
    :schema="schema"
    :initial-values="initialValues"
    :busy="busy"
    @submit="submitForm"
  >
    <fieldset class="lc-fieldset lc-form-group">
      <legend class="lc-form-group__legend text-body-2">Your name</legend>

      <div class="lc-profile-names">
        <Field name="first_name" v-slot="{ componentField, errorMessage }">
          <v-text-field
            v-bind="componentField"
            label="First name"
            prepend-inner-icon="mdi-account-outline"
            :counter="20"
            :error-messages="errorMessage"
          ></v-text-field>
        </Field>

        <Field name="last_name" v-slot="{ componentField, errorMessage }">
          <v-text-field
            v-bind="componentField"
            label="Last name"
            :counter="20"
            :error-messages="errorMessage"
          ></v-text-field>
        </Field>
      </div>
    </fieldset>

    <v-divider class="my-4"></v-divider>

    <fieldset class="lc-fieldset">
      <legend class="lc-form-group__legend text-body-2">Avatar</legend>
      <v-radio-group v-model="draft.male" hide-details inline aria-label="Avatar">
        <v-radio
          v-for="option in avatars"
          :key="String(option.value)"
          :value="option.value"
          :label="option.label"
        >
          <template v-slot:label>
            <span class="d-inline-flex align-center ga-2">
              <v-avatar :image="option.image" size="40"></v-avatar>
              <span>{{ option.label }}</span>
            </span>
          </template>
        </v-radio>
      </v-radio-group>
    </fieldset>

    <v-divider class="my-4"></v-divider>

    <fieldset class="lc-fieldset">
      <legend class="lc-form-group__legend text-body-2">Your colour</legend>
      <v-chip-group
        v-model="draft.user_color"
        selected-class="text-primary"
        aria-label="Your colour"
        column
        mandatory
      >
        <v-chip
          v-for="colour in USER_COLORS"
          :key="colour.value"
          :value="colour.value"
          :aria-label="colour.name"
          filter
        >
          <v-icon
            :color="colour.value"
            icon="mdi-circle"
            size="14"
            start
            aria-hidden="true"
          ></v-icon>
          {{ colour.name }}
        </v-chip>
      </v-chip-group>
    </fieldset>
  </LcFormDialog>
</template>

<script setup>
// defineModel is a compiler macro.
import { computed, ref, watch } from "vue";
import { Field } from "vee-validate";
import * as yup from "yup";
import { useUserStore } from "@/stores/user";
import { useChoreStore } from "@/stores/chores";
import { USER_COLORS, avatarOptions } from "@/utils/labels";
import LcFormDialog from "@/components/LcFormDialog.vue";

const model = defineModel({ type: Boolean, default: false });

const userstore = useUserStore();
// The GLOBAL snackbar, which is wired to the live-region announcer, so profile
// feedback is spoken. The screen used to carry a second one of its own that
// never was.
const chorestore = useChoreStore();

const busy = ref(false);

// The pickers are plain v-models, as they are in the area editor: a radio group
// and a mandatory chip group cannot be empty or malformed, so there is nothing
// for a schema to say about them.
const draft = ref(seedDraft());

function seedDraft() {
  return {
    male: userstore.male,
    user_color: userstore.user_color,
  };
}

// A snapshot taken on open rather than a computed off the store -- see
// ChoreEditDialog. vee-validate re-seeds untouched fields when initialValues
// changes, which would let a background refresh edit a half-filled form.
const initialValues = ref(seedValues());

function seedValues() {
  return {
    first_name: userstore.firstname,
    last_name: userstore.lastname,
  };
}

watch(model, open => {
  if (!open) return;
  draft.value = seedDraft();
  initialValues.value = seedValues();
});

const avatars = computed(() => avatarOptions(userstore.isChild));

const schema = yup.object({
  first_name: yup
    .string()
    .required("First name is required")
    .max(20, "First name must be 20 characters or less"),
  last_name: yup
    .string()
    .required("Last name is required")
    .max(20, "Last name must be 20 characters or less"),
});

/**
 * Closes only once the save has actually resolved.
 *
 * The old form had no pending state at all: it fired updateProfile and showed
 * a snackbar, so a slow save looked like nothing was happening and a failed
 * one put an error toast over a screen that had already gone back to showing
 * the stale values as though they had been written.
 */
const submitForm = async values => {
  if (busy.value) return;
  busy.value = true;
  try {
    await userstore.updateProfile({ ...draft.value, ...values });
    chorestore.showSnackbar("Profile updated", "success");
    model.value = false;
  } catch (error) {
    const detail = error.response?.data?.detail;
    chorestore.showSnackbar(detail || "Profile not updated", "error");
  } finally {
    busy.value = false;
  }
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

/* Side by side where there is room, stacked on a phone. */
.lc-profile-names {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0 var(--lc-space-3);
}

@media (min-width: 480px) {
  .lc-profile-names {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
