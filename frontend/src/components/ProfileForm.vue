<template>
  <v-card class="lc-profile mx-auto" max-width="560" :elevation="0" border>
    <!-- Was color="primary" with white text on it. Now a neutral themed
         surface, matching the card language everywhere else, so contrast is a
         property of the theme rather than of one hand-picked pairing. -->
    <div class="d-flex align-center ga-4 pa-4">
      <v-avatar :image="avatarPreview" size="72" class="lc-profile__avatar">
      </v-avatar>
      <div class="min-width-0">
        <p class="text-subtitle-1 font-weight-medium text-truncate mb-0">
          {{ formData.first_name }} {{ formData.last_name }}
        </p>
        <p class="text-body-2 text-medium-emphasis text-truncate mb-0">
          {{ formData.email }}
        </p>
      </div>
    </div>

    <v-divider></v-divider>

    <v-card-text>
      <Form
        @submit="submitForm"
        :validation-schema="schema"
        :initial-values="{
          first_name: formData.first_name,
          last_name: formData.last_name,
        }"
        v-slot="{ errors }"
      >
        <div class="lc-profile__names">
          <Field name="first_name" v-slot="{ field }">
            <v-text-field
              v-bind="field"
              label="First name"
              :counter="20"
              :error-messages="errors.first_name"
            ></v-text-field>
          </Field>
          <Field name="last_name" v-slot="{ field }">
            <v-text-field
              v-bind="field"
              label="Last name"
              :counter="20"
              :error-messages="errors.last_name"
            ></v-text-field>
          </Field>
        </div>

        <!-- Both pickers previously offered options with NO readable name: the
             avatars were bare images in a radio label, and the colours were
             called Color1..Color4. The group headings were loose <div>s, so
             neither was tied to the control it headed either. -->
        <fieldset class="lc-fieldset mb-4">
          <legend class="text-subtitle-2 mb-2">Avatar</legend>
          <v-radio-group
            v-model="formData.male"
            hide-details
            inline
            aria-label="Avatar"
          >
            <v-radio
              v-for="option in avatarOptions"
              :key="String(option.value)"
              :value="option.value"
              :label="option.label"
            >
              <template v-slot:label>
                <span class="d-inline-flex align-center ga-2">
                  <v-avatar :image="option.image" size="40"></v-avatar>
                  <span>{{ option.label }}</span>
                </span>
              </template>
            </v-radio>
          </v-radio-group>
        </fieldset>

        <fieldset class="lc-fieldset mb-2">
          <legend class="text-subtitle-2 mb-2">Your colour</legend>
          <v-chip-group
            v-model="formData.user_color"
            selected-class="text-primary"
            aria-label="Your colour"
            column
            mandatory
          >
            <v-chip
              v-for="colour in colors"
              :key="colour.value"
              :value="colour.value"
              :aria-label="colour.name"
              filter
            >
              <v-icon
                :color="colour.value"
                icon="mdi-circle"
                size="14"
                start
                aria-hidden="true"
              ></v-icon>
              {{ colour.name }}
            </v-chip>
          </v-chip-group>
        </fieldset>

        <v-divider class="my-4"></v-divider>

        <template v-if="pushSupported">
          <div class="d-flex align-center ga-3">
            <div class="flex-grow-1 min-width-0">
              <p class="text-subtitle-2 mb-0">Daily reminders</p>
              <p class="text-caption text-medium-emphasis mb-0">
                A daily summary of what's due and overdue.
              </p>
            </div>
            <v-switch
              v-model="notifyEnabled"
              color="primary"
              density="compact"
              hide-details
              aria-label="Daily reminders"
              :loading="notifyBusy"
              @update:modelValue="onToggleReminders"
            ></v-switch>
          </div>

          <div v-if="notifyEnabled" class="d-flex align-center ga-3 mt-2">
            <span id="remind-at-label" class="text-body-2">Remind me at</span>
            <div
              role="group"
              aria-labelledby="remind-at-label"
              style="min-width: 150px"
            >
              <VueDatePicker
                v-model="notifyTime"
                time-picker
                auto-apply
                :dark="theme.global.current.value.dark"
                :teleport="true"
                @update:modelValue="onTimeChange"
              ></VueDatePicker>
            </div>
          </div>
        </template>
        <p v-else class="text-caption text-medium-emphasis mb-0">
          Daily reminders aren't supported on this device or browser.
        </p>

        <v-card-actions class="px-0 pt-4">
          <!-- Was a button with no click handler at all: it looked like a
               feature and did nothing. Now wired to allauth's headless
               password-change endpoint. -->
          <v-btn
            variant="text"
            prepend-icon="mdi-key-outline"
            @click="passwordDialog = true"
          >
            Change password
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn variant="flat" color="primary" type="submit">
            Save changes
          </v-btn>
        </v-card-actions>
      </Form>
    </v-card-text>

    <v-dialog v-model="passwordDialog" max-width="440">
      <v-card>
        <v-card-title>Change password</v-card-title>
        <v-divider></v-divider>
        <v-form @submit.prevent="submitPassword">
          <v-card-text class="d-flex flex-column ga-2">
            <v-text-field
              v-model="passwordForm.current_password"
              label="Current password"
              type="password"
              autocomplete="current-password"
              :error-messages="passwordErrors.current_password"
            ></v-text-field>
            <v-text-field
              v-model="passwordForm.new_password"
              label="New password"
              type="password"
              autocomplete="new-password"
              :error-messages="passwordErrors.new_password"
            ></v-text-field>
            <v-alert
              v-if="passwordErrors.__all__"
              type="error"
              density="compact"
              :text="passwordErrors.__all__"
            ></v-alert>
          </v-card-text>
          <v-divider></v-divider>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn variant="text" @click="closePasswordDialog">Cancel</v-btn>
            <v-btn
              variant="flat"
              color="primary"
              type="submit"
              :loading="passwordBusy"
            >
              Change password
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { Form, Field } from "vee-validate";
import * as yup from "yup";
import { useUserStore } from "@/stores/user";
import { useChoreStore } from "@/stores/chores";
import { usePush } from "@/composables/pushComposable";
import { useTheme } from "vuetify";
import axios from "axios";
import VueDatePicker from "@vuepic/vue-datepicker";
import "@vuepic/vue-datepicker/dist/main.css";

