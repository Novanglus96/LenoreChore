import { describe, it, expect, vi, beforeEach } from "vitest";
import { ref } from "vue";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

const GROUP_A = { id: 1, group_name: "Downstairs", group_color: "area1", group_order: 1 };
const GROUP_B = { id: 2, group_name: "Upstairs", group_color: "area2", group_order: 2 };

const AREAS = [
  { id: 10, area_name: "Kitchen", group: GROUP_A },
  { id: 11, area_name: "Living room", group: GROUP_A },
  { id: 12, area_name: "Bathroom", group: GROUP_B },
];

vi.mock("@/composables/areasComposable", () => ({
  useAreas: () => ({ areas: ref(AREAS), isLoading: ref(false) }),
}));

vi.mock("@/composables/areaGroupsComposable", () => ({
  useAreaGroups: () => ({
    areagroups: ref([GROUP_A, GROUP_B]),
    isLoading: ref(false),
  }),
}));

vi.mock("@/composables/choresComposasble", () => ({
  useChoreNames: () => ({
    choreNames: ref([
      { chore_name: "Dust", chore_count: 4, area_count: 4 },
      { chore_name: "Vacuum", chore_count: 2, area_count: 2 },
    ]),
    isLoading: ref(false),
  }),
}));

vi.mock("@/composables/usersComposable", () => ({
  useUsers: () => ({
    users: ref([
      { id: 7, fullname: "Ada Lovelace", email: "ada@example.com" },
      { id: 8, fullname: "   ", email: "grace@example.com" },
    ]),
  }),
}));

import ChoreFilterBar from "@/components/ChoreFilterBar.vue";
import { useChoreStore } from "@/stores/chores";
import { useUserStore } from "@/stores/user";

const vuetify = createVuetify({ components, directives });

function mountBar(count = 3) {
  const wrapper = mount(ChoreFilterBar, {
    props: { count, loading: false },
    global: { plugins: [vuetify] },
  });
  return wrapper;
}

describe("ChoreFilterBar — quick filters", () => {
  let store;

  beforeEach(() => {
    setActivePinia(createPinia());
    store = useChoreStore();
    // The "Mine" chip only renders for a signed-in user.
    useUserStore().id = 7;
  });

  it("toggles overdue on and off", async () => {
    const wrapper = mountBar();
    expect(store.filters.overdue).toBe(false);

    wrapper.vm.toggleOverdue();
    expect(store.filters.overdue).toBe(true);

    wrapper.vm.toggleOverdue();
    expect(store.filters.overdue).toBe(false);
  });

  it("maps Mine onto the signed-in user's id", async () => {
    const wrapper = mountBar();
    wrapper.vm.toggleMine();
    expect(store.filters.assignee_id).toBe(7);

    wrapper.vm.toggleMine();
    expect(store.filters.assignee_id).toBeNull();
  });

  it("maps Due today onto timeframe 0, not null", async () => {
    // 0 is falsy, so anything treating "no timeframe" as !timeframe would drop
    // this filter entirely.
    const wrapper = mountBar();
    wrapper.vm.toggleDueToday();
    expect(store.filters.timeframe).toBe(0);
    expect(wrapper.vm.isDueToday).toBe(true);

    wrapper.vm.toggleDueToday();
    expect(store.filters.timeframe).toBeNull();
  });
});

describe("ChoreFilterBar — group narrows the area list", () => {
  let store;

  beforeEach(() => {
    setActivePinia(createPinia());
    store = useChoreStore();
    useUserStore().id = 7;
  });

  it("offers every area when no group is chosen", () => {
    const wrapper = mountBar();
    expect(wrapper.vm.areasInGroup.map(a => a.id)).toEqual([10, 11, 12]);
  });

  it("offers only that group's areas once one is chosen", async () => {
    const wrapper = mountBar();
    store.filters.group_id = GROUP_A.id;
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.areasInGroup.map(a => a.id)).toEqual([10, 11]);
  });

  it("clears the area when the group chip is removed", async () => {
    const wrapper = mountBar();
    store.filters.group_id = GROUP_A.id;
    store.filters.area_id = 10;
    await wrapper.vm.$nextTick();

    const groupChip = wrapper.vm.activeChips.find(c => c.key === "group");
    groupChip.clear();

    // Leaving area_id set would filter by an area the UI no longer offers.
    expect(store.filters.group_id).toBeNull();
    expect(store.filters.area_id).toBeNull();
  });
});

