<template>
  <div class="dash">
    <AreaCard />
  </div>
</template>

<script>
// @ is an alias to /src
import AreaCard from '@/components/AreaCard.vue'

export default {
  name: 'DashView',
  components: {
    AreaCard
  }
}
</script>
