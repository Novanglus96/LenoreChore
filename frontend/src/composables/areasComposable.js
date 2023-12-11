import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query"
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

  async function createAreaFunction(newArea) {
    const chorestore = useChoreStore();
    try {
      const response = await apiClient.post('/areas', newArea)
      chorestore.showSnackbar('Area created successfully!', 'success')
      return response.data
    } catch (error) {
      handleApiError(error, 'Area not created: ')
    }

  }

  async function updateAreaFunction(updatedArea) {
    const chorestore = useChoreStore();
    try {
      const response = await apiClient.put('/areas/' + updatedArea.id, updatedArea)
      chorestore.showSnackbar('Area updated successfully!', 'success')
      return response.data
    } catch (error) {
      handleApiError(error, 'Area not updated: ')
    }
  }

  async function deleteAreaFunction(deletedArea) {
    const chorestore = useChoreStore();
    try {
      const response = await apiClient.delete('/areas/' + deletedArea.id)
      chorestore.showSnackbar('Area deleted successfully!', 'success')
      return response.data
    } catch (error) {
      handleApiError(error, 'Area not deleted: ')
    }

  }

  async function getAreasFunction() {
    try {
      const response = await apiClient.get('/areas')
      return response.data
    } catch (error) {
      handleApiError(error, 'Areas not fetched: ')
    }

  }

export function useAreas() {
    const queryClient = useQueryClient()
    const { data: areas, isLoading } = useQuery({
      queryKey: ['areas'],
      queryFn: getAreasFunction,
      select: (response) => response,
      client: queryClient
    })
    
    const createAreaMutation = useMutation({
      mutationFn: createAreaFunction,
      onSuccess: () => {
        console.log('Success adding area')
        queryClient.invalidateQueries({ queryKey: ['areas'] })
      }
    })

    const updateAreaMutation = useMutation({
      mutationFn: updateAreaFunction,
      onSuccess: () => {
        console.log('Success updating area')
        queryClient.invalidateQueries({ queryKey: ['areas']})
      }
    })

    const deleteAreaMutation = useMutation({
      mutationFn: deleteAreaFunction,
      onSuccess: () => {
        console.log('Success deleting area')
        queryClient.invalidateQueries({ queryKey: ['areas']})
      }
    })
  
    async function addArea(newArea) {
      createAreaMutation.mutate(newArea);
    }

    async function editArea(updatedArea) {
      updateAreaMutation.mutate(updatedArea);
    }

    async function removeArea(deletedArea) {
      deleteAreaMutation.mutate(deletedArea);
    }
    
    return {
      areas,
      isLoading,
      addArea,
      editArea,
      removeArea
    }
  }
