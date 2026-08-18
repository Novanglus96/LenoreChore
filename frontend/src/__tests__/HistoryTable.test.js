import { describe, it, expect, vi } from "vitest";
import { ref } from "vue";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

const items = [
  {
    id: 1,
    completed_date: "2026-08-01",
    chore: { chore_name: "Vacuum living room" },
    completed_by: { fullname: "Ada Lovelace", email: "ada@example.com" },
  },
  {
    id: 2,
    completed_date: "2026-08-02",
    chore: { chore_name: "Take out bins" },
    // fullname absent -> should fall back to the email
    completed_by: { fullname: "   ", email: "grace@example.com" },
  },
  {
    id: 3,
    completed_date: "2026-08-03",
    chore: { chore_name: "Mop kitchen" },
    // The regression: completed_by is Optional on HistoryItemOut and goes null
    // when the completer is deleted. This row used to throw and take the whole
    // table down with it.
    completed_by: null,
  },
];

vi.mock("@/composables/historyItemsComposable", () => ({
  useHistoryItems: () => ({
    historyItems: ref({ items, total_records: items.length }),
    isLoading: ref(false),
  }),
}));

import HistoryTable from "@/components/HistoryTable.vue";

const vuetify = createVuetify({ components, directives });

describe("HistoryTable — completed_by can be null", () => {
  it("renders every row, including one whose completer was deleted", () => {
    setActivePinia(createPinia());
    const wrapper = mount(HistoryTable, { global: { plugins: [vuetify] } });
    const text = wrapper.text();

    expect(text).toContain("Vacuum living room");
    expect(text).toContain("Take out bins");
    // The row that used to throw:
    expect(text).toContain("Mop kitchen");
    expect(text).toContain("Deleted member");
  });

  it("shows the full name, falling back to the email when it is blank", () => {
    setActivePinia(createPinia());
    const wrapper = mount(HistoryTable, { global: { plugins: [vuetify] } });
    const text = wrapper.text();

    expect(text).toContain("Ada Lovelace");
    expect(text).toContain("grace@example.com");
  });
});
