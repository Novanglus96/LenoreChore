<template>
  <!-- Changing your password.
       ─────────────────────────────────────────────────────────────────────
       Already a dialog, but a hand-rolled one: its own v-form inside a bare
       v-card, no toolbar, not fullscreen on a phone, and no client-side
       validation at all -- an empty field went to the server to be refused.
       On the shared shell now, like everything else. -->
  <LcFormDialog
    v-model="model"
    title="Change password"
    icon="mdi-key-outline"
    submit-label="Change password"
    submit-icon="mdi-key-outline"
    :schema="schema"
    :busy="busy"
    @submit="submitForm"
    @cancel="reset"
  >
    <!-- Anything allauth returns without a `param` is a form-level problem.
         It used to be dropped silently. -->
    <v-alert
      v-if="serverErrors.__all__"
      type="error"
      variant="tonal"
      density="compact"
      class="mb-4"
      :text="serverErrors.__all__"
    ></v-alert>

    <fieldset class="lc-fieldset lc-form-group">
      <Field name="current_password" v-slot="{ componentField, errorMessage }">
        <v-text-field
          v-bind="componentField"
          label="Current password"
          type="password"
          autocomplete="current-password"
          prepend-inner-icon="mdi-lock-outline"
          :error-messages="errorMessage || serverErrors.current_password"
        ></v-text-field>
      </Field>

      <Field name="new_password" v-slot="{ componentField, errorMessage }">
        <v-text-field
          v-bind="componentField"
          label="New password"
          type="password"
          autocomplete="new-password"
          prepend-inner-icon="mdi-lock-plus-outline"
          :error-messages="errorMessage || serverErrors.new_password"
        ></v-text-field>
      </Field>
    </fieldset>
  </LcFormDialog>
</template>

<script setup>
// defineModel is a compiler macro.
import { ref } from "vue";
import { Field } from "vee-validate";
import * as yup from "yup";
import axios from "axios";
import { useChoreStore } from "@/stores/chores";
import LcFormDialog from "@/components/LcFormDialog.vue";

const model = defineModel({ type: Boolean, default: false });

const chorestore = useChoreStore();

const busy = ref(false);
const serverErrors = ref({});

// Only presence. The password rules themselves are the server's to enforce --
// duplicating Django's validators here is how the two drift apart and start
// disagreeing about what is acceptable.
const schema = yup.object({
  current_password: yup.string().required("Enter your current password"),
  new_password: yup.string().required("Choose a new password"),
});

const reset = () => {
  serverErrors.value = {};
};

/**
 * allauth's headless endpoint, verified against the running backend:
 *   POST /_allauth/browser/v1/account/password/change
 *        {current_password, new_password}
 *   400 -> { errors: [{ message, code, param }] }
 *
 * Plain axios rather than apiClient: apiClient is baseURL'd to /api/v2 and its
 * interceptor force-logs-out on 401, which is the wrong response to a rejected
 * password attempt.
 */
const submitForm = async values => {
  if (busy.value) return;
  busy.value = true;
  serverErrors.value = {};
  try {
    await axios.post("/_allauth/browser/v1/account/password/change", values);
    model.value = false;
    reset();
    chorestore.showSnackbar("Password changed", "success");
  } catch (error) {
    const errors = error.response?.data?.errors;
    if (Array.isArray(errors) && errors.length) {
      // A field can carry SEVERAL errors -- rejecting "abc" returns both "too
      // short" and "too common". Collecting them into arrays keeps all of them;
      // assigning e.message per field would show only the last, hiding half of
      // what the user needs to fix. v-text-field takes an array.
      const mapped = {};
      for (const e of errors) {
        const key = e.param || "__all__";
        (mapped[key] ||= []).push(e.message);
      }
      // The alert renders one string.
      if (mapped.__all__) mapped.__all__ = mapped.__all__.join(" ");
      serverErrors.value = mapped;
    } else {
      serverErrors.value = { __all__: "Could not change your password." };
    }
  } finally {
    busy.value = false;
  }
};
</script>

<style scoped>
.lc-form-group {
  display: flex;
  flex-direction: column;
  gap: var(--lc-space-1);
}
</style>
