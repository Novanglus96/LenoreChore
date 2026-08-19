import { describe, it, expect, vi, beforeEach } from "vitest";
import { ref } from "vue";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

const area = (id, name, group, extra = {}) => ({
  id,
  area_name: name,
  area_icon: "mdi-home",
  group,
  group_id: group?.id ?? null,
  dirtiness: 0,
  dueCount: 0,
  totalCount: 0,
  total_dirtiness: 0,
  ...extra,
});

const GROUP_A = { id: 1, group_name: "Downstairs", group_color: "area1", group_order: 2 };
const GROUP_B = { id: 2, group_name: "Upstairs", group_color: "area2", group_order: 1 };

let areasData = ref([]);
let groupsData = ref([]);
const editAreaGroup = vi.fn().mockResolvedValue({});

vi.mock("@/composables/areasComposable", () => ({
  useAreas: () => ({
    areas: areasData,
    isLoading: ref(false),
    editArea: vi.fn(),
    removeArea: vi.fn(),
  }),
}));

vi.mock("@/composables/areaGroupsComposable", () => ({
  useAreaGroups: () => ({
    areagroups: groupsData,
    isLoading: ref(false),
    addAreaGroup: vi.fn(),
    editAreaGroup: (...a) => editAreaGroup(...a),
    removeAreaGroup: vi.fn().mockResolvedValue({}),
  }),
}));

// AreaCard calls useRouter() for its "See chores" button. No router is
// installed here, so stub it rather than let every mount warn.
vi.mock("vue-router", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

vi.mock("@/composables/optionsComposable", () => ({
  useOptions: () => ({
    options: ref({ med_thresh: 49, high_thresh: 74, vacation_mode: false }),
  }),
}));

import DashView from "@/views/DashView.vue";

const vuetify = createVuetify({ components, directives });

const mountDash = () =>
  mount(DashView, { global: { plugins: [vuetify, createPinia()] } });

describe("DashView — areas are grouped, not flattened", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    editAreaGroup.mockClear();
    areasData = ref([]);
    groupsData = ref([]);
  });

  it("renders one section per group, in group_order", () => {
    groupsData.value = [GROUP_A, GROUP_B];
    areasData.value = [
      area(10, "Kitchen", GROUP_A),
      area(11, "Bathroom", GROUP_B),
    ];

    const text = mountDash().text();
    // GROUP_B has the lower group_order, so it comes first despite being
    // second in the array.
    expect(text.indexOf("Upstairs")).toBeLessThan(text.indexOf("Downstairs"));
    expect(text).toContain("Kitchen");
    expect(text).toContain("Bathroom");
  });

  it("keeps an empty group visible", () => {
    groupsData.value = [GROUP_A, GROUP_B];
    areasData.value = [area(10, "Kitchen", GROUP_A)];

    // A group that renders as nothing looks broken rather than empty.
    const text = mountDash().text();
    expect(text).toContain("Upstairs");
    expect(text).toContain("No areas in this group yet");
  });

  it("shows an area whose group is null rather than dropping it", async () => {
    // AreaOut.group is Optional now, matching the nullable column.
    groupsData.value = [GROUP_A];
    areasData.value = [
      area(10, "Kitchen", GROUP_A),
      area(12, "Orphan room", null),
    ];

    const wrapper = mountDash();
    // The bucket is present and named, but folded by default -- so the area is
    // reachable rather than on screen. Opening it is what reveals the area.
    expect(wrapper.text()).toContain("No group");

    const ungrouped = wrapper
      .findAllComponents({ name: "AreaGroupSection" })
      .find(c => c.props("group").id === null);
    ungrouped.vm.dashboard.toggleGroup(null);
    await wrapper.vm.$nextTick();

    expect(wrapper.text()).toContain("Orphan room");
  });

  it("totals due and total counts per group", () => {
    groupsData.value = [GROUP_B];
    areasData.value = [
      area(10, "Bathroom", GROUP_B, { dueCount: 2, totalCount: 5 }),
      area(11, "Landing", GROUP_B, { dueCount: 1, totalCount: 3 }),
    ];

    expect(mountDash().text()).toContain("3 / 8 due");
  });

  it("weights group dirtiness by chore count, not by area", () => {
    groupsData.value = [GROUP_B];
    areasData.value = [
      // 1 chore at 100%
      area(10, "Big", GROUP_B, { totalCount: 1, total_dirtiness: 100 }),
      // 9 chores at 0%
      area(11, "Small", GROUP_B, { totalCount: 9, total_dirtiness: 0 }),
    ];

    const wrapper = mountDash();
    const section = wrapper.findComponent({ name: "AreaGroupSection" });
    // A mean of the two areas' percentages would be 50. Chore-weighted is 10.
    expect(section.vm.dirtiness).toBe(10);
  });
});

