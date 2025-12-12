<template>
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <aside class="dashboard-sidebar">
      <Sidebar :items="sidebarItems" :activeTab="activeTab" @tab-change="handleTabChange" />
    </aside>

    <!-- Main Content -->
    <main class="dashboard-main">
      <!-- Dashboard Tab -->
      <div v-if="activeTab === 'dashboard'" class="fade-in">
        <div class="page-header">
          <h1>Welcome, {{ patientInfo.name }}!</h1>
          <p>Manage your appointments and health records</p>
        </div>

        <!-- Quick Stats -->
        <div class="stats-grid stats-grid-3">
          <StatCard title="Upcoming Appointments" :value="upcomingAppointments.length" icon="calendar-check" color="purple" />
          <StatCard title="Available Departments" :value="departments.length" icon="building" color="green" />
          <div class="quick-action-card" @click="activeTab = 'doctors'">
            <div class="quick-action-icon">
              <i class="bi bi-plus"></i>
            </div>
            <div class="quick-action-text">
              <span class="quick-action-label">Book Appointment</span>
              <span class="quick-action-hint">Find a doctor</span>
            </div>
          </div>
        </div>

        <!-- Departments -->
        <div class="content-section">
          <div class="section-header">
            <h2>Departments</h2>
          </div>
          <div class="departments-grid">
            <div class="dept-card" v-for="dept in departments" :key="dept.id" @click="filterByDepartment(dept)">
              <div class="dept-icon">
                <i :class="`bi bi-${getDeptIcon(dept.name)}`"></i>
              </div>
              <div class="dept-info">
                <span class="dept-name">{{ dept.name }}</span>
                <span class="dept-count">{{ dept.doctors_count }} doctors</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming Appointments -->
        <div class="content-section">
          <div class="section-header">
            <h2>Upcoming Appointments</h2>
          </div>
          <div class="card">
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Doctor</th>
                    <th>Specialization</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="apt in upcomingAppointments" :key="apt.id">
                    <td>Dr. {{ apt.doctor_name }}</td>
                    <td class="text-muted">{{ apt.specialization }}</td>
                    <td>{{ formatDate(apt.appointment_date) }}</td>
                    <td>{{ apt.appointment_time }}</td>
                    <td>
                      <span class="status-badge status-booked">{{ apt.status }}</span>
                    </td>
                    <td>
                      <div class="action-buttons">
                        <button class="btn-action btn-action-primary" @click="openRescheduleModal(apt)" title="Reschedule">
                          <i class="bi bi-calendar"></i>
                        </button>
                        <button class="btn-action btn-action-danger" @click="cancelAppointment(apt)" title="Cancel">
                          <i class="bi bi-x-lg"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="!upcomingAppointments.length">
                    <td colspan="6" class="empty-state">
                      <i class="bi bi-calendar-x empty-icon"></i>
                      <p>No upcoming appointments</p>
                      <a href="#" @click.prevent="activeTab = 'doctors'">Book your first appointment</a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Find Doctors Tab -->
      <div v-if="activeTab === 'doctors'" class="fade-in">
        <DoctorsTab
          :departments="departments"
          @show-toast="$emit('show-toast', $event)"
          @refresh="loadDashboard"
        />
      </div>

      <!-- My Appointments Tab -->
      <div v-if="activeTab === 'appointments'" class="fade-in">
        <MyAppointmentsTab
          :upcomingAppointments="upcomingAppointments"
          :pastAppointments="pastAppointments"
          @show-toast="$emit('show-toast', $event)"
          @refresh="loadDashboard"
        />
      </div>

      <!-- Treatment History Tab -->
      <div v-if="activeTab === 'history'" class="fade-in">
        <TreatmentHistoryTab @show-toast="$emit('show-toast', $event)" />
      </div>

      <!-- Profile Tab -->
      <div v-if="activeTab === 'profile'" class="fade-in">
        <ProfileTab
          :patientInfo="patientInfo"
          @show-toast="$emit('show-toast', $event)"
          @refresh="loadDashboard"
        />
      </div>
    </main>

    <!-- Reschedule Modal -->
    <div class="modal fade" id="rescheduleModal" tabindex="-1" ref="rescheduleModalRef">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Reschedule Appointment</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedAppointment" class="modal-info-box">
              <strong>Dr. {{ selectedAppointment.doctor_name }}</strong><br>
              <span class="text-muted">Current: {{ formatDate(selectedAppointment.appointment_date) }} at {{ selectedAppointment.appointment_time }}</span>
            </div>

            <form @submit.prevent="rescheduleAppointment">
              <div class="form-group">
                <label class="form-label">New Date <span class="required">*</span></label>
                <input type="date" class="form-control" v-model="rescheduleForm.appointment_date" :min="minDate" required>
              </div>
              <div class="form-group">
                <label class="form-label">New Time <span class="required">*</span></label>
                <select class="form-select" v-model="rescheduleForm.appointment_time" required>
                  <option value="">Select time</option>
                  <option v-for="time in timeSlots" :key="time" :value="time">{{ time }}</option>
                </select>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="rescheduleAppointment">
              Confirm
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { patientService } from '@/services/api'
import { Modal } from 'bootstrap'
import Sidebar from '@/components/shared/Sidebar.vue'
import StatCard from '@/components/shared/StatCard.vue'
import DoctorsTab from '@/components/patient/DoctorsTab.vue'
import MyAppointmentsTab from '@/components/patient/MyAppointmentsTab.vue'
import TreatmentHistoryTab from '@/components/patient/TreatmentHistoryTab.vue'
import ProfileTab from '@/components/patient/ProfileTab.vue'

