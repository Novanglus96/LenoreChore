import { describe, it, expect, vi, beforeEach } from "vitest";
import { ref } from "vue";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

const GROUP = { id: 1, group_name: "Downstairs", group_color: "area1", group_order: 1 };

let choresData = ref([]);

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
    complete: vi.fn(),
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
    const wrapper = mount(ListView, { global: { plugins: [vuetify] } });
    expect(wrapper.text()).toContain("Nothing needs doing");
    expect(wrapper.text()).not.toContain("Nothing matches those filters");
  });

  it("says nothing matches once a filter is on", async () => {
    const wrapper = mount(ListView, { global: { plugins: [vuetify] } });
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
    const wrapper = mount(ListView, { global: { plugins: [vuetify] } });
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
