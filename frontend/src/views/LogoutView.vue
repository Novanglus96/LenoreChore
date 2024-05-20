<template>
  <div class="logout">
    <header class="bg-white shadow">
      <div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Logout</h1>
      </div>
    </header>
    <main>
      <div class="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
        <LogoutForm />
      </div>
    </main>
  </div>
</template>

<script>
// @ is an alias to /src
import LogoutForm from "@/components/LogoutForm.vue";

export default {
  name: "ListView",
  components: {
    LogoutForm,
  },
};
</script>
