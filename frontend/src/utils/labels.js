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

/**
 * Effort levels, named.
 *
 * The 3-star rating was presented as a bolded word next to an unexplained
 * widget: nothing said what one star meant versus three. The rating control
 * stays -- it reads at a glance in a list -- but it now carries the word too,
 * for the same reason the dirtiness bands do: so the meaning does not depend on
 * counting glyphs.
 *
 * Keys are the values Chore.effort stores (1..3).
 */
export const EFFORT_LEVELS = {
  1: "Quick",
  2: "Some work",
  3: "Big job",
};

/**
 * @param {number} effort 1..3
 * @returns {string} the level's name, or "" for anything unexpected
 */
export function effortLabel(effort) {
  return EFFORT_LEVELS[effort] ?? "";
}

/**
 * The four colours a household member can be.
 *
 * ⚠️ The VALUES are persisted in CustomUser.user_color as literal hex strings.
 * Changing one silently re-colours nobody -- it orphans every user already
 * holding the old value. Only the names are free to change, and these are the
 * Material palette names for the same four hexes: "Color1".."Color4" told a
 * sighted user nothing and a screen reader user less than nothing, since the
 * swatch beside them is decorative.
 *
 * Lives here rather than in the profile screen because the profile is no
 * longer the only thing that renders a member's colour.
 */
export const USER_COLORS = [
  { name: "Pink", value: "#E91E63" },
  { name: "Indigo", value: "#3F51B5" },
  { name: "Teal", value: "#009688" },
  { name: "Lime", value: "#CDDC39" },
];

/**
 * The avatar illustration for a member.
 *
 * The four filenames were spelled out at three call sites, each rebuilding the
 * same child/adult × masculine/feminine matrix by hand.
 *
 * @param {boolean} male which illustration, not an assertion about the person
 * @param {boolean} isChild whether they are in the child group
 */
export function avatarImage(male, isChild) {
  const age = isChild ? "child" : "adult";
  return `${age}_${male ? "male" : "female"}_avatar.jpg`;
}

/**
 * The avatar choices, named. Each radio used to contain ONLY an image, so both
 * options announced as blank and were indistinguishable without sight. The
 * label describes the illustration rather than the person choosing it.
 */
export function avatarOptions(isChild) {
  return [
    { value: true, label: "Masculine", image: avatarImage(true, isChild) },
    { value: false, label: "Feminine", image: avatarImage(false, isChild) },
  ];
}
