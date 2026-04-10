<template>
  <div>
    <v-card
      class="mx-auto pa-12 pb-8"
      elevation="8"
      max-width="448"
      rounded="lg"
    >
      <div class="text-subtitle-1 text-medium-emphasis">Account</div>
      <Form @submit="login" :validation-schema="schema" v-slot="{ errors }">
        <Field name="email" v-slot="{ field }">
          <v-text-field
            v-bind="field"
            density="compact"
            placeholder="Email address"
            prepend-inner-icon="mdi-email-outline"
            variant="outlined"
            :error-messages="errors.email"
          ></v-text-field>
        </Field>

        <div
          class="text-subtitle-1 text-medium-emphasis d-flex align-center justify-space-between"
        >
          Password
        </div>

        <Field name="password" v-slot="{ field }">
          <v-text-field
            v-bind="field"
            :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
            :type="visible ? 'text' : 'password'"
            density="compact"
            placeholder="Enter your password"
            prepend-inner-icon="mdi-lock-outline"
            variant="outlined"
            @click:append-inner="visible = !visible"
            :error-messages="errors.password"
          ></v-text-field>
        </Field>

        <v-card class="mb-12" color="surface-variant" variant="tonal">
          <v-card-text class="text-medium-emphasis text-caption"> </v-card-text>
        </v-card>

        <v-btn
          block
          class="mb-8"
          color="blue"
          size="large"
          variant="tonal"
          type="submit"
        >
          Log In
        </v-btn>
      </Form>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { Form, Field } from "vee-validate";
import * as yup from "yup";

const emit = defineEmits(["loginUser"]);

const visible = ref(false);

const schema = yup.object({
  email: yup.string().required("Email is required").email("Must be a valid email"),
  password: yup.string().required("Password is required"),
});

const login = (values) => {
  emit("loginUser", { email: values.email, password: values.password });
};
</script>
