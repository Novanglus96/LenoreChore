import { computed } from "vue";
import { useUserStore } from "@/stores/user";
import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import apiClient from "@/api/client";
import { useChoreStore } from "@/stores/chores";
import { handleApiError } from "@/utils/apiErrorHandler";

async function createChoreFunction(newChore) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.post("/chores", newChore);
    chorestore.showSnackbar("Chore created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Chore not created: ");
  }
}

async function updateChoreFunction(updatedChore) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.put(
      "/chores/" + updatedChore.id,
      updatedChore,
    );
    chorestore.showSnackbar("Chore updated successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Chore not updated: ");
  }
}

async function completeChoreFunction(completedChore) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.patch(
      "/chores/completechore/" + completedChore.id,
      completedChore,
    );
    chorestore.showSnackbar("Chore completed successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Chore not completed: ");
  }
}

async function snoozeChoreFunction(snoozedChore) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.patch(
      "/chores/snoozechore/" + snoozedChore.id,
      snoozedChore,
    );
    chorestore.showSnackbar("Chore snoozed successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Chore not snoozed: ");
  }
}

async function claimChoreFunction(claimedChore) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.patch(
      "/chores/claimchore/" + claimedChore.id,
      claimedChore,
    );
    chorestore.showSnackbar("Chore claimed successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Chore not claimed: ");
  }
}

async function toggleChoreFunction(toggledChore) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.patch(
      "/chores/togglechore/" + toggledChore.id,
      toggledChore,
    );
    chorestore.showSnackbar("Chore toggled successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Chore not toggled: ");
  }
}

async function deleteChoreFunction(deletedChore) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.delete("/chores/" + deletedChore.id);
    chorestore.showSnackbar("Chore deleted successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Chore not deleted: ");
  }
}

async function getChoresFunction(filters) {
  try {
    let params = "";
    params = "inactive=" + filters.inactive;
    if (filters.timeframe != null) {
      params = params + "&timeframe=" + filters.timeframe;
    }
    if (filters.assignee_id) {
      params = params + "&assignee_id=" + filters.assignee_id;
    }
    if (filters.area_id) {
      params = params + "&area_id=" + filters.area_id;
    }
    const response = await apiClient.get("/chores?" + params);
    return response.data;
  } catch (error) {
    handleApiError(error, "Chores not fetched: ");
  }
}

