<template>
  <v-app>
    <VueQueryDevtools />
    <AppNavigationVue />
    <v-main>
      <v-container fluid class="pa-2">
        <router-view />
      </v-container>
      <v-snackbar
        v-model="chorestore.snackbar"
        :color="chorestore.snackbarColor"
        :timeout="chorestore.snackbarTimeout"
        content-class="centered-text"
      >
        {{ chorestore.snackbarText }}
      </v-snackbar>
      <v-snackbar
        v-model="showBanner"
        color="secondary"
        location="top"
        timeout="-1"
        :multi-line="true"
      >
        There's been an update to the application. Click refresh to get the new
        changes!
        <template v-slot:actions>
          <v-btn color="primary" variant="text" @click="showBanner = false">
            Close
          </v-btn>
          <v-btn color="primary" variant="text" @click="reloadPage"
            >Refresh</v-btn
          >
        </template>
      </v-snackbar>
    </v-main>
  </v-app>
</template>

<script setup>
import AppNavigationVue from "./views/AppNavigation.vue";
import { useChoreStore } from "@/stores/chores";
import { useUserStore } from "@/stores/user";
import { useThemeStore } from "@/stores/theme";
import { onMounted, computed, ref, watch, onUnmounted } from "vue";
import { VueQueryDevtools } from "@tanstack/vue-query-devtools";
import { useVersion } from "@/composables/versionComposable";
import { useQueryClient } from "@tanstack/vue-query";
import { useRouter } from "vue-router";
import { useTheme } from "vuetify";
import axios from "axios";
import { version as appVersion } from "../package.json";

const reloadPage = () => {
  window.location.reload();
};
const chorestore = useChoreStore();
const userstore = useUserStore();
const themeStore = useThemeStore();
const vuetifyTheme = useTheme();
const router = useRouter();
const queryClient = useQueryClient();
const { prefetchVersion, version } = useVersion();
const showBanner = ref(false);

const checkVersion = computed(() => {
  return version.value && version.value.version_number !== appVersion;
});

const updateBanner = () => {
  showBanner.value = checkVersion.value;
};

const checkSession = async () => {
  try {
    await axios.get("/_allauth/browser/v1/auth/session");
  } catch (error) {
    if (error.response && error.response.status === 401 && userstore.isLoggedIn) {
      userstore.logoutUser();
      router.push("/login");
    }
  }
};

// Apply persisted theme on load
vuetifyTheme.global.name.value = themeStore.isDark
  ? "myCustomDarkTheme"
  : "myCustomLightTheme";

watch(
  () => themeStore.isDark,
  isDark => {
    vuetifyTheme.global.name.value = isDark
      ? "myCustomDarkTheme"
      : "myCustomLightTheme";
  }
);

onMounted(async () => {
  const handleVisibilityChange = () => {
    if (!document.hidden) {
      checkSession();
      prefetchVersion().then(() => {
        updateBanner();
      });
    }
  };

  document.addEventListener("visibilitychange", handleVisibilityChange);

  const sessionPoll = setInterval(checkSession, 5 * 60 * 1000);

  onUnmounted(() => {
    document.removeEventListener("visibilitychange", handleVisibilityChange);
    clearInterval(sessionPoll);
  });

  await checkSession();
  prefetchVersion();
  updateBanner();
});

watch(checkVersion, newValue => {
  showBanner.value = newValue;
});

watch(
  () => userstore.isLoggedIn,
  isLoggedIn => {
    if (!isLoggedIn) {
      queryClient.clear();
    }
  }
);
</script>

<style></style>
