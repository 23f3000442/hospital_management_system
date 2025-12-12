import axios from 'axios'

const API_BASE_URL = 'http://localhost:5001/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authService = {
  async login(username, password) {
    const response = await api.post('/auth/login', { username, password })
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
    }
    return response.data
  },

  async register(userData) {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me')
    return response.data
  },

  logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  },

  getUser() {
    const user = localStorage.getItem('user')
    return user ? JSON.parse(user) : null
  },

  isAuthenticated() {
    return !!localStorage.getItem('token')
  }
}

export const adminService = {
  async getDashboard() {
    const response = await api.get('/admin/dashboard')
    return response.data
  },

  async getDepartments() {
    const response = await api.get('/admin/departments')
    return response.data
  },

  async getDoctors(search = '') {
    const response = await api.get('/admin/doctors', { params: { search } })
    return response.data
  },

  async createDoctor(doctorData) {
    const response = await api.post('/admin/doctors', doctorData)
    return response.data
  },

  async updateDoctor(doctorId, doctorData) {
    const response = await api.put(`/admin/doctors/${doctorId}`, doctorData)
    return response.data
  },

  async deleteDoctor(doctorId) {
    const response = await api.delete(`/admin/doctors/${doctorId}`)
    return response.data
  },

  async getPatients(search = '') {
    const response = await api.get('/admin/patients', { params: { search } })
    return response.data
  },

  async updatePatient(patientId, patientData) {
    const response = await api.put(`/admin/patients/${patientId}`, patientData)
    return response.data
  },

  async deletePatient(patientId) {
    const response = await api.delete(`/admin/patients/${patientId}`)
    return response.data
  },

  async getAppointments(status = '') {
    const response = await api.get('/admin/appointments', { params: { status } })
    return response.data
  },

  async search(query, type = 'all') {
    const response = await api.get('/admin/search', { params: { q: query, type } })
    return response.data
  }
}

export const doctorService = {
  async getDashboard() {
    const response = await api.get('/doctor/dashboard')
    return response.data
  },

  async getAppointments(status = '') {
    const response = await api.get('/doctor/appointments', { params: { status } })
    return response.data
  },

  async completeAppointment(appointmentId, treatmentData) {
    const response = await api.put(`/doctor/appointments/${appointmentId}/complete`, treatmentData)
    return response.data
  },

  async cancelAppointment(appointmentId) {
    const response = await api.put(`/doctor/appointments/${appointmentId}/cancel`)
    return response.data
  },

  async getPatients() {
    const response = await api.get('/doctor/patients')
    return response.data
  },

  async getPatientHistory(patientId) {
    const response = await api.get(`/doctor/patients/${patientId}/history`)
    return response.data
  },

  async getAvailability() {
    const response = await api.get('/doctor/availability')
    return response.data
  },

  async setAvailability(availabilityData) {
    const response = await api.post('/doctor/availability', availabilityData)
    return response.data
  }
}

export const patientService = {
  async getDashboard() {
    const response = await api.get('/patient/dashboard')
    return response.data
  },

  async getProfile() {
    const response = await api.get('/patient/profile')
    return response.data
  },

  async updateProfile(profileData) {
    const response = await api.put('/patient/profile', profileData)
    return response.data
  },

  async getDoctors(params = {}) {
    const response = await api.get('/patient/doctors', { params })
    return response.data
  },

  async getDepartments() {
    const response = await api.get('/patient/departments')
    return response.data
  },

  async bookAppointment(appointmentData) {
    const response = await api.post('/patient/appointments', appointmentData)
    return response.data
  },

  async rescheduleAppointment(appointmentId, appointmentData) {
    const response = await api.put(`/patient/appointments/${appointmentId}`, appointmentData)
    return response.data
  },

  async cancelAppointment(appointmentId) {
    const response = await api.delete(`/patient/appointments/${appointmentId}`)
    return response.data
  },

  async getTreatmentHistory() {
    const response = await api.get('/patient/treatment-history')
    return response.data
  },

  async exportTreatments() {
    const response = await api.get('/patient/export-treatments')
    return response.data
  },

  async exportTreatmentsAsync() {
    const response = await api.post('/patient/export-treatments/async')
    return response.data
  },

  async getExportStatus(taskId) {
    const response = await api.get(`/patient/export-treatments/status/${taskId}`)
    return response.data
  }
}

export default api
