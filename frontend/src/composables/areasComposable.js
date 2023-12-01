import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import ChoreService from '@/services/ChoreService.js'

  async function createAreaFunction(newArea) {

    ChoreService.createArea(newArea)
    .then((response) => {
      return response.data
    })
    .catch((error) => {
      console.log(error)
    })

  }

  async function updateAreaFunction(updatedArea) {

    ChoreService.updateArea(updatedArea)
    .then((response) => {
      return response.data
    })
    .catch((error) => {
      console.log(error)
    })

  }

  async function deleteAreaFunction(deletedArea) {
    
    ChoreService.deleteArea(deletedArea)
    .then((response) => {
      return response.data
    })
    .catch((error) => {
      console.log(error)
    })

  }
  
  export function useAreas() {
    const queryClient = useQueryClient()

    const { data: areas, isLoading } = useQuery({
      queryKey: ['areas'],
      queryFn: () => ChoreService.getAreas(),
      select: (response) => response.data
    })
    
    const createAreaMutation = useMutation({
      mutationFn: createAreaFunction,
      onSuccess: () => {
        console.log('Success adding area group')
        queryClient.invalidateQueries({ queryKey: ['areas'] })
      }
    })

    const updateAreaMutation = useMutation({
      mutationFn: updateAreaFunction,
      onSuccess: () => {
        console.log('Success updating area group')
        queryClient.invalidateQueries({ queryKey: ['areas']})
      }
    })

    const deleteAreaMutation = useMutation({
      mutationFn: deleteAreaFunction,
      onSuccess: () => {
        console.log('Success deleting area group')
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
