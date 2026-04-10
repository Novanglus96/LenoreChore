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

    chorestore.showSnackbar("Syncing offline changes...", "info");

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
        // Server error: count retries, discard after max
        offlineStore.incrementRetries(mutation.id);
        if (mutation.retries + 1 >= 3) {
          offlineStore.dequeue(mutation.id);
          failed++;
        }
      }
    }

    if (succeeded > 0) {
      queryClient.invalidateQueries();
      chorestore.showSnackbar(
        `Synced ${succeeded} offline change${succeeded !== 1 ? "s" : ""}`,
        "success"
      );
    }
    if (failed > 0) {
      chorestore.showSnackbar(
        `${failed} change${failed !== 1 ? "s" : ""} could not be synced and were discarded`,
        "error"
      );
    }
  }

  return { replayQueue };
}
