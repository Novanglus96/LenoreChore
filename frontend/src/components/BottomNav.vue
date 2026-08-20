<template>
  <!-- Bottom navigation, phones only.
       ─────────────────────────────────────────────────────────────────────
       This is an installed PWA, and the only route between Dashboard, List,
       Graphs and History was a hamburger in the top-LEFT corner -- the single
       hardest place to reach one-handed on a phone, and two taps deep for every
       move. Four destinations is exactly what bottom navigation is for.

       Rendered as a sibling of v-main so Vuetify's layout reserves space for
       it: v-main gets the padding automatically, and VSnackbar picks up the
       same mainStyles, so toasts sit above the bar rather than behind it. -->
  <v-bottom-navigation
    v-if="visible"
    :model-value="active"
    tag="nav"
    aria-label="Main"
    color="primary"
    bg-color="surface"
    grow
    class="lc-bottom-nav"
  >
    <v-btn
      v-for="destination in DESTINATIONS"
      :key="destination.url"
      :value="destination.url"
      :to="destination.url"
      :aria-current="active === destination.url ? 'page' : undefined"
    >
      <v-icon
        :icon="
          active === destination.url ? destination.activeIcon : destination.icon
        "
      ></v-icon>
      <span>{{ destination.title }}</span>
    </v-btn>
  </v-bottom-navigation>
</template>

<script setup>
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useDisplay } from "vuetify";
import { useUserStore } from "@/stores/user";
import { DESTINATIONS, activeDestination } from "@/utils/navigation";

const route = useRoute();
const display = useDisplay();
const store = useUserStore();

// Desktop keeps the overflow menu: a bar pinned to the bottom of a 1440px
// window is a long way from where the eye already is.
const visible = computed(() => store.isLoggedIn && display.smAndDown.value);

// Derived from the route rather than held as local state, so the highlight
// follows a back gesture and a deep link, not just a tap on the bar.
const active = computed(() => activeDestination(route.path));
</script>

<style scoped>
.lc-bottom-nav {
  /* An installed PWA sits under the home indicator on iOS, which would put the
     bar's labels behind it. env() resolves to 0 everywhere else. */
  padding-bottom: env(safe-area-inset-bottom, 0px);
  height: calc(56px + env(safe-area-inset-bottom, 0px)) !important;
}

/* Vuetify's default is uppercase with wide tracking, which at 10px reads as
   noise rather than as four words. */
.lc-bottom-nav :deep(.v-btn) {
  text-transform: none;
  letter-spacing: normal;
  min-width: 0;
}
</style>
