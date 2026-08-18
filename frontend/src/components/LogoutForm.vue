<template>
  <!-- Was a bare color="blue" tonal block button on an otherwise empty page --
       the only blue left in the app, three components after the palette said
       otherwise, and with no heading of its own once the scaffold <header> that
       used to carry the <h1> came out.

       It is a confirmation now, built in the same language as LoginForm:
       borderless card, own heading, and a text escape hatch beside a filled
       primary action so the two do not read as equals. -->
  <v-card class="mx-auto" max-width="440" :elevation="0" border>
    <v-card-text class="text-center pa-6">
      <v-avatar size="56" class="lc-logout__badge mb-3">
        <v-icon icon="mdi-logout" size="28" color="primary"></v-icon>
      </v-avatar>
      <h1 class="text-h6 mb-1">Sign out?</h1>
      <p class="text-body-2 text-medium-emphasis mb-0">
        You'll need to log in again to see what needs doing.
      </p>
    </v-card-text>

    <v-divider></v-divider>

    <v-card-actions>
      <v-btn variant="text" :disabled="busy" @click="cancel">
        Stay signed in
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn
        variant="flat"
        color="primary"
        prepend-icon="mdi-logout"
        :loading="busy"
        @click="logout"
      >
        Log out
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
// Was the Options API with mapActions, the last component in the app still on
// it. Converted to <script setup> to match everything around it.
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import { logoutUser } from "@/composables/usersComposable";

const router = useRouter();
const userstore = useUserStore();

// The button had no pending state, so a slow round trip looked like a dead
// click and invited a second one.
const busy = ref(false);

const logout = async () => {
  if (busy.value) return;
  busy.value = true;
  try {
    // `logoutUser` names two different things: the API call imported above, and
    // the store action that clears local session state. Both have to run.
    await logoutUser();
    userstore.logoutUser();
    router.push("/login");
  } finally {
    busy.value = false;
  }
};

const cancel = () => {
  router.push("/");
};
</script>

<style scoped>
.lc-logout__badge {
  background: rgb(var(--v-theme-surface-variant));
}
</style>
