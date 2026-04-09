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
import { logoutUser } from "@/composables/usersComposable";

export default {
  methods: {
    ...mapActions(useUserStore, ["logoutUser"]),

    async logout() {
      await logoutUser();
      this.logoutUser();
      this.$router.push("/login");
    },
  },
};
</script>
