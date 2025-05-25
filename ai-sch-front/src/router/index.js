import Vue from 'vue'
import VueRouter from 'vue-router'
import Layout from '@/layout'

Vue.use(VueRouter)

// 公共路由 - 无需登录即可访问
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },
  {
    path: '/404',
    component: () => import('@/views/error-page/404'),
    hidden: true
  },
  {
    path: '/',
    redirect: '/home',
  },
  {
    path: '/home',
    component: Layout,
    name: 'Home',
    meta: { title: '首页', icon: 'el-icon-s-home' },
    children: [
      {
        path: '',
        name: 'HomePage',
        component: () => import('@/views/home/index'),
        meta: { title: '首页概览', icon: 'dashboard' }
      }
    ]
  }
]

// 异步路由 - 需要根据用户角色动态加载
export const asyncRoutes = [
  {
    path: '/basic-data',
    component: Layout,
    redirect: '/basic-data/departments',
    name: 'BasicData',
    meta: { title: '基础数据', icon: 'el-icon-document' },
    children: [
      {
        path: 'departments',
        name: 'Departments',
        component: () => import('@/views/basic-data/departments/index'),
        meta: { title: '部门管理' }
      },
      {
        path: 'majors',
        name: 'Majors',
        component: () => import('@/views/basic-data/majors/index'),
        meta: { title: '专业管理' }
      },
      {
        path: 'classes',
        name: 'Classes',
        component: () => import('@/views/basic-data/classes/index'),
        meta: { title: '班级管理' }
      },
      {
        path: 'teachers',
        name: 'Teachers',
        component: () => import('@/views/basic-data/teachers/index'),
        meta: { title: '教师管理' }
      },
      {
        path: 'classrooms',
        name: 'Classrooms',
        component: () => import('@/views/basic-data/classrooms/index'),
        meta: { title: '教室管理' }
      },
      {
        path: 'courses',
        name: 'Courses',
        component: () => import('@/views/basic-data/courses/index'),
        meta: { title: '课程管理' }
      }
    ]
  },
  {
    path: '/scheduling',
    component: Layout,
    redirect: '/scheduling/tasks',
    name: 'Scheduling',
    meta: { title: '排课管理', icon: 'el-icon-date' },
    children: [
      {
        path: 'tasks',
        name: 'SchedulingTasks',
        component: () => import('@/views/scheduling/tasks/index'),
        meta: { title: '排课任务管理' }
      },
      {
        path: 'strategy',
        name: 'SchedulingStrategy',
        component: () => import('@/views/scheduling/strategy/index'),
        meta: { title: '排课策略设置' }
      },
      {
        path: 'results',
        name: 'SchedulingResults',
        component: () => import('@/views/scheduling/results/index'),
        meta: { title: '排课结果查看' }
      },
      {
        path: 'manual',
        name: 'ManualScheduling',
        component: () => import('@/views/scheduling/results/manual'),
        meta: { title: '手动排课' }
      }
    ]
  },
  {
    path: '/statistics',
    component: Layout,
    redirect: '/statistics/classroom-utilization',
    name: 'Statistics',
    meta: { title: '统计分析', icon: 'el-icon-data-analysis' },
    children: [
      {
        path: 'classroom-utilization',
        name: 'ClassroomUtilization',
        component: () => import('@/views/dashboard/index'),
        meta: { title: '教室利用率分析', icon: 'dashboard' }
      },
      {
        path: 'teacher-workload',
        component: () => import('@/views/dashboard/teacher-workload'),
        name: 'TeacherWorkload',
        meta: { title: '教师工作量统计', icon: 'peoples' }
      },
      {
        path: 'resource-analysis',
        component: () => import('@/views/dashboard/resource-analysis'),
        name: 'ResourceAnalysis',
        meta: { title: '教学资源分析', icon: 'chart' }
      }
    ]
  },
  // 404页必须放在最后
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new VueRouter({
  mode: 'history',
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// 重置路由方法
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher
}

export default router
