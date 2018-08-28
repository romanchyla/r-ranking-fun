import '@babel/polyfill'
import Vue from 'vue'
import './plugins/vuetify'
import App from './App.vue'
import VueRouter from 'vue-router'
import routes from './routes'
import store from './store'


Vue.config.productionTip = false
Vue.use(VueRouter)


const router = new VueRouter({
  routes: routes
})

window.app = new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
