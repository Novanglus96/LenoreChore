import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { VTextField } from "vuetify/components";

// The reminders section subscribes to push and reads prefs on mount. None of
// that is what this file is about, and a real usePush would reach for
// navigator.serviceWorker.
vi.mock("@/composables/pushComposable", () => ({
  usePush: () => ({
    isSupported: () => false,
    subscribe: vi.fn(),
    unsubscribe: vi.fn(),
    getPrefs: vi.fn().mockResolvedValue({ notify_enabled: false }),
    savePrefs: vi.fn(),
  }),
}));

import ProfileView from "@/views/ProfileView.vue";
import { useUserStore } from "@/stores/user";

const vuetify = createVuetify({ components, directives });

const mounted = [];

function mountView() {
  const wrapper = mount(ProfileView, {
    global: { plugins: [vuetify] },
    attachTo: document.body,
  });
  mounted.push(wrapper);
  return wrapper;
}

function teardown() {
  while (mounted.length) mounted.pop().unmount();
  document.body.innerHTML = "";
}

const overlay = () => document.querySelector(".v-overlay-container");
const overlayText = () => overlay()?.textContent ?? "";

const tick = async () => {
  await new Promise(resolve => setTimeout(resolve, 0));
  await new Promise(resolve => setTimeout(resolve, 0));
};

const until = check => vi.waitFor(check, { timeout: 2000, interval: 10 });

const seedUser = (overrides = {}) => {
  const store = useUserStore();
  Object.assign(
    store,
    {
      firstname: "John",
      lastname: "Adams",
      email: "john@example.com",
      user_color: "#3F51B5",
      male: true,
      isChild: false,
      isAdmin: false,
    },
    overrides
  );
  return store;
};

describe("ProfileView — a summary, not a form", () => {
  beforeEach(() => setActivePinia(createPinia()));
  afterEach(teardown);

  it("shows who you are without opening an editor", () => {
    seedUser();
    const wrapper = mountView();

    expect(wrapper.text()).toContain("John Adams");
    expect(wrapper.text()).toContain("john@example.com");
    // The colour identifies you across the app but was only ever visible as a
    // selected chip inside the form.
    expect(wrapper.text()).toContain("Indigo");
  });

  it("falls back to the email rather than showing the store's placeholders", () => {
    // Both defaults have to be stripped -- dropping only the first leaves a
    // profile headed "LastName".
    seedUser({ firstname: "FirstName", lastname: "LastName" });
    const wrapper = mountView();

    expect(wrapper.text()).not.toContain("FirstName");
    expect(wrapper.text()).not.toContain("LastName");
    expect(wrapper.text()).toContain("john@example.com");
  });

  it("does not put a Save button on the page itself", () => {
    // The bug this screen had: one "Save changes" governing about a third of
    // what was on it, with the reminders writing immediately and the password
    // in its own dialog.
    seedUser();
    const wrapper = mountView();

    expect(wrapper.text()).not.toContain("Save changes");
    expect(wrapper.text()).toContain("Edit profile");
    expect(wrapper.text()).toContain("Saved as soon as you change them");
  });

  it("edits in the shared dialog, seeded from the store", async () => {
    seedUser();
    const wrapper = mountView();

    const edit = wrapper
      .findAll("button")
      .find(b => b.text().includes("Edit profile"));
    await edit.trigger("click");
    await tick();

    await until(() => expect(overlayText()).toContain("Edit profile"));

    const field = label =>
      wrapper.findAllComponents(VTextField).find(f => f.props("label") === label);

    expect(field("First name").props("modelValue")).toBe("John");
    expect(field("Last name").props("modelValue")).toBe("Adams");
  });

  it("opens the password dialog from the settings list", async () => {
    seedUser();
    const wrapper = mountView();

    const row = wrapper
      .findAll(".v-list-item")
      .find(el => el.text().includes("Change password"));
    expect(row).toBeTruthy();

    await row.trigger("click");
    await until(() => expect(overlayText()).toContain("Current password"));
  });

  it("says so when the device cannot do reminders", () => {
    seedUser();
    const wrapper = mountView();
    expect(wrapper.text()).toContain("Not supported on this device");
  });
});
