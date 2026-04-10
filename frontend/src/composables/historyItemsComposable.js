import { computed } from "vue";
import { useUserStore } from "@/stores/user";
import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import apiClient from "@/api/client";
import { useChoreStore } from "@/stores/chores";
import { useHistoryItemsStore } from "@/stores/historyitems";
import { handleApiError } from "@/utils/apiErrorHandler";

async function createHistoryItemFunction(newHistoryItem) {
  const chorestore = useChoreStore();
  try {
    const response = await apiClient.post("/historyitems", newHistoryItem);
    chorestore.showSnackbar("History Item created successfully!", "success");
    return response.data;
  } catch (error) {
    handleApiError(error, "History Item not created: ");
  }
}

async function getHistoryItemsFunction(pageinfo) {
  try {
    let params = "?page=" + pageinfo.page + "&page_size=" + pageinfo.page_size;
    const response = await apiClient.get("/historyitems" + params);
    return response.data;
  } catch (error) {
    handleApiError(error, "History Items not fetched: ");
  }
}

async function getWeeklyTotalsFunction(graph) {
  try {
    const response = await apiClient.get("/weeklytotals?week=" + graph.week);
    return response.data;
  } catch (error) {
    handleApiError(error, "Weekly Totals not fetched: ");
  }
}

export function useHistoryItems() {
  const queryClient = useQueryClient();
  const userStore = useUserStore();
  const isAuthenticated = computed(() => userStore.isLoggedIn);
  const historystore = useHistoryItemsStore();
  const { data: historyItems, isLoading } = useQuery({
    queryKey: ["historyitems", historystore.pageinfo],
    queryFn: () => getHistoryItemsFunction(historystore.pageinfo),
    select: response => response,
    enabled: isAuthenticated,
  });

  const createHistoryItemMutation = useMutation({
    mutationFn: createHistoryItemFunction,
    onSuccess: () => {
      console.log("Success adding history item");
      queryClient.invalidateQueries({ queryKey: ["historyitems"] });
    },
  });

  async function addHistoryItem(newHistoryItem) {
    createHistoryItemMutation.mutate(newHistoryItem);
  }

  return {
    historyItems,
    isLoading,
    addHistoryItem,
  };
}

export function useWeeklyTotals() {
  const userStore = useUserStore();
  const isAuthenticated = computed(() => userStore.isLoggedIn);
  const historystore = useHistoryItemsStore();
  const { data: weeklyTotals, isLoading } = useQuery({
    queryKey: ["weeklytotals", historystore.graph],
    queryFn: () => getWeeklyTotalsFunction(historystore.graph),
    select: response => response,
    enabled: isAuthenticated,
  });

  return {
    isLoading,
    weeklyTotals,
  };
}
