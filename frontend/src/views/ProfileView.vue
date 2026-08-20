<template>
  <!-- The profile screen.
       ─────────────────────────────────────────────────────────────────────
       Was a single card with an inline <Form> in it -- the last edit in the
       app still done in place rather than in the shared dialog. It read oddly
       for a reason: "Save changes" sat at the bottom of everything but
       governed only the top third. The reminders switch and its time picker
       wrote the instant you touched them, and the password had its own dialog.

       Summary first, then the two things that are actually settings. Editing
       happens in LcFormDialog, the same way an area or a chore is edited. -->
  <div class="profile">
    <v-container :class="$vuetify.display.smAndDown ? 'px-2 pt-2' : ''">
      <h1 class="lc-visually-hidden">Profile</h1>

      <div class="lc-profile-page">
        <v-card class="lc-profile" tag="section" :elevation="0" border>
          <div class="lc-profile__identity">
            <v-avatar
              :image="avatar"
              size="72"
              class="lc-profile__avatar flex-shrink-0"
            ></v-avatar>

            <div class="flex-grow-1 min-width-0">
              <p class="text-h6 text-truncate mb-0">{{ fullName }}</p>
              <p class="text-body-2 text-medium-emphasis text-truncate mb-2">
                {{ userstore.email }}
              </p>

              <div class="d-flex align-center ga-2 flex-wrap">
                <!-- The colour was only ever visible as a selected chip inside
                     the form. It identifies you across the app, so the profile
                     should say which one is yours without opening an editor. -->
                <v-chip size="small" variant="tonal">
                  <v-icon
                    :color="userstore.user_color"
                    icon="mdi-circle"
                    size="14"
                    start
                    aria-hidden="true"
                  ></v-icon>
                  {{ colourName }}
                </v-chip>

                <v-chip v-if="userstore.isAdmin" size="small" variant="tonal">
                  <v-icon
                    icon="mdi-shield-account-outline"
                    size="14"
                    start
                    aria-hidden="true"
                  ></v-icon>
                  Admin
                </v-chip>
              </div>
            </div>
          </div>

          <v-divider></v-divider>

          <v-card-actions class="lc-profile__actions">
            <v-btn
              variant="tonal"
              size="small"
              prepend-icon="mdi-account-edit-outline"
              @click="editOpen = true"
            >
              Edit profile
            </v-btn>
          </v-card-actions>
        </v-card>

        <v-card tag="section" :elevation="0" border aria-labelledby="settings-heading">
          <div class="lc-profile__section">
            <h2
              id="settings-heading"
              class="text-subtitle-1 font-weight-medium mb-1"
            >
              Settings
            </h2>
            <!-- Says when they save, because they do not save the way the
                 profile above them does. -->
            <p class="text-caption text-medium-emphasis mb-4">
              Saved as soon as you change them.
            </p>

            <ReminderSettings />
          </div>

          <v-divider></v-divider>

          <v-list class="py-0">
            <v-list-item
              prepend-icon="mdi-key-outline"
              append-icon="mdi-chevron-right"
              title="Change password"
              @click="passwordOpen = true"
            ></v-list-item>
          </v-list>
        </v-card>
      </div>

      <ProfileEditDialog v-model="editOpen" />
      <PasswordDialog v-model="passwordOpen" />
    </v-container>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useUserStore } from "@/stores/user";
import { USER_COLORS, avatarImage } from "@/utils/labels";
import ProfileEditDialog from "@/components/ProfileEditDialog.vue";
import PasswordDialog from "@/components/PasswordDialog.vue";
import ReminderSettings from "@/components/ReminderSettings.vue";

const userstore = useUserStore();

const editOpen = ref(false);
const passwordOpen = ref(false);

// Derived rather than copied into local state: the summary has nothing to edit,
// so it can read the store directly and update the moment a save lands.
const avatar = computed(() =>
  avatarImage(userstore.male, userstore.isChild)
);

// The store seeds both names with placeholders -- "FirstName" and "LastName".
// Greeting somebody by a placeholder is worse than falling back to the email
// the account is actually known by, and BOTH have to be stripped: dropping only
// the first leaves a profile headed "LastName".
const PLACEHOLDER_NAMES = new Set(["FirstName", "LastName"]);

const realName = value =>
  value && !PLACEHOLDER_NAMES.has(value) ? value : "";

const fullName = computed(() => {
  const name = `${realName(userstore.firstname)} ${realName(
    userstore.lastname
  )}`.trim();
  return name || userstore.email;
});

const colourName = computed(
  () =>
    USER_COLORS.find(c => c.value === userstore.user_color)?.name ||
    "No colour"
);
</script>

<style scoped>
/* One column of cards. The profile is a narrow screen by nature -- stretching
   it across a 27" monitor would put the email a foot from the avatar. */
.lc-profile-page {
  display: flex;
  flex-direction: column;
  gap: var(--lc-space-4);
  max-width: 560px;
  margin-inline: auto;
}

.lc-profile {
  background: rgb(var(--v-theme-surface));
}

/* Was color="primary" with white text on it. A neutral themed surface now,
   matching the card language everywhere else, so contrast is a property of the
   theme rather than of one hand-picked pairing. */
.lc-profile__identity {
  display: flex;
  align-items: center;
  gap: var(--lc-space-4);
  padding: var(--lc-space-4);
}

.lc-profile__avatar {
  background: rgb(var(--v-theme-surface-variant));
}

.lc-profile__actions {
  padding-inline: var(--lc-space-3);
}

.lc-profile__section {
  padding: var(--lc-space-4);
}

.min-width-0 {
  min-width: 0;
}
</style>
