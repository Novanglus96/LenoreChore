<template>
    <v-app>
        <VueQueryDevtools/>
        <AppNavigationVue/>
        <v-main>
            <v-container fluid class="pa-2">
                <router-view/>
            </v-container>
            <v-snackbar
                v-model="chorestore.snackbar"
                :color="chorestore.snackbarColor"
                :timeout="chorestore.snackbarTimeout"
                content-class="centered-text"
            >
                {{ chorestore.snackbarText }}
            </v-snackbar>
        </v-main>
    </v-app>
</template>

<script setup>
    import AppNavigationVue from "./views/AppNavigation.vue";
    import { onMounted } from 'vue';
    import { useChoreStore } from '@/stores/chores';
    import { VueQueryDevtools } from '@tanstack/vue-query-devtools'

    const chorestore = useChoreStore();

    onMounted(() => {
      chorestore.fetchAll();
    });

</script>

<style>
</style>