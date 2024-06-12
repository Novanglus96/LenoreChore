import { useQuery, useMutation, useQueryClient } from "@tanstack/vue-query";
import axios from "axios";
import { useChoreStore } from "@/stores/chores";
import { useHistoryItemsStore } from "@/stores/historyitems";

const apiClient = axios.create({
  baseURL: "/api/v2",
  withCredentials: false,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },
});

function handleApiError(error, message) {
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

async function getWeeklyTotalsFunction() {
  try {
    const response = await apiClient.get("/weeklytotals");
    return response.data;
  } catch (error) {
    handleApiError(error, "Weekly Totals not fetched: ");
  }
}

export function useHistoryItems() {
  const queryClient = useQueryClient();
  const historystore = useHistoryItemsStore();
  const { data: historyItems, isLoading } = useQuery({
    queryKey: ["historyitems", historystore.pageinfo],
    queryFn: () => getHistoryItemsFunction(historystore.pageinfo),
    select: response => response,
    client: queryClient,
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
  const queryClient = useQueryClient();
  const { data: weeklyTotals, isLoading } = useQuery({
    queryKey: ["weeklytotals"],
    queryFn: getWeeklyTotalsFunction,
    select: response => response,
    client: queryClient,
  });

  return {
    isLoading,
    weeklyTotals,
  };
}
