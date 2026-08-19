<template>
  <v-card class="lc-login mx-auto" max-width="440" :elevation="0" border>
    <div class="text-center pt-8 px-6">
      <v-img
        src="logov2.png"
        max-width="180"
        class="mx-auto mb-4"
        alt=""
      ></v-img>
      <h1 class="text-h6 mb-1">Welcome back</h1>
      <p class="text-body-2 text-medium-emphasis mb-0">
        Sign in to see what needs doing.
      </p>
    </div>

    <v-card-text class="pt-6">
      <Form @submit="login" :validation-schema="schema" v-slot="{ errors }">
        <!-- Both fields used a PLACEHOLDER in place of a label. A placeholder
             is not a label: it disappears the moment you type, it is rendered
             at low contrast by design, and it is not announced as the field's
             name. Real labels, and the loose "Account" / "Password" headings
             that stood in for them are gone. -->
        <Field name="email" v-slot="{ componentField }">
          <v-text-field
            v-bind="componentField"
            label="Email address"
            type="email"
            autocomplete="username"
            prepend-inner-icon="mdi-email-outline"
            :error-messages="errors.email"
          ></v-text-field>
        </Field>

        <Field name="password" v-slot="{ componentField }">
          <v-text-field
            v-bind="componentField"
            label="Password"
            :type="visible ? 'text' : 'password'"
            autocomplete="current-password"
            prepend-inner-icon="mdi-lock-outline"
            :error-messages="errors.password"
          >
            <!-- Was append-inner-icon with @click:append-inner. That renders a
                 bare icon with no accessible name and no button semantics, so
                 it was unreachable by keyboard and silent to a screen reader. -->
            <template v-slot:append-inner>
              <v-btn
                :icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
                :aria-label="visible ? 'Hide password' : 'Show password'"
                :aria-pressed="visible ? 'true' : 'false'"
                variant="text"
                density="comfortable"
                @click="visible = !visible"
              >
                <v-icon :icon="visible ? 'mdi-eye-off' : 'mdi-eye'"></v-icon>
              </v-btn>
            </template>
          </v-text-field>
        </Field>

        <v-btn
          block
          class="mt-2"
          color="primary"
          size="large"
          variant="flat"
          type="submit"
        >
          Log in
        </v-btn>
      </Form>
    </v-card-text>
  </v-card>
</template>

<script setup>
// defineEmits is a compiler macro; importing it warns on every build.
import { ref } from "vue";
import { Form, Field } from "vee-validate";
import * as yup from "yup";

const emit = defineEmits(["loginUser"]);

const visible = ref(false);

const schema = yup.object({
  email: yup
    .string()
    .required("Email is required")
    .email("Must be a valid email"),
  password: yup.string().required("Password is required"),
});

const login = values => {
  emit("loginUser", { email: values.email, password: values.password });
};
</script>

<style scoped>
.lc-login {
  background: rgb(var(--v-theme-surface));
}
</style>
