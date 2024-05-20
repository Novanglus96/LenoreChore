<template>
  <div>
    <v-btn
      block
      class="mb-8"
      color="blue"
      size="large"
      variant="tonal"
      type="submit"
      @click="logout"
    >
      Log Out
    </v-btn>
  </div>
</template>

<script>
import { mapActions } from "pinia";
import { useUserStore } from "../stores/user";

export default {
  methods: {
    ...mapActions(useUserStore, ["logoutUser"]),

    logout() {
      // Clear the token from local storage or Vuex
      localStorage.removeItem("authToken");
      this.logoutUser();
      // Redirect to the login page or another desired page
      this.$router.push("/login");
    },
  },
};
</script>
