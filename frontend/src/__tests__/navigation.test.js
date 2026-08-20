import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import { DESTINATIONS, activeDestination } from "@/utils/navigation";

describe("activeDestination", () => {
  it("matches the dashboard only on an exact /", () => {
    // The trap: every path starts with "/", so a prefix test would report the
    // dashboard as the active destination on every screen in the app.
    expect(activeDestination("/")).toBe("/");
    expect(activeDestination("/list")).toBe("/list");
    expect(activeDestination("/graphs")).toBe("/graphs");
    expect(activeDestination("/history")).toBe("/history");
  });

  it("matches nested paths to their section", () => {
    expect(activeDestination("/list/42")).toBe("/list");
    expect(activeDestination("/history?page=2".split("?")[0])).toBe("/history");
  });

  it("returns nothing for a path outside the four destinations", () => {
    // Profile, About and Logout are reachable from the account menu, and
    // highlighting a bottom-nav tab on them would be a lie.
    expect(activeDestination("/profile")).toBeUndefined();
    expect(activeDestination("/about")).toBeUndefined();
    expect(activeDestination("/login")).toBeUndefined();
  });
});

// ── BottomNav ─────────────────────────────────────────────────────────────
let currentPath = "/";

vi.mock("vue-router", () => ({
  useRoute: () => ({
    get path() {
      return currentPath;
    },
  }),
}));

import BottomNav from "@/components/BottomNav.vue";
import { useUserStore } from "@/stores/user";

const vuetify = createVuetify({ components, directives });

/**
 * happy-dom defaults to a desktop width, and its innerWidth is not a plain
 * writable property, so it is redefined rather than assigned. Vuetify's display
 * reads it when the plugin installs into each mounted app.
 */
function setViewport(width) {
  Object.defineProperty(window, "innerWidth", {
    value: width,
    writable: true,
    configurable: true,
  });
  window.dispatchEvent(new Event("resize"));
}

/**
 * VBottomNavigation registers itself with Vuetify's layout and throws
 * "Could not find injected layout" without one -- it is a sibling of v-main
 * inside v-app in the real app, which is exactly what reserves space for it.
 * The harness reproduces that rather than working around it.
 *
 * No pinia plugin: passing createPinia() here would give the component a
 * DIFFERENT store instance from the one the test writes to, so every store
 * assignment would silently have no effect. The active pinia is used instead.
 */
const Harness = {
  components: { BottomNav },
  template: "<v-layout><BottomNav /></v-layout>",
};

function mountNav() {
  const wrapper = mount(Harness, { global: { plugins: [vuetify] } });
  return wrapper.findComponent(BottomNav);
}

describe("BottomNav — when it appears", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    currentPath = "/";
  });

  it("shows the four destinations on a phone", async () => {
    setViewport(390);
    useUserStore().isLoggedIn = true;
    const wrapper = mountNav();
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.visible).toBe(true);
    const text = wrapper.text();
    for (const destination of DESTINATIONS) {
      expect(text).toContain(destination.title);
    }
  });

  it("stays out of the way on a desktop", async () => {
    // A bar pinned to the bottom of a 1440px window is a long way from where
    // the eye already is; the overflow menu keeps that job.
    setViewport(1440);
    useUserStore().isLoggedIn = true;
    const wrapper = mountNav();
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.visible).toBe(false);
    expect(wrapper.text()).toBe("");
  });

  it("does not render for a signed-out visitor", async () => {
    setViewport(390);
    useUserStore().isLoggedIn = false;
    const wrapper = mountNav();
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.visible).toBe(false);
  });
});

describe("BottomNav — the active tab follows the route", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    setViewport(390);
  });

  it("tracks the current path rather than the last tap", async () => {
    // Derived from the route, so a back gesture or a deep link moves the
    // highlight too -- local state would only follow taps on the bar.
    currentPath = "/graphs";
    useUserStore().isLoggedIn = true;
    const wrapper = mountNav();
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.active).toBe("/graphs");
  });

  it("highlights nothing on a screen outside the four", async () => {
    currentPath = "/profile";
    useUserStore().isLoggedIn = true;
    const wrapper = mountNav();
    await wrapper.vm.$nextTick();

    expect(wrapper.vm.active).toBeUndefined();
  });
});
