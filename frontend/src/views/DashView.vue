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
    <v-snackbar
      v-model="snackbar"
      :color="snackbarColor"
      :timeout="snackbarTimeout"
      content-class="centered-text"
    >
      {{ snackbarText }}
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import AreaCard from '@/components/AreaCard.vue';
import { useAreas } from '@/composables/areasComposable';

const snackbar = ref(false);
const snackbarText = ref('');
const snackbarColor = ref('');
const snackbarTimeout = ref(1500);
const { areas, isLoading, editArea, removeArea } = useAreas();

const updateArea = async (updatedArea) => {
  try{
    await editArea(updatedArea)
    showSnackbar('Area updated', 'success')
  } catch {
    showSnackbar('Area not updated', 'error')
  }
}

const deleteArea = async (deletedArea) => {
  try{
    await removeArea(deletedArea)
    showSnackbar('Area deleted', 'success')
  } catch {
    showSnackbar('Area not deleted', 'error')
  }
}

const showSnackbar = (text, color) => {
  snackbarText.value = text;
  snackbarColor.value = color;
  snackbar.value = true;
}

</script>
