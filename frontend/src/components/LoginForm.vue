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

      <div class="text-subtitle-1 text-medium-emphasis d-flex align-center justify-space-between">
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

      <v-card
        class="mb-12"
        color="surface-variant"
        variant="tonal"
      >
        <v-card-text class="text-medium-emphasis text-caption">
          {{ this.errormsg }}
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

<script>
import axios from 'axios';
import { mapActions } from 'pinia';
import { useUserStore } from '../stores/user';

export default {
  data() {
    return {
      credentials: {
        username: '',
        password: '',
      },
      errormsg: '',
    };
  },
  computed: {
    
  },
  methods: {
    ...mapActions(useUserStore, ['loginUser']),

    async login() {
      try {
        const response = await axios.post('https://chores.danielleandjohn.love/api/users/login/', this.credentials);
        const { token } = response.data.token;

        // Store the token in local storage or Vuex store
        localStorage.setItem('authToken', token);
        this.loginUser(response.data.firstname, response.data.lastname, response.data.email, response.data.isAdmin, response.data.male, response.data.id, response.data.user_color, response.data.groups)

        //this.userStore.picture = response.data.picture
        
        // Redirect to the desired page (e.g., dashboard)
        this.$router.push('/');
      } catch (error) {
        console.error('Login failed:', error);
        // Handle login error (e.g., show an error message)
        this.errormsg = 'Login failed'
      }
    },
  },
};
</script>
