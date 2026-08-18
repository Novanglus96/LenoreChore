import { computed } from "vue";
import { useUserStore } from "@/stores/user";
import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import apiClient from "@/api/client";
import { useChoreStore } from "@/stores/chores";
import { handleApiError } from "@/utils/apiErrorHandler";

async function createAreaFunction(newArea) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.post("/areas", newArea);
    chorestore.showSnackbar("Area created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Area not created: ");
  }
}

async function updateAreaFunction(updatedArea) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.put(
      "/areas/" + updatedArea.id,
      updatedArea,
    );
    chorestore.showSnackbar("Area updated successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Area not updated: ");
  }
}

async function deleteAreaFunction(deletedArea) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.delete("/areas/" + deletedArea.id);
    chorestore.showSnackbar("Area deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Area not deleted: ");
  }
}

async function getAreasFunction() {
  try {
    const response = await apiClient.get("/areas");
    return response.data;
  } catch (error) {
    handleApiError(error, "Areas not fetched: ");
  }
}

export function useAreas() {
  const queryClient = useQueryClient();
  const userStore = useUserStore();
  const isAuthenticated = computed(() => userStore.isLoggedIn);
  const { data: areas, isLoading } = useQuery({
    queryKey: ["areas"],
    queryFn: getAreasFunction,
    select: response => response,
    enabled: isAuthenticated,
  });

  const createAreaMutation = useMutation({
    mutationFn: createAreaFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["areas"] });
    },
  });

  const updateAreaMutation = useMutation({
    mutationFn: updateAreaFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["areas"] });
    },
  });

  const deleteAreaMutation = useMutation({
    mutationFn: deleteAreaFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["areas"] });
    },
  });

  // mutateAsync, not mutate: the caller needs to know whether this actually
  // succeeded. The form dialogs keep themselves open and disabled until it
  // settles, and close only on success -- previously they closed synchronously
  // on the next line, so a failed POST showed an error over a dialog that had
  // already vanished with the user's input in it.
  //
  // mutationFn rejects on failure: every *Function above routes its catch
  // through handleApiError, which rethrows on every branch.
  async function addArea(newArea) {
    return createAreaMutation.mutateAsync(newArea);
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
    removeArea,
  };
}
