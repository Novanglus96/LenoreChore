import { useQuery } from "@tanstack/vue-query";
import ChoreService from '@/services/ChoreService.js';
import { ref } from 'vue';
  
  export function useUsers() {

    const { data: users, isLoading } = useQuery({
      queryKey: ['users'],
      queryFn: () => ChoreService.getUsers(),
      select: (response) => response.data
    })
  
    return {
      users,
      isLoading
    }
  }

  export async function loginUser(credentials) {
    const user = ref(null);
    const error = ref(null);

    try {
        const response = await ChoreService.loginUser(credentials);
        user.value = response.data;
    } catch (err) {
        error.value = err;
    } finally {
        isLoading.value = false;
    }

    return {
        user,
        error
    }
  }
