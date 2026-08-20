<template>
  <!-- The overflow menu, shared by every card that has more actions than it
       has room for.
       ─────────────────────────────────────────────────────────────────────
       Cards used to carry every action as its own icon button in the action
       bar -- six of them on a chore card. On a phone that is six unlabelled
       glyphs eating 264px of a 360px screen, because a v-tooltip needs hover
       and a touch device has none. The names those buttons carried existed
       only for screen readers; a sighted touch user had to tap and find out.

       So: the common action stays on the card as a labelled button, and
       everything else moves in here, where each item has a name in words.

       A v-menu anchored to a button near the bottom of a long scrolling list
       opens wherever it can fit, which on a phone is often over the thing you
       were looking at. Below the `sm` breakpoint this is a bottom sheet
       instead -- anchored to the bottom of the screen, in reach of a thumb,
       always in the same place. Same items, same events, same markup. -->
  <component :is="surface" v-model="open" v-bind="surfaceProps">
    <template v-slot:activator="{ props: activatorProps }">
      <slot name="activator" :props="activatorProps"></slot>
    </template>

    <v-list :density="mobile ? 'default' : 'compact'" :lines="false">
      <!-- The sheet covers the card that opened it, so on a phone it has to
           say what it is acting on. A menu sits next to its card and does
           not. -->
      <template v-if="mobile && title">
        <v-list-subheader class="text-truncate">{{ title }}</v-list-subheader>
        <v-divider></v-divider>
      </template>

      <template v-for="item in items" :key="item.key">
        <v-divider v-if="item.dividerBefore" class="my-1"></v-divider>
        <v-list-item
          :prepend-icon="item.icon"
          :base-color="item.color"
          :disabled="item.disabled"
          @click="select(item)"
        >
          <v-list-item-title>{{ item.title }}</v-list-item-title>
          <v-list-item-subtitle v-if="item.subtitle">
            {{ item.subtitle }}
          </v-list-item-subtitle>
        </v-list-item>
      </template>
    </v-list>
  </component>
</template>

<script setup>
// defineProps/defineEmits are compiler macros.
import { computed, ref } from "vue";
import { useDisplay } from "vuetify";

// smAndDown, not `display.mobile`: Vuetify's mobileBreakpoint defaults to `lg`,
// so `mobile` is true right up to 1280px and a 1200px laptop would get a bottom
// sheet. This is the same threshold LcFormDialog goes fullscreen at and the one
// BottomNav appears at, so a screen either behaves like a phone throughout or
// does not.
const { smAndDown } = useDisplay();
const mobile = smAndDown;

defineProps({
  /**
   * `[{ key, title, icon, subtitle?, color?, disabled?, dividerBefore? }]`
   *
   * `key` is what comes back on `select`, so a consumer switches on a name it
   * chose rather than on an array index that shifts when an item is added.
   */
  items: { type: Array, default: () => [] },
  /** What the menu acts on. Shown as a subheader on the bottom sheet only. */
  title: { type: String, default: "" },
});

const emit = defineEmits(["select"]);

const open = ref(false);

// Resolved by name rather than by importing the components, because the app
// registers all of Vuetify globally and importing them here would pull a
// second copy into this chunk.
const surface = computed(() => (mobile.value ? "v-bottom-sheet" : "v-menu"));

const surfaceProps = computed(() =>
  mobile.value
    ? { contentClass: "lc-action-sheet" }
    : // Anchored under the button rather than over it, so the control you
      // just pressed stays visible.
      { location: "bottom end", offset: 4 }
);

const select = item => {
  if (item.disabled) return;
  open.value = false;
  emit("select", item.key);
};
</script>

<style>
/* Deliberately NOT scoped, and reached by a content-class rather than by a
   descendant selector: an overlay's content is teleported to
   .v-overlay-container, outside this component's tree, so a scoped
   `:deep(...)` rule compiles to `[data-v-x] .y` and matches nothing.

   A bottom sheet is a temporary surface, so it gets the sheet treatment: top
   corners rounded, and the safe-area inset honoured or on an installed PWA the
   last item sits under the home indicator. */
.lc-action-sheet .v-list {
  border-start-start-radius: var(--lc-radius-lg);
  border-start-end-radius: var(--lc-radius-lg);
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
</style>
