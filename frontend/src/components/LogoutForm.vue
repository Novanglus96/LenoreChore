<template>
  <div>
    <h2>Logout</h2>
    <button @click="logout">Logout</button>
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
