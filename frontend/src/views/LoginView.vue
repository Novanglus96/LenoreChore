<template>
  <!-- Was wrapped in <header class="bg-white shadow"> with Tailwind type
       classes. Tailwind is not a dependency, so the type classes did nothing --
       but bg-white and shadow ARE Vuetify utilities, so this screen painted a
       literal white bar that stayed white in the dark theme. It is also the
       first screen anyone sees.

       The view is now a thin wrapper, matching ProfileView and GraphView:
       LoginForm owns its own card, heading and spacing. -->
  <div class="lc-login-view">
    <LoginForm @login-user="login" />
  </div>
</template>

<script setup>
import LoginForm from "@/components/LoginForm.vue";
import { useUserStore } from "@/stores/user";
import { useRouter } from "vue-router";
import { loginUser } from "@/composables/usersComposable";

const router = useRouter();
const login = async credentials => {
  const user = await loginUser(credentials);
  if (!user) return;
  const userstore = useUserStore();
  userstore.loginUser(
    user.first_name,
    user.last_name,
    user.email,
    user.is_superuser,
    user.male,
    user.id,
    user.user_color,
    user.groups,
  );
  router.push("/");
};
</script>

<style scoped>
/* Breathing room above the card, so it does not sit jammed against the app bar
   on a tall screen. Token-based rather than a Vuetify padding utility, because
   the gap wanted is between two of the spacing steps. */
.lc-login-view {
  padding: var(--lc-space-6) var(--lc-space-4) var(--lc-space-5);
}
</style>
