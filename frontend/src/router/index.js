import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '@/services/api'

// Auth views
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'

// Dashboard views
import AdminDashboard from '@/views/admin/AdminDashboard.vue'
import DoctorDashboard from '@/views/doctor/DoctorDashboard.vue'
import PatientDashboard from '@/views/patient/PatientDashboard.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { guest: true }
  },
  // Admin routes
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  },
  // Doctor routes
  {
    path: '/doctor',
    name: 'DoctorDashboard',
    component: DoctorDashboard,
    meta: { requiresAuth: true, role: 'doctor' }
  },
  // Patient routes
  {
    path: '/patient',
    name: 'PatientDashboard',
    component: PatientDashboard,
    meta: { requiresAuth: true, role: 'patient' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = authService.isAuthenticated()
  const user = authService.getUser()

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && isAuthenticated) {
    // Redirect authenticated users to their dashboard
    if (user) {
      switch (user.role) {
        case 'admin':
          next('/admin')
          break
        case 'doctor':
          next('/doctor')
          break
        case 'patient':
          next('/patient')
          break
        default:
          next('/login')
      }
    } else {
      next('/login')
    }
  } else if (to.meta.role && user && to.meta.role !== user.role) {
    // Redirect to correct dashboard if role doesn't match
    switch (user.role) {
      case 'admin':
        next('/admin')
        break
      case 'doctor':
        next('/doctor')
        break
      case 'patient':
        next('/patient')
        break
      default:
        next('/login')
    }
  } else {
    next()
  }
})

export default router

