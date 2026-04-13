<template>
  <v-card color="primary" class="mx-auto" max-width="434" rounded="0" outline>
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
    <v-card-subtitle
      >{{ formData.first_name }} {{ formData.last_name }}</v-card-subtitle
    >
    <v-card-text class="py-0">
      <Form @submit="submitForm" :validation-schema="schema" v-slot="{ errors }">
        <v-container>
          <v-row>
            <v-col>
              <Field name="first_name" v-slot="{ field }">
                <v-text-field
                  v-bind="field"
                  :counter="20"
                  label="First name"
                  :error-messages="errors.first_name"
                ></v-text-field>
              </Field>
            </v-col>
            <v-col>
              <Field name="last_name" v-slot="{ field }">
                <v-text-field
                  v-bind="field"
                  :counter="20"
                  label="Last name"
                  :error-messages="errors.last_name"
                ></v-text-field>
              </Field>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              Pick Your Avatar
              <v-radio-group v-model="formData.male" v-if="!userstore.isChild">
                <v-radio :value="true"
                  ><v-avatar image="adult_male_avatar.jpg"></v-avatar
                ></v-radio>
                <v-radio :value="false"
                  ><v-avatar image="adult_female_avatar.jpg"></v-avatar
                ></v-radio>
              </v-radio-group>
              <v-radio-group v-model="formData.male" v-if="userstore.isChild">
                <v-radio :value="true"
                  ><v-avatar image="child_male_avatar.jpg"></v-avatar
                ></v-radio>
                <v-radio :value="false"
                  ><v-avatar image="child_female_avatar.jpg"></v-avatar
                ></v-radio>
              </v-radio-group>
            </v-col>
            <v-col>
              Pick Your Color
              <v-chip-group v-model="formData.user_color" mandatory column>
                <v-chip
                  v-for="color in colors"
                  :key="color.name"
                  :value="color.value"
                  filter
                >
                  <v-icon icon="mdi-square" :color="color.value"></v-icon
                  >{{ color.name }}
                </v-chip>
              </v-chip-group>
            </v-col>
          </v-row>
        </v-container>
        <v-card-actions>
          <v-btn variant="outlined">Change Password</v-btn>
          <v-btn variant="outlined" type="submit">Save Changes</v-btn>
        </v-card-actions>
      </Form>
    </v-card-text>
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
import { ref } from "vue";
import { Form, Field } from "vee-validate";
import * as yup from "yup";
import { useUserStore } from "@/stores/user";

const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("");
const snackbarTimeout = ref(1500);
const userstore = useUserStore();

const colors = ref([
  { name: "Color1", value: "#E91E63" },
  { name: "Color2", value: "#3F51B5" },
  { name: "Color3", value: "#009688" },
  { name: "Color4", value: "#CDDC39" },
]);

const schema = yup.object({
  first_name: yup
    .string()
    .required("First name is required")
    .max(20, "First name must be 20 characters or less"),
  last_name: yup
    .string()
    .required("Last name is required")
    .max(20, "Last name must be 20 characters or less"),
});

const formData = ref({
  first_name: userstore.firstname,
  last_name: userstore.lastname,
  email: userstore.email,
  male: userstore.male,
  user_color: userstore.user_color,
  avatar: userstore.avatar,
  isAdmin: userstore.isAdmin,
  id: userstore.id,
});

const submitForm = (values) => {
  try {
    userstore.updateProfile({ ...formData.value, ...values });
    showSnackbar("Profile updated successfully!", "success");
  } catch (error) {
    showSnackbar("Profile not updated!", "error");
  }
};

const showSnackbar = (text, color) => {
  snackbarText.value = text;
  snackbarColor.value = color;
  snackbar.value = true;
};
</script>
