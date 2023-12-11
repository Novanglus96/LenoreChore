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

  async function createOptionFunction(newOption) {
    const chorestore = useChoreStore();
    try {
      const response = await apiClient.post('/options', newOption)
      chorestore.showSnackbar('Options created successfully!', 'success')
      return response.data
    } catch (error) {
      handleApiError(error, 'Options not created: ')
    }

  }

  async function updateOptionFunction(updatedOption) {
    const chorestore = useChoreStore();
    try {
      const response = await apiClient.put('/options/' + updatedOption.id, updatedOption)
      chorestore.showSnackbar('Options updated successfully!', 'success')
      return response.data
    } catch (error) {
      handleApiError(error, 'Options not updated: ')
    }

  }

  async function deleteOptionFunction(deletedOption) {
    const chorestore = useChoreStore();
    try {
      const response = await apiClient.delete('/options/' + deletedOption.id)
      chorestore.showSnackbar('Options deleted successfully!', 'success')
      return response.data
    } catch (error) {
      handleApiError(error, 'Options not deleted: ')
    }

  }

  async function getOptionsFunction() {
    try {
      const response = await apiClient.get('/options/1/')
      return response.data
    } catch (error) {
      handleApiError(error, 'Options not fetched: ')
    }

  }
  
export function useOptions() {
    const queryClient = useQueryClient()
    const { data: options, isLoading } = useQuery({
      queryKey: ['options'],
      queryFn: getOptionsFunction,
      select: (response) => response,
      client: queryClient
    })
    
    const createOptionMutation = useMutation({
      mutationFn: createOptionFunction,
      onSuccess: () => {
        console.log('Success adding option')
        queryClient.invalidateQueries({ queryKey: ['options'] })
      }
    })

    const updateOptionMutation = useMutation({
      mutationFn: updateOptionFunction,
      onSuccess: () => {
        console.log('Success updating option')
        queryClient.invalidateQueries({ queryKey: ['options']})
      }
    })

    const deleteOptionMutation = useMutation({
      mutationFn: deleteOptionFunction,
      onSuccess: () => {
        console.log('Success deleting option')
        queryClient.invalidateQueries({ queryKey: ['options']})
      }
    })
  
    async function addOption(newOption) {
      createOptionMutation.mutate(newOption);
    }

    async function editOption(updatedOption) {
      updateOptionMutation.mutate(updatedOption);
    }

    async function removeOption(deletedOption) {
      deleteOptionMutation.mutate(deletedOption);
    }
  
    return {
      options,
      isLoading,
      addOption,
      editOption,
      removeOption
    }
  }
