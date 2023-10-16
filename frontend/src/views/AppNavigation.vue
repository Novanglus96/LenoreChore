<template>
    <v-app-bar
        color="primary"
        density=compact
        app
    >
        <v-menu v-if="store.isLoggedIn">
            <template v-slot:activator="{ props }">
                <v-btn icon="mdi-menu" v-bind="props"></v-btn>
            </template>
            <v-list>
                <v-list-item
                    v-for="(menu, i) in menus"
                    :key="i"
                    :to="menu.url"
                >
                <template v-slot:prepend>
                    <v-icon :icon="menu.icon"></v-icon>
                </template>
                    <v-list-item-title>{{ menu.title }}</v-list-item-title>
                </v-list-item>
            </v-list>
            <v-divider></v-divider>
            <v-list v-if="!store.isChild">
                <AddAreaForm />
                <AddChoreForm />
                <AddAreaGroupForm />
            </v-list>
        </v-menu>
        <v-app-bar-title>Chores</v-app-bar-title>
        <v-menu
            v-model="menu"
            :close-on-content-click="false"
            location="end"
            v-if="store.isLoggedIn"
        >
            <template v-slot:activator="{ props }">
                <v-btn icon="mdi-dots-vertical" v-bind="props"></v-btn>
            </template>

            <v-card min-width="300">
                <v-list bg-color="accent">
                    <v-list-item
                        :prepend-avatar="store.avatar"
                    >
                        <v-list-item-title> {{store.fullname}}</v-list-item-title>
                        <v-list-item-subtitle> {{store.email}}</v-list-item-subtitle>
                    </v-list-item>
                </v-list>

                <v-divider :thickness="3" color="black"></v-divider>

                <v-list>
                    <v-list-item v-if="!store.isChild">
                        <v-list-item-title> Vacation Mode </v-list-item-title>
                        <v-btn-toggle v-model="chorestore.vacation_mode" divided variant="outlined" color="primary" mandatory @update:modelValue="toggleVacationMode(chorestore.vacation_mode)">
                            <v-btn :value="true">On</v-btn>
                            <v-btn :value="false">Off</v-btn>
                        </v-btn-toggle>
                    </v-list-item>
                    <v-list-item v-if="store.isAdmin">
                        <v-divider :thickness="3" color="black"></v-divider>
                    </v-list-item>
                    <v-list-item v-if="store.isAdmin">
                        <div>
                            <div class="text-caption">
                                Medium Threshold
                            </div>
                            <v-slider
                                v-model="chorestore.med_thresh"
                                thumb-label="always"
                                :min=0
                                :max=100
                                :step=1
                            >
                                <template v-slot:append>
                                    <v-text-field
                                        v-model="chorestore.med_thresh"
                                        hide-details
                                        single-line
                                        density="compact"
                                        type="number"
                                        style="width: 70px"
                                    ></v-text-field>
                                </template>
                            </v-slider>
                        </div>
                    </v-list-item>
                    <v-list-item v-if="store.isAdmin">
                        <div>
                            <div class="text-caption">
                                High Threshold
                            </div>
                            <v-slider
                                v-model="chorestore.high_thresh"
                                thumb-label="always"
                                :min=0
                                :max=100
                                :step=1
                            >
                                <template v-slot:append>
                                    <v-text-field
                                        v-model="chorestore.high_thresh"
                                        hide-details
                                        single-line
                                        density="compact"
                                        type="number"
                                        style="width: 70px"
                                    ></v-text-field>
                                </template>
                            </v-slider>
                        </div>
                    </v-list-item>
                </v-list>

                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn
                        variant="text"
                        @click="menu = false"
                    >
                        Cancel
                    </v-btn>
                    <v-btn
                        color="primary"
                        variant="text"
                        @click="callSaveOptions(chorestore.med_thresh, chorestore.high_thresh)"
                    >
                        Save
                    </v-btn>
                </v-card-actions>
            </v-card>
            <v-divider :thickness="3" color="error"></v-divider>
            <v-list>
                <v-list-item
                    to="/profile"
                    prepend-icon="mdi-account"
                >
                    <v-list-item-title>Profile</v-list-item-title>
                </v-list-item>
                <v-list-item
                    as="a"
                    href="/admin"
                    v-if="store.isAdmin"
                    prepend-icon="mdi-security"
                >
                    <v-list-item-title>Admin</v-list-item-title>
                </v-list-item>
                <v-list-item
                    to="/logout"
                    prepend-icon="mdi-logout"
                >
                    <v-list-item-title>Logout</v-list-item-title>
                </v-list-item>
            </v-list>
        </v-menu>
    </v-app-bar>
</template>

<script setup>
    import { ref } from 'vue';
    import { useUserStore } from '@/stores/user'
    import { useChoreStore } from '@/stores/chores'
    import AddAreaForm from '@/components/AddAreaForm.vue'
    import AddChoreForm from '@/components/AddChoreForm.vue'
    import AddAreaGroupForm from '@/components/AddAreaGroupForm.vue'

    const store = useUserStore();
    const chorestore = useChoreStore();

    const callSaveOptions = async (med_thresh, high_thresh) => {
        try {
            const store = useChoreStore();
            await store.saveOptions(med_thresh, high_thresh);
            menu.value = false;
        } catch (error) {
            console.log(error)
        }
    }

    const toggleVacationMode = async (enable) => {
        try {
            const store = useChoreStore();
            if (enable){
                await store.enableVacationMode();
            } else {
                await store.disableVacationMode();
            }
        } catch (error) {
            console.log(error);
        }
    }

    const menus = [
        { title: 'Dashboard', url: '/', icon: 'mdi-home' },
        { title: 'List', url: '/list/All', icon: 'mdi-view-list' },
        { title: 'Graphs', url: '/graphs', icon: 'mdi-chart-bar' },
        { title: 'History', url: '/history', icon: 'mdi-clipboard-clock-outline' },
      ]

    const menu = ref(false);

</script>

<style scoped>
</style>