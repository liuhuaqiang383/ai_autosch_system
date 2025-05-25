import router from './router'
import store from './store'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import { getToken } from '@/utils/auth'

NProgress.configure({ showSpinner: false })

const whiteList = ['/login'] // 不重定向白名单

router.beforeEach((to, from, next) => {
  // 开始进度条
  NProgress.start()

  // 设置页面标题
  document.title = '智能排课系统'
  
  // 判断是否有token
  const hasToken = getToken()
  
  if (hasToken) {
    if (to.path === '/login') {
      // 如果已经登录，并且要访问登录页，则重定向到首页
      next({ path: '/home' })
      NProgress.done()
    } else {
      // 确保路由已经加载
      if (store.getters.roles && store.getters.roles.length > 0) {
        next()
      } else {
        // 获取用户信息
        store.dispatch('user/getInfo').then(res => {
          // 根据角色生成可访问路由
          const roles = res && res.roles ? res.roles : ['admin']
          store.dispatch('permission/generateRoutes', roles).then(() => {
            // 动态添加路由
            router.addRoutes(store.getters.addRoutes)
            // 设置replace: true，这样导航就不会留下历史记录
            next({ ...to, replace: true })
          })
        }).catch(err => {
          // 获取用户信息失败，可能是token过期或者其他原因
          store.dispatch('user/resetToken')
          console.error(err)
          next(`/login?redirect=${to.path}`)
          NProgress.done()
        })
      }
    }
  } else {
    if (whiteList.indexOf(to.path) !== -1) {
      // 在免登录白名单，直接进入
      next()
    } else {
      // 否则全部重定向到登录页
      next(`/login?redirect=${to.path}`)
      NProgress.done()
    }
  }
})

router.afterEach(() => {
  // 结束进度条
  NProgress.done()
}) 
