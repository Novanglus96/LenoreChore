/**
 * Dirtiness: the bands, and how a set of areas averages into one number.
 *
 * Both of these were copied into three components each. `dirtBand` lived
 * identically in ChoreCard, AreaCard and AreaGroupSection, and the weighted
 * average lived in AreaGroupSection alone -- which was fine until the
 * dashboard's house needed the same number and would otherwise have grown a
 * fourth copy of the formula. A house that disagrees with the bar underneath it
 * is worse than no house.
 */

/** The app's defaults, used when the household has not set its own. */
export const DEFAULT_MED_THRESH = 49;
export const DEFAULT_HIGH_THRESH = 74;

/**
 * The band a dirtiness percentage falls in.
 *
 * Carries BOTH a colour and a word. Colour alone fails for anyone who cannot
 * tell the hues apart -- and because the thresholds are user-configurable, the
 * word is also the only thing that explains why a given percentage counts as
 * "filthy" in this particular household.
 *
 * @param {number} dirt 0..100
 * @param {number} [med] upper bound of the clean band
 * @param {number} [high] upper bound of the middle band
 * @returns {{color: string, label: string}} a theme colour name and its word
 */
export function dirtBand(
  dirt,
  med = DEFAULT_MED_THRESH,
  high = DEFAULT_HIGH_THRESH,
) {
  const value = dirt ?? 0;
  if (value <= med) return { color: "clean", label: "clean-ish" };
  if (value <= high) return { color: "soiled", label: "getting there" };
  return { color: "filthy", label: "filthy" };
}

/**
 * The dirtiness of a set of areas, weighted by how many chores each holds.
 *
 * Chore-weighted, not a mean of means: `total_dirtiness` is the SUM of the
 * chore dirtiness in an area and `totalCount` the chore count, so dividing the
 * sums gives the same answer a single area holding all those chores would
 * report. Averaging each area's percentage would let a one-chore area outvote
 * a twenty-chore one.
 *
 * @param {Array<{total_dirtiness?: number, totalCount?: number}>} areas
 * @returns {number} 0..100, rounded
 */
export function weightedDirtiness(areas) {
  const list = areas ?? [];
  const chores = list.reduce((sum, a) => sum + (a.totalCount || 0), 0);
  if (!chores) return 0;
  const total = list.reduce((sum, a) => sum + (a.total_dirtiness || 0), 0);
  return Math.min(100, Math.round(total / chores));
}
