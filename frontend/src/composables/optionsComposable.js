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

  async function createOptionFunction(newOption) {

    try {
      const response = await apiClient.post('/options', newOption)
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

  async function updateOptionFunction(updatedOption) {

    try {
      const response = await apiClient.put('/options/' + updatedOption.id, updatedOption)
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

  async function deleteOptionFunction(deletedOption) {
    
    try {
      const response = await apiClient.delete('/options/' + deletedOption.id)
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

  async function getOptionsFunction() {
    
    try {
      const response = await apiClient.get('/options/1/')
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
  
  export function useOptions() {
    const queryClient = useQueryClient()

    const { data: options, isLoading } = useQuery({
      queryKey: ['options'],
      queryFn: getOptionsFunction,
      select: (response) => response
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
