<template>
  <!-- The bar was hardcoded to #c8f0ff, so it stayed pale cyan in the dark
       theme regardless. Using a theme colour lets each theme define it. -->
  <v-app-bar color="surface" density="compact" border app>
    <v-menu v-if="store.isLoggedIn" v-model="navMenu">
      <template v-slot:activator="{ props: activatorProps }">
        <v-btn
          v-bind="activatorProps"
          icon="mdi-menu"
          aria-label="Main menu"
          :aria-expanded="navMenu ? 'true' : 'false'"
        >
          <v-icon icon="mdi-menu"></v-icon>
        </v-btn>
      </template>
      <v-list nav>
        <!-- The v-for alias used to be named `menu`, which shadowed the ref
             holding the overflow menu's open state -- so `@click="menu = false"`
             assigned to the loop variable and the intended close never
             happened. It only looked like it worked because navigating closes
             the menu as a side effect. -->
        <v-list-item
          v-for="item in menus"
          :key="item.url"
          :to="item.url"
          @click="navMenu = false"
        >
          <template v-slot:prepend>
            <v-icon :icon="item.icon" aria-hidden="true"></v-icon>
          </template>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
      <v-divider></v-divider>
      <v-list v-if="!store.isChild">
        <AddAreaForm />
        <AddChoreForm />
        <AddAreaGroupForm />
      </v-list>
      <v-divider></v-divider>
      <v-list>
        <v-list-item to="/about">
          <v-list-item-title class="text-body-2 font-italic text-secondary text-center">
            About LenoreChore
          </v-list-item-title>
          <v-list-item-title class="text-caption font-italic text-medium-emphasis text-center">
            {{ appVersion }}
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
    <v-img
      :width="180"
      aspect-ratio="1/1"
      src="logov2.png"
      alt="LenoreChore"
      inline
    ></v-img>
    <v-spacer></v-spacer>

    <!-- Offline is STATUS, not a control. It was a tooltip on an unlabelled
         button, so the queue count was reachable only by hovering — which a
         touch device cannot do and a screen reader never announced. It is now a
         live region that speaks when connectivity changes. -->
    <div
      v-if="!offlineStore.isOnline"
      class="d-flex align-center"
      role="status"
      aria-live="polite"
    >
      <v-chip
        size="small"
        color="soiled"
        variant="tonal"
        prepend-icon="mdi-wifi-off"
      >
        <span class="d-none d-sm-inline">{{ offlineLabel }}</span>
        <span class="d-sm-none">Offline</span>
      </v-chip>
      <span class="lc-visually-hidden">{{ offlineLabel }}</span>
    </div>

    <v-btn
      :icon="themeStore.isDark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
      :aria-label="
        themeStore.isDark ? 'Switch to light theme' : 'Switch to dark theme'
      "
      :aria-pressed="themeStore.isDark ? 'true' : 'false'"
      @click="themeStore.toggle()"
    >
      <v-icon
        :icon="themeStore.isDark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
      ></v-icon>
      <v-tooltip activator="parent" location="bottom">
        {{ themeStore.isDark ? "Light theme" : "Dark theme" }}
      </v-tooltip>
    </v-btn>

    <v-menu v-model="menu" location="end" v-if="store.isLoggedIn">
      <template v-slot:activator="{ props: activatorProps }">
        <v-btn
          v-bind="activatorProps"
          icon="mdi-dots-vertical"
          aria-label="Account and settings"
          :aria-expanded="menu ? 'true' : 'false'"
        >
          <v-icon icon="mdi-dots-vertical"></v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-list-item
          href="/admin/"
          v-if="store.isAdmin"
          prepend-icon="mdi-security"
        >
          <v-list-item-title>Admin</v-list-item-title>
        </v-list-item>
        <v-list-item prepend-icon="mdi-island" @click="showVacationForm = true">
          <v-list-item-title>
            {{
              options?.vacation_mode !== true
                ? "Enable Vacation"
                : "Disable Vacation"
            }}
          </v-list-item-title>
        </v-list-item>
        <v-list-item to="/profile" prepend-icon="mdi-account">
          <v-list-item-title>Profile</v-list-item-title>
        </v-list-item>
        <v-list-item to="/logout" prepend-icon="mdi-logout">
          <v-list-item-title>Logout</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
    <VacationForm
      v-if="store.isLoggedIn"
      v-model="showVacationForm"
      @update-dialog="updateVacationDialog"
    />
  </v-app-bar>
</template>

<script setup>
  import { ref, computed } from "vue";
  import { useUserStore } from "@/stores/user";
  import { useThemeStore } from "@/stores/theme";
  import { useOfflineStore } from "@/stores/offline";
  import AddAreaForm from "@/components/AddAreaForm.vue";
  import AddChoreForm from "@/components/AddChoreForm.vue";
  import AddAreaGroupForm from "@/components/AddAreaGroupForm.vue";
  import { useOptions } from "@/composables/optionsComposable";
  import VacationForm from "@/components/VacationForm.vue";
  import { version as appVersion } from "../../package.json";

  const themeStore = useThemeStore();
  const offlineStore = useOfflineStore();

  const { options } = useOptions();
  const showVacationForm = ref(false);
  const store = useUserStore();

  const menus = [
    { title: "Dashboard", url: "/", icon: "mdi-home" },
    { title: "List", url: "/list", icon: "mdi-view-list" },
    { title: "Graphs", url: "/graphs", icon: "mdi-chart-bar" },
    { title: "History", url: "/history", icon: "mdi-clipboard-clock-outline" },
  ];

  const menu = ref(false);
  const navMenu = ref(false);

  // Spelled out rather than assembled in the template, so the same wording
  // reaches both the visible chip and the live region.
  const offlineLabel = computed(() => {
    const queued = offlineStore.mutationQueue.length;
    if (queued === 0) {
      return "Offline — changes will sync when you reconnect";
    }
    return `Offline — ${queued} change${queued === 1 ? "" : "s"} saved locally, will sync when you reconnect`;
  });

  const updateVacationDialog = () => {
    showVacationForm.value = false;
  };
</script>

<style scoped></style>
