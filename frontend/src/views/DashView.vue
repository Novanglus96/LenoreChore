<template>
  <div class="areas">
    <v-container>
      <v-row dense v-if="!isLoading">
        <v-col cols="12">
          <AreaCard
            v-for="area in areas"
            :area="area"
            :key="area.id"
            @edit-area="updateArea"
            @remove-area="deleteArea"
          />
        </v-col>
      </v-row>
      <v-row dense v-else>
        <v-col cols="12">
          <v-skeleton-loader type="card" color="primary"></v-skeleton-loader>
        </v-col>
      </v-row>
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
