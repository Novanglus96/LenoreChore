<template>
    <v-dialog
      v-model="dialog"
      persistent
      width="1024"
    >
      <template v-slot:activator="{ props }">
        <v-list-item
                key="2"
                v-bind="props"
              >
                <template v-slot:prepend>
                  <v-icon icon="mdi-plus-circle"></v-icon>
                </template>
                <v-list-item-title>Add Chore</v-list-item-title>
        </v-list-item>
      </template>
      <v-card>
        <v-card-title>
          <span class="text-h5">Add Chore</span>
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
                    v-for="icon in icons"
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
            @click="submitForm()"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
</template>
<script>
import axios from 'axios';

  export default {
    data: () => ({
      dialog: false,
      formData: {
        area_name: '',
        area_icon: 'mdi-home',
      },
      icons: [
        'mdi-home', 'mdi-fridge', 'mdi-sofa', 'mdi-water', 'mdi-help', 'mdi-home',
      ],
    }),
    methods: {
    async submitForm() {
      try {
        // Make a POST request to your API endpoint
        const response = await axios.post('https://chores.danielleandjohn.love/api/areas/', this.formData);

        // Handle the response here (e.g., show a success message)
        console.log('Response:', response.data);
        this.dialog = false
      } catch (error) {
        // Handle errors (e.g., show an error message)
        console.error('Error:', error);
      }
    },
  },
  }
</script>