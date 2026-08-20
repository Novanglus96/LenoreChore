import { defineStore } from "pinia";

export const useHistoryItemsStore = defineStore("historyitems", {
    state: () => ({
        pageinfo: {
            page: 1,
            page_size: 15
        },
        graph: {
            week: 0,
        }
    }),
    getters: {
    },
    actions: {
      },
});