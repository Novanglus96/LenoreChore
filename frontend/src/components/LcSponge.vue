<template>
  <!-- The last one.
       ─────────────────────────────────────────────────────────────────────
       Clearing the final chore is the emotional peak of a chore app, and it
       was marked by mdi-party-popper -- a glyph from a set of six thousand,
       carrying no more of this app's world than the printer icon does.

       A sponge and its bubbles instead, drawn in the theme's own colours so it
       re-lights in dark mode. It keeps the entrance it already had: ListView
       puts .lc-cleared on the empty state, and tokens.css springs the media
       slot on the same curve as the completion beat. -->
  <svg
    :width="size"
    :height="Math.round(size * 0.73)"
    viewBox="0 0 130 96"
    aria-hidden="true"
    focusable="false"
  >
    <ellipse cx="65" cy="86" rx="40" ry="5" fill="currentColor" opacity=".07" />

    <!-- The sponge: accent body, a paler scouring face. -->
    <rect
      x="30"
      y="44"
      width="70"
      height="34"
      rx="10"
      fill="rgb(var(--v-theme-accent))"
    />
    <rect
      x="30"
      y="44"
      width="70"
      height="15"
      rx="8"
      fill="rgb(var(--v-theme-surface-variant))"
    />
    <g fill="rgb(var(--v-theme-outline))">
      <circle cx="46" cy="53" r="2.6" opacity=".45" />
      <circle cx="58" cy="50" r="2" opacity=".4" />
      <circle cx="72" cy="53" r="2.4" opacity=".45" />
      <circle cx="84" cy="50" r="1.8" opacity=".4" />
    </g>

    <g fill="none" stroke="rgb(var(--v-theme-primary))" stroke-width="2">
      <circle cx="34" cy="24" r="9" />
      <circle cx="62" cy="14" r="6" />
      <circle cx="90" cy="26" r="11" />
      <circle cx="108" cy="12" r="5" />
    </g>

    <path
      d="M18 34 l2.6 6.4 L27 43 l-6.4 2.6 L18 52 l-2.6-6.4 L9 43 l6.4-2.6 Z"
      fill="rgb(var(--v-theme-clean))"
    />
  </svg>
</template>

<script setup>
// defineProps is a compiler macro.
defineProps({
  size: { type: Number, default: 120 },
});
</script>
