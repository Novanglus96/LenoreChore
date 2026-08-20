import { ref, nextTick } from "vue";

/**
 * Screen-reader announcements.
 *
 * The app's entire feedback channel is the snackbar -- every success, every
 * error, the offline-queue notices -- and Vuetify's VSnackbar is not a live
 * region, so none of it was ever announced. A sighted user gets confirmation
 * that a chore was completed; a screen reader user got silence.
 *
 * ── Why not just put aria-live on the snackbar ──
 * A live region has to be PRESENT IN THE DOM BEFORE its content changes for
 * assistive tech to observe the mutation. VSnackbar renders its content only
 * while it is open, so it appears and disappears wholesale -- adding aria-live
 * to it announces unreliably or not at all, depending on the screen reader.
 *
 * The regions below are mounted once in App.vue for the life of the app and
 * only ever have their text swapped, which is the pattern that actually works.
 *
 * ── Why two regions ──
 * Politeness cannot be changed on a live region after the fact with any
 * reliability, so urgency is chosen by writing to a different region rather
 * than by mutating an attribute. Errors interrupt; everything else waits for a
 * pause.
 *
 * Module-level state on purpose: these back exactly one pair of DOM nodes, so
 * every caller must share them.
 */

const politeMessage = ref("");
const assertiveMessage = ref("");

let clearTimer = null;

/**
 * Announce a message to assistive technology.
 *
 * @param {string} message Text to announce.
 * @param {"polite"|"assertive"} [urgency] "assertive" interrupts; default waits.
 */
async function announce(message, urgency = "polite") {
  if (!message) return;

  const target = urgency === "assertive" ? assertiveMessage : politeMessage;

  // Writing the same string twice is a no-op to a screen reader -- it observes
  // mutations, and setting a node's text to what it already says is not one. So
  // "Chore completed successfully!" twice in a row would announce once. Clearing
  // first, then setting after the DOM has flushed, makes the second one land.
  target.value = "";
  await nextTick();
  target.value = message;

  // Emptied afterwards so the text is not left sitting in the accessibility
  // tree, where a user navigating by element would meet a stale announcement
  // long after it stopped being true.
  if (clearTimer) clearTimeout(clearTimer);
  clearTimer = setTimeout(() => {
    politeMessage.value = "";
    assertiveMessage.value = "";
  }, 5000);
}

export function useAnnouncer() {
  return { politeMessage, assertiveMessage, announce };
}
