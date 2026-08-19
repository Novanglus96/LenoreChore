import { describe, it, expect, vi, beforeEach } from "vitest";
import { ref } from "vue";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

const GROUP = { id: 1, group_name: "Downstairs", group_color: "area1", group_order: 1 };

let choresData = ref([]);

// `complete` mimics the real optimistic update: the chore leaves the list the
// instant the mutation starts, well before it resolves.
const complete = vi.fn(async () => {
  choresData.value = [];
});

const completeAll = vi.fn(async () => {
  choresData.value = [];
  return { completed: 2 };
});

vi.mock("@/composables/choresComposasble", () => ({
  // ChoreFilterBar pulls useChoreNames from this same module, so the mock has
  // to cover it or every mount here fails at setup.
  useChoreNames: () => ({ choreNames: ref([]), isLoading: ref(false) }),
  useChores: () => ({
    chores: choresData,
    isLoading: ref(false),
    editChore: vi.fn(),
    removeChore: vi.fn(),
    snooze: vi.fn(),
    complete: (...a) => complete(...a),
    completeAll: (...a) => completeAll(...a),
    toggle: vi.fn(),
    claim: vi.fn(),
  }),
}));

vi.mock("@/composables/areasComposable", () => ({
  useAreas: () => ({
    areas: ref([{ id: 10, area_name: "Kitchen", group: GROUP }]),
    isLoading: ref(false),
  }),
}));

vi.mock("@/composables/areaGroupsComposable", () => ({
  useAreaGroups: () => ({ areagroups: ref([GROUP]), isLoading: ref(false) }),
}));

vi.mock("@/composables/usersComposable", () => ({
  useUsers: () => ({ users: ref([]) }),
}));

import ListView from "@/views/ListView.vue";
import { useChoreStore } from "@/stores/chores";

const vuetify = createVuetify({ components, directives });

describe("ListView — the two empty states", () => {
  let store;

  beforeEach(() => {
    setActivePinia(createPinia());
    store = useChoreStore();
    choresData = ref([]);
  });

  it("says nothing needs doing when there are no chores and no filters", () => {
    const wrapper = mount(ListView, {
      global: { plugins: [vuetify], stubs: { ChoreCard: true } },
    });
    expect(wrapper.text()).toContain("Nothing needs doing");
    expect(wrapper.text()).not.toContain("Nothing matches those filters");
  });

  it("says nothing matches once a filter is on", async () => {
    const wrapper = mount(ListView, {
      global: { plugins: [vuetify], stubs: { ChoreCard: true } },
    });
    store.filters.overdue = true;
    await wrapper.vm.$nextTick();

    // This is the integration worth pinning: ListView reads hasActiveFilters
    // off the bar through a template ref and defineExpose. An exposed computed
    // that failed to unwrap would be a truthy ref object here, and the wrong
    // empty state would never show.
    expect(wrapper.vm.hasActiveFilters).toBe(true);
    expect(wrapper.text()).toContain("Nothing matches those filters");
    expect(wrapper.text()).not.toContain("Nothing needs doing");
  });

  it("clears the filters from the empty state's action", async () => {
    const wrapper = mount(ListView, {
      global: { plugins: [vuetify], stubs: { ChoreCard: true } },
    });
    store.filters.overdue = true;
    store.filters.area_id = 10;
    await wrapper.vm.$nextTick();

    wrapper.vm.clearFilters();
    await wrapper.vm.$nextTick();

    expect(store.filters.overdue).toBe(false);
    expect(store.filters.area_id).toBeNull();
    expect(wrapper.text()).toContain("Nothing needs doing");
  });
});

