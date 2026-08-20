import { defineStore } from "pinia";

/**
 * Dashboard view preferences.
 *
 * Which groups are folded away is a per-person, per-device preference rather
 * than household data, so it lives here and is persisted locally instead of
 * going near the API. A household that only cares about upstairs folds the rest
 * away once and it stays folded.
 */
export const useDashboardStore = defineStore("dashboard", {
  state: () => ({
    /**
     * IDs of collapsed groups. An array rather than a Set because
     * pinia-plugin-persistedstate round-trips through JSON, and a Set
     * serialises to {}.
     */
    collapsedGroups: [],
    /**
     * The synthetic "No group" bucket starts FOLDED, and needs its own flag to
     * say so: it has no id, and defaulting it via collapsedGroups could not
     * tell "never touched" from "deliberately expanded".
     *
     * It is a leftovers bin rather than a group someone made, so it should sit
     * out of the way until it is wanted -- and on a healthy household it is
     * empty and never rendered at all.
     */
    ungroupedExpanded: false,
  }),
  getters: {
    isCollapsed: state => groupId =>
      groupId === null
        ? !state.ungroupedExpanded
        : state.collapsedGroups.includes(groupId),
  },
  actions: {
    toggleGroup(groupId) {
      if (groupId === null) {
        this.ungroupedExpanded = !this.ungroupedExpanded;
        return;
      }
      const at = this.collapsedGroups.indexOf(groupId);
      if (at === -1) {
        this.collapsedGroups.push(groupId);
      } else {
        this.collapsedGroups.splice(at, 1);
      }
    },
    /**
     * Drop ids that no longer exist, so a deleted group cannot sit in local
     * storage forever and silently collapse a future group that reuses its id.
     */
    prune(existingIds) {
      this.collapsedGroups = this.collapsedGroups.filter(id =>
        existingIds.includes(id)
      );
    },
  },
  persist: true,
});
