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
import { mapActions } from 'vuex';

export default {
  methods: {
    ...mapActions(['clearAuthToken']), // Vuex action to clear the auth token

    logout() {
      // Clear the token from local storage or Vuex
      localStorage.removeItem('authToken');
      this.clearAuthToken(); // Dispatch the Vuex action to clear the token

      // Redirect to the login page or another desired page
      this.$router.push('/login');
    },
  },
};
</script>
