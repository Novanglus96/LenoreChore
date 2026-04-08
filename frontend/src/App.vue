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
import { onMounted, computed, ref, watch, onUnmounted } from "vue";
import { VueQueryDevtools } from "@tanstack/vue-query-devtools";
import { useVersion } from "@/composables/versionComposable";
import { useRouter } from "vue-router";
import axios from "axios";

const reloadPage = () => {
  window.location.reload();
};
const chorestore = useChoreStore();
const userstore = useUserStore();
const router = useRouter();
const { prefetchVersion, version } = useVersion();
const showBanner = ref(false);

const checkVersion = computed(() => {
  return version.value && version.value.version_number !== "1.2.24";
});

const updateBanner = () => {
  showBanner.value = checkVersion.value;
};

const checkSession = async () => {
  if (!localStorage.getItem("authToken")) return;
  try {
    await axios.get("/api/v2/me");
  } catch (error) {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("authToken");
      userstore.logoutUser();
      router.push("/login");
    }
  }
};

onMounted(async () => {
  await checkSession();
  prefetchVersion();

  // Check version initially
  updateBanner();

  const handleVisibilityChange = () => {
    if (!document.hidden) {
      checkSession();
      prefetchVersion().then(() => {
        updateBanner();
      });
    }
  };

  document.addEventListener("visibilitychange", handleVisibilityChange);

  // Clean up the event listener when the component is unmounted
  onUnmounted(() => {
    document.removeEventListener("visibilitychange", handleVisibilityChange);
  });
});

// Watch for changes in the computed property
watch(checkVersion, newValue => {
  showBanner.value = newValue;
});
</script>

<style></style>
