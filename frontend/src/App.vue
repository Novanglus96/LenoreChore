<template>
    <v-app>
        <AppNavigationVue/>
        <v-main>
            <v-container fluid class="pa-2">
                <router-view/>
            </v-container>
        </v-main>
    </v-app>
</template>

<script setup>
    import AppNavigationVue from "./views/AppNavigation.vue";
    import { onMounted } from 'vue';
    import { useChoreStore } from '@/stores/chores';

    const chorestore = useChoreStore();

    onMounted(() => {
      chorestore.fetchAreas();
      chorestore.fetchChores();
      chorestore.fetchUsers();
      chorestore.fetchHistoryItems();
    });
</script>

<style>
</style>