<template>
  <v-app-bar color="#c8f0ff" density="compact" app>
    <v-menu v-if="store.isLoggedIn">
      <template v-slot:activator="{ props }">
        <v-btn icon="mdi-menu" v-bind="props"></v-btn>
      </template>
      <v-list>
        <v-list-item
          v-for="(menu, i) in menus"
          :key="i"
          :to="menu.url"
          @click="menu = false"
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
    <v-img :width="208" aspect-ratio="1/1" src="logov2.png" inline></v-img>
    <span class="text-subtitle-2 font-italic text-grey-darken-1">v1.2.24</span>
    <v-spacer></v-spacer>
    <v-menu
      v-model="menu"
      :close-on-content-click="false"
      location="end"
      v-if="store.isLoggedIn"
    >
      <template v-slot:activator="{ props }">
        <v-btn icon="mdi-dots-vertical" v-bind="props"></v-btn>
      </template>
      <v-list>
        <v-list-item
          as="a"
          href="/admin"
          v-if="store.isAdmin"
          prepend-icon="mdi-security"
        >
          <v-list-item-title>Admin</v-list-item-title>
        </v-list-item>
        <v-list-item prepend-icon="mdi-island" @click="showVacationForm = true">
          <v-list-item-title>
            {{
              options.vacation_mode == false
                ? "Enable Vacation"
                : "Disable Vacation"
            }}
          </v-list-item-title>
        </v-list-item>
        <VacationForm
          v-model="showVacationForm"
          @update-dialog="updateVacationDialog"
        />
        <v-list-item to="/logout" prepend-icon="mdi-logout">
          <v-list-item-title>Logout</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
  </v-app-bar>
</template>

<script setup>
  import { ref } from "vue";
  import { useUserStore } from "@/stores/user";
  import AddAreaForm from "@/components/AddAreaForm.vue";
  import AddChoreForm from "@/components/AddChoreForm.vue";
  import AddAreaGroupForm from "@/components/AddAreaGroupForm.vue";
  import { useOptions } from "@/composables/optionsComposable";
  import VacationForm from "@/components/VacationForm.vue";

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
  const updateVacationDialog = () => {
    showVacationForm.value = false;
  };
</script>

<style scoped></style>
