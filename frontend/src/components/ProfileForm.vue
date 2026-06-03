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
      <Form
        @submit="submitForm"
        :validation-schema="schema"
        :initial-values="{
          first_name: formData.first_name,
          last_name: formData.last_name,
        }"
        v-slot="{ errors }"
      >
        <v-container>
          <v-row>
            <v-col>
              <Field name="first_name" v-slot="{ field }">
                <div class="text-body-2 mb-1">First name</div>
                <v-text-field
                  v-bind="field"
                  :counter="20"
                  :error-messages="errors.first_name"
                ></v-text-field>
              </Field>
            </v-col>
            <v-col>
              <Field name="last_name" v-slot="{ field }">
                <div class="text-body-2 mb-1">Last name</div>
                <v-text-field
                  v-bind="field"
                  :counter="20"
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
        <v-divider class="mb-3"></v-divider>
        <v-container>
          <template v-if="pushSupported">
            <v-row align="center" no-gutters>
              <v-col>
                <div class="text-subtitle-2">Daily reminders</div>
                <div class="text-caption text-medium-emphasis">
                  A daily summary of what's due and overdue.
                </div>
              </v-col>
              <v-col cols="auto">
                <v-switch
                  v-model="notifyEnabled"
                  color="white"
                  hide-details
                  :loading="notifyBusy"
                  @update:modelValue="onToggleReminders"
                ></v-switch>
              </v-col>
            </v-row>
            <v-row v-if="notifyEnabled" no-gutters align="center" class="mt-2">
              <v-col cols="auto" class="me-3 text-body-2">Remind me at</v-col>
              <v-col cols="auto" style="min-width: 150px">
                <VueDatePicker
                  v-model="notifyTime"
                  time-picker
                  auto-apply
                  :teleport="true"
                  @update:modelValue="onTimeChange"
                ></VueDatePicker>
              </v-col>
            </v-row>
          </template>
          <div v-else class="text-caption text-medium-emphasis">
            Daily reminders aren't supported on this device or browser.
          </div>
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
import { ref, onMounted } from "vue";
import { Form, Field } from "vee-validate";
import * as yup from "yup";
import { useUserStore } from "@/stores/user";
import { usePush } from "@/composables/pushComposable";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";

const snackbar = ref(false);
const snackbarText = ref("");
const snackbarColor = ref("");
const snackbarTimeout = ref(1500);
const userstore = useUserStore();

// ── Daily reminders ──────────────────────────────────────────────────────────
const { isSupported, subscribe, unsubscribe, getPrefs, savePrefs } = usePush();
const pushSupported = isSupported();
const notifyEnabled = ref(false);
const notifyTime = ref({ hours: 8, minutes: 0, seconds: 0 });
const notifyBusy = ref(false);

const pad = (n) => String(n).padStart(2, "0");
const timeToString = (t) => `${pad(t.hours)}:${pad(t.minutes)}:${pad(t.seconds || 0)}`;
const stringToTime = (s) => {
  const [h, m, sec] = s.split(":").map(Number);
  return { hours: h || 0, minutes: m || 0, seconds: sec || 0 };
};

onMounted(async () => {
  if (!pushSupported) return;
  try {
    const prefs = await getPrefs();
    notifyEnabled.value = prefs.notify_enabled;
    if (prefs.notify_time) notifyTime.value = stringToTime(prefs.notify_time);
  } catch {
    // Leave defaults if prefs can't be loaded.
  }
});

const onToggleReminders = async (value) => {
  notifyBusy.value = true;
  try {
    if (value) {
      await subscribe();
      await savePrefs(true, timeToString(notifyTime.value));
      showSnackbar("Daily reminders enabled!", "success");
    } else {
      await savePrefs(false, timeToString(notifyTime.value));
      await unsubscribe();
      showSnackbar("Daily reminders disabled.", "success");
    }
  } catch (error) {
    notifyEnabled.value = !value; // revert on failure
    showSnackbar(error.message || "Could not update reminders.", "error");
  } finally {
    notifyBusy.value = false;
  }
};

const onTimeChange = async () => {
  if (!notifyEnabled.value) return;
  try {
    await savePrefs(true, timeToString(notifyTime.value));
    showSnackbar("Reminder time updated.", "success");
  } catch {
    showSnackbar("Could not update reminder time.", "error");
  }
};

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
