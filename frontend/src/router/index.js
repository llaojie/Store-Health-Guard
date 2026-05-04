import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: '门店总览' }
  },
  {
    path: '/store/:id',
    name: 'StoreDetail',
    component: () => import('../views/StoreDetail.vue'),
    meta: { title: '门店详情' }
  },
  {
    path: '/alerts',
    name: 'AlertCenter',
    component: () => import('../views/AlertCenter.vue'),
    meta: { title: '预警中心' }
  },
  {
    path: '/diagnosis',
    name: 'Diagnosis',
    component: () => import('../views/Diagnosis.vue'),
    meta: { title: '诊断工具' }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = `${to.meta.title || '门店健康度预警系统'} - Store Health Guard`
})

export default router
