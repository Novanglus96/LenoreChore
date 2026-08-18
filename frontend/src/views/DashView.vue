<template>
  <div class="areas">
    <v-container :class="$vuetify.display.smAndDown ? 'pa-0' : ''">
      <h1 class="lc-visually-hidden">Dashboard</h1>

      <!-- Loading. Three skeletons rather than one, so the placeholder has the
           same shape as the grid it is standing in for and the layout does not
           jump when the data lands. -->
      <div v-if="isLoading" class="lc-card-grid" aria-hidden="true">
        <v-skeleton-loader
          v-for="n in 3"
          :key="n"
          type="article, actions"
        ></v-skeleton-loader>
      </div>

      <div v-else-if="areas && areas.length" class="lc-card-grid">
        <AreaCard
          v-for="area in areas"
          :area="area"
          :key="area.id"
          @edit-area="updateArea"
          @remove-area="deleteArea"
        />
      </div>

      <!-- Previously an empty screen with no explanation. -->
      <v-empty-state
        v-else
        icon="mdi-home-heart"
        title="No areas yet"
        text="Areas are the rooms and spaces you keep track of. Add one from the menu to get started."
      ></v-empty-state>
    </v-container>
  </div>
</template>

<script setup>
import AreaCard from "@/components/AreaCard.vue";
import { useAreas } from "@/composables/areasComposable";

const { areas, isLoading, editArea, removeArea } = useAreas();

const updateArea = async updatedArea => {
  await editArea(updatedArea);
};

const deleteArea = async deletedArea => {
  await removeArea(deletedArea);
};
</script>
