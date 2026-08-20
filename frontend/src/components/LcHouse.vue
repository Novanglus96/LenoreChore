<template>
  <!-- The house.
       ─────────────────────────────────────────────────────────────────────
       A banner above the greeting that grimes up as the household does. It is
       ornament, but it is ornament that READS: the app's personality has lived
       in how things move rather than in illustration (see tokens.css), and the
       rule this extends that doctrine with is that decoration must respond to
       state. A house that just sat there would be wallpaper.

       Drawn rather than photographed, and inline rather than fetched, for four
       reasons that all matter here: every fill is a theme token so it re-lights
       in dark mode instead of inverting; it is markup, so it adds nothing to
       the PWA's precache; it is a few KB against the 175KB of one avatar JPEG;
       and the windows have to be tinted with colours the user picked, which a
       raster could never do.

       aria-hidden throughout. The greeting directly beneath already states the
       same thing in words, so this is always the redundant copy and never the
       only signal. -->
  <div class="lc-house" :class="{ 'lc-house--still': reducedMotion }">
    <svg
      class="lc-house__stage"
      viewBox="0 0 800 300"
      preserveAspectRatio="xMidYMid slice"
      aria-hidden="true"
      focusable="false"
    >
      <defs>
        <linearGradient :id="id('sky')" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" :stop-color="skyTop" class="lc-house__sky-stop" />
          <stop offset="100%" stop-color="rgb(var(--v-theme-background))" />
        </linearGradient>

        <!-- Why the splotches do not read as ellipses. Hand-drawing organic
             blobs as path data would be both longer and worse. -->
        <filter :id="id('rough')" x="-25%" y="-25%" width="150%" height="150%">
          <feTurbulence
            type="fractalNoise"
            baseFrequency="0.045"
            numOctaves="3"
            seed="7"
            result="noise"
          />
          <feDisplacementMap
            in="SourceGraphic"
            in2="noise"
            scale="16"
            xChannelSelector="R"
            yChannelSelector="G"
          />
        </filter>

        <filter :id="id('soft')" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="7" />
        </filter>

        <linearGradient :id="id('streak')" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#3B2E1B" stop-opacity=".55" />
          <stop offset="100%" stop-color="#3B2E1B" stop-opacity="0" />
        </linearGradient>

        <clipPath :id="id('wall')">
          <rect x="286" y="132" width="228" height="96" rx="2" />
        </clipPath>
        <clipPath :id="id('roof')">
          <polygon points="262,136 400,52 538,136" />
        </clipPath>
      </defs>

      <rect x="0" y="0" width="800" height="300" :fill="`url(#${id('sky')})`" />
      <rect
        x="0"
        y="228"
        width="800"
        height="72"
        fill="var(--lc-house-earth)"
      />

      <!-- The sun hazes over as things slide. -->
      <circle
        cx="662"
        cy="66"
        r="26"
        fill="var(--lc-house-glow)"
        :opacity="sunOpacity"
      />
      <circle
        cx="662"
        cy="66"
        r="40"
        fill="var(--lc-house-glow)"
        :opacity="hazeOpacity"
        :filter="`url(#${id('soft')})`"
      />

      <g :opacity="plantingOpacity">
        <rect
          x="146"
          y="196"
          width="12"
          height="34"
          rx="3"
          fill="var(--lc-house-roof)"
        />
        <circle
          cx="152"
          cy="180"
          r="34"
          fill="rgb(var(--v-theme-clean))"
          opacity=".85"
        />
        <circle
          cx="128"
          cy="192"
          r="22"
          fill="rgb(var(--v-theme-clean))"
          opacity=".7"
        />
        <circle
          cx="176"
          cy="192"
          r="20"
          fill="rgb(var(--v-theme-clean))"
          opacity=".65"
        />
        <circle
          cx="640"
          cy="214"
          r="20"
          fill="rgb(var(--v-theme-clean))"
          opacity=".75"
        />
        <circle
          cx="664"
          cy="220"
          r="14"
          fill="rgb(var(--v-theme-clean))"
          opacity=".6"
        />
      </g>

      <g>
        <rect
          x="286"
          y="132"
          width="228"
          height="96"
          rx="2"
          fill="var(--lc-house-wall)"
        />
        <rect
          x="286"
          y="132"
          width="228"
          height="96"
          rx="2"
          fill="none"
          stroke="rgb(var(--v-theme-outline-variant))"
          stroke-width="1.5"
        />
        <polygon points="262,136 400,52 538,136" fill="var(--lc-house-roof)" />
        <rect
          x="474"
          y="70"
          width="24"
          height="42"
          rx="2"
          fill="var(--lc-house-roof)"
        />

        <!-- A household being kept up is a lived-in one. -->
        <g :opacity="smokeOpacity">
          <circle
            cx="486"
            cy="58"
            r="6"
            fill="rgb(var(--v-theme-outline))"
            opacity=".5"
          />
          <circle
            cx="492"
            cy="42"
            r="8"
            fill="rgb(var(--v-theme-outline))"
            opacity=".35"
          />
          <circle
            cx="484"
            cy="26"
            r="10"
            fill="rgb(var(--v-theme-outline))"
            opacity=".2"
          />
        </g>

        <rect
          x="378"
          y="180"
          width="44"
          height="48"
          rx="3"
          fill="var(--lc-house-wall-shade)"
          stroke="rgb(var(--v-theme-outline-variant))"
          stroke-width="1.5"
        />
        <circle cx="413" cy="205" r="2.6" fill="rgb(var(--v-theme-outline))" />

        <!-- One window per area GROUP, not per area.
             Areas are user-created and their icon list includes a car, a tree
             and a picnic table -- there is no cutaway house those fit into.
             Groups are few, ordered and already coloured, and each already
             knows its own chore-weighted dirtiness. -->
        <g v-for="win in windows" :key="win.key">
          <rect
            :x="win.x"
            y="148"
            :width="WINDOW_W"
            :height="WINDOW_H"
            rx="3"
            :fill="win.fill"
          />
          <rect
            :x="win.x"
            y="148"
            :width="WINDOW_W"
            :height="WINDOW_H"
            rx="3"
            fill="var(--lc-house-glow)"
            :opacity="win.lit"
          />
          <g stroke="var(--lc-house-roof)" stroke-width="2.5" fill="none">
            <line
              :x1="win.x + WINDOW_W / 2"
              y1="148"
              :x2="win.x + WINDOW_W / 2"
              :y2="148 + WINDOW_H"
            />
            <line
              :x1="win.x"
              :y1="148 + WINDOW_H / 2"
              :x2="win.x + WINDOW_W"
              :y2="148 + WINDOW_H / 2"
            />
            <rect
              :x="win.x"
              y="148"
              :width="WINDOW_W"
              :height="WINDOW_H"
              rx="3"
            />
          </g>
          <rect
            :x="win.x"
            y="148"
            :width="WINDOW_W"
            :height="WINDOW_H"
            rx="3"
            fill="#3B2E1B"
            :opacity="win.soot"
          />
        </g>

        <!-- The grime layers come in on staggered curves. Fading them together
             would read as one opacity slider, which is exactly what it must
             not look like. -->
        <g :clip-path="`url(#${id('wall')})`" :opacity="wallGrime">
          <g :filter="`url(#${id('rough')})`">
            <ellipse
              cx="322"
              cy="216"
              rx="46"
              ry="20"
              fill="#4A3A22"
              opacity=".5"
            />
            <ellipse
              cx="470"
              cy="222"
              rx="52"
              ry="18"
              fill="#4A3A22"
              opacity=".45"
            />
            <ellipse
              cx="398"
              cy="226"
              rx="70"
              ry="14"
              fill="#4A3A22"
              opacity=".4"
            />
            <ellipse
              cx="300"
              cy="150"
              rx="22"
              ry="14"
              fill="#4A3A22"
              opacity=".3"
            />
          </g>
          <rect
            x="300"
            y="132"
            width="7"
            height="96"
            :fill="`url(#${id('streak')})`"
          />
          <rect
            x="352"
            y="132"
            width="5"
            height="70"
            :fill="`url(#${id('streak')})`"
          />
          <rect
            x="446"
            y="132"
            width="6"
            height="84"
            :fill="`url(#${id('streak')})`"
          />
          <rect
            x="498"
            y="132"
            width="8"
            height="60"
            :fill="`url(#${id('streak')})`"
          />
        </g>

        <g :clip-path="`url(#${id('roof')})`" :opacity="roofGrime">
          <g :filter="`url(#${id('rough')})`">
            <ellipse
              cx="340"
              cy="120"
              rx="60"
              ry="20"
              fill="#2A2116"
              opacity=".55"
            />
            <ellipse
              cx="452"
              cy="112"
              rx="54"
              ry="18"
              fill="#2A2116"
              opacity=".5"
            />
            <ellipse
              cx="400"
              cy="76"
              rx="40"
              ry="16"
              fill="#2A2116"
              opacity=".4"
            />
          </g>
        </g>
      </g>

      <g :opacity="yardGrime" :filter="`url(#${id('rough')})`">
        <ellipse
          cx="230"
          cy="252"
          rx="60"
          ry="12"
          fill="#4A3A22"
          opacity=".35"
        />
        <ellipse
          cx="576"
          cy="262"
          rx="72"
          ry="13"
          fill="#4A3A22"
          opacity=".3"
        />
      </g>

      <!-- Bubbles when clean, dust when filthy. Both are decoration on top of
           a reading that is already complete without them. -->
      <g :opacity="bubbleOpacity">
        <circle
          v-for="b in BUBBLES"
          :key="`b${b.i}`"
          class="lc-house__bubble"
          :cx="b.cx"
          :cy="b.cy"
          :r="b.r"
          fill="none"
          stroke="rgb(var(--v-theme-primary))"
          stroke-width="1.4"
          :style="{
            animationDuration: `${b.dur}s`,
            animationDelay: `${b.delay}s`,
          }"
        />
      </g>

      <g :opacity="moteOpacity">
        <circle
          v-for="m in MOTES"
          :key="`m${m.i}`"
          class="lc-house__mote"
          :cx="m.cx"
          :cy="m.cy"
          :r="m.r"
          fill="#6B5836"
          :style="{
            animationDuration: `${m.dur}s`,
            animationDelay: `${m.delay}s`,
          }"
        />
      </g>
    </svg>
  </div>