export function useChores() {
  const queryClient = useQueryClient();
  const userStore = useUserStore();
  const isAuthenticated = computed(() => userStore.isLoggedIn);
  const chorestore = useChoreStore();
  const { data: chores, isLoading } = useQuery({
    queryKey: ["chores", chorestore.filters],
    queryFn: () => getChoresFunction(chorestore.filters),
    select: response => response,
    enabled: isAuthenticated,
  });

  const createChoreMutation = useMutation({
    mutationFn: createChoreFunction,
    onSuccess: () => {
      console.log("Success adding chore");
      queryClient.invalidateQueries({ queryKey: ["chores"] });
      queryClient.invalidateQueries({ queryKey: ["areas"] });
    },
  });

  const updateChoreMutation = useMutation({
    mutationFn: updateChoreFunction,
    onSuccess: () => {
      console.log("Success updating chore");
      queryClient.invalidateQueries({ queryKey: ["chores"] });
      queryClient.invalidateQueries({ queryKey: ["areas"] });
    },
  });

  const completeChoreMutation = useMutation({
    mutationFn: completeChoreFunction,
    onMutate: async (completedChore) => {
      await queryClient.cancelQueries({ queryKey: ["chores"] });
      const snapshots = queryClient.getQueriesData({ queryKey: ["chores"] });
      queryClient.setQueriesData({ queryKey: ["chores"] }, (old) =>
        Array.isArray(old) ? old.filter((c) => c.id !== completedChore.id) : old
      );
      return { snapshots };
    },
    onError: (error, _vars, context) => {
      if (!error.queued) {
        context?.snapshots?.forEach(([key, data]) =>
          queryClient.setQueryData(key, data)
        );
      }
    },
    onSuccess: () => {
      console.log("Success completing chore");
      queryClient.invalidateQueries({ queryKey: ["chores"] });
      queryClient.invalidateQueries({ queryKey: ["areas"] });
      queryClient.invalidateQueries({ queryKey: ["historyitems"] });
      queryClient.invalidateQueries({ queryKey: ["weeklytotals"] });
    },
  });

  const snoozeChoreMutation = useMutation({
    mutationFn: snoozeChoreFunction,
    onMutate: async (snoozedChore) => {
      await queryClient.cancelQueries({ queryKey: ["chores"] });
      const snapshots = queryClient.getQueriesData({ queryKey: ["chores"] });
      queryClient.setQueriesData({ queryKey: ["chores"] }, (old) =>
        Array.isArray(old)
          ? old.map((c) =>
              c.id === snoozedChore.id ? { ...c, nextDue: snoozedChore.nextDue } : c
            )
          : old
      );
      return { snapshots };
    },
    onError: (error, _vars, context) => {
      if (!error.queued) {
        context?.snapshots?.forEach(([key, data]) =>
          queryClient.setQueryData(key, data)
        );
      }
    },
    onSuccess: () => {
      console.log("Success snoozing chore");
      queryClient.invalidateQueries({ queryKey: ["chores"] });
      queryClient.invalidateQueries({ queryKey: ["areas"] });
    },
  });

  const claimChoreMutation = useMutation({
    mutationFn: claimChoreFunction,
    onMutate: async (claimedChore) => {
      await queryClient.cancelQueries({ queryKey: ["chores"] });
      const snapshots = queryClient.getQueriesData({ queryKey: ["chores"] });
      const users = queryClient.getQueryData(["users"]);
      const newAssignee =
        users?.find((u) => u.id === claimedChore.assignee_id) ?? null;
      queryClient.setQueriesData({ queryKey: ["chores"] }, (old) =>
        Array.isArray(old)
          ? old.map((c) =>
              c.id === claimedChore.id
                ? {
                    ...c,
                    assignee_id: claimedChore.assignee_id,
                    assignee: newAssignee,
                    isAssigned: !!claimedChore.assignee_id,
                  }
                : c
            )
          : old
      );
      return { snapshots };
    },
    onError: (error, _vars, context) => {
      if (!error.queued) {
        context?.snapshots?.forEach(([key, data]) =>
          queryClient.setQueryData(key, data)
        );
      }
    },
    onSuccess: () => {
      console.log("Success claiming chore");
      queryClient.invalidateQueries({ queryKey: ["chores"] });
      queryClient.invalidateQueries({ queryKey: ["areas"] });
    },
  });

  const toggleChoreMutation = useMutation({
    mutationFn: toggleChoreFunction,
    onMutate: async (toggledChore) => {
      await queryClient.cancelQueries({ queryKey: ["chores"] });
      const snapshots = queryClient.getQueriesData({ queryKey: ["chores"] });
      queryClient.setQueriesData({ queryKey: ["chores"] }, (old) =>
        Array.isArray(old)
          ? old.map((c) =>
              c.id === toggledChore.id ? { ...c, status: toggledChore.status } : c
            )
          : old
      );
      return { snapshots };
    },
    onError: (error, _vars, context) => {
      if (!error.queued) {
        context?.snapshots?.forEach(([key, data]) =>
          queryClient.setQueryData(key, data)
        );
      }
    },
    onSuccess: () => {
      console.log("Success toggling chore");
      queryClient.invalidateQueries({ queryKey: ["chores"] });
      queryClient.invalidateQueries({ queryKey: ["areas"] });
    },
  });

  const deleteChoreMutation = useMutation({
    mutationFn: deleteChoreFunction,
    onSuccess: () => {
      console.log("Success deleting chore");
      queryClient.invalidateQueries({ queryKey: ["chores"] });
      queryClient.invalidateQueries({ queryKey: ["areas"] });
    },
  });

  async function addChore(newChore) {
    createChoreMutation.mutate(newChore);
  }

  async function editChore(updatedChore) {
    updateChoreMutation.mutate(updatedChore);
  }

  async function complete(completedChore) {
    completeChoreMutation.mutate(completedChore);
  }
  async function snooze(snoozedChore) {
    snoozeChoreMutation.mutate(snoozedChore);
  }
  async function claim(claimedChore) {
    claimChoreMutation.mutate(claimedChore);
  }
  async function toggle(toggledChore) {
    toggleChoreMutation.mutate(toggledChore);
  }

  async function removeChore(deletedChore) {
    deleteChoreMutation.mutate(deletedChore);
  }

  return {
    chores,
    isLoading,
    addChore,
    editChore,
    removeChore,
    complete,
    snooze,
    claim,
    toggle,
  };
}