describe("ChoreFilterBar — active filters and counts", () => {
  let store;

  beforeEach(() => {
    setActivePinia(createPinia());
    store = useChoreStore();
    useUserStore().id = 7;
  });

  it("does not count sort as an active filter", async () => {
    const wrapper = mountBar();
    store.filters.sort = "dirtiest";
    await wrapper.vm.$nextTick();

    // Sorting is not filtering; counting it would leave Clear all permanently
    // enabled and show a filter chip for a view preference.
    expect(wrapper.vm.hasActiveFilters).toBe(false);
    expect(wrapper.vm.activeChips).toHaveLength(0);
  });

  it("badges only the filters hidden behind the button", async () => {
    const wrapper = mountBar();
    store.filters.overdue = true; // visible as a quick chip
    store.filters.area_id = 10; // hidden in the panel
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.advancedCount).toBe(1);
    expect(wrapper.vm.hasActiveFilters).toBe(true);
  });

  it("names each active filter in its chip", async () => {
    const wrapper = mountBar();
    store.filters.group_id = GROUP_B.id;
    store.filters.assignee_id = 7;
    store.filters.overdue = true;
    await wrapper.vm.$nextTick();

    const labels = wrapper.vm.activeChips.map(c => c.label);
    expect(labels).toContain("Overdue");
    expect(labels).toContain("Group: Upstairs");
    expect(labels).toContain("Assignee: you");
  });

  it("resets every filter but leaves the sort alone", async () => {
    const wrapper = mountBar();
    Object.assign(store.filters, {
      group_id: 1,
      area_id: 10,
      assignee_id: 7,
      timeframe: 3,
      overdue: true,
      inactive: true,
      chore_name: "Dust",
      sort: "dirtiest",
    });
    await wrapper.vm.$nextTick();

    wrapper.vm.resetFilters();

    expect(store.filters.group_id).toBeNull();
    expect(store.filters.area_id).toBeNull();
    expect(store.filters.assignee_id).toBeNull();
    expect(store.filters.timeframe).toBeNull();
    expect(store.filters.overdue).toBe(false);
    expect(store.filters.inactive).toBe(false);
    expect(store.filters.chore_name).toBeNull();
    // Silently reordering the list on "Clear all" would be a surprise.
    expect(store.filters.sort).toBe("dirtiest");
  });

  it("shows the task filter as its own chip and badges it", async () => {
    const wrapper = mountBar();
    store.filters.chore_name = "Dust";
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.activeChips.map(c => c.label)).toContain("Task: Dust");
    // It lives behind the Filters button, so it counts toward the badge.
    expect(wrapper.vm.advancedCount).toBe(1);
    expect(wrapper.vm.hasActiveFilters).toBe(true);
  });

  it("clears the task filter from its chip", async () => {
    const wrapper = mountBar();
    store.filters.chore_name = "Dust";
    await wrapper.vm.$nextTick();

    wrapper.vm.activeChips.find(c => c.key === "chore_name").clear();
    expect(store.filters.chore_name).toBeNull();
  });

  it("composes the task filter with the others", async () => {
    // "Dusting, upstairs only" has to be expressible.
    const wrapper = mountBar();
    store.filters.chore_name = "Dust";
    store.filters.group_id = GROUP_B.id;
    await wrapper.vm.$nextTick();

    const keys = wrapper.vm.activeChips.map(c => c.key);
    expect(keys).toEqual(expect.arrayContaining(["chore_name", "group"]));
    expect(wrapper.vm.advancedCount).toBe(2);
  });

  it("pluralises the result count", async () => {
    expect(mountBar(1).vm.countLabel).toBe("1 chore");
    expect(mountBar(4).vm.countLabel).toBe("4 chores");
    expect(mountBar(0).vm.countLabel).toBe("0 chores");
  });
});
