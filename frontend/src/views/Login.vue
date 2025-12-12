<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card card">
        <div class="auth-header">
          <div class="auth-logo">
            <i class="bi bi-heart-pulse-fill"></i>
          </div>
          <h2>MediCare HMS</h2>
          <p>Sign in to your account</p>
        </div>
        
        <div class="auth-body">
          <div v-if="error" class="alert alert-danger">
            <i class="bi bi-exclamation-circle me-2"></i>
            {{ error }}
          </div>
          
          <form @submit.prevent="handleLogin">
            <div class="form-group">
              <label class="form-label">Username</label>
              <input
                type="text"
                class="form-control"
                v-model="username"
                placeholder="Enter username"
                required
                autocomplete="username"
              >
            </div>
            
            <div class="form-group">
              <label class="form-label">Password</label>
              <div class="password-input">
                <input
                  :type="showPassword ? 'text' : 'password'"
                  class="form-control"
                  v-model="password"
                  placeholder="Enter password"
                  required
                  autocomplete="current-password"
                >
                <button
                  type="button"
                  class="password-toggle"
                  @click="showPassword = !showPassword"
                >
                  <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                </button>
              </div>
            </div>
            
            <button
              type="submit"
              class="btn btn-primary btn-block"
              :disabled="isLoading"
            >
              <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
              {{ isLoading ? 'Signing in...' : 'Sign in' }}
            </button>
          </form>
          
          <div class="auth-footer">
            <span>Don't have an account?</span>
            <router-link to="/register">Register</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/api'

export default {
  name: 'Login',
  emits: ['show-toast', 'login-success'],
  setup(props, { emit }) {
    const router = useRouter()
    const username = ref('')
    const password = ref('')
    const showPassword = ref(false)
    const isLoading = ref(false)
    const error = ref('')

    const handleLogin = async () => {
      error.value = ''
      isLoading.value = true

      try {
        const data = await authService.login(username.value, password.value)
        emit('login-success', data.user)
        emit('show-toast', { type: 'success', message: 'Login successful!' })
        
        switch (data.user.role) {
          case 'admin':
            router.push('/admin')
            break
          case 'doctor':
            router.push('/doctor')
            break
          case 'patient':
            router.push('/patient')
            break
          default:
            router.push('/')
        }
      } catch (err) {
        error.value = err.response?.data?.error || 'Login failed. Please check your credentials.'
      } finally {
        isLoading.value = false
      }
    }

    return {
      username,
      password,
      showPassword,
      isLoading,
      error,
      handleLogin
    }
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: #fafafa;
}

.auth-container {
  width: 100%;
  max-width: 380px;
}

.auth-card {
  border-radius: 12px;
}

.auth-header {
  text-align: center;
  padding: 32px 32px 24px;
  border-bottom: 1px solid #e8e8e8;
}

.auth-logo {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #5e5ce6, #7c7aff);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.auth-logo i {
  font-size: 24px;
  color: white;
}

.auth-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 4px;
  color: #1a1a1a;
}

.auth-header p {
  font-size: 13px;
  color: #999;
  margin: 0;
}

.auth-body {
  padding: 24px 32px 32px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 6px;
}

.password-input {
  position: relative;
}

.password-input .form-control {
  padding-right: 40px;
}

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 0;
}

.password-toggle:hover {
  color: #666;
}

.btn-block {
  width: 100%;
  padding: 10px;
  font-weight: 500;
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e8e8e8;
  font-size: 13px;
  color: #666;
}

.auth-footer a {
  margin-left: 4px;
  font-weight: 500;
}
</style>
