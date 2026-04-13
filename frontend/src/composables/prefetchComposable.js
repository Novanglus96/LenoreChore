import { useQueryClient } from "@tanstack/vue-query";
import apiClient from "@/api/client";

// Default filters matching the chore list default state
const DEFAULT_CHORE_FILTERS = {
  inactive: false,
  timeframe: null,
  assignee_id: null,
  area_id: null,
};

export function usePrefetch() {
  const queryClient = useQueryClient();

  async function prefetchCriticalData() {
    // Only prefetch if data is older than 2 minutes to avoid redundant fetches
    const staleTime = 2 * 60 * 1000;

    await Promise.allSettled([
      queryClient.prefetchQuery({
        queryKey: ["chores", DEFAULT_CHORE_FILTERS],
        queryFn: () =>
          apiClient.get("/chores?inactive=false").then((r) => r.data),
        staleTime,
      }),
      queryClient.prefetchQuery({
        queryKey: ["areas"],
        queryFn: () => apiClient.get("/areas").then((r) => r.data),
        staleTime,
      }),
      queryClient.prefetchQuery({
        queryKey: ["areagroups"],
        queryFn: () => apiClient.get("/areagroups").then((r) => r.data),
        staleTime,
      }),
      queryClient.prefetchQuery({
        queryKey: ["options"],
        queryFn: () => apiClient.get("/options/1").then((r) => r.data),
        staleTime,
      }),
      queryClient.prefetchQuery({
        queryKey: ["users"],
        queryFn: () => apiClient.get("/users").then((r) => r.data),
        staleTime,
      }),
    ]);
  }

  return { prefetchCriticalData };
}
