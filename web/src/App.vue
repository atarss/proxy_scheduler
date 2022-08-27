<script setup>
import ProxyList from './components/ProxyList.vue';

</script>

<template>
  <div class="main_container">
    <h3>Proxy Controller</h3>
    <p>&nbsp;</p>
    <!-- <h6>&nbsp;</h6> -->
    <div class="proxy_container">
      <ProxyList />
    </div>
  </div>
</template>

<style scoped>
.main_container {
  margin: auto;
  padding: 10px;
  width: 100%;
  max-width: 600px;
}

.proxy_container {
  margin: 10px;
}
</style>
