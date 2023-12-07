import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v2',
  withCredentials: false,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json'
  }
})

  async function createAreaGroupFunction(newAreaGroup) {

    try {
      const response = await apiClient.post('/areagroups', newAreaGroup)
      return response.data
    } catch (error) {
      if (error.response) {
        console.error('Response error:', error.response.data)
        console.error('Status code:', error.response.status)
        console.error('Headers', error.response.headers)
      } else if (error.request){
        console.error('No response received:', error.request)
      } else {
        console.error('Error during request setup:', error.message)
      }
      throw error
    }

  }

  async function updateAreaGroupFunction(updatedAreaGroup) {

    try {
      const response = await apiClient.put('/areagroups' + updatedAreaGroup.id, updatedAreaGroup)
      return response.data
    } catch (error) {
      if (error.response) {
        console.error('Response error:', error.response.data)
        console.error('Status code:', error.response.status)
        console.error('Headers', error.response.headers)
      } else if (error.request){
        console.error('No response received:', error.request)
      } else {
        console.error('Error during request setup:', error.message)
      }
      throw error
    }

  }

  async function deleteAreaGroupFunction(deletedAreaGroup) {
    
    try {
      const response = await apiClient.delete('/areagroups' + deletedAreaGroup.id)
      return response.data
    } catch (error) {
      if (error.response) {
        console.error('Response error:', error.response.data)
        console.error('Status code:', error.response.status)
        console.error('Headers', error.response.headers)
      } else if (error.request){
        console.error('No response received:', error.request)
      } else {
        console.error('Error during request setup:', error.message)
      }
      throw error
    }

  }

  async function getAreaGroupsFunction() {
    
    try {
      const response = await apiClient.get('/areagroups')
      return response.data
    } catch (error) {
      if (error.response) {
        console.error('Response error:', error.response.data)
        console.error('Status code:', error.response.status)
        console.error('Headers', error.response.headers)
      } else if (error.request){
        console.error('No response received:', error.request)
      } else {
        console.error('Error during request setup:', error.message)
      }
      throw error
    }

  }
  
  export function useAreaGroups() {
    const queryClient = useQueryClient()

    const { data: areagroups, isLoading } = useQuery({
      queryKey: ['areagroups'],
      queryFn: getAreaGroupsFunction,
      select: (response) => response
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