</template>

<script setup>
// defineProps is a compiler macro.
import { computed, useId } from "vue";

const WINDOW_W = 40;
const WINDOW_H = 34;
const WINDOW_GAP = 16;
/** Past this the windows stop fitting between the door frame and the corners. */
const MAX_WINDOWS = 6;

const props = defineProps({
  /** The household's chore-weighted dirtiness, 0..100. */
  dirtiness: { type: Number, default: 0 },
  /**
   * `[{ id, name, color, dirtiness }]` -- one window each, in dashboard order.
   * `color` is a Vuetify theme colour name (area1..area6), which is what the
   * group actually stores.
   */
  groups: { type: Array, default: () => [] },
});

// Namespaced per instance. SVG filter and clip ids are document-global, so two
// houses on one page would have the second silently referencing the first's
// defs -- and useId is stable across SSR and hydration.
const uid = useId();
const id = name => `lc-house-${name}-${uid}`;

const clamp = (v, min = 0, max = 1) => Math.min(max, Math.max(min, v));

/** 0..1. */
const t = computed(() => clamp((props.dirtiness ?? 0) / 100));

const skyTop = computed(() =>
  t.value > 0.5 ? "var(--lc-house-sky-filthy)" : "var(--lc-house-sky-clean)",
);

const sunOpacity = computed(() => (0.9 - 0.55 * t.value).toFixed(2));
const hazeOpacity = computed(() => (0.3 * t.value).toFixed(2));
const smokeOpacity = computed(() => (1 - t.value).toFixed(2));
const plantingOpacity = computed(() => (1 - 0.35 * t.value).toFixed(2));

