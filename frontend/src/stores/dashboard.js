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
  }),
  getters: {
    isCollapsed: state => groupId => state.collapsedGroups.includes(groupId),
  },
  actions: {
    toggleGroup(groupId) {
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
