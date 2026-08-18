/**
 * Human-readable names for values that are stored as identifiers.
 *
 * These exist because several pickers offered options whose only
 * differentiator was a coloured square or an icon glyph — identical and
 * nameless to a screen reader, and barely more use to a sighted one.
 *
 * ⚠️ The linter cannot catch this class of problem. eslint-plugin-vuejs-
 * accessibility matches native elements, and its `anchor-has-content` rule is
 * mapped onto VBtn only — v-chip carries no such rule, so a chip containing a
 * bare icon reports clean. A zero-warning lint is not evidence these are fine.
 */

/**
 * Derive a readable name from an MDI icon id.
 *
 * Derived rather than kept as a parallel lookup table, so the labels cannot
 * fall out of step with the icon list they describe when someone adds an icon.
 *
 * @param {string} icon e.g. "mdi-tumble-dryer"
 * @returns {string} e.g. "Tumble dryer"
 */
export function iconLabel(icon) {
  return String(icon)
    .replace(/^mdi-/, "")
    .replace(/-/g, " ")
    .replace(/^./, c => c.toUpperCase());
}

/**
 * Selectable colours for an area group.
 *
 * ⚠️ The VALUES are persisted: AreaGroup.group_color stores the literal string
 * "area1".."area6" and Vuetify resolves it as a theme colour at render time.
 * Renaming a value silently breaks every existing group. Only the labels are
 * free to change, and these match the hues those theme keys now carry.
 */
export const AREA_GROUP_COLORS = [
  { name: "Blue", value: "area1" },
  { name: "Cyan", value: "area2" },
  { name: "Green", value: "area3" },
  { name: "Purple", value: "area4" },
  { name: "Pink", value: "area5" },
  { name: "Amber", value: "area6" },
];

/** The twelve months, for the "active months" pickers. */
export const MONTHS = [
  { value: 1, label: "Jan" },
  { value: 2, label: "Feb" },
  { value: 3, label: "Mar" },
  { value: 4, label: "Apr" },
  { value: 5, label: "May" },
  { value: 6, label: "Jun" },
  { value: 7, label: "Jul" },
  { value: 8, label: "Aug" },
  { value: 9, label: "Sep" },
  { value: 10, label: "Oct" },
  { value: 11, label: "Nov" },
  { value: 12, label: "Dec" },
];
