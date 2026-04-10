import apiClient from "@/api/client";
import { useOfflineStore } from "@/stores/offline";
import { useChoreStore } from "@/stores/chores";
import { useQueryClient } from "@tanstack/vue-query";

export function useSync() {
  const offlineStore = useOfflineStore();
  const chorestore = useChoreStore();
  const queryClient = useQueryClient();

  async function replayQueue() {
    if (offlineStore.mutationQueue.length === 0) return;

    const queue = [...offlineStore.mutationQueue];
    let succeeded = 0;
    let failed = 0;

    for (const mutation of queue) {
      try {
        await apiClient.request({
          method: mutation.method,
          url: mutation.url,
          data: mutation.data,
        });
        offlineStore.dequeue(mutation.id);
        succeeded++;
      } catch (error) {
        if (error.queued) {
          // Still offline — stop replaying
          break;
        }
        // Server error: count retries, discard after max attempts
        offlineStore.incrementRetries(mutation.id);
        if (mutation.retries + 1 >= 3) {
          offlineStore.dequeue(mutation.id);
          failed++;
        }
      }
    }

    if (succeeded > 0) {
      queryClient.invalidateQueries();
    }
    if (failed > 0) {
      chorestore.showSnackbar(
        `${failed} offline change${failed !== 1 ? "s" : ""} could not be applied and were discarded`,
        "error"
      );
    }
  }

  return { replayQueue };
}
