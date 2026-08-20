import { describe, it, expect } from "vitest";
import { greeting, choreSummary } from "@/utils/greeting";

const at = hour => new Date(2026, 7, 18, hour, 0, 0);

describe("greeting", () => {
  it("changes at noon and at six", () => {
    // Injected clock, so the boundaries are tested rather than whichever one
    // the suite happens to run inside.
    expect(greeting(at(0))).toBe("Good morning");
    expect(greeting(at(11))).toBe("Good morning");
    expect(greeting(at(12))).toBe("Good afternoon");
    expect(greeting(at(17))).toBe("Good afternoon");
    expect(greeting(at(18))).toBe("Good evening");
    expect(greeting(at(23))).toBe("Good evening");
  });
});

describe("choreSummary", () => {
  it("says nothing is waiting when nothing is", () => {
    expect(choreSummary(0, 0)).toBe("Nothing needs doing right now.");
  });

  it("singularises one chore", () => {
    expect(choreSummary(1, 0)).toBe("1 chore due.");
    expect(choreSummary(2, 0)).toBe("2 chores due.");
  });

  it("calls out overdue separately", () => {
    // Folding overdue into the due count is how it stops registering.
    expect(choreSummary(5, 2)).toBe("5 chores due, 2 overdue.");
    expect(choreSummary(1, 1)).toBe("1 chore due, 1 overdue.");
  });
});
