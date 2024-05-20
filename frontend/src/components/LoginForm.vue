<template>
  <div>
    <v-card
      class="mx-auto pa-12 pb-8"
      elevation="8"
      max-width="448"
      rounded="lg"
    >
      <div class="text-subtitle-1 text-medium-emphasis">Account</div>
      <v-form @submit.prevent="login">
        <v-text-field
          v-model="credentials.username"
          density="compact"
          placeholder="Email address"
          prepend-inner-icon="mdi-email-outline"
          variant="outlined"
        ></v-text-field>

        <div
          class="text-subtitle-1 text-medium-emphasis d-flex align-center justify-space-between"
        >
          Password
        </div>

        <v-text-field
          v-model="credentials.password"
          :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
          :type="visible ? 'text' : 'password'"
          density="compact"
          placeholder="Enter your password"
          prepend-inner-icon="mdi-lock-outline"
          variant="outlined"
          @click:append-inner="visible = !visible"
        ></v-text-field>

        <v-card class="mb-12" color="surface-variant" variant="tonal">
          <v-card-text class="text-medium-emphasis text-caption">
            <!-- TODO : Implement Login Error Messages
          {{ this.errormsg }} -->
          </v-card-text>
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
      </v-form>
    </v-card>
  </div>
</template>

<script setup>
import { defineEmits, ref } from "vue";

const emit = defineEmits(["loginUser"]);

const credentials = ref({
  username: "",
  password: "",
});

const login = async () => {
  emit("loginUser", credentials.value);
};
</script>
