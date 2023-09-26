<template>
    <v-app>
        <AppNavigationVue/>
        <v-main>
            <v-container fluid>
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
    });
</script>

<style>
</style>