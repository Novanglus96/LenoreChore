import { describe, it, expect, vi, beforeEach } from "vitest";
import { ref } from "vue";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

// useOptions runs a TanStack query; the card only reads the dirtiness
// thresholds off it, so a plain ref keeps the test free of a QueryClient.
vi.mock("@/composables/optionsComposable", () => ({
  useOptions: () => ({
    options: ref({ med_thresh: 49, high_thresh: 74, vacation_mode: false }),
  }),
}));

import ChoreCard from "@/components/ChoreCard.vue";

const vuetify = createVuetify({ components, directives });

function makeChore(overrides = {}) {
  return {
    id: 1,
    chore_name: "Vacuum living room",
    status: 0,
    dirtiness: 20,
    duedays: 3,
    effort: 1,
    unit: "day(s)",
    intervalNumber: 7,
    active_months: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    nextDue: "2026-08-20",
    lastCompleted: "2026-08-13",
    assignee_id: null,
    assignee: null,
    isAssigned: false,
    isOverdue: false,
    history: false,
    last_three_history_items: [],
    area: {
      area_name: "Living Room",
      area_icon: "mdi-sofa",
      group: { group_color: "#3F51B5", group_name: "Downstairs" },
    },
    ...overrides,
  };
}

function mountCard(chore) {
  return mount(ChoreCard, {
    props: { chore },
    global: { plugins: [vuetify] },
  });
}

const nameField = wrapper =>
  wrapper.findAll("input").find(i => i.element.type === "text");

// Select by icon, never by index: v-rating renders three star buttons ahead of
// the action bar, so positional lookups silently hit the wrong control.
const button = (wrapper, icon) =>
  wrapper.findAll("button").find(b => b.html().includes(icon));

async function openEditPanel(wrapper) {
  await button(wrapper, "mdi-chevron-down").trigger("click");
  await wrapper.vm.$nextTick();
  await wrapper.vm.$nextTick();
}

describe("ChoreCard — remote updates vs unsaved edits", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("applies a remote update when there are no unsaved edits", async () => {
    const wrapper = mountCard(makeChore());

    await wrapper.setProps({
      chore: makeChore({ chore_name: "Vacuum lounge", dirtiness: 80 }),
    });

    expect(wrapper.text()).toContain("Vacuum lounge");
  });

  it("does not discard unsaved edits when a remote update arrives", async () => {
    // The regression this guards: another household member completing a chore
    // publishes an SSE event, which invalidates ["chores"] and hands this
    // component a new object. That used to replace the open edit panel's
    // contents mid-typing.
    const wrapper = mountCard(makeChore());

    await openEditPanel(wrapper);

    const field = nameField(wrapper);
    expect(field).toBeTruthy();
    await field.setValue("Vacuum living room THOROUGHLY");

    await wrapper.setProps({
      chore: makeChore({ chore_name: "Renamed by someone else" }),
    });

    expect(nameField(wrapper).element.value).toBe(
      "Vacuum living room THOROUGHLY"
    );
    expect(wrapper.text()).not.toContain("Renamed by someone else");
  });

  it("warns that the chore changed elsewhere while edits are held back", async () => {
    const wrapper = mountCard(makeChore());

    await openEditPanel(wrapper);
    await nameField(wrapper).setValue("My edit");

    expect(wrapper.text()).not.toContain("changed this chore");

    await wrapper.setProps({
      chore: makeChore({ chore_name: "Renamed by someone else" }),
    });

    expect(wrapper.text()).toContain("changed this chore");
  });

  it("reset discards local edits and loads the newer server copy", async () => {
    const wrapper = mountCard(makeChore());

    await openEditPanel(wrapper);
    await nameField(wrapper).setValue("My edit");

    await wrapper.setProps({
      chore: makeChore({ chore_name: "Renamed by someone else" }),
    });

    const resetButton = button(wrapper, "mdi-arrow-u-left-top-bold");
    expect(resetButton).toBeTruthy();
    await resetButton.trigger("click");
    await wrapper.vm.$nextTick();

    expect(nameField(wrapper).element.value).toBe("Renamed by someone else");
    expect(wrapper.text()).not.toContain("changed this chore");
  });

  it("emits editChore with the user's edits, not the reverted values", async () => {
    const wrapper = mountCard(makeChore());

    await openEditPanel(wrapper);
    await nameField(wrapper).setValue("My edit");

    await wrapper.setProps({
      chore: makeChore({ chore_name: "Renamed by someone else" }),
    });

    await button(wrapper, "mdi-content-save-outline").trigger("click");

    const emitted = wrapper.emitted("editChore");
    expect(emitted).toBeTruthy();
    expect(emitted[0][0].chore_name).toBe("My edit");
  });
});
