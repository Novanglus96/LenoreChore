import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import ChoreService from '@/services/ChoreService.js'

  async function createAreaGroupFunction(newAreaGroup) {

    ChoreService.createAreaGroup(newAreaGroup)
    .then((response) => {
      return response.data
    })
    .catch((error) => {
      console.log(error)
    })

  }

  async function updateAreaGroupFunction(updatedAreaGroup) {

    ChoreService.updateAreaGroup(updatedAreaGroup)
    .then((response) => {
      return response.data
    })
    .catch((error) => {
      console.log(error)
    })

  }

  async function deleteAreaGroupFunction(deletedAreaGroup) {
    
    ChoreService.deleteAreaGroup(deletedAreaGroup)
    .then((response) => {
      return response.data
    })
    .catch((error) => {
      console.log(error)
    })

  }
  
  export function useAreaGroups() {
    const queryClient = useQueryClient()

    const { data: areagroups, isLoading } = useQuery({
      queryKey: ['areagroups'],
      queryFn: () => ChoreService.getAreaGroups(),
      select: (response) => response.data
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
