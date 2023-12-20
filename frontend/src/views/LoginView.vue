<template>
  <div class="login">
    <header class="bg-white shadow">
      <div class="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Login</h1>
      </div>
    </header>
    <main>
      <div class="mx-auto max-w-7xl py-6 sm:px-6 lg:px-8">
        <LoginForm @login-user="login"/>
      </div>
    </main>
  </div>
</template>

<script setup>
// @ is an alias to /src
import LoginForm from '@/components/LoginForm.vue';
import { useUserStore } from '@/stores/user';
import { useRouter } from 'vue-router';
import { loginUser } from '@/composables/usersComposable';

const router = useRouter();
const login = async (credentials) => {
  const user = await loginUser(credentials)
    const token = user.token
    const userstore = useUserStore();
    localStorage.setItem('authToken', token);
    userstore.loginUser(user.firstname, user.lastname, user.email, user.isAdmin, user.male, user.id, user.user_color, user.groups)
    router.push('/');
}

</script>
