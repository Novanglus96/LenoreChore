<template>
  <!-- Same scaffold wrapper as the other three views. The <h1> it used to carry
       is preserved here, visually hidden, matching how DashView and ListView
       name themselves above a v-empty-state that carries its own title. -->
  <div class="lc-notfound-view">
    <h1 class="lc-visually-hidden">Page not found</h1>
    <NotFound />
  </div>
</template>

<script setup>
import NotFound from "@/components/NotFound.vue";
</script>

<style scoped>
.lc-notfound-view {
  padding: var(--lc-space-5) var(--lc-space-4);
}
</style>
