import { describe, it, expect, vi, beforeEach } from "vitest";
import { ref } from "vue";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

// The behaviour under test is what the form does with the mutation's RESULT, so
// addArea is the seam. It is redefined per test.
let addArea = vi.fn();

vi.mock("@/composables/areasComposable", () => ({
  useAreas: () => ({
    areas: ref([]),
    isLoading: ref(false),
    addArea: (...args) => addArea(...args),
  }),
}));

vi.mock("@/composables/areaGroupsComposable", () => ({
  useAreaGroups: () => ({
    areagroups: ref([{ id: 1, group_name: "Downstairs" }]),
    isLoading: ref(false),
  }),
}));

import AddAreaForm from "@/components/AddAreaForm.vue";

const vuetify = createVuetify({ components, directives });

/** Mount, open the dialog, and type a name into the one required field. */
async function openAndFill(wrapper, name = "Pantry") {
  wrapper.vm.dialog = true;
  await new Promise(r => setTimeout(r, 0));
  await wrapper.vm.$nextTick();

  const input = document.querySelector(".lc-form-dialog input");
  expect(input, "the dialog should render its fields").toBeTruthy();
  input.value = name;
  input.dispatchEvent(new Event("input", { bubbles: true }));
  input.dispatchEvent(new Event("change", { bubbles: true }));
  await wrapper.vm.$nextTick();
  return input;
}

/** Submit the dialog's form and let vee-validate's async validation settle. */
async function submit(wrapper) {
  const form = document.querySelector("form.lc-form-dialog__form");
  expect(form, "the shell should render a form element").toBeTruthy();
  form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
  for (let i = 0; i < 6; i++) {
    await new Promise(r => setTimeout(r, 0));
    await wrapper.vm.$nextTick();
  }
}

describe("AddAreaForm — a failed save must not discard what was typed", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    document.body.innerHTML = "";
  });

  it("keeps the dialog open when the mutation rejects", async () => {
    // handleApiError rethrows on every branch, so a failed request surfaces
    // here as a rejection.
    addArea = vi.fn().mockRejectedValue(new Error("500"));

    const wrapper = mount(AddAreaForm, { global: { plugins: [vuetify] } });
    await openAndFill(wrapper, "Pantry");
    await submit(wrapper);

    expect(addArea).toHaveBeenCalledTimes(1);
    expect(addArea.mock.calls[0][0]).toMatchObject({ area_name: "Pantry" });

    // The regression this guards: submitForm used to close the dialog on the
    // line after firing the mutation, so the error snackbar landed on a dialog
    // that had already gone, taking the user's input with it.
    expect(wrapper.vm.dialog).toBe(true);
    expect(document.querySelector(".lc-form-dialog input").value).toBe("Pantry");

    // And the button is usable again rather than stuck spinning.
    expect(wrapper.vm.busy).toBe(false);
  });

  it("closes and resets only once the mutation resolves", async () => {
    addArea = vi.fn().mockResolvedValue({ id: 7 });

    const wrapper = mount(AddAreaForm, { global: { plugins: [vuetify] } });
    await openAndFill(wrapper, "Pantry");
    await submit(wrapper);

    expect(addArea).toHaveBeenCalledTimes(1);
    expect(wrapper.vm.dialog).toBe(false);
    expect(wrapper.vm.busy).toBe(false);
    // Reset, so the next open does not inherit the last area's icon/group.
    expect(wrapper.vm.formData).toMatchObject({
      area_icon: "mdi-home",
      group_id: 1,
    });
  });

  it("does not call the mutation at all when the name is empty", async () => {
    addArea = vi.fn().mockResolvedValue({ id: 7 });

    const wrapper = mount(AddAreaForm, { global: { plugins: [vuetify] } });
    await openAndFill(wrapper, "");
    await submit(wrapper);

    expect(addArea).not.toHaveBeenCalled();
    expect(wrapper.vm.dialog).toBe(true);
  });
});
