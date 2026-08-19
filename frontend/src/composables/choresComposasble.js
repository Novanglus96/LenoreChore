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
    // URLSearchParams rather than string concatenation: the hand-built version
    // was one missing "&" away from a silently wrong query, and it grew a
    // parameter every time the filter did.
    const params = new URLSearchParams();
    params.set("inactive", String(Boolean(filters.inactive)));
    if (filters.timeframe != null) {
      params.set("timeframe", filters.timeframe);
    }
    if (filters.assignee_id) {
      params.set("assignee_id", filters.assignee_id);
    }
    if (filters.area_id) {
      params.set("area_id", filters.area_id);
    }
    if (filters.group_id) {
      params.set("group_id", filters.group_id);
    }
    if (filters.chore_name) {
      params.set("chore_name", filters.chore_name);
    }
    if (filters.overdue) {
      params.set("overdue", "true");
    }
    // Omitted when it is the default, so the common request keeps the URL --
    // and therefore the Workbox cache entry -- it had before.
    if (filters.sort && filters.sort !== "due") {
      params.set("sort", filters.sort);
    }
    const response = await apiClient.get("/chores?" + params.toString());
    return response.data;
  } catch (error) {
    handleApiError(error, "Chores not fetched: ");
  }
}

async function getChoreNamesFunction() {
  try {
    const response = await apiClient.get("/chores/names");
    return response.data;
  } catch (error) {
    handleApiError(error, "Chore names not fetched: ");
  }
}

/**
 * The names that exist on more than one active chore -- dusting that lives
 * separately in every room, and so on. Feeds the "one task, every area" filter.
 *
 * Its own query rather than something derived from the chores list, because
 * that list is itself filtered: deriving the options from it would make them
 * disappear as soon as one was chosen.
 */
export function useChoreNames() {
  const userStore = useUserStore();
  const isAuthenticated = computed(() => userStore.isLoggedIn);

  const { data: choreNames, isLoading } = useQuery({
    queryKey: ["chorenames"],
    queryFn: getChoreNamesFunction,
    select: response => response,
    enabled: isAuthenticated,
  });

  return { choreNames, isLoading };
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
      queryClient.invalidateQueries({ queryKey: ["chores"] });
      // The chore-name index counts ACTIVE chores by name, so a create,
      // rename, delete or disable can change it. complete/snooze/claim
      // cannot, and deliberately do not refetch it.
      queryClient.invalidateQueries({ queryKey: ["chorenames"] });
      queryClient.invalidateQueries({ queryKey: ["areas"] });
    },
  });

  const updateChoreMutation = useMutation({
    mutationFn: updateChoreFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chores"] });
      // The chore-name index counts ACTIVE chores by name, so a create,
      // rename, delete or disable can change it. complete/snooze/claim
      // cannot, and deliberately do not refetch it.
      queryClient.invalidateQueries({ queryKey: ["chorenames"] });
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
      if (error.queued) {
        chorestore.showSnackbar(
          "Chore marked complete — will sync when reconnected",
          "warning"
        );
      } else {
        context?.snapshots?.forEach(([key, data]) =>
          queryClient.setQueryData(key, data)
        );
      }
    },
    onSuccess: () => {
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
      if (error.queued) {
        chorestore.showSnackbar(
          "Chore snoozed — will sync when reconnected",
          "warning"
        );
      } else {
        context?.snapshots?.forEach(([key, data]) =>
          queryClient.setQueryData(key, data)
        );
      }
    },
    onSuccess: () => {
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
      if (error.queued) {
        chorestore.showSnackbar(
          "Chore assignment updated — will sync when reconnected",
          "warning"
        );
      } else {
        context?.snapshots?.forEach(([key, data]) =>
          queryClient.setQueryData(key, data)
        );
      }
    },
    onSuccess: () => {
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
      if (error.queued) {
        chorestore.showSnackbar(
          "Chore toggled — will sync when reconnected",
          "warning"
        );
      } else {
        context?.snapshots?.forEach(([key, data]) =>
          queryClient.setQueryData(key, data)
        );
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chores"] });
      // The chore-name index counts ACTIVE chores by name, so a create,
      // rename, delete or disable can change it. complete/snooze/claim
      // cannot, and deliberately do not refetch it.
      queryClient.invalidateQueries({ queryKey: ["chorenames"] });
      queryClient.invalidateQueries({ queryKey: ["areas"] });
    },
  });

  const deleteChoreMutation = useMutation({
    mutationFn: deleteChoreFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chores"] });
      // The chore-name index counts ACTIVE chores by name, so a create,
      // rename, delete or disable can change it. complete/snooze/claim
      // cannot, and deliberately do not refetch it.
      queryClient.invalidateQueries({ queryKey: ["chorenames"] });
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
  async function addChore(newChore) {
    return createChoreMutation.mutateAsync(newChore);
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