const wallGrime = computed(() => clamp((t.value - 0.1) / 0.75).toFixed(2));
const roofGrime = computed(() => clamp((t.value - 0.25) / 0.7).toFixed(2));
const yardGrime = computed(() => clamp((t.value - 0.45) / 0.55).toFixed(2));

const bubbleOpacity = computed(() => clamp(1 - t.value * 1.9).toFixed(2));
const moteOpacity = computed(() => clamp((t.value - 0.35) / 0.6).toFixed(2));

const windows = computed(() => {
  const groups = (props.groups ?? []).slice(0, MAX_WINDOWS);
  if (!groups.length) return [];

  const span = groups.length * WINDOW_W + (groups.length - 1) * WINDOW_GAP;
  const startX = 400 - span / 2;

  return groups.map((group, index) => {
    const gt = clamp((group.dirtiness ?? 0) / 100);
    return {
      key: group.id ?? `ungrouped-${index}`,
      x: startX + index * (WINDOW_W + WINDOW_GAP),
      // The group's own colour, so the house is tinted by the household's own
      // choices rather than by a palette invented here.
      fill: `rgb(var(--v-theme-${group.color || "outline"}))`,
      lit: (0.85 * (1 - gt)).toFixed(2),
      soot: (0.62 * gt).toFixed(2),
    };
  });
});

