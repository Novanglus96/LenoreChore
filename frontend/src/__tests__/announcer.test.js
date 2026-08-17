import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { nextTick } from "vue";
import { useAnnouncer } from "@/composables/announcerComposable";

describe("useAnnouncer", () => {
  let politeMessage, assertiveMessage, announce;

  beforeEach(async () => {
    vi.useFakeTimers();
    ({ politeMessage, assertiveMessage, announce } = useAnnouncer());
    // Module-level state is shared by design, so each test starts from a known
    // point rather than inheriting the previous one's text.
    politeMessage.value = "";
    assertiveMessage.value = "";
    await nextTick();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("routes ordinary messages to the polite region", async () => {
    await announce("Chore completed successfully!");
    expect(politeMessage.value).toBe("Chore completed successfully!");
    expect(assertiveMessage.value).toBe("");
  });

  it("routes urgent messages to the assertive region", async () => {
    await announce("Chore not saved", "assertive");
    expect(assertiveMessage.value).toBe("Chore not saved");
    expect(politeMessage.value).toBe("");
  });

  it("re-announces an identical consecutive message", async () => {
    // The reason this composable exists rather than binding text directly:
    // a screen reader observes DOM mutations, and setting a node's text to what
    // it already says is not one. Completing two chores in a row would announce
    // once. The clear-then-set has to survive refactoring.
    await announce("Chore completed successfully!");
    expect(politeMessage.value).toBe("Chore completed successfully!");

    // Not awaited: this catches the state between the clear and the re-set.
    const pending = announce("Chore completed successfully!");
    expect(politeMessage.value).toBe("");

    await pending;
    expect(politeMessage.value).toBe("Chore completed successfully!");
  });

  it("clears the regions so stale text is not left in the a11y tree", async () => {
    await announce("Chore snoozed");
    expect(politeMessage.value).toBe("Chore snoozed");

    vi.advanceTimersByTime(5000);
    expect(politeMessage.value).toBe("");
    expect(assertiveMessage.value).toBe("");
  });

  it("ignores empty messages", async () => {
    await announce("");
    expect(politeMessage.value).toBe("");
  });
});
