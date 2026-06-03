import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

// ── EventSource mock ─────────────────────────────────────────────────────────

let _instance = null;

class MockEventSource {
  constructor(url) {
    this.url = url;
    this.readyState = MockEventSource.CONNECTING;
    this._listeners = {};
    _instance = this;
  }
  addEventListener(event, handler) {
    this._listeners[event] = handler;
  }
  close() {
    this.readyState = MockEventSource.CLOSED;
  }
  _emit(event, data) {
    if (this._listeners[event]) {
      this._listeners[event](data);
    }
  }
}
MockEventSource.CONNECTING = 0;
MockEventSource.OPEN = 1;
MockEventSource.CLOSED = 2;

// ── Dependency mocks ─────────────────────────────────────────────────────────

const mockInvalidateQueries = vi.fn();

vi.mock("@tanstack/vue-query", () => ({
  useQueryClient: () => ({ invalidateQueries: mockInvalidateQueries }),
}));

vi.mock("@/stores/offline", () => ({
  useOfflineStore: () => ({ isOnline: true }),
}));

// ── Tests ────────────────────────────────────────────────────────────────────

describe("useSSE", () => {
  beforeEach(() => {
    _instance = null;
    mockInvalidateQueries.mockClear();
    global.EventSource = MockEventSource;
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  it("connect() creates an EventSource at /api/v2/events/", async () => {
    const { useSSE } = await import("@/composables/sseComposable");
    const { connect } = useSSE();

    connect();

    expect(_instance).not.toBeNull();
    expect(_instance.url).toBe("/api/v2/events/");
  });

  it("connect() is idempotent — a second call does not open a second connection", async () => {
    const { useSSE } = await import("@/composables/sseComposable");
    const { connect } = useSSE();

    connect();
    const first = _instance;
    first.readyState = MockEventSource.OPEN;

    connect();

    expect(_instance).toBe(first);
  });

  it("disconnect() closes the EventSource", async () => {
    const { useSSE } = await import("@/composables/sseComposable");
    const { connect, disconnect } = useSSE();

    connect();
    disconnect();

    expect(_instance.readyState).toBe(MockEventSource.CLOSED);
  });

  it("chores event invalidates chores and areas query keys", async () => {
    const { useSSE } = await import("@/composables/sseComposable");
    const { connect } = useSSE();

    connect();
    _instance._emit("message", { data: JSON.stringify({ type: "chores" }) });

    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: ["chores"] });
    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: ["areas"] });
  });

  it("connected event does not trigger query invalidation", async () => {
    const { useSSE } = await import("@/composables/sseComposable");
    const { connect } = useSSE();

    connect();
    _instance._emit("message", { data: JSON.stringify({ type: "connected" }) });

    expect(mockInvalidateQueries).not.toHaveBeenCalled();
  });

  it("options event invalidates options query key", async () => {
    const { useSSE } = await import("@/composables/sseComposable");
    const { connect } = useSSE();

    connect();
    _instance._emit("message", { data: JSON.stringify({ type: "options" }) });

    expect(mockInvalidateQueries).toHaveBeenCalledWith({ queryKey: ["options"] });
  });

  it("malformed event data does not throw", async () => {
    const { useSSE } = await import("@/composables/sseComposable");
    const { connect } = useSSE();

    connect();
    expect(() =>
      _instance._emit("message", { data: "not-json{{{" })
    ).not.toThrow();
    expect(mockInvalidateQueries).not.toHaveBeenCalled();
  });
});
