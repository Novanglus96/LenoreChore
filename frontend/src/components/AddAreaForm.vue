<template>
  <v-row justify="center">
    <v-dialog
      v-model="dialog"
      persistent
      width="1024"
    >
      <template v-slot:activator="{ props }">
        <v-btn
          color="info"
          v-bind="props"
        >
          Add Area
        </v-btn>
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
                <v-color-picker
                  label="BG Color"
                  class="ma-2"
                  :swatches="swatches"
                  :modes="['hexa']"
                  show-swatches
                  v-model="formData.area_bgcolor"
                ></v-color-picker>
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
  </v-row>
</template>
<script>
import axios from 'axios';

  export default {
    data: () => ({
      dialog: false,
      swatches: [
        ['#3391A1', '#335AA1', '#33A17A'],
        ['#FF0000', '#AA0000', '#550000'],
        ['#FFFF00', '#AAAA00', '#555500'],
        ['#00FF00', '#00AA00', '#005500'],
        ['#00FFFF', '#00AAAA', '#005555'],
      ],
      formData: {
        area_name: '',
        area_bgcolor: '#FFFFFF',
        area_textcolor: '#FFFFFF',
      }
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