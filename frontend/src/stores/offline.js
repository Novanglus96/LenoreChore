import { defineStore } from "pinia";
import { ref } from "vue";

export const useOfflineStore = defineStore(
  "offline",
  () => {
    const isOnline = ref(navigator.onLine);
    const mutationQueue = ref([]);

    function setOnline(val) {
      isOnline.value = val;
    }

    function enqueue(mutation) {
      mutationQueue.value.push({
        id: crypto.randomUUID(),
        timestamp: Date.now(),
        retries: 0,
        ...mutation, // { method, url, data }
      });
    }

    function dequeue(id) {
      mutationQueue.value = mutationQueue.value.filter((m) => m.id !== id);
    }

    function incrementRetries(id) {
      const m = mutationQueue.value.find((m) => m.id === id);
      if (m) m.retries++;
    }

    function clearQueue() {
      mutationQueue.value = [];
    }

    return {
      isOnline,
      mutationQueue,
      setOnline,
      enqueue,
      dequeue,
      incrementRetries,
      clearQueue,
    };
  },
  {
    persist: {
      paths: ["mutationQueue"], // isOnline is always derived fresh on init
    },
  }
);