describe("DashView — reordering repairs the legacy all-ties state", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    editAreaGroup.mockClear();
    areasData = ref([]);
    groupsData = ref([]);
  });

  it("renumbers when every group shares group_order", async () => {
    // The state every existing install is in: AddAreaGroupForm hardcoded
    // group_order: 1 on every group it ever created. A swap of two 1s is a
    // no-op, which is why this renumbers instead.
    const tied = [
      { id: 1, group_name: "Alpha", group_color: "area1", group_order: 1 },
      { id: 2, group_name: "Beta", group_color: "area2", group_order: 1 },
      { id: 3, group_name: "Gamma", group_color: "area3", group_order: 1 },
    ];
    groupsData.value = tied;

    const wrapper = mountDash();
    // Move Gamma (last) up one place -> Alpha, Gamma, Beta.
    await wrapper.vm.moveGroup(tied[2], -1);

    const written = editAreaGroup.mock.calls.map(c => [c[0].id, c[0].group_order]);
    // Alpha already wants 1 and holds 1, so it is not rewritten.
    expect(written).toEqual([
      [3, 2],
      [2, 3],
    ]);
  });

  it("does nothing at the ends of the list", async () => {
    groupsData.value = [
      { id: 1, group_name: "Alpha", group_color: "area1", group_order: 1 },
      { id: 2, group_name: "Beta", group_color: "area2", group_order: 2 },
    ];

    const wrapper = mountDash();
    await wrapper.vm.moveGroup(groupsData.value[0], -1);
    await wrapper.vm.moveGroup(groupsData.value[1], 1);

    expect(editAreaGroup).not.toHaveBeenCalled();
  });
});

describe("DashView — the greeting", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    areasData = ref([]);
    groupsData = ref([]);
  });

  it("sums due and overdue across every area", () => {
    groupsData.value = [GROUP_A, GROUP_B];
    areasData.value = [
      area(10, "Kitchen", GROUP_A, { dueCount: 2, overdueCount: 1 }),
      area(11, "Bathroom", GROUP_B, { dueCount: 3, overdueCount: 2 }),
    ];

    const wrapper = mountDash();
    expect(wrapper.vm.dueCount).toBe(5);
    expect(wrapper.vm.overdueCount).toBe(3);
    expect(wrapper.text()).toContain("5 chores due, 3 overdue.");
  });

  it("does not greet the user by the store's placeholder name", () => {
    // useUserStore's default firstname is the literal "FirstName"; greeting a
    // real person by a placeholder is worse than not greeting them.
    groupsData.value = [GROUP_A];
    areasData.value = [area(10, "Kitchen", GROUP_A)];

    const wrapper = mountDash();
    expect(wrapper.vm.firstName).toBe("");
    expect(wrapper.text()).not.toContain("FirstName");
  });

  it("says nothing is waiting when nothing is", () => {
    groupsData.value = [GROUP_A];
    areasData.value = [area(10, "Kitchen", GROUP_A)];

    expect(mountDash().text()).toContain("Nothing needs doing right now.");
  });
});

describe("DashView — the No group bucket", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    areasData = ref([]);
    groupsData = ref([]);
  });

  const withOrphan = () => {
    groupsData.value = [GROUP_A, GROUP_B];
    areasData.value = [
      area(10, "Kitchen", GROUP_A),
      area(12, "Orphan room", null),
      area(11, "Bathroom", GROUP_B),
    ];
  };

  it("sorts to the bottom, after every real group", () => {
    withOrphan();
    const wrapper = mountDash();

    const order = wrapper
      .findAllComponents({ name: "AreaGroupSection" })
      .map(c => c.props("group").group_name);
    expect(order[order.length - 1]).toBe("No group");
  });

  it("starts collapsed, while real groups start open", () => {
    // A leftovers bin rather than a group anyone made, so it stays out of the
    // way until it is wanted.
    withOrphan();
    const wrapper = mountDash();

    const sections = wrapper.findAllComponents({ name: "AreaGroupSection" });
    const ungrouped = sections.find(c => c.props("group").id === null);
    const real = sections.find(c => c.props("group").id !== null);

    expect(ungrouped.vm.expanded).toBe(false);
    expect(real.vm.expanded).toBe(true);
    // Its area is not on screen until it is opened.
    expect(wrapper.text()).not.toContain("Orphan room");
  });

  it("opens on demand and stays open", async () => {
    withOrphan();
    const wrapper = mountDash();
    const ungrouped = wrapper
      .findAllComponents({ name: "AreaGroupSection" })
      .find(c => c.props("group").id === null);

    ungrouped.vm.dashboard.toggleGroup(null);
    await wrapper.vm.$nextTick();

    expect(ungrouped.vm.expanded).toBe(true);
    expect(wrapper.text()).toContain("Orphan room");
  });

  it("offers no management menu, having no row to manage", () => {
    // Rename would open a form for nothing, move is a no-op, and delete would
    // have sent DELETE /areagroups/null.
    withOrphan();
    const wrapper = mountDash();
    const sections = wrapper.findAllComponents({ name: "AreaGroupSection" });

    expect(
      sections.find(c => c.props("group").id === null).vm.isRealGroup
    ).toBe(false);
    expect(
      sections.find(c => c.props("group").id !== null).vm.isRealGroup
    ).toBe(true);
  });
});
