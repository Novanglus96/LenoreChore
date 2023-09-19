<template>
  <div>
      <v-container>
        <v-row dense>
          <v-col cols="12" v-for="item in items" :key="item.id">
            <v-card
              color="primary"
              theme="dark"
            >
              <div class="d-flex flex-no-wrap justify-space-between">
                <div>
                  <v-card-title class="text-h5">
                    <v-icon>{{ item.area_icon }}</v-icon>
                    {{ item.area_name }}
                  </v-card-title>

                  <v-card-subtitle>{{ item.area_duecount }} Chores Due Today</v-card-subtitle>

                  <v-card-actions>
                    <v-btn
                      class="ms-2"
                      variant="outlined"
                      size="small"
                      to="/list"
                    >
                      See Chores
                    </v-btn>
                  </v-card-actions>
                </div>
                <v-progress-circular
                  :rotate="360"
                  :size="125"
                  :width="15"
                  :model-value="item.area_cleanlevel"
                  color="red"
                >
                  {{ item.area_cleanlevel }}
                </v-progress-circular>

              </div>
            </v-card>
          </v-col>

        </v-row>
      </v-container>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      items: [], // Initialize an empty array to hold the fetched data
    };
  },
  created() {
    setInterval(this.fetchData, 1000)
  },
  mounted() {
    this.fetchData(); // Call the fetchData method when the component is mounted
  },
  methods: {
    fetchData() {
      // Make an Axios GET request to your Django API endpoint
      axios.get('https://chores.danielleandjohn.love/api/areas/')
        .then((response) => {
          this.items = response.data; // Assign the fetched data to the items array
        })
        .catch((error) => {
          console.error('Error fetching data:', error);
        });
    },
  },
};
</script>