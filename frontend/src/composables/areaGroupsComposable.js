import { computed } from "vue";
import { useUserStore } from "@/stores/user";
import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import apiClient from "@/api/client";
import { useChoreStore } from "@/stores/chores";
import { handleApiError } from "@/utils/apiErrorHandler";

async function createAreaGroupFunction(newAreaGroup) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.post("/areagroups", newAreaGroup);
    chorestore.showSnackbar("Area group created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Area group not created: ");
  }
}

async function updateAreaGroupFunction(updatedAreaGroup) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.put(
      "/areagroups" + updatedAreaGroup.id,
      updatedAreaGroup,
    );
    chorestore.showSnackbar("Area group updated successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Area group not updated: ");
  }
}

async function deleteAreaGroupFunction(deletedAreaGroup) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.delete(
      "/areagroups" + deletedAreaGroup.id,
    );
    chorestore.showSnackbar("Area group deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Area group not deleted: ");
  }
}

async function getAreaGroupsFunction() {
  try {
    const response = await apiClient.get("/areagroups");
    return response.data;
  } catch (error) {
    handleApiError(error, "Area groups not fetched: ");
  }
}

export function useAreaGroups() {
  const queryClient = useQueryClient();
  const userStore = useUserStore();
  const isAuthenticated = computed(() => userStore.isLoggedIn);
  const { data: areagroups, isLoading } = useQuery({
    queryKey: ["areagroups"],
    queryFn: getAreaGroupsFunction,
    select: response => response,
    enabled: isAuthenticated,
  });

  const createAreaGroupMutation = useMutation({
    mutationFn: createAreaGroupFunction,
    onSuccess: () => {
      console.log("Success adding area group");
      queryClient.invalidateQueries({ queryKey: ["areagroups"] });
    },
  });

  const updateAreaGroupMutation = useMutation({
    mutationFn: updateAreaGroupFunction,
    onSuccess: () => {
      console.log("Success updating area group");
      queryClient.invalidateQueries({ queryKey: ["areagroups"] });
    },
  });

  const deleteAreaGroupMutation = useMutation({
    mutationFn: deleteAreaGroupFunction,
    onSuccess: () => {
      console.log("Success deleting area group");
      queryClient.invalidateQueries({ queryKey: ["areagroups"] });
    },
  });

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
    removeAreaGroup,
  };
}
