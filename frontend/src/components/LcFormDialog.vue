<template>
  <!-- The shared shell for every form dialog in the app.
       ─────────────────────────────────────────────────────────────────────
       The add-and-edit dialogs were each a copy of the Vuetify docs example:
       a v-container/v-row/v-col grid inside a width="1024" surface, so a
       desktop showed one 330px field in the corner of a 1024px dialog. Their
       buttons were color="blue-darken-1" -- stock Material Blue, not the
       palette -- with Cancel and Save both variant="text", so the escape hatch
       and the commit action carried identical weight.

       Worst of all on a phone: :fullscreen="smAndDown" with no toolbar and no
       sticky footer, so Save sat below twelve month checkboxes, off-screen,
       and there was no visible way out at all.

       This owns all of that once: the toolbar, the scrolling body, the pinned
       action bar, the width, the pending state, and the vee-validate <Form>
       itself -- so a consumer supplies fields and nothing else. -->
  <v-dialog
    v-model="model"
    :max-width="maxWidth"
    :fullscreen="display.smAndDown.value"
    scrim
    persistent
  >
    <template
      v-if="$slots.activator"
      v-slot:activator="{ props: activatorProps }"
    >
      <slot name="activator" :props="activatorProps"></slot>
    </template>

    <!-- persistent keeps a stray backdrop tap from binning a half-typed form,
         which matters more here than usual because the dialog is fullscreen on
         a phone. It also swallows Escape, and a modal a keyboard user cannot
         dismiss is not acceptable, so Escape is handled explicitly. -->
    <v-card
      ref="cardRef"
      class="lc-form-dialog"
      :rounded="display.smAndDown.value ? 0 : 'lg'"
      :elevation="display.smAndDown.value ? 0 : 8"
      role="dialog"
      aria-modal="true"
      :aria-label="title"
      @keydown.esc.stop="cancel"
    >
      <v-toolbar class="lc-form-dialog__bar" color="surface" density="comfortable">
        <v-btn
          icon="mdi-close"
          :aria-label="`Close ${title} without saving`"
          :disabled="busy"
          @click="cancel"
        >
          <v-icon icon="mdi-close"></v-icon>
        </v-btn>

        <v-toolbar-title class="text-subtitle-1 font-weight-medium">
          <v-icon
            v-if="icon"
            :icon="icon"
            size="20"
            class="mr-2"
            aria-hidden="true"
          ></v-icon>
          {{ title }}
        </v-toolbar-title>
      </v-toolbar>

      <v-divider></v-divider>

      <!-- The <Form> lives here rather than in each consumer so that the submit
           button in the action bar below is inside the form element it submits.
           Consumers get `errors` through the default slot.

           ⚠️ Consumers must bind their controls with `componentField`, NEVER
           with `field`. vee-validate's `field` is for NATIVE inputs: it sets a
           plain `value`, which on a Vuetify component is not a prop, so it
           falls through to the inner <input> as a DOM attribute. The browser
           then paints that text while the component's own modelValue stays
           undefined -- so it believes it is empty and leaves the label sitting
           unfloated on top of the value. `componentField` binds modelValue.

           Keyed on the open count so it is a fresh mount every time the dialog
           opens. v-dialog keeps its content alive once shown, and vee-validate
           treats a changed `initialValues` as a non-forced reseed that
           deliberately leaves dirty fields alone -- so without this, a dialog
           closed with Cancel came back still holding the draft the user had
           just abandoned, and a newer server copy never reached the field. -->
      <Form
        :key="formKey"
        class="lc-form-dialog__form"
        :validation-schema="schema"
        :initial-values="initialValues"
        v-slot="{ errors }"
        @submit="onSubmit"
      >
        <div class="lc-form-dialog__body">
          <slot :errors="errors"></slot>
        </div>

        <v-divider></v-divider>

        <!-- Pinned, so the commit action is reachable without scrolling past
             the whole form. -->
        <v-card-actions class="lc-form-dialog__actions">
          <v-btn variant="text" :disabled="busy" @click="cancel">
            {{ cancelLabel }}
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            type="submit"
            variant="flat"
            color="primary"
            :prepend-icon="submitIcon"
            :loading="busy"
          >
            {{ submitLabel }}
          </v-btn>
        </v-card-actions>
      </Form>
    </v-card>
  </v-dialog>
