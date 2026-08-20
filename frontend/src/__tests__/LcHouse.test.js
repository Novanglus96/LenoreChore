import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

import LcHouse from "@/components/LcHouse.vue";

const vuetify = createVuetify({ components, directives });

const GROUPS = [
  { id: 1, name: "Downstairs", color: "area1", dirtiness: 10 },
  { id: 2, name: "Upstairs", color: "area2", dirtiness: 80 },
];

function mountHouse(props = {}) {
  return mount(LcHouse, {
    props: { dirtiness: 0, groups: GROUPS, ...props },
    global: { plugins: [vuetify] },
  });
}

describe("LcHouse", () => {
  it("is hidden from assistive tech", () => {
    // The greeting beneath already states the same thing in words. The house is
    // the redundant copy, never the only signal.
    const wrapper = mountHouse();
    expect(wrapper.find("svg").attributes("aria-hidden")).toBe("true");
    expect(wrapper.text()).toBe("");
  });

  it("draws one window per group, tinted with that group's colour", () => {
    const wrapper = mountHouse();
    const html = wrapper.html();
    expect(html).toContain("rgb(var(--v-theme-area1))");
    expect(html).toContain("rgb(var(--v-theme-area2))");
  });

  it("falls back to outline for a group with no colour", () => {
    // The "No group" bucket is synthetic and carries outline, but a real group
    // could also arrive mid-migration with nothing set.
    const wrapper = mountHouse({
      groups: [{ id: null, name: "No group", color: "", dirtiness: 0 }],
    });
    expect(wrapper.html()).toContain("rgb(var(--v-theme-outline))");
  });

  it("caps the windows so they cannot overrun the wall", () => {
    const many = Array.from({ length: 10 }, (_, i) => ({
      id: i,
      name: `G${i}`,
      color: "area1",
      dirtiness: 0,
    }));
    const wrapper = mountHouse({ groups: many });
    // Six windows, each drawn from four <rect> plus the frame's own rect.
    const soot = wrapper.findAll('rect[fill="#3B2E1B"]');
    expect(soot).toHaveLength(6);
  });

  it("grimes each window on its own group's reading", () => {
    const wrapper = mountHouse({ groups: GROUPS });
    const soot = wrapper.findAll('rect[fill="#3B2E1B"]');
    expect(soot).toHaveLength(2);

    const dirty = Number(soot[1].attributes("opacity"));
    const clean = Number(soot[0].attributes("opacity"));
    // Upstairs is at 80, Downstairs at 10 — a house where every window read the
    // same would throw away the only structure that makes this mapping work.
    expect(dirty).toBeGreaterThan(clean);
  });

  it("stays clean at zero and grimes up as the household slides", () => {
    const spotless = mountHouse({ dirtiness: 0 });
    const filthy = mountHouse({ dirtiness: 100 });

    // The wall layer is the first to arrive, at 10%.
    const wallOf = w =>
      Number(
        w
          .findAll("g[clip-path]")
          .find(g => g.html().includes("#4A3A22"))
          .attributes("opacity")
      );

    expect(wallOf(spotless)).toBe(0);
    expect(wallOf(filthy)).toBe(1);
  });

  it("brings the grime layers in on staggered curves", () => {
    // Fading them together would read as one opacity slider, which is exactly
    // what it must not look like. At 30% the walls have started and the yard
    // (which waits until 45%) has not.
    const wrapper = mountHouse({ dirtiness: 30 });
    const layers = wrapper.findAll("g[opacity]");
    const opacities = layers.map(l => Number(l.attributes("opacity")));

    expect(opacities.some(o => o > 0 && o < 1)).toBe(true);
    expect(opacities.some(o => o === 0)).toBe(true);
  });

  it("gives its filter ids a per-instance namespace", () => {
    // SVG filter and clipPath ids are document-global, so two houses on one
    // page would have the second silently reference the first's defs.
    //
    // Both have to be mounted in ONE app: useId counts per app instance, so
    // two separate mount() calls each start again at v-0 and would pass this
    // no matter what the component did.
    const wrapper = mount(
      {
        components: { LcHouse },
        template: '<div><LcHouse :groups="g"/><LcHouse :groups="g"/></div>',
        data: () => ({ g: GROUPS }),
      },
      { global: { plugins: [vuetify] } }
    );

    const ids = wrapper.findAll("filter").map(f => f.attributes("id"));
    expect(ids.length).toBeGreaterThan(1);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it("renders nothing for a household with no groups yet", () => {
    const wrapper = mountHouse({ groups: [] });
    expect(wrapper.findAll('rect[fill="#3B2E1B"]')).toHaveLength(0);
    // The house itself still stands — an empty household is not a broken one.
    expect(wrapper.find("polygon").exists()).toBe(true);
  });
});
