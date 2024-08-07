import { useQuery, useQueryClient } from "@tanstack/vue-query";
import axios from "axios";
import { useChoreStore } from "@/stores/chores";

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

async function getVersionFunction() {
  try {
    const response = await apiClient.get("/version/list");
    return response.data;
  } catch (error) {
    handleApiError(error, "Version not fetched: ");
  }
}

export function useVersion() {
  const queryClient = useQueryClient();
  const { data: version, isLoading } = useQuery({
    queryKey: ["version"],
    queryFn: () => getVersionFunction(),
    select: response => response,
    client: queryClient,
  });

  const prefetchVersion = async () => {
    await queryClient.prefetchQuery({
      queryKey: ["version"],
      queryFn: () => getVersionFunction(),
    });
  };

  return {
    isLoading,
    version,
    prefetchVersion,
  };
}
