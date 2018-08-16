<template>
  <div id="app">
    <Header />
    <WelcomePage msg="stranger"/>
  </div>
</template>

<script>
import WelcomePage from './components/WelcomePage.vue'
import Header from './components/Header.vue'

export default {
  name: 'app',
  components: {
    WelcomePage,
    Header
  }
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  text-align: left;
}
</style>
