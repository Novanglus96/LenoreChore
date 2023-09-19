<template>
  <v-card max-width="448" class="mx-auto" variant="tonal" color="white">
    <v-layout>
      <v-app-bar
        color="info"
        density=compact
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
            <v-list v-if="store.isAdmin">
                <AddAreaForm/>
                <AddChoreForm/>
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
        <v-list>
          <v-list-item
            :prepend-avatar="store.avatar"
          >
          <v-list-item-title> {{store.fullname}}</v-list-item-title>
          <v-list-item-subtitle> {{store.email}}</v-list-item-subtitle>
          </v-list-item>
        </v-list>

        <v-divider :thickness="3" color="error"></v-divider>

        <v-list>
          <v-list-item>
            <v-switch
              v-model="vacation"
              color="purple"
              label="Enable Vacation Mode"
              hide-details
            ></v-switch>
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
            @click="menu = false"
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

      <v-main>
        <v-container fluid>
          <router-view/>
        </v-container>
      </v-main>
    </v-layout>
  </v-card>
</template>
<script setup>
    import { ref } from 'vue';
    import { useUserStore } from '@/stores/user'
    import AddAreaForm from '@/components/AddAreaForm.vue'
    import AddChoreForm from '@/components/AddChoreForm.vue'

    const store = useUserStore()

    const menus = [
        { title: 'Dashboard', url: '/', icon: 'mdi-home' },
        { title: 'List', url: '/list', icon: 'mdi-view-list' },
        { title: 'Graphs', url: '/graphs', icon: 'mdi-chart-bar' },
        { title: 'History', url: '/history', icon: 'mdi-clipboard-clock-outline' },
      ]

    const menu = ref(false);
    const vacation = ref(false);
</script>