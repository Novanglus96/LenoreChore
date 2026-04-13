import { useChoreStore } from "@/stores/chores";

export function handleApiError(error, message) {
  if (error.response?.status === 401) throw error;
  if (error.queued) throw error; // Propagate to onError so optimistic UI update is kept until sync

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
  chorestore.showSnackbar(
    message + "Error #" + error.response?.status,
    "error"
  );
  throw error;
}
