<template>
  <v-app>
    <VueQueryDevtools />
    <AppNavigationVue />
    <v-main>
      <v-container fluid :class="$vuetify.display.smAndDown ? 'pa-0' : 'pa-2'">
        <router-view />
      </v-container>

      <!-- General action snackbar -->
      <v-snackbar
        v-model="chorestore.snackbar"
        :color="chorestore.snackbarColor"
        :timeout="chorestore.snackbarTimeout"
        content-class="centered-text"
      >
        {{ chorestore.snackbarText }}
      </v-snackbar>

      <!-- App update banner -->
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
          <v-btn color="primary" variant="text" @click="reloadPage">
            Refresh
          </v-btn>
        </template>
      </v-snackbar>

      <!-- Offline indicator -->
      <v-snackbar
        v-model="offlineStore.isOnline"
        color="warning"
        location="top"
        timeout="-1"
        :model-value="!offlineStore.isOnline"
      >
        <v-icon start>mdi-wifi-off</v-icon>
        You are offline.
        <span v-if="offlineStore.mutationQueue.length > 0">
          {{ offlineStore.mutationQueue.length }} change{{
            offlineStore.mutationQueue.length !== 1 ? "s" : ""
          }}
          pending sync.
        </span>
      </v-snackbar>

      <!-- PWA install prompt (Android/Chrome) -->
      <v-snackbar
        v-model="showInstallPrompt"
        color="primary"
        location="bottom"
        timeout="-1"
        :multi-line="true"
      >
        Install LenoreChore for a better experience!
        <template v-slot:actions>
          <v-btn variant="text" @click="showInstallPrompt = false">
            Not now
          </v-btn>
          <v-btn variant="text" @click="installApp"> Install </v-btn>
        </template>
      </v-snackbar>

      <!-- iOS install instructions -->
      <v-snackbar
        v-model="showIOSPrompt"
        color="primary"
        location="bottom"
        timeout="10000"
        :multi-line="true"
      >
        <v-icon start>mdi-apple</v-icon>
        To install: tap
        <v-icon size="small">mdi-export-variant</v-icon>
        then "Add to Home Screen"
        <template v-slot:actions>
          <v-btn variant="text" @click="showIOSPrompt = false"> Got it </v-btn>
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
import { useOfflineStore } from "@/stores/offline";
import { onMounted, computed, ref, watch, onUnmounted } from "vue";
import { VueQueryDevtools } from "@tanstack/vue-query-devtools";
import { useVersion } from "@/composables/versionComposable";
import { useSync } from "@/composables/syncComposable";
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
const offlineStore = useOfflineStore();
const vuetifyTheme = useTheme();
const router = useRouter();
const queryClient = useQueryClient();
const { prefetchVersion, version } = useVersion();
const { replayQueue } = useSync();

const showBanner = ref(false);
const showInstallPrompt = ref(false);
const showIOSPrompt = ref(false);
let deferredInstallPrompt = null;

// ── Version update ──────────────────────────────────────────────────────────
const checkVersion = computed(() => {
  return version.value && version.value.version_number !== appVersion;
});

const updateBanner = () => {
  showBanner.value = checkVersion.value;
};

// ── Session check ───────────────────────────────────────────────────────────
const checkSession = async () => {
  try {
    await axios.get("/_allauth/browser/v1/auth/session");
  } catch (error) {
    if (
      error.response &&
      error.response.status === 401 &&
      userstore.isLoggedIn
    ) {
      userstore.logoutUser();
      router.push("/login");
    }
  }
};

// ── Theme ───────────────────────────────────────────────────────────────────
vuetifyTheme.global.name.value = themeStore.isDark
  ? "myCustomDarkTheme"
  : "myCustomLightTheme";

watch(
  () => themeStore.isDark,
  (isDark) => {
    vuetifyTheme.global.name.value = isDark
      ? "myCustomDarkTheme"
      : "myCustomLightTheme";
  }
);

// ── PWA install prompt ──────────────────────────────────────────────────────
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
const isInStandaloneMode =
  window.matchMedia("(display-mode: standalone)").matches ||
  navigator.standalone;

const installApp = async () => {
  if (!deferredInstallPrompt) return;
  deferredInstallPrompt.prompt();
  const { outcome } = await deferredInstallPrompt.userChoice;
  if (outcome === "accepted") {
    deferredInstallPrompt = null;
    showInstallPrompt.value = false;
  }
};

// ── Lifecycle ───────────────────────────────────────────────────────────────
onMounted(async () => {
  // Visibility / version polling
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

  // Online / offline tracking
  const handleOnline = () => {
    offlineStore.setOnline(true);
    replayQueue();
  };
  const handleOffline = () => {
    offlineStore.setOnline(false);
  };
  window.addEventListener("online", handleOnline);
  window.addEventListener("offline", handleOffline);

  // Android/Chrome install prompt
  const handleInstallPrompt = (e) => {
    e.preventDefault();
    deferredInstallPrompt = e;
    if (!isInStandaloneMode) {
      showInstallPrompt.value = true;
    }
  };
  window.addEventListener("beforeinstallprompt", handleInstallPrompt);

  // iOS: show instructions once if not already installed
  if (isIOS && !isInStandaloneMode) {
    const dismissed = localStorage.getItem("ios-install-dismissed");
    if (!dismissed) {
      showIOSPrompt.value = true;
      localStorage.setItem("ios-install-dismissed", "1");
    }
  }

  onUnmounted(() => {
    document.removeEventListener("visibilitychange", handleVisibilityChange);
    clearInterval(sessionPoll);
    window.removeEventListener("online", handleOnline);
    window.removeEventListener("offline", handleOffline);
    window.removeEventListener("beforeinstallprompt", handleInstallPrompt);
  });

  await checkSession();
  prefetchVersion();
  updateBanner();

  // Replay any mutations that were queued in a previous offline session
  if (offlineStore.isOnline && offlineStore.mutationQueue.length > 0) {
    replayQueue();
  }
});

watch(checkVersion, (newValue) => {
  showBanner.value = newValue;
});

watch(
  () => userstore.isLoggedIn,
  (isLoggedIn) => {
    if (!isLoggedIn) {
      queryClient.clear();
    }
  }
);
</script>

<style></style>
