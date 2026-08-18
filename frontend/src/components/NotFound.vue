<template>
  <!-- Was a loose div: an image, an unwrapped sentence and an inline link, with
       no heading and no structure. The app already has an empty-state language
       -- DashView and ListView both use it -- so this uses the same one instead
       of inventing a third look for "there is nothing here". -->
  <v-empty-state
    title="That page doesn't exist"
    text="The link may be out of date, or the page may have moved."
  >
    <template v-slot:media>
      <!-- alt="" because the heading right below says the same thing; a
           duplicate announcement is noise. -->
      <v-img
        src="404.png"
        :width="320"
        class="mx-auto mb-2"
        alt=""
      ></v-img>
    </template>

    <template v-slot:actions>
      <v-btn variant="flat" color="primary" prepend-icon="mdi-home" to="/">
        Back to the dashboard
      </v-btn>
    </template>
  </v-empty-state>
</template>
