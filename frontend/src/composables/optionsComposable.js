import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import ChoreService from '@/services/ChoreService.js'

  async function createOptionFunction(newOption) {

    ChoreService.createOption(newOption)
    .then((response) => {
      return response.data
    })
    .catch((error) => {
      console.log(error)
    })

  }

  async function updateOptionFunction(updatedOption) {

    ChoreService.updateOption(updatedOption)
    .then((response) => {
      return response.data
    })
    .catch((error) => {
      console.log(error)
    })

  }

  async function deleteOptionFunction(deletedOption) {
    
    ChoreService.deleteOption(deletedOption)
    .then((response) => {
      return response.data
    })
    .catch((error) => {
      console.log(error)
    })

  }
  
  export function useOptions() {
    const queryClient = useQueryClient()

    const { data: options, isLoading } = useQuery({
      queryKey: ['options'],
      queryFn: () => ChoreService.getOptions(),
      select: (response) => response.data
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
