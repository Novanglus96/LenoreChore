import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import axios from 'axios'
import { useChoreStore } from '@/stores/chores'

const apiClient = axios.create({
  baseURL: '/api/v2',
  withCredentials: false,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json'
  }
})

function handleApiError(error, message) {
  const chorestore = useChoreStore();
  if (error.response) {
    console.error('Response error:', error.response.data)
    console.error('Status code:', error.response.status)
    console.error('Headers', error.response.headers)
  } else if (error.request){
    console.error('No response received:', error.request)
  } else {
    console.error('Error during request setup:', error.message)
  }
  chorestore.showSnackbar(message + 'Error #' + error.response.status, 'error')
  throw error
}

async function createChoreFunction(newChore) {
    const chorestore = useChoreStore();
    try {
      const response = await apiClient.post('/chores', newChore)
      chorestore.showSnackbar('Chore created successfully!', 'success')
      return response.data
    } catch (error) {
      handleApiError(error, 'Chore not created: ')
    }

  }

  async function updateChoreFunction(updatedChore) {
    const chorestore = useChoreStore();
    try {
      const response = await apiClient.put('/chores/' + updatedChore.id, updatedChore)
      chorestore.showSnackbar('Chore updated successfully!', 'success')
      return response.data
    } catch (error) {
      handleApiError(error, 'Chore not updated: ')
    }
  }

  async function deleteChoreFunction(deletedChore) {
    const chorestore = useChoreStore();
    try {
      const response = await apiClient.delete('/chores/' + deletedChore.id)
      chorestore.showSnackbar('Chore deleted successfully!', 'success')
      return response.data
    } catch (error) {
      handleApiError(error, 'Chore not deleted: ')
    }

  }

  async function getChoresFunction() {
    try {
      const response = await apiClient.get('/chores')
      return response.data
    } catch (error) {
      handleApiError(error, 'Chores not fetched: ')
    }

  }

export function useChores() {
    const queryClient = useQueryClient()
    const { data: chores, isLoading } = useQuery({
      queryKey: ['chores'],
      queryFn: getChoresFunction,
      select: (response) => response,
      client: queryClient
    })
    
    const createChoreMutation = useMutation({
      mutationFn: createChoreFunction,
      onSuccess: () => {
        console.log('Success adding chore')
        queryClient.invalidateQueries({ queryKey: ['chores'] })
        queryClient.invalidateQueries({ queryKey: ['areas'] })
      }
    })

    const updateChoreMutation = useMutation({
      mutationFn: updateChoreFunction,
      onSuccess: () => {
        console.log('Success updating chore')
        queryClient.invalidateQueries({ queryKey: ['chores'] })
        queryClient.invalidateQueries({ queryKey: ['areas'] })
      }
    })

    const deleteChoreMutation = useMutation({
      mutationFn: deleteChoreFunction,
      onSuccess: () => {
        console.log('Success deleting chore')
        queryClient.invalidateQueries({ queryKey: ['chores'] })
        queryClient.invalidateQueries({ queryKey: ['areas'] })
      }
    })
  
    async function addChore(newChore) {
      createChoreMutation.mutate(newChore);
    }

    async function editChore(updatedChore) {
      updateChoreMutation.mutate(updatedChore);
    }

    async function removeChore(deletedChore) {
      deleteChoreMutation.mutate(deletedChore);
    }
    
    return {
      chores,
      isLoading,
      addChore,
      editChore,
      removeChore
    }
  }