/**
 * The one line of personality at the top of the dashboard.
 *
 * The app bar is a logo and two icon buttons, and the dashboard opened straight
 * into a grid of cards — nothing anywhere said hello, or gave the summary
 * before the detail that a dashboard is supposed to lead with.
 */

/**
 * @param {Date} [now] injectable so the boundaries are testable rather than
 *   depending on when the suite happens to run
 * @returns {string} "Good morning" / "Good afternoon" / "Good evening"
 */
export function greeting(now = new Date()) {
  const hour = now.getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

/**
 * What is waiting, phrased as a sentence rather than two numbers.
 *
 * Overdue is called out separately because it is the thing worth acting on;
 * lumping it into the due count is how it stops registering.
 *
 * @param {number} due total chores due
 * @param {number} overdue how many of those are past their date
 * @returns {string}
 */
export function choreSummary(due, overdue) {
  if (!due && !overdue) return "Nothing needs doing right now.";

  const dueBit = `${due} ${due === 1 ? "chore" : "chores"} due`;
  if (!overdue) return `${dueBit}.`;
  return `${dueBit}, ${overdue} overdue.`;
}
