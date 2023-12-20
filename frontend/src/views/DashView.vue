<template>
  <div class="areas">
    <v-container>
      <v-row dense v-if="!isLoading">
        <v-col cols="12">
          <AreaCard v-for="area in areas" :area="area" :key="area.id" @edit-area="updateArea" @remove-area="deleteArea"/>
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
import AreaCard from '@/components/AreaCard.vue';
import { useAreas } from '@/composables/areasComposable';
import { useChoreStore } from '@/stores/chores'

const chorestore = useChoreStore();
const { areas, isLoading, editArea, removeArea } = useAreas();

const updateArea = async (updatedArea) => {
  try{
    await editArea(updatedArea)
    chorestore.showSnackbar('Area updated', 'success')
  } catch {
    chorestore.showSnackbar('Area not updated', 'error')
  }
}

const deleteArea = async (deletedArea) => {
  try{
    await removeArea(deletedArea)
    chorestore.showSnackbar('Area deleted', 'success')
  } catch {
    chorestore.showSnackbar('Area not deleted', 'error')
  }
}

</script>