export default {
  name: 'PatientDashboard',
  components: {
    Sidebar,
    StatCard,
    DoctorsTab,
    MyAppointmentsTab,
    TreatmentHistoryTab,
    ProfileTab
  },
  emits: ['show-toast', 'set-loading'],
  setup(props, { emit }) {
    const activeTab = ref('dashboard')
    const patientInfo = ref({})
    const departments = ref([])
    const upcomingAppointments = ref([])
    const pastAppointments = ref([])
    const selectedAppointment = ref(null)
    const rescheduleModalRef = ref(null)
    let rescheduleModal = null

    const rescheduleForm = reactive({
      appointment_date: '',
      appointment_time: ''
    })

    const timeSlots = [
      '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
      '12:00', '12:30', '14:00', '14:30', '15:00', '15:30',
      '16:00', '16:30', '17:00'
    ]

    const sidebarItems = [
      { id: 'dashboard', name: 'Dashboard', icon: 'grid-1x2' },
      { id: 'doctors', name: 'Find Doctors', icon: 'person-badge' },
      { id: 'appointments', name: 'Appointments', icon: 'calendar3' },
      { id: 'history', name: 'History', icon: 'clock-history' },
      { id: 'profile', name: 'Profile', icon: 'person' }
    ]

    const minDate = computed(() => new Date().toISOString().split('T')[0])

    const loadDashboard = async () => {
      try {
        emit('set-loading', true)
        const data = await patientService.getDashboard()
        patientInfo.value = data.patient_info || {}
        departments.value = data.departments || []
        upcomingAppointments.value = data.upcoming_appointments || []
        pastAppointments.value = data.past_appointments || []
      } catch (error) {
        emit('show-toast', { type: 'danger', message: error.response?.data?.error || 'Failed to load dashboard' })
      } finally {
        emit('set-loading', false)
      }
    }

    const handleTabChange = (tab) => {
      activeTab.value = tab
    }

    const filterByDepartment = (dept) => {
      activeTab.value = 'doctors'
    }

    const getDeptIcon = (name) => {
      const icons = {
        'Cardiology': 'heart-pulse',
        'Neurology': 'lightning',
        'Orthopedics': 'person-walking',
        'Pediatrics': 'emoji-smile',
        'Dermatology': 'person',
        'General Medicine': 'plus-circle'
      }
      return icons[name] || 'hospital'
    }

    const openRescheduleModal = (apt) => {
      selectedAppointment.value = apt
      rescheduleForm.appointment_date = ''
      rescheduleForm.appointment_time = ''
      nextTick(() => {
        if (!rescheduleModal) rescheduleModal = new Modal(rescheduleModalRef.value)
        rescheduleModal.show()
      })
    }

    const rescheduleAppointment = async () => {
      if (!rescheduleForm.appointment_date || !rescheduleForm.appointment_time) {
        emit('show-toast', { type: 'warning', message: 'Please select new date and time' })
        return
      }
      try {
        await patientService.rescheduleAppointment(selectedAppointment.value.id, rescheduleForm)
        emit('show-toast', { type: 'success', message: 'Appointment rescheduled successfully!' })
        rescheduleModal.hide()
        loadDashboard()
      } catch (error) {
        emit('show-toast', { type: 'danger', message: error.response?.data?.error || 'Failed to reschedule' })
      }
    }

    const cancelAppointment = async (apt) => {
      if (!confirm(`Cancel your appointment with Dr. ${apt.doctor_name}?`)) return
      try {
        await patientService.cancelAppointment(apt.id)
        emit('show-toast', { type: 'success', message: 'Appointment cancelled' })
        loadDashboard()
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to cancel appointment' })
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    }

    onMounted(loadDashboard)

    return {
      activeTab,
      patientInfo,
      departments,
      upcomingAppointments,
      pastAppointments,
      selectedAppointment,
      rescheduleModalRef,
      rescheduleForm,
      timeSlots,
      sidebarItems,
      minDate,
      loadDashboard,
      handleTabChange,
      filterByDepartment,
      getDeptIcon,
      openRescheduleModal,
      rescheduleAppointment,
      cancelAppointment,
      formatDate
    }
  }
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: calc(100vh - 52px);
}

.dashboard-sidebar {
  width: 220px;
  flex-shrink: 0;
  background: #fbfbfb;
  border-right: 1px solid #e8e8e8;
}

.dashboard-main {
  flex: 1;
  padding: 32px;
  background: #fafafa;
  overflow-y: auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 4px;
}

.page-header p {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stats-grid-3 {
  grid-template-columns: repeat(3, 1fr);
}

.quick-action-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.quick-action-card:hover {
  border-color: #5e5ce6;
  box-shadow: 0 4px 12px rgba(94, 92, 230, 0.1);
}

.quick-action-icon {
  width: 40px;
  height: 40px;
  background: rgba(94, 92, 230, 0.1);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #5e5ce6;
  font-size: 20px;
}

.quick-action-text {
  display: flex;
  flex-direction: column;
}

.quick-action-label {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.quick-action-hint {
  font-size: 12px;
  color: #999;
}

.content-section {
  margin-bottom: 32px;
}

.section-header {
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.departments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.dept-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.dept-card:hover {
  border-color: #d4d4d4;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.dept-icon {
  width: 36px;
  height: 36px;
  background: #f5f5f5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 16px;
}

.dept-info {
  display: flex;
  flex-direction: column;
}

.dept-name {
  font-size: 13px;
  font-weight: 500;
  color: #1a1a1a;
}

.dept-count {
  font-size: 12px;
  color: #999;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 500;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: #f5f5f5;
  border-bottom: 1px solid #e8e8e8;
}

.data-table td {
  padding: 14px 16px;
  font-size: 13px;
  color: #1a1a1a;
  border-bottom: 1px solid #e8e8e8;
}

.data-table tbody tr:hover {
  background: #f9f9f9;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.status-booked {
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
}

.action-buttons {
  display: flex;
  gap: 6px;
}

.btn-action {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s ease;
}

.btn-action-primary {
  background: rgba(94, 92, 230, 0.1);
  color: #5e5ce6;
}

.btn-action-primary:hover {
  background: #5e5ce6;
  color: white;
}

.btn-action-danger {
  background: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
}

.btn-action-danger:hover {
  background: #ff3b30;
  color: white;
}

.empty-state {
  text-align: center;
  padding: 48px 16px !important;
  color: #999;
}

.empty-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-state p {
  margin: 0 0 8px;
}

.empty-state a {
  color: #5e5ce6;
  text-decoration: none;
}

.empty-state a:hover {
  text-decoration: underline;
}

.modal-info-box {
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
}

.form-group {
  margin-bottom: 16px;
}

.required {
  color: #ff3b30;
}

@media (max-width: 1200px) {
  .stats-grid, .stats-grid-3 {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-layout {
    flex-direction: column;
  }
  
  .dashboard-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e8e8e8;
  }
  
  .dashboard-main {
    padding: 20px;
  }
  
  .stats-grid, .stats-grid-3 {
    grid-template-columns: 1fr;
  }
}
</style>