const userstore = useUserStore();
const theme = useTheme();

// Uses the GLOBAL snackbar rather than a second one local to this component.
// The global one is wired to the live-region announcer, so profile feedback is
// now spoken; the local copy never was, and having two meant the same class of
// message behaved differently depending on which screen you were on.
const chorestore = useChoreStore();
const showSnackbar = (text, color) => chorestore.showSnackbar(text, color);

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

// The VALUES are persisted in CustomUser.user_color and must not change --
// only the labels do. "Color1".."Color4" told a sighted user nothing and a
// screen reader user less than nothing, since the swatch beside them is
// decorative. These are the Material palette names for the same four hexes.
const colors = ref([
  { name: "Pink", value: "#E91E63" },
  { name: "Indigo", value: "#3F51B5" },
  { name: "Teal", value: "#009688" },
  { name: "Lime", value: "#CDDC39" },
]);

// Each avatar radio used to contain ONLY an image, so both options announced
// as blank and were indistinguishable without sight. The label describes the
// illustration rather than asserting anything about the person choosing it.
const avatarOptions = computed(() => {
  const child = userstore.isChild;
  return [
    {
      value: true,
      label: "Masculine",
      image: child ? "child_male_avatar.jpg" : "adult_male_avatar.jpg",
    },
    {
      value: false,
      label: "Feminine",
      image: child ? "child_female_avatar.jpg" : "adult_female_avatar.jpg",
    },
  ];
});

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

// Live avatar preview that follows the selected gender (and child role),
// so picking a different avatar updates the picture immediately.
const avatarPreview = computed(() => {
  const child = userstore.isChild;
  if (formData.value.male) {
    return child ? "child_male_avatar.jpg" : "adult_male_avatar.jpg";
  }
  return child ? "child_female_avatar.jpg" : "adult_female_avatar.jpg";
});

// Must be async and must await: updateProfile is async, so the previous
// non-awaited call could never be caught here and the success snackbar fired
// unconditionally -- including on a failed save.
const submitForm = async (values) => {
  try {
    await userstore.updateProfile({ ...formData.value, ...values });
    showSnackbar("Profile updated successfully!", "success");
  } catch (error) {
    const detail = error.response?.data?.detail;
    showSnackbar(detail || "Profile not updated!", "error");
  }
};



// ── Change password ─────────────────────────────────────────────────────────
// allauth's headless endpoint, verified against the running backend:
//   POST /_allauth/browser/v1/account/password/change {current_password, new_password}
//   400 -> { errors: [{ message, code, param }] }
// Plain axios rather than apiClient: apiClient is baseURL'd to /api/v2 and its
// interceptor force-logs-out on 401, which is the wrong response to a rejected
// password attempt.
const passwordDialog = ref(false);
const passwordBusy = ref(false);
const passwordForm = ref({ current_password: "", new_password: "" });
const passwordErrors = ref({});

const closePasswordDialog = () => {
  passwordDialog.value = false;
  passwordForm.value = { current_password: "", new_password: "" };
  passwordErrors.value = {};
};

const submitPassword = async () => {
  passwordBusy.value = true;
  passwordErrors.value = {};
  try {
    await axios.post(
      "/_allauth/browser/v1/account/password/change",
      passwordForm.value
    );
    closePasswordDialog();
    showSnackbar("Password changed.", "success");
  } catch (error) {
    // allauth returns per-field errors; anything without a `param` is a
    // form-level problem and is surfaced above the buttons rather than being
    // silently dropped.
    const errors = error.response?.data?.errors;
    if (Array.isArray(errors) && errors.length) {
      // A field can carry SEVERAL errors -- rejecting "abc" returns both "too
      // short" and "too common". Collecting them into arrays keeps all of them;
      // assigning e.message per field would have shown only the last, hiding
      // half of what the user needs to fix. v-text-field takes an array.
      const mapped = {};
      for (const e of errors) {
        const key = e.param || "__all__";
        (mapped[key] ||= []).push(e.message);
      }
      // The form-level slot renders one string.
      if (mapped.__all__) mapped.__all__ = mapped.__all__.join(" ");
      passwordErrors.value = mapped;
    } else {
      passwordErrors.value = { __all__: "Could not change your password." };
    }
  } finally {
    passwordBusy.value = false;
  }
};

</script>

<style scoped>
.lc-profile {
  background: rgb(var(--v-theme-surface));
}

.lc-profile__avatar {
  background: rgb(var(--v-theme-surface-variant));
}

/* Side by side where there is room, stacked on a phone — previously a fixed
   two-column v-row, which squeezed both name fields at any width. */
.lc-profile__names {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0 var(--lc-space-3);
}

@media (min-width: 480px) {
  .lc-profile__names {
    grid-template-columns: 1fr 1fr;
  }
}

/* A fieldset carries a border and padding by default; the legend is what makes
   the group announce, so only the chrome is removed. */
.lc-fieldset {
  border: 0;
  padding: 0;
  margin: 0;
  min-inline-size: 0;
}

.min-width-0 {
  min-width: 0;
}
</style>
