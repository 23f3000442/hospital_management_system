<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card card">
        <div class="auth-header">
          <div class="auth-logo">
            <i class="bi bi-person-plus-fill"></i>
          </div>
          <h2>Create Account</h2>
          <p>Register as a new patient</p>
        </div>
        
        <div class="auth-body">
          <div v-if="error" class="alert alert-danger">
            <i class="bi bi-exclamation-circle me-2"></i>
            {{ error }}
          </div>
          
          <div v-if="success" class="alert alert-success">
            <i class="bi bi-check-circle me-2"></i>
            {{ success }}
          </div>
          
          <form v-if="!success" @submit.prevent="handleRegister">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Username <span class="required">*</span></label>
                <input
                  type="text"
                  class="form-control"
                  v-model="form.username"
                  placeholder="Choose username"
                  required
                >
              </div>
              
              <div class="form-group">
                <label class="form-label">Email <span class="required">*</span></label>
                <input
                  type="email"
                  class="form-control"
                  v-model="form.email"
                  placeholder="you@example.com"
                  required
                >
              </div>
            </div>
            
            <div class="form-group">
              <label class="form-label">Password <span class="required">*</span></label>
              <div class="password-input">
                <input
                  :type="showPassword ? 'text' : 'password'"
                  class="form-control"
                  v-model="form.password"
                  placeholder="Min. 6 characters"
                  required
                  minlength="6"
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
            
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Full Name <span class="required">*</span></label>
                <input
                  type="text"
                  class="form-control"
                  v-model="form.name"
                  placeholder="Your name"
                  required
                >
              </div>
              
              <div class="form-group">
                <label class="form-label">Phone <span class="required">*</span></label>
                <input
                  type="tel"
                  class="form-control"
                  v-model="form.phone"
                  placeholder="Phone number"
                  required
                >
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Date of Birth</label>
                <input
                  type="date"
                  class="form-control"
                  v-model="form.date_of_birth"
                >
              </div>
              
              <div class="form-group">
                <label class="form-label">Gender</label>
                <select class="form-select" v-model="form.gender">
                  <option value="">Select</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Blood Group</label>
                <select class="form-select" v-model="form.blood_group">
                  <option value="">Select</option>
                  <option v-for="bg in bloodGroups" :key="bg" :value="bg">{{ bg }}</option>
                </select>
              </div>
              
              <div class="form-group">
                <label class="form-label">Address</label>
                <input
                  type="text"
                  class="form-control"
                  v-model="form.address"
                  placeholder="Your address"
                >
              </div>
            </div>
            
            <button
              type="submit"
              class="btn btn-primary btn-block"
              :disabled="isLoading"
            >
              <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
              {{ isLoading ? 'Creating account...' : 'Create account' }}
            </button>
          </form>
          
          <div class="auth-footer">
            <span>Already have an account?</span>
            <router-link to="/login">Sign in</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/api'

export default {
  name: 'Register',
  emits: ['show-toast'],
  setup(props, { emit }) {
    const router = useRouter()
    const showPassword = ref(false)
    const isLoading = ref(false)
    const error = ref('')
    const success = ref('')
    
    const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    
    const form = reactive({
      username: '',
      email: '',
      password: '',
      name: '',
      phone: '',
      date_of_birth: '',
      gender: '',
      blood_group: '',
      address: ''
    })

    const handleRegister = async () => {
      error.value = ''
      success.value = ''
      isLoading.value = true

      try {
        await authService.register(form)
        success.value = 'Account created successfully! Redirecting to login...'
        emit('show-toast', { type: 'success', message: 'Registration successful!' })
        
        setTimeout(() => {
          router.push('/login')
        }, 2000)
      } catch (err) {
        error.value = err.response?.data?.error || 'Registration failed. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    return {
      showPassword,
      isLoading,
      error,
      success,
      bloodGroups,
      form,
      handleRegister
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
  max-width: 480px;
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
  background: linear-gradient(135deg, #34c759, #30d158);
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  margin-bottom: 6px;
}

.required {
  color: #ff3b30;
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
  margin-top: 8px;
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

@media (max-width: 480px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
