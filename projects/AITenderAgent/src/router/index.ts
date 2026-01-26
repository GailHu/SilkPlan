import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import FileUploadView from '../views/FileUploadView.vue'
import ProposalEditorView from '../views/ProposalEditorView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/upload',
      name: 'upload',
      component: FileUploadView,
      meta: { requiresAuth: true }
    },
    {
      path: '/editor',
      name: 'editor',
      component: ProposalEditorView,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
