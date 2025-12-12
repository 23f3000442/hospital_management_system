<template>
  <div id="app">
    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="text-center">
        <div class="spinner-custom mb-3"></div>
        <p class="text-muted">Loading...</p>
      </div>
    </div>

    <!-- Toast Container -->
    <div class="toast-container">
      <div
        v-for="(toast, index) in toasts"
        :key="index"
        class="toast show mb-2"
        :class="`bg-${toast.type}`"
        role="alert"
      >
        <div class="toast-body text-white d-flex justify-content-between align-items-center">
          <span>{{ toast.message }}</span>
          <button type="button" class="btn-close btn-close-white" @click="removeToast(index)"></button>
        </div>
      </div>
    </div>

    <!-- Navbar (shown only when authenticated) -->
    <Navbar v-if="isAuthenticated" :user="user" @logout="handleLogout" />

    <!-- Router View -->
    <router-view 
      @show-toast="showToast" 
      @set-loading="setLoading"
      @login-success="handleLoginSuccess"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/api'
import Navbar from '@/components/shared/Navbar.vue'

export default {
  name: 'App',
  components: {
    Navbar
  },
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const toasts = ref([])
    const user = ref(null)

    const isAuthenticated = computed(() => authService.isAuthenticated())

    onMounted(() => {
      user.value = authService.getUser()
    })

    const handleLoginSuccess = (userData) => {
      user.value = userData
    }

    const handleLogout = () => {
      authService.logout()
      user.value = null
      router.push('/login')
      showToast({ type: 'info', message: 'Logged out successfully' })
    }

    const showToast = (toast) => {
      const id = Date.now()
      toasts.value.push({ ...toast, id })
      setTimeout(() => {
        const index = toasts.value.findIndex(t => t.id === id)
        if (index > -1) {
          toasts.value.splice(index, 1)
        }
      }, 4000)
    }

    const removeToast = (index) => {
      toasts.value.splice(index, 1)
    }

    const setLoading = (value) => {
      loading.value = value
    }

    return {
      loading,
      toasts,
      user,
      isAuthenticated,
      handleLoginSuccess,
      handleLogout,
      showToast,
      removeToast,
      setLoading
    }
  }
}
</script>

<style>
#app {
  min-height: 100vh;
}
</style>
