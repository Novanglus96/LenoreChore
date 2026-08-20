import { describe, it, expect } from "vitest";
import { dirtBand, weightedDirtiness } from "@/utils/dirt";

describe("dirtBand", () => {
  it("names the band as well as colouring it", () => {
    // Colour alone fails for anyone who cannot tell the hues apart, so every
    // band carries a word too.
    expect(dirtBand(0)).toEqual({ color: "clean", label: "clean-ish" });
    expect(dirtBand(60)).toEqual({ color: "soiled", label: "getting there" });
    expect(dirtBand(90)).toEqual({ color: "filthy", label: "filthy" });
  });

  it("treats the thresholds as inclusive upper bounds", () => {
    expect(dirtBand(49).color).toBe("clean");
    expect(dirtBand(50).color).toBe("soiled");
    expect(dirtBand(74).color).toBe("soiled");
    expect(dirtBand(75).color).toBe("filthy");
  });

  it("honours a household's own thresholds", () => {
    // They are user-configurable, which is exactly why the word matters: it is
    // the only thing explaining why 30% is "filthy" in this house.
    expect(dirtBand(30, 10, 20).label).toBe("filthy");
    expect(dirtBand(30, 40, 80).label).toBe("clean-ish");
  });

  it("reads a missing value as clean rather than throwing", () => {
    expect(dirtBand(undefined).color).toBe("clean");
    expect(dirtBand(null).color).toBe("clean");
  });
});

describe("weightedDirtiness", () => {
  it("weights by chore count, not by area", () => {
    // The regression this guards: a mean of means lets a one-chore area
    // outvote a twenty-chore one. Here 20 chores are spotless and 1 is filthy,
    // so the household is nearly clean — averaging the percentages would call
    // it 50.
    const areas = [
      { total_dirtiness: 0, totalCount: 20 },
      { total_dirtiness: 100, totalCount: 1 },
    ];
    expect(weightedDirtiness(areas)).toBe(5);
  });

  it("matches what one area holding all the chores would report", () => {
    const split = [
      { total_dirtiness: 120, totalCount: 3 },
      { total_dirtiness: 80, totalCount: 2 },
    ];
    const merged = [{ total_dirtiness: 200, totalCount: 5 }];
    expect(weightedDirtiness(split)).toBe(weightedDirtiness(merged));
  });

  it("is zero for an empty or chore-less household", () => {
    expect(weightedDirtiness([])).toBe(0);
    expect(weightedDirtiness(undefined)).toBe(0);
    expect(weightedDirtiness([{ total_dirtiness: 0, totalCount: 0 }])).toBe(0);
  });

  it("never exceeds 100", () => {
    // dirtiness is clamped per chore server-side, but a stale cache could still
    // hand us a sum that overshoots, and a bar wider than its track looks like
    // a rendering bug rather than a dirty house.
    expect(weightedDirtiness([{ total_dirtiness: 500, totalCount: 2 }])).toBe(100);
  });
});
