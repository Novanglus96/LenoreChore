import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
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
    last_three_history_items: [],
    area: {
      area_name: "Living Room",
      area_icon: "mdi-sofa",
      group: { group_color: "#3F51B5", group_name: "Downstairs" },
    },
    ...overrides,
  };
}

const mounted = [];

// attachTo matters now. The editor is a dialog, and Vuetify teleports overlay
// content into a .v-overlay-container hung off the document -- so it is NOT a
// descendant of the wrapper, and neither wrapper.find nor wrapper.text() can
// see any of it. Everything inside the editor is queried through the document.
function mountCard(chore) {
  const wrapper = mount(ChoreCard, {
    props: { chore },
    global: { plugins: [vuetify] },
    attachTo: document.body,
  });
  mounted.push(wrapper);
  return wrapper;
}

/**
 * Unmount everything and clear the document between tests.
 *
 * Both halves are load-bearing. A wrapper left mounted keeps its Vuetify app
 * alive, and each app owns its own .v-overlay-container -- so after a few
 * tests there are several in the document and `document.querySelector` starts
 * answering with a previous test's dialog. Wiping innerHTML alone does not
 * help: it detaches the container while leaving the app that owns it running.
 */
function teardown() {
  while (mounted.length) mounted.pop().unmount();
  document.body.innerHTML = "";
}

// Select by icon, never by index: v-rating renders three star buttons ahead of
// the action bar, so positional lookups silently hit the wrong control.
const button = (wrapper, icon) =>
  wrapper.findAll("button").find(b => b.html().includes(icon));

const overlay = () => document.querySelector(".v-overlay-container");

/** The chore-name input, which lives in the teleported edit dialog. */
const nameField = () =>
  [...(overlay()?.querySelectorAll("input") ?? [])].find(
    i => i.type === "text"
  );

const overlayText = () => overlay()?.textContent ?? "";

/** A button in the teleported dialog, found by the icon it renders. */
const overlayButton = icon =>
  [...(overlay()?.querySelectorAll("button") ?? [])].find(b =>
    b.innerHTML.includes(icon)
  );

const setValue = async (input, value) => {
  input.value = value;
  input.dispatchEvent(new Event("input"));
  await tick();
};

const tick = async () => {
  // Two frames: one for the state change, one for the overlay to render or
  // tear down the teleported content it owns.
  await new Promise(resolve => setTimeout(resolve, 0));
  await new Promise(resolve => setTimeout(resolve, 0));
};

/**
 * Poll until a condition holds.
 *
 * A fixed number of ticks is not enough for anything that goes through a
 * submit: vee-validate validates asynchronously, so the emit lands a variable
 * number of microtasks after the click and a `await tick()` passed most of the
 * time and failed roughly one run in ten.
 */
const until = check => vi.waitFor(check, { timeout: 2000, interval: 10 });

/**
 * Open the editor the way a user does: the overflow menu, then "Edit chore".
 *
 * Deliberately not a shortcut that flips the dialog's model directly -- the
 * menu IS the new affordance, and a test that skipped it would keep passing if
 * the item were ever dropped from the list.
 */
async function openEditor(wrapper) {
  await button(wrapper, "mdi-dots-vertical").trigger("click");

  const editItem = await until(() => {
    const item = [...overlay().querySelectorAll(".v-list-item")].find(el =>
      el.textContent.includes("Edit chore")
    );
    expect(item).toBeTruthy();
    return item;
  });

  editItem.click();
  await until(() => expect(nameField()).toBeTruthy());
}

describe("ChoreCard — remote updates vs unsaved edits", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  afterEach(teardown);

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
    // component a new object. That used to replace the open editor's contents
    // mid-typing.
    const wrapper = mountCard(makeChore());

    await openEditor(wrapper);

    const field = nameField();
    expect(field).toBeTruthy();
    await setValue(field, "Vacuum living room THOROUGHLY");

    await wrapper.setProps({
      chore: makeChore({ chore_name: "Renamed by someone else" }),
    });
    await tick();

    expect(nameField().value).toBe("Vacuum living room THOROUGHLY");
    expect(wrapper.text()).not.toContain("Renamed by someone else");
  });

  it("warns that the chore changed elsewhere while edits are held back", async () => {
    const wrapper = mountCard(makeChore());

    await openEditor(wrapper);
    await setValue(nameField(), "My edit");

    expect(overlayText()).not.toContain("changed this chore");

    await wrapper.setProps({
      chore: makeChore({ chore_name: "Renamed by someone else" }),
    });

    await until(() => expect(overlayText()).toContain("changed this chore"));
  });

  it("cancel discards local edits and loads the newer server copy", async () => {
    // Cancel is what Reset used to be. The old panel needed a separate button
    // for it because closing the panel was disabled the moment anything
    // changed; a dialog's way out does the job.
    const wrapper = mountCard(makeChore());

    await openEditor(wrapper);
    await setValue(nameField(), "My edit");

    await wrapper.setProps({
      chore: makeChore({ chore_name: "Renamed by someone else" }),
    });
    await tick();

    const closeButton = overlayButton("mdi-close");
    expect(closeButton).toBeTruthy();
    closeButton.click();

    await until(() => expect(wrapper.text()).toContain("Renamed by someone else"));

    // Reopening shows the server's copy, not the abandoned draft.
    await openEditor(wrapper);
    expect(nameField().value).toBe("Renamed by someone else");
    expect(overlayText()).not.toContain("changed this chore");
  });

  it("emits editChore with the user's edits, not the reverted values", async () => {
    const wrapper = mountCard(makeChore());

    await openEditor(wrapper);
    await setValue(nameField(), "My edit");

    await wrapper.setProps({
      chore: makeChore({ chore_name: "Renamed by someone else" }),
    });
    await tick();

    overlayButton("mdi-content-save-outline").click();

    await until(() => expect(wrapper.emitted("editChore")).toBeTruthy());
    expect(wrapper.emitted("editChore")[0][0].chore_name).toBe("My edit");
  });
});

describe("ChoreCard — the action bar", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  afterEach(teardown);

  it("names its actions in words, not in tooltips", async () => {
    // The bar was six icon buttons whose only labels were tooltips, which a
    // touch device never shows.
    const wrapper = mountCard(makeChore());

    expect(wrapper.text()).toContain("Done");
    expect(wrapper.text()).toContain("Snooze");
  });

  it("offers the rest of the actions by name in the overflow menu", async () => {
    const wrapper = mountCard(makeChore());

    await button(wrapper, "mdi-dots-vertical").trigger("click");

    await until(() => expect(overlayText()).toContain("Edit chore"));

    const text = overlayText();
    expect(text).toContain("Recent history");
    expect(text).toContain("Disable chore");
    expect(text).toContain("Delete chore");
  });

  it("says when the chore was last done rather than hiding it in a panel", () => {
    const wrapper = mountCard(
      makeChore({
        last_three_history_items: [
          { completed_date: "2026-08-13", completed_by: "John" },
        ],
      })
    );

    expect(wrapper.text()).toContain("Last done");
    expect(wrapper.text()).toContain("John");
  });

  it("says so when a chore has never been completed", () => {
    const wrapper = mountCard(makeChore());
    expect(wrapper.text()).toContain("Never completed");
  });

  it("claims the chore from the assignee button", async () => {
    const wrapper = mountCard(makeChore());

    const claim = wrapper
      .findAll("button")
      .find(b => b.text().includes("Unassigned"));
    expect(claim).toBeTruthy();

    await claim.trigger("click");
    expect(wrapper.emitted("claimChore")).toBeTruthy();
  });
});
