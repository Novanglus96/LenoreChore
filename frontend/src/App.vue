<template>
  <v-card max-width="448" class="mx-auto">
    <v-layout>
      <v-app-bar
        color="info"
        density=compact
      >
        <v-menu>
            <template v-slot:activator="{ props }">
                <v-btn icon="mdi-menu" v-bind="props"></v-btn>
            </template>
            <v-list>
                <v-list-item
                v-for="(menu, i) in menus"
                :key="i"
                :to="menu.url"
              >
                <v-list-item-title>{{ menu.title }}</v-list-item-title>
              </v-list-item>
            </v-list>
        </v-menu>

        <v-app-bar-title>Chores</v-app-bar-title>

        <v-menu
          v-model="menu"
          :close-on-content-click="false"
          location="end"
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

        <v-divider></v-divider>

        <v-list>
          <v-list-item>
            <v-switch
              v-model="message"
              color="purple"
              label="Enable messages"
              hide-details
            ></v-switch>
          </v-list-item>

          <v-list-item>
            <v-switch
              v-model="hints"
              color="purple"
              label="Enable hints"
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

    const store = useUserStore()

    const menus = [
        { title: 'Dashboard', url: '/' },
        { title: 'List', url: '/list' },
        { title: 'Graphs', url: '/graphs' },
        { title: 'History', url: '/history' },
      ]

    const fav = ref(true);
    const menu = ref(false);
    const message = ref(false);
    const hints = ref(true);
</script>