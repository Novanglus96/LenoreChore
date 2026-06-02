<template>
  <v-container class="pa-4 mx-auto" style="max-width: 700px">
    <v-card :rounded="$vuetify.display.smAndDown ? 0 : undefined">
      <v-card-item>
        <v-img src="logov2.png" max-width="200" class="mb-2"></v-img>
        <v-card-title>About LenoreChore</v-card-title>
        <v-card-subtitle>A simple chore app</v-card-subtitle>
      </v-card-item>

      <v-divider></v-divider>

      <v-card-text>
        <v-list density="compact" class="bg-transparent">
          <v-list-item title="Frontend version">
            <template v-slot:append>
              <span class="text-medium-emphasis">{{ appVersion }}</span>
            </template>
          </v-list-item>
          <v-list-item title="Backend version">
            <template v-slot:append>
              <span class="text-medium-emphasis">{{
                versionDetails?.app_version ?? "—"
              }}</span>
            </template>
          </v-list-item>
          <v-list-item title="Python">
            <template v-slot:append>
              <span class="text-medium-emphasis">{{
                versionDetails?.python_version ?? "—"
              }}</span>
            </template>
          </v-list-item>
          <v-list-item title="Django">
            <template v-slot:append>
              <span class="text-medium-emphasis">{{
                versionDetails?.django_version ?? "—"
              }}</span>
            </template>
          </v-list-item>
        </v-list>

        <div
          v-if="
            !isLoading && appVersion !== versionDetails?.app_version &&
            versionDetails?.app_version
          "
          class="text-warning text-caption px-4 pb-2"
        >
          <v-icon icon="mdi-alert" size="small"></v-icon>
          Frontend and backend versions differ.
        </div>

        <v-divider class="my-2"></v-divider>

        <div class="text-subtitle-2 px-4 pb-1">Backend packages</div>
        <div v-if="isLoading" class="text-center py-4">
          <v-progress-circular
            indeterminate
            color="primary"
            size="28"
          ></v-progress-circular>
        </div>
        <v-table v-else-if="versionDetails" density="compact">
          <tbody>
            <tr v-for="(ver, name) in versionDetails.packages" :key="name">
              <td>{{ name }}</td>
              <td class="text-right text-medium-emphasis">{{ ver }}</td>
            </tr>
          </tbody>
        </v-table>
        <div v-else class="text-medium-emphasis px-4 py-2">
          Version details unavailable.
        </div>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-btn
          href="https://github.com/Novanglus96/LenoreChore"
          target="_blank"
          rel="noopener"
          prepend-icon="mdi-github"
          variant="text"
        >
          GitHub
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn to="/" variant="text">Back</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup>
import { useVersionDetails } from "@/composables/versionComposable";
import { version as appVersion } from "../../package.json";

const { versionDetails, isLoading } = useVersionDetails();
</script>

<style scoped></style>
