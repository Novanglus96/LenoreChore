/**
 * The app's primary destinations.
 *
 * Shared because two components render them now -- the overflow menu in the app
 * bar and the bottom navigation -- and a second copy is how the two end up
 * offering different places to go.
 */
export const DESTINATIONS = [
  { title: "Dashboard", url: "/", icon: "mdi-home", activeIcon: "mdi-home" },
  {
    title: "List",
    url: "/list",
    icon: "mdi-view-list-outline",
    activeIcon: "mdi-view-list",
  },
  {
    title: "Graphs",
    url: "/graphs",
    icon: "mdi-chart-bar",
    activeIcon: "mdi-chart-bar",
  },
  {
    title: "History",
    url: "/history",
    icon: "mdi-clipboard-clock-outline",
    activeIcon: "mdi-clipboard-clock",
  },
];

/**
 * Which destination a path belongs to.
 *
 * "/" has to be matched exactly -- every path starts with it, so a prefix test
 * would report the dashboard as active on every screen in the app.
 *
 * @param {string} path the current route path
 * @returns {string|undefined} the matching destination's url
 */
export function activeDestination(path) {
  if (path === "/") return "/";
  return DESTINATIONS.find(d => d.url !== "/" && path.startsWith(d.url))?.url;
}
