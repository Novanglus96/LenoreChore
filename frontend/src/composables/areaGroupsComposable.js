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

  async function createAreaGroupFunction(newAreaGroup) {
    const chorestore = useChoreStore();
    try {
      const response = await apiClient.post('/areagroups', newAreaGroup)
      chorestore.showSnackbar('Area group created successfully!', 'success')
      return response.data
    } catch (error) {
      handleApiError(error, 'Area group not created: ')
    }

  }

  async function updateAreaGroupFunction(updatedAreaGroup) {
    const chorestore = useChoreStore();
    try {
      const response = await apiClient.put('/areagroups' + updatedAreaGroup.id, updatedAreaGroup)
      chorestore.showSnackbar('Area group updated successfully!', 'success')
      return response.data
    } catch (error) {
      handleApiError(error, 'Area group not updated: ')
    }

  }

  async function deleteAreaGroupFunction(deletedAreaGroup) {
    const chorestore = useChoreStore();
    try {
      const response = await apiClient.delete('/areagroups' + deletedAreaGroup.id)
      chorestore.showSnackbar('Area group deleted successfully!', 'success')
      return response.data
    } catch (error) {
      handleApiError(error, 'Area group not deleted: ')
    }

  }

  async function getAreaGroupsFunction() {
    try {
      const response = await apiClient.get('/areagroups')
      return response.data
    } catch (error) {
      handleApiError(error, 'Area groups not fetched: ')
    }

  }
  
  export function useAreaGroups() {
    const queryClient = useQueryClient()
    const { data: areagroups, isLoading } = useQuery({
      queryKey: ['areagroups'],
      queryFn: getAreaGroupsFunction,
      select: (response) => response,
      client: queryClient
    })
    
    const createAreaGroupMutation = useMutation({
      mutationFn: createAreaGroupFunction,
      onSuccess: () => {
        console.log('Success adding area group')
        queryClient.invalidateQueries({ queryKey: ['areagroups'] })
      }
    })

    const updateAreaGroupMutation = useMutation({
      mutationFn: updateAreaGroupFunction,
      onSuccess: () => {
        console.log('Success updating area group')
        queryClient.invalidateQueries({ queryKey: ['areagroups']})
      }
    })

    const deleteAreaGroupMutation = useMutation({
      mutationFn: deleteAreaGroupFunction,
      onSuccess: () => {
        console.log('Success deleting area group')
        queryClient.invalidateQueries({ queryKey: ['areagroups']})
      }
    })
  
    async function addAreaGroup(newAreaGroup) {
      createAreaGroupMutation.mutate(newAreaGroup);
    }

    async function editAreaGroup(updatedAreaGroup) {
      updateAreaGroupMutation.mutate(updatedAreaGroup);
    }

    async function removeAreaGroup(deletedAreaGroup) {
      deleteAreaGroupMutation.mutate(deletedAreaGroup);
    }
  
    return {
      areagroups,
      isLoading,
      addAreaGroup,
      editAreaGroup,
      removeAreaGroup
    }
  }
