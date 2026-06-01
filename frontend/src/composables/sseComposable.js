import { useQueryClient } from "@tanstack/vue-query";
import { useOfflineStore } from "@/stores/offline";

const QUERY_KEYS = {
  chores: ["chores", "areas"],
  areas: ["areas", "areagroups"],
  areagroups: ["areagroups"],
  options: ["options"],
  history: ["historyitems"],
  users: ["users"],
};

export function useSSE() {
  const queryClient = useQueryClient();
  const offlineStore = useOfflineStore();

  let source = null;
  let reconnectTimer = null;
  let reconnectDelay = 2000;

  function connect() {
    if (offlineStore.isOffline) return;
    if (source && source.readyState !== EventSource.CLOSED) return;

    source = new EventSource("/api/v2/events/");

    source.addEventListener("message", (event) => {
      reconnectDelay = 2000;
      let data;
      try {
        data = JSON.parse(event.data);
      } catch {
        return;
      }
      if (data.type === "connected") return;

      const keys = QUERY_KEYS[data.type];
      if (keys) {
        keys.forEach((key) => queryClient.invalidateQueries({ queryKey: [key] }));
      }
    });

    source.addEventListener("error", () => {
      source.close();
      source = null;
      if (!offlineStore.isOffline) {
        reconnectTimer = setTimeout(() => {
          reconnectDelay = Math.min(reconnectDelay * 2, 30000);
          connect();
        }, reconnectDelay);
      }
    });
  }

  function disconnect() {
    clearTimeout(reconnectTimer);
    if (source) {
      source.close();
      source = null;
    }
  }

  return { connect, disconnect };
}