/**
 * Fixed rather than random.
 *
 * Math.random() here would reposition every bubble on each re-render -- and
 * this component re-renders whenever any chore anywhere changes, because the
 * dashboard's numbers move. Scattered-looking but deterministic.
 */
const scatter = (count, seed) =>
  Array.from({ length: count }, (_, i) => {
    const n = Math.sin(seed + i * 12.9898) * 43758.5453;
    const a = n - Math.floor(n);
    const m = Math.sin(seed + i * 78.233) * 12345.6789;
    const b = m - Math.floor(m);
    return { i, a, b };
  });

const BUBBLES = scatter(14, 1).map(({ i, a, b }) => ({
  i,
  cx: Math.round(40 + a * 720),
  cy: Math.round(40 + b * 200),
  r: (3 + a * 6).toFixed(1),
  dur: (7 + b * 7).toFixed(1),
  delay: -(a * 10).toFixed(1),
}));

const MOTES = scatter(26, 2).map(({ i, a, b }) => ({
  i,
  cx: Math.round(20 + a * 760),
  cy: Math.round(30 + b * 220),
  r: (1 + b * 1.6).toFixed(1),
  dur: (9 + a * 9).toFixed(1),
  delay: -(b * 12).toFixed(1),
}));

// Checked once rather than watched: this only decides whether the ambient
// drift runs at all, and someone changing the OS setting mid-session will get
// the new answer on the next navigation. The media query in the stylesheet
// handles the rest.
const reducedMotion =
  typeof window !== "undefined" &&
  typeof window.matchMedia === "function" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;
</script>

<style scoped>
.lc-house {
  /* The artwork's own palette, tied to the theme rather than to literals, so
     the whole thing re-lights in dark mode instead of inverting into mud. */
  --lc-house-sky-clean: #dcf1fa;
  --lc-house-sky-filthy: #cfc4ae;
  --lc-house-wall: rgb(var(--v-theme-surface));
  --lc-house-wall-shade: rgb(var(--v-theme-surface-variant));
  --lc-house-roof: rgb(var(--v-theme-secondary));
  --lc-house-earth: rgb(var(--v-theme-surface-variant));
  --lc-house-glow: #ffd79a;

  border-radius: var(--lc-radius-lg);
  overflow: hidden;
  background: rgb(var(--v-theme-surface));
}

:global(.v-theme--myCustomDarkTheme) .lc-house {
  --lc-house-sky-clean: #123039;
  --lc-house-sky-filthy: #2e2a21;
  --lc-house-glow: #ffce7b;
}

.lc-house__stage {
  display: block;
  width: 100%;
  /* Short and wide: a banner, not a picture. Shorter still on a phone, where
     vertical space is the scarce thing and the greeting below it matters
     more than the artwork does. */
  height: 168px;
}

@media (max-width: 599px) {
  .lc-house {
    border-radius: 0;
  }

  .lc-house__stage {
    height: 112px;
  }
}

/* Everything below the sky transitions, so a completion visibly cleans the
   house rather than cutting to a new state. */
.lc-house__stage :is(g, circle, rect) {
  transition: opacity var(--lc-dur-slow) var(--lc-ease-standard);
}

.lc-house__sky-stop {
  transition: stop-color var(--lc-dur-slow) var(--lc-ease-standard);
}

@keyframes lc-house-drift {
  0%,
  100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(6px, -18px);
  }
}

@keyframes lc-house-swirl {
  0% {
    transform: translate(0, 0);
  }
  100% {
    transform: translate(26px, 14px);
  }
}

.lc-house__bubble {
  animation: lc-house-drift 10s ease-in-out infinite;
}

.lc-house__mote {
  animation: lc-house-swirl 14s linear infinite;
}

/* Ambient drift is exactly what this query exists to prevent, so it stops
   outright rather than running faster. The house still reads: every other
   signal in it is opacity, which conveys state without implied movement. */
@media (prefers-reduced-motion: reduce) {
  .lc-house__bubble,
  .lc-house__mote {
    animation: none;
  }
}

.lc-house--still .lc-house__bubble,
.lc-house--still .lc-house__mote {
  animation: none;
}
</style>