describe("ListView — the last chore", () => {
  let store;

  beforeEach(() => {
    setActivePinia(createPinia());
    store = useChoreStore();
    choresData = ref([]);
    complete.mockClear();
  });

  it("celebrates when a completion empties the list", async () => {
    choresData.value = [{ id: 1, chore_name: "Dust" }];
    const wrapper = mount(ListView, {
      global: { plugins: [vuetify], stubs: { ChoreCard: true } },
    });

    await wrapper.vm.completeChore(1, 7);
    await wrapper.vm.$nextTick();

    expect(complete).toHaveBeenCalled();
    expect(wrapper.vm.justCleared).toBe(true);
    expect(wrapper.text()).toContain("That was the last one");
  });

  it("stays quiet when the list was already empty", async () => {
    // Arriving at an empty list is not an achievement, and cheering it would
    // cheapen the times it is.
    const wrapper = mount(ListView, {
      global: { plugins: [vuetify], stubs: { ChoreCard: true } },
    });
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.justCleared).toBe(false);
    expect(wrapper.text()).toContain("Nothing needs doing");
  });

  it("stays quiet when a filter empties the list", async () => {
    choresData.value = [{ id: 1, chore_name: "Dust" }];
    const wrapper = mount(ListView, {
      global: { plugins: [vuetify], stubs: { ChoreCard: true } },
    });
    await wrapper.vm.$nextTick();

    // No completion involved -- just a filter that matches nothing.
    store.filters.overdue = true;
    choresData.value = [];
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.justCleared).toBe(false);
    expect(wrapper.text()).toContain("Nothing matches those filters");
  });

  it("stops celebrating once chores come back", async () => {
    choresData.value = [{ id: 1, chore_name: "Dust" }];
    const wrapper = mount(ListView, {
      global: { plugins: [vuetify], stubs: { ChoreCard: true } },
    });
    await wrapper.vm.completeChore(1, 7);
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.justCleared).toBe(true);

    choresData.value = [{ id: 2, chore_name: "Mop" }];
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.justCleared).toBe(false);
  });
});

describe("ListView — completing a whole round", () => {
  let store;

  const mountList = () =>
    mount(ListView, {
      global: { plugins: [vuetify], stubs: { ChoreCard: true } },
    });

  beforeEach(() => {
    setActivePinia(createPinia());
    store = useChoreStore();
    choresData = ref([]);
    completeAll.mockClear();
  });

  it("is not offered without a task filter", () => {
    // "Complete everything on screen" is a far more dangerous button than
    // "complete every Dust", so the task filter is what unlocks it.
    choresData.value = [{ id: 1 }, { id: 2 }];
    const wrapper = mountList();

    expect(wrapper.vm.roundOf).toBeNull();
    expect(wrapper.text()).not.toContain("Complete all");
  });

  it("is offered once the list is one task", async () => {
    choresData.value = [{ id: 1 }, { id: 2 }];
    store.filters.chore_name = "Dust";
    const wrapper = mountList();
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.roundOf).toBe("Dust");
    expect(wrapper.text()).toContain("Doing a round of Dust");
    expect(wrapper.text()).toContain("2 chores");
  });

  it("is not offered when the filtered list is empty", async () => {
    store.filters.chore_name = "Dust";
    const wrapper = mountList();
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.roundOf).toBeNull();
  });

  it("sends every id on the list", async () => {
    choresData.value = [{ id: 4 }, { id: 9 }];
    store.filters.chore_name = "Dust";
    const wrapper = mountList();
    await wrapper.vm.$nextTick();

    await wrapper.vm.completeRound();

    expect(completeAll).toHaveBeenCalledTimes(1);
    expect(completeAll.mock.calls[0][0].ids).toEqual([4, 9]);
    expect(wrapper.vm.completingAll).toBe(false);
  });

  it("gets the last-one moment when the round empties the list", async () => {
    choresData.value = [{ id: 4 }, { id: 9 }];
    store.filters.chore_name = "Dust";
    const wrapper = mountList();
    await wrapper.vm.$nextTick();

    await wrapper.vm.completeRound();
    await wrapper.vm.$nextTick();

    // Finishing a round is a completion emptying the list, so it earns the
    // same moment a final single completion does.
    expect(wrapper.vm.justCleared).toBe(true);
  });
});
