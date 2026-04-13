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
          <v-btn variant="text" @click="dismissInstall"> Not now </v-btn>
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
import { usePrefetch } from "@/composables/prefetchComposable";
import { useQueryClient } from "@tanstack/vue-query";
import { useRouter } from "vue-router";
import { useTheme } from "vuetify";
import axios from "axios";
import { version as appVersion } from "../package.json";

const reloadPage = async () => {
  // Clear TanStack Query cache so stale data isn't served after reload
  queryClient.clear();

  // Clear all Workbox/SW caches so the new assets are fetched from the network
  if ("caches" in window) {
    const cacheNames = await caches.keys();
    await Promise.all(cacheNames.map(name => caches.delete(name)));
  }

  // Tell the waiting SW (if any) to take control immediately, then reload
  if ("serviceWorker" in navigator) {
    const registration = await navigator.serviceWorker.getRegistration();
    if (registration?.waiting) {
      registration.waiting.postMessage({ type: "SKIP_WAITING" });
      await new Promise(resolve => navigator.serviceWorker.addEventListener("controllerchange", resolve, { once: true }));
    }
  }

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
const { prefetchCriticalData } = usePrefetch();

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

const INSTALL_DISMISSED_KEY = "pwa-install-dismissed";
const INSTALL_DISMISSED_DAYS = 7;

function installDismissed() {
  return !!localStorage.getItem(INSTALL_DISMISSED_KEY);
}

function setInstallDismissed() {
  const expires = Date.now() + INSTALL_DISMISSED_DAYS * 24 * 60 * 60 * 1000;
  localStorage.setItem(INSTALL_DISMISSED_KEY, String(expires));
}

function clearExpiredDismissal() {
  const val = localStorage.getItem(INSTALL_DISMISSED_KEY);
  if (val && Date.now() > Number(val)) {
    localStorage.removeItem(INSTALL_DISMISSED_KEY);
  }
}

const dismissInstall = () => {
  showInstallPrompt.value = false;
  setInstallDismissed();
};

const installApp = async () => {
  if (!deferredInstallPrompt) return;
  try {
    await deferredInstallPrompt.prompt();
    const { outcome } = await deferredInstallPrompt.userChoice;
    if (outcome === "dismissed") {
      setInstallDismissed();
    }
  } catch (err) {
    console.error("PWA install prompt failed:", err);
    chorestore.showSnackbar("Install unavailable — try using the browser menu", "warning");
  } finally {
    deferredInstallPrompt = null;
    showInstallPrompt.value = false;
  }
};

// ── Lifecycle ───────────────────────────────────────────────────────────────
onMounted(async () => {
  // Visibility / version polling + data prefetch
  const handleVisibilityChange = () => {
    if (!document.hidden) {
      checkSession();
      prefetchVersion().then(() => {
        updateBanner();
      });
      if (userstore.isLoggedIn) {
        prefetchCriticalData();
      }
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
  clearExpiredDismissal();
  const handleInstallPrompt = (e) => {
    e.preventDefault();
    deferredInstallPrompt = e;
    if (!isInStandaloneMode && !installDismissed()) {
      showInstallPrompt.value = true;
    }
  };
  window.addEventListener("beforeinstallprompt", handleInstallPrompt);

  const handleAppInstalled = () => {
    deferredInstallPrompt = null;
    showInstallPrompt.value = false;
  };
  window.addEventListener("appinstalled", handleAppInstalled);

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
    window.removeEventListener("appinstalled", handleAppInstalled);
  });

  await checkSession();
  prefetchVersion();
  updateBanner();

  // Pre-warm critical API data in TanStack Query + Workbox cache
  if (userstore.isLoggedIn) {
    prefetchCriticalData();
  }

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
    } else {
      prefetchCriticalData();
    }
  }
);
</script>

<style></style>