</template>

<script setup>
// defineProps/defineEmits/defineModel are compiler macros; importing them warns
// on every build.
import { ref, watch, nextTick } from "vue";
import { useDisplay } from "vuetify";
import { Form } from "vee-validate";

const display = useDisplay();

const model = defineModel({ type: Boolean, default: false });

defineProps({
  /** Dialog heading, and the accessible name of the dialog and its close button. */
  title: { type: String, required: true },
  /** Optional MDI id shown beside the title. */
  icon: { type: String, default: "" },
  /** Text on the confirming button. "Save" is rarely the most useful word. */
  submitLabel: { type: String, default: "Save" },
  submitIcon: { type: String, default: undefined },
  cancelLabel: { type: String, default: "Cancel" },
  /** yup schema handed to vee-validate. */
  schema: { type: Object, default: undefined },
  initialValues: { type: Object, default: undefined },
  /**
   * True while the mutation is in flight. The old forms had no such state:
   * submitForm fired the mutation and closed the dialog on the next line, so a
   * failed POST put an error snackbar over a dialog that had already vanished
   * and taken the user's input with it.
   */
  busy: { type: Boolean, default: false },
  /**
   * 560px rather than 1024: one column of fields does not need more, and the
   * old width left most of the surface empty.
   */
  maxWidth: { type: [Number, String], default: 560 },
});

const emit = defineEmits(["submit", "cancel"]);

const cardRef = ref(null);
const formKey = ref(0);

const cancel = () => {
  emit("cancel");
  model.value = false;
};

const onSubmit = values => {
  // Deliberately does NOT close. The consumer closes once its mutation has
  // actually resolved, which is the whole point of the busy prop.
  emit("submit", values);
};

watch(model, async open => {
  if (!open) return;
  formKey.value++;
  // Only on a pointer-sized screen. Focusing a text field on a phone summons
  // the keyboard over a dialog the user has not read yet.
  if (display.smAndDown.value) return;
  await nextTick();
  const root = cardRef.value?.$el;
  const first = root?.querySelector(
    "input:not([type='hidden']):not([disabled]), textarea:not([disabled])"
  );
  first?.focus();
});
</script>

<style scoped>
/* The card is a flex column so the body scrolls between a fixed toolbar and a
   fixed action bar. v-dialog's own `scrollable` cannot do this here: it expects
   v-card-text and v-card-actions as DIRECT children of v-card, and the <Form>
   element sits between them. */
.lc-form-dialog {
  display: flex;
  flex-direction: column;
  max-height: 100%;
  background: rgb(var(--v-theme-surface));
}

.lc-form-dialog__bar {
  flex: 0 0 auto;
}

.lc-form-dialog__form {
  display: flex;
  flex-direction: column;
  /* min-height:0 is what actually lets the body shrink and scroll; without it a
     flex child refuses to go below its content height and the action bar gets
     pushed off the bottom of the viewport -- the original bug, reproduced. */
  min-height: 0;
  flex: 1 1 auto;
}

.lc-form-dialog__body {
  overflow-y: auto;
  min-height: 0;
  flex: 1 1 auto;
  padding: var(--lc-space-5) var(--lc-space-5) var(--lc-space-4);
}

.lc-form-dialog__actions {
  flex: 0 0 auto;
  padding: var(--lc-space-3) var(--lc-space-4);
}

@media (max-width: 599px) {
  .lc-form-dialog__body {
    padding: var(--lc-space-4);
  }
}
</style>
