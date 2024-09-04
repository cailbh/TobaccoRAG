import Vue from 'vue'
import App from './App.vue'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import VueResource from 'vue-resource'
import axios from "axios";
import VueCookies from "vue-cookies";

import * as echarts from 'echarts'

axios.defaults.headers.post['Content-Type'] = 'application/json';
Vue.prototype.$axios = axios;
Vue.prototype.$echarts = echarts;

Vue.use(VueResource);
Vue.use(ElementUI);
Vue.use(VueCookies);
Vue.config.productionTip = true;

import router from '@/router';
new Vue({
  render: h => h(App),
  router,
  beforeCreate() {
    Vue.prototype.$bus = this;
  }
}).$mount('#app')
