<template>
  <v-card
    color="primary"
    class="mx-auto"
    max-width="434"
    rounded="0"
    outline
  >
    <v-avatar
        :image="formData.avatar"
        size="80"
        color="white"
        tonal
        rounded="0"
    ></v-avatar>
    <v-card-title>
      {{ formData.email }}
    </v-card-title>
      <v-card-subtitle>{{ formData.first_name }} {{ formData.last_name }}</v-card-subtitle>
      <v-card-text class="py-0">
        <v-form v-model="valid">
          <v-container>
            <v-row>
              <v-col>
                <v-text-field
                  v-model="formData.first_name"
                  :rules="nameRules"
                  :counter="20"
                  label="First name"
                  required
                ></v-text-field>
              </v-col>
              <v-col>
                <v-text-field
                  v-model="formData.last_name"
                  :rules="nameRules"
                  :counter="20"
                  label="Last name"
                  required
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col>
                Pick Your Avatar
                <v-radio-group v-model="formData.male">
                  <v-radio :value="true"><v-avatar image="male_avatar.jpg"></v-avatar></v-radio>
                  <v-radio :value="false"><v-avatar image="female_avatar.jpg"></v-avatar></v-radio>
                </v-radio-group>
              </v-col>
              <v-col>
                Pick Your Color
                <v-chip-group
                    v-model="formData.user_color"
                    mandatory
                    column
                >
                    <v-chip 
                    v-for="color in colors"
                    :key="color.name"
                    :value="color.value"
                    filter
                    >
                    <v-icon icon="mdi-square" :color="color.value"></v-icon>{{ color.name }}
                    </v-chip>
                </v-chip-group>
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn variant="outlined">Change Password</v-btn>
        <v-btn variant="outlined" @click="submitForm">Save Changes</v-btn>
      </v-card-actions>
      <v-snackbar
        v-model="snackbar"
        :color="snackbarColor"
        :timeout="snackbarTimeout"
        content-class="centered-text"
      >
        {{ snackbarText }}
      </v-snackbar>
  </v-card>
</template>
<script setup>
  import { ref } from 'vue'
  import { useUserStore } from '@/stores/user';

  const snackbar = ref(false);
  const snackbarText = ref('');
  const snackbarColor = ref('');
  const snackbarTimeout = ref(1500);
  const userstore = useUserStore();
  const colors = ref([
    {
      name: "Color1",
      value: "#E91E63",
    },
    {
      name: "Color2",
      value: "#3F51B5",
    },
    {
      name: "Color3",
      value: "#009688",
    },
    {
      name: "Color4",
      value: "#CDDC39",
    },
  ],
  );

  const valid = ref(false)
  const nameRules = ref([
      v => !!v || 'Name is required',
      v => v.length <= 20 || 'Name must be less than 20 characters',
    ])

  const formData = ref({
        first_name: userstore.firstname,
        last_name: userstore.lastname,
        email: userstore.email,
        male: userstore.male,
        user_color: userstore.user_color,
        avatar: userstore.avatar,
        isAdmin: userstore.isAdmin,
        id: userstore.id,
      })
  
  const submitForm = async () => {
    try {
      userstore.updateProfile(formData.value);
      showSnackbar('Profile updated successfully!', 'success');
    } catch (error) {
      // Handle errors (e.g., show an error message)
      console.log('Error:', error);
      showSnackbar('Profile not updated!', 'error');
    }
  }

  const showSnackbar = (text, color) => {
    snackbarText.value = text;
    snackbarColor.value = color;
    snackbar.value = true;
  }
</script>