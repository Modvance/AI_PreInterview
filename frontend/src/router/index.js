import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/interview',
    name: 'InterviewSetup',
    component: () => import('@/views/InterviewSetup.vue')
  },
  {
    path: '/interview/:sessionId',
    name: 'Interview',
    component: () => import('@/views/Interview.vue'),
    props: true
  },
  {
    path: '/report/:sessionId',
    name: 'Report',
    component: () => import('@/views/Report.vue'),
    props: true
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
