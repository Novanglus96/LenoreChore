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
                  label="Chore name*"
                  required
                  v-model="formData.chore_name"
                ></v-text-field>
              </v-col>
              <v-col
                cols="12"
                sm="6"
                md="4"
              >
                <v-select
                    label="Area*"
                    required
                    :items="areas"
                    item-title="area_name"
                    item-value="id"
                    v-model="formData.area"
                    return-object   
                >
                </v-select>
              </v-col>
                </v-row>
                <v-row>
                  <v-col
                cols="12"
                sm="6"
                md="4"
              >
              <span class="text-h9">Repeat</span>
                  </v-col>
              </v-row>
                <v-row>
                  <v-col
                cols="12"
                sm="6"
                md="4"
              >
              <v-select
                    label="Interval*"
                    required
                    :items="intervals"
                    v-model="formData.intervalNumber"   
                >
                </v-select>
                  </v-col>
                  <v-col
                cols="12"
                sm="6"
                md="4"
              >
                <v-select
                    label="Unit(s)*"
                    required
                    :items="units"
                    v-model="formData.unit"   
                >
                </v-select>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col
                cols="12"
                sm="6"
                md="4"
              >
              <span class="text-h9">Active Months</span>
                  </v-col>
              </v-row>
                <v-row>
                  <v-col
                cols="4"
                sm="6"
                md="4"
              >
              <v-checkbox
                v-model="formData.active_months"
                label="Jan"
                color="primary"
                hide-details
                :value="1"
              >
              </v-checkbox>
                  </v-col>
                  <v-col
                cols="4"
                sm="6"
                md="4"
              >
              <v-checkbox
                v-model="formData.active_months"
                label="Feb"
                color="primary"
                hide-details
                :value="2"
              >
              </v-checkbox>
                  </v-col>
                  <v-col
                cols="4"
                sm="6"
                md="4"
              >
              <v-checkbox
                v-model="formData.active_months"
                label="Mar"
                color="primary"
                hide-details
                :value="3"
              >
              </v-checkbox>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col
                cols="4"
                sm="6"
                md="4"
              >
              <v-checkbox
                v-model="formData.active_months"
                label="Apr"
                color="primary"
                hide-details
                :value="4"
              >
              </v-checkbox>
                  </v-col>               
                  <v-col
                cols="4"
                sm="6"
                md="4"
              >
              <v-checkbox
                v-model="formData.active_months"
                label="May"
                color="primary"
                hide-details
                :value="5"
              >
              </v-checkbox>
                  </v-col>
                  <v-col
                cols="4"
                sm="6"
                md="4"
              >
              <v-checkbox
                v-model="formData.active_months"
                label="Jun"
                color="primary"
                hide-details
                :value="6"
              >
              </v-checkbox>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col
                cols="4"
                sm="6"
                md="4"
              >
              <v-checkbox
                v-model="formData.active_months"
                label="Jul"
                color="primary"
                hide-details
                :value="7"
              >
              </v-checkbox>
                  </v-col>
                  <v-col
                cols="4"
                sm="6"
                md="4"
              >
              <v-checkbox
                v-model="formData.active_months"
                label="Aug"
                color="primary"
                hide-details
                :value="8"
              >
              </v-checkbox>
                  </v-col>               
                  <v-col
                cols="4"
                sm="6"
                md="4"
              >
              <v-checkbox
                v-model="formData.active_months"
                label="Sep"
                color="primary"
                hide-details
                :value="9"
              >
              </v-checkbox>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col
                cols="4"
                sm="6"
                md="4"
              >
              <v-checkbox
                v-model="formData.active_months"
                label="Oct"
                color="primary"
                hide-details
                :value="10"
              >
              </v-checkbox>
                  </v-col>
                  <v-col
                cols="4"
                sm="6"
                md="4"
              >
              <v-checkbox
                v-model="formData.active_months"
                label="Nov"
                color="primary"
                hide-details
                :value="11"
              >
              </v-checkbox>
                  </v-col>
                  <v-col
                cols="4"
                sm="6"
                md="4"
              >
              <v-checkbox
                v-model="formData.active_months"
                label="Dec"
                color="primary"
                hide-details
                :value="12"
              >
              </v-checkbox>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col
                cols="12"
                sm="6"
                md="4"
              >
                <b>Effort </b>
                <v-rating
                  label="Effort"
                  v-model="formData.effort"
                  length="3"
                  size="20"
                ></v-rating>
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
<script setup>
  import { ref, computed } from 'vue';
  import { useChoreStore } from '@/stores/chores';
  import { useAreas } from '@/composables/areasComposable'

  const chorestore = useChoreStore();
  const dialog = ref(false)
  const formData = ref({
        chore_name: '',
        area: '',
        unit: '',
        effort: 1,
        active_months: [1,2,3,4,5,6,7,8,9,10,11,12],
        intervalNumber: '',
      })
  const { areas } = useAreas()

  const units = computed(() => {
    return chorestore.units;
  });
  const intervals = computed(() => {
    return chorestore.intervals;
  });

  const submitForm = async () => {
    try {
      chorestore.addChore(formData.value);
      dialog.value = false;
    } catch (error) {
      // Handle errors (e.g., show an error message)
      console.log('Error:', error);
    }
  };
</script>