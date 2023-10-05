<template>
    <v-dialog
      v-model="dialog"
      persistent
      width="1024"
    >
      <template v-slot:activator="{ props }">
        <v-list-item
                key="1"
                v-bind="props"
              >
                <template v-slot:prepend>
                  <v-icon icon="mdi-plus-circle"></v-icon>
                </template>
                <v-list-item-title>Add Area</v-list-item-title>
        </v-list-item>
      </template>
      <v-card>
        <v-card-title>
          <span class="text-h5">Add Area</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col
                cols="12"
                sm="6"
                md="4"
              >
                <v-text-field
                  label="Area name*"
                  required
                  v-model="formData.area_name"
                ></v-text-field>
              </v-col>
              <v-col
                cols="12"
                sm="6"
                md="4"
              >
                <v-chip-group
                  v-model="formData.area_icon"
                  selected-class="text-deep-purple-accent-4"
                  mandatory
                >
                  <v-chip 
                    v-for="icon in chorestore.areaicons"
                    :key="icon"
                    :value="icon"
                  >
                  <v-icon>{{ icon }}</v-icon>
                  </v-chip>
                </v-chip-group>
              </v-col>
            </v-row>
          </v-container>
          <small>*indicates required field</small>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="blue-darken-1"
            variant="text"
            @click="dialog = false"
          >
            Close
          </v-btn>
          <v-btn
            color="blue-darken-1"
            variant="text"
            @click="submitForm"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
</template>
<script setup>
  import { ref } from 'vue';
  import { useChoreStore } from '@/stores/chores';

  const chorestore = useChoreStore();
  const dialog = ref(false)
  const formData = ref({
        area_name: '',
        area_icon: 'mdi-home',
      })

  const submitForm = async () => {
    try {
      chorestore.addArea(formData.value);
      dialog.value = false;
    } catch (error) {
      // Handle errors (e.g., show an error message)
      console.log('Error:', error);
    }
  };
</script>