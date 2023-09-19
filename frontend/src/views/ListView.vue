<template>
  <div class="list">
    <ChoreCard />
  </div>
</template>

<script>
// @ is an alias to /src
import ChoreCard from '@/components/ChoreCard.vue'

export default {
  name: 'ListView',
  components: {
    ChoreCard
  }
}
</script>
