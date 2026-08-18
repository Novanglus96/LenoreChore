<template>
  <!-- Same scaffold wrapper as LoginView, same fix: LogoutForm owns its card
       and its heading, and this view just places it. -->
  <div class="lc-logout-view">
    <LogoutForm />
  </div>
</template>

<script setup>
import LogoutForm from "@/components/LogoutForm.vue";
</script>

<style scoped>
.lc-logout-view {
  padding: var(--lc-space-6) var(--lc-space-4) var(--lc-space-5);
}
</style>
