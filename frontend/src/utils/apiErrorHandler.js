import { useChoreStore } from "@/stores/chores";

/**
 * A human reason for a failed request, in the app's voice.
 *
 * @param {object} error an axios error
 * @returns {string} a sentence fragment to follow the caller's prefix
 */
function describe(error) {
  if (!error.response) {
    // No reply at all: DNS, a dropped connection, a server that is not there.
    return "no reply from the server — you may be offline.";
  }
  const status = error.response.status;
  if (status >= 500) return `something went wrong on the server (${status}).`;
  if (status === 404) return "it wasn't there any more.";
  if (status === 403) return `you don't have permission (${status}).`;
  return `the server turned it down (${status}).`;
}

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
  // "Chore not updated: Error #500" told the user nothing they could act on
  // and read like a stack trace. The status stays -- it is the one thing worth
  // quoting in a bug report -- but it now sits inside a sentence that says
  // whose problem it is.
  chorestore.showSnackbar(message + describe(error), "error");
  throw error;
}
