<template>
  <v-form v-model="valid">
    <v-container>
      <v-row>
        <v-col
          cols="12"
          md="4"
        >
          <v-text-field
            v-model="firstname"
            :rules="nameRules"
            :counter="20"
            label="First name"
            required
          ></v-text-field>
        </v-col>

        <v-col
          cols="12"
          md="4"
        >
          <v-text-field
            v-model="lastname"
            :rules="nameRules"
            :counter="20"
            label="Last name"
            required
          ></v-text-field>
        </v-col>

        <v-col
          cols="12"
          md="4"
        >
          <v-text-field
            v-model="email"
            :rules="emailRules"
            label="E-mail"
            required
          ></v-text-field>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>
<script setup>
    import { ref } from 'vue'
    import { useUserStore } from '@/stores/user';

  const userstore = useUserStore();

    const valid = ref(false)
    const firstname =  ref(userstore.firstname)
    const lastname =  ref(userstore.lastname)
    const nameRules = ref([
        v => !!v || 'Name is required',
        v => v.length <= 20 || 'Name must be less than 20 characters',
      ])
    const email = ref(userstore.email)
    const emailRules = ref([
        v => !!v || 'E-mail is required',
        v => /.+@.+/.test(v) || 'E-mail must be valid',
      ])
</script>