<template>
  <div>
    <h2>Login</h2>
    <form @submit.prevent="login">
      <div>
        <label for="username">Username:</label>
        <input type="text" id="username" v-model="credentials.username" />
      </div>
      <div>
        <label for="password">Password:</label>
        <input type="password" id="password" v-model="credentials.password" />
      </div>
      <div>
        <button type="submit">Login</button>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';
import { mapActions } from 'vuex';

export default {
  data() {
    return {
      credentials: {
        username: '',
        password: '',
      },
    };
  },
  methods: {
    ...mapActions(['setAuthToken']), // Vuex action to set the auth token

    async login() {
      try {
        const response = await axios.post('https://chores.danielleandjohn.love/api/users/login/', this.credentials);
        const { token } = response.data;

        // Store the token in local storage or Vuex store
        localStorage.setItem('authToken', token);
        this.setAuthToken(token); // Dispatch the Vuex action to set the token

        // Redirect to the desired page (e.g., dashboard)
        this.$router.push('/');
      } catch (error) {
        console.error('Login failed:', error);
        // Handle login error (e.g., show an error message)
      }
    },
  },
};
</script>
