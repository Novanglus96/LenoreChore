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
    chorestore.showSnackbar("Group added", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Area group not created: ");
  }
}

// NOTE: both of these were "/areagroups" + id -- with no slash -- so they built
// /areagroups5 and would have 404'd on the first call. Nothing ever called
// them: they were exported and unused until this feature, which is exactly how
// a broken URL survives in a codebase. Compare areasComposable, which has the
// slash.
async function updateAreaGroupFunction(updatedAreaGroup) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.put(
      "/areagroups/" + updatedAreaGroup.id,
      updatedAreaGroup,
    );
    chorestore.showSnackbar("Group saved", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "Area group not updated: ");
  }
}

/**
 * @param {object} deletedAreaGroup `{ id, reassign_to }`. `reassign_to` names
 *   the group this group's areas move into; the API defaults to the
 *   lowest-ordered remaining group and refuses to delete the last group.
 */
async function deleteAreaGroupFunction(deletedAreaGroup) {
  const chorestore = useChoreStore();
  try {
    const query =
      deletedAreaGroup.reassign_to != null
        ? "?reassign_to=" + deletedAreaGroup.reassign_to
        : "";
    const response = await apiClient.delete(
      "/areagroups/" + deletedAreaGroup.id + query,
    );
    const moved = response.data?.areas_moved ?? 0;
    chorestore.showSnackbar(
      moved > 0
        ? `Group deleted — ${moved} area${moved === 1 ? "" : "s"} moved`
        : "Group deleted",
      "success",
    );
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
      queryClient.invalidateQueries({ queryKey: ["areagroups"] });
    },
  });

  // A group's name and colour are rendered on every area card AND every chore
  // card (the stripe), and a delete moves areas between groups -- so both of
  // these have to invalidate more than their own list.
  const updateAreaGroupMutation = useMutation({
    mutationFn: updateAreaGroupFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["areagroups"] });
      queryClient.invalidateQueries({ queryKey: ["areas"] });
      queryClient.invalidateQueries({ queryKey: ["chores"] });
    },
  });

  const deleteAreaGroupMutation = useMutation({
    mutationFn: deleteAreaGroupFunction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["areagroups"] });
      queryClient.invalidateQueries({ queryKey: ["areas"] });
      queryClient.invalidateQueries({ queryKey: ["chores"] });
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
  async function addAreaGroup(newAreaGroup) {
    return createAreaGroupMutation.mutateAsync(newAreaGroup);
  }

  async function editAreaGroup(updatedAreaGroup) {
    return updateAreaGroupMutation.mutateAsync(updatedAreaGroup);
  }

  async function removeAreaGroup(deletedAreaGroup) {
    return deleteAreaGroupMutation.mutateAsync(deletedAreaGroup);
  }

  return {
    areagroups,
    isLoading,
    addAreaGroup,
    editAreaGroup,
    removeAreaGroup,
  };
}
