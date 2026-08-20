<template>
  <!-- The dirtiness bar, once.
       ─────────────────────────────────────────────────────────────────────
       ChoreCard, AreaCard and AreaGroupSection each carried their own copy of
       this markup and their own identical `dirtBand` computed. The dashboard's
       house needs the same reading, and a house that disagrees with the bar
       underneath it is worse than no house at all.

       The texture is the new part. Vuetify's `striped` was switched on for any
       dirt above zero and rendered identically at 5% and at 95%, so it said
       "there is some dirt" and nothing more. This grime tightens its pitch and
       deepens as the band rises, making it a second reading of severity
       alongside the colour and the word -- one that survives being unable to
       tell the hues apart. -->
  <v-progress-linear
    class="lc-dirt"
    :model-value="value"
    :color="band.color"
    :height="height"
    :style="{ '--lc-dirt-grime': grimeImage }"
    rounded
    :aria-label="ariaLabel"
  >
    <span v-if="showLabel" class="text-caption font-weight-medium">
      {{ Math.ceil(value) }}% · {{ band.label }}
    </span>
  </v-progress-linear>
</template>

<script setup>
// defineProps is a compiler macro.
import { computed } from "vue";
import { useOptions } from "@/composables/optionsComposable";
import {
  dirtBand,
  DEFAULT_MED_THRESH,
  DEFAULT_HIGH_THRESH,
} from "@/utils/dirt";

const { options } = useOptions();

const props = defineProps({
  /** 0..100. */
  value: { type: Number, default: 0 },
  height: { type: [Number, String], default: 22 },
  showLabel: { type: Boolean, default: true },
  /**
   * Prefixed to the spoken label, for bars that belong to something named --
   * a collapsed group says which group it is reporting on.
   */
  label: { type: String, default: "" },
});

const band = computed(() =>
  dirtBand(
    props.value,
    options.value?.med_thresh ?? DEFAULT_MED_THRESH,
    options.value?.high_thresh ?? DEFAULT_HIGH_THRESH,
  ),
);

const ariaLabel = computed(() => {
  const reading = `${Math.ceil(props.value)} percent dirty, ${band.value.label}`;
  return props.label ? `${props.label}: ${reading}` : reading;
});

/**
 * Pitch tightens from 14px to 5px and the ink deepens from 12% to 42% across
 * the range, so the fill reads visibly differently at 20% and at 80%.
 *
 * Handed down as a custom property rather than rendered as an element: the
 * default slot's content is a full-width overlay in Vuetify's markup, so a
 * span in there would hatch the empty track too. The determinate element is
 * the one that is actually the width of the reading.
 */
const grimeImage = computed(() => {
  if (!props.value) return "none";
  const t = Math.min(1, Math.max(0, props.value / 100));
  const pitch = 14 - 9 * t;
  const ink = 0.12 + 0.3 * t;
  const half = (pitch / 2).toFixed(1);
  return (
    `repeating-linear-gradient(115deg,` +
    `rgba(0,0,0,${ink.toFixed(2)}) 0 ${half}px,` +
    `transparent ${half}px ${pitch.toFixed(1)}px)`
  );
});
</script>

<style scoped>
.lc-dirt :deep(.v-progress-linear__determinate) {
  background-image: var(--lc-dirt-grime);
  transition:
    width var(--lc-dur-base) var(--lc-ease-standard),
    background-image var(--lc-dur-base) var(--lc-ease-standard);
}
</style>
