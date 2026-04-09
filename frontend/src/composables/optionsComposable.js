import { computed } from "vue";
import { useUserStore } from "@/stores/user";
import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import apiClient from "@/api/client";
import { useChoreStore } from "@/stores/chores";


function handleApiError(error, message) {
  if (error.response?.status === 401) throw error;
  const chorestore = useChoreStore();
  if (error.response) {
    console.error("Response error:", error.response.data);
    console.error("Status code:", error.response.status);
    console.error("Headers", error.response.headers);
  } else if (error.request) {
    console.error("No response received:", error.request);
  } else {
    console.error("Error during request setup:", error.message);
  }
  chorestore.showSnackbar(message + "Error #" + error.response.status, "error");
  throw error;
}

async function createOptionFunction(newOption) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.post("/options", newOption);
    chorestore.showSnackbar("Options created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Options not created: ");
  }
}

async function updateOptionFunction(updatedOption) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.put(
      "/options/" + updatedOption.id,
      updatedOption,
    );
    chorestore.showSnackbar("Options updated successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Options not updated: ");
  }
}

async function toggleVacationFunction() {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.post("/toggle_vacation");
    chorestore.showSnackbar("Vacation mode toggled successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Vacation mode not toggled: ");
  }
}

async function deleteOptionFunction(deletedOption) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.delete("/options/" + deletedOption.id);
    chorestore.showSnackbar("Options deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Options not deleted: ");
  }
}

async function getOptionsFunction() {
  try {
    const response = await apiClient.get("/options/1");
    return response.data;
  } catch (error) {
    handleApiError(error, "Options not fetched: ");
  }
}

export function useOptions() {
  const queryClient = useQueryClient();
  const userStore = useUserStore();
  const isAuthenticated = computed(() => userStore.isLoggedIn);
  const { data: options, isLoading } = useQuery({
    queryKey: ["options"],
    queryFn: getOptionsFunction,
    select: response => response,
    enabled: isAuthenticated,
  });

  const createOptionMutation = useMutation({
    mutationFn: createOptionFunction,
    onSuccess: () => {
      console.log("Success adding option");
      queryClient.invalidateQueries({ queryKey: ["options"] });
    },
  });

  const updateOptionMutation = useMutation({
    mutationFn: updateOptionFunction,
    onSuccess: () => {
      console.log("Success updating option");
      queryClient.invalidateQueries({ queryKey: ["options"] });
    },
  });

  const deleteOptionMutation = useMutation({
    mutationFn: deleteOptionFunction,
    onSuccess: () => {
      console.log("Success deleting option");
      queryClient.invalidateQueries({ queryKey: ["options"] });
    },
  });

  const toggleVacationMutation = useMutation({
    mutationFn: toggleVacationFunction,
    onSuccess: () => {
      console.log("Success toggling vacation mode");
      queryClient.invalidateQueries({ queryKey: ["options"] });
      queryClient.invalidateQueries({ queryKey: ["chores"] });
      queryClient.invalidateQueries({ queryKey: ["areas"] });
    },
  });
  async function addOption(newOption) {
    createOptionMutation.mutate(newOption);
  }

  async function editOption(updatedOption) {
    updateOptionMutation.mutate(updatedOption);
  }

  async function removeOption(deletedOption) {
    deleteOptionMutation.mutate(deletedOption);
  }

  async function toggleVacation() {
    toggleVacationMutation.mutate();
  }

  return {
    options,
    isLoading,
    addOption,
    editOption,
    removeOption,
    toggleVacation,
  };
}
