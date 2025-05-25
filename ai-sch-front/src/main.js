import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// 引入Element UI组件库
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
// 引入全局CSS
import '@/styles/index.scss'

// 引入全局组件
import Pagination from '@/components/Pagination'
// 全局注册组件
Vue.component('Pagination', Pagination)

// 引入权限控制
import './permission'

// 设置为 false 以阻止 vue 在启动时生成生产提示
Vue.config.productionTip = false

// 使用Element UI
Vue.use(ElementUI)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app') 
