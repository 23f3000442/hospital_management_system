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
          <h1>Dashboard</h1>
          <p>Welcome back, Dr. {{ doctorInfo.name }}</p>
        </div>

        <!-- Doctor Info -->
        <div class="info-card">
          <div class="info-card-avatar">
            {{ doctorInfo.name ? doctorInfo.name.charAt(0) : 'D' }}
          </div>
          <div class="info-card-content">
            <h3>Dr. {{ doctorInfo.name }}</h3>
            <div class="info-card-meta">
              <span><i class="bi bi-stethoscope"></i> {{ doctorInfo.specialization }}</span>
              <span><i class="bi bi-building"></i> {{ doctorInfo.department }}</span>
            </div>
          </div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
          <StatCard title="Today's Appointments" :value="dashboardStats.today_appointments || 0" icon="calendar-day" color="purple" />
          <StatCard title="Upcoming (7 days)" :value="dashboardStats.upcoming_appointments || 0" icon="calendar-week" color="green" />
          <StatCard title="Total Patients" :value="dashboardStats.total_patients || 0" icon="people" color="orange" />
          <StatCard title="Completed" :value="dashboardStats.completed_appointments || 0" icon="check-circle" color="blue" />
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
                    <th>Patient</th>
                    <th>Phone</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Reason</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="apt in upcomingAppointments" :key="apt.id">
                    <td>
                      <div class="user-cell">
                        <div class="user-avatar-sm">{{ apt.patient_name.charAt(0) }}</div>
                        <span>{{ apt.patient_name }}</span>
                      </div>
                    </td>
                    <td class="text-muted">{{ apt.patient_phone || '-' }}</td>
                    <td>{{ formatDate(apt.appointment_date) }}</td>
                    <td>{{ apt.appointment_time }}</td>
                    <td class="text-muted">{{ apt.reason || '-' }}</td>
                    <td>
                      <div class="action-buttons">
                        <button class="btn-action btn-action-success" @click="openCompleteModal(apt)" title="Complete">
                          <i class="bi bi-check-lg"></i>
                        </button>
                        <button class="btn-action btn-action-danger" @click="cancelAppointment(apt)" title="Cancel">
                          <i class="bi bi-x-lg"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="!upcomingAppointments.length">
                    <td colspan="6" class="empty-state">
                      No upcoming appointments
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Appointments Tab -->
      <div v-if="activeTab === 'appointments'" class="fade-in">
        <AppointmentsTab 
          @show-toast="$emit('show-toast', $event)" 
          @refresh="loadDashboard"
        />
      </div>

      <!-- Patients Tab -->
      <div v-if="activeTab === 'patients'" class="fade-in">
        <PatientsTab @show-toast="$emit('show-toast', $event)" />
      </div>

      <!-- Availability Tab -->
      <div v-if="activeTab === 'availability'" class="fade-in">
        <AvailabilityTab @show-toast="$emit('show-toast', $event)" />
      </div>
    </main>

    <!-- Complete Appointment Modal -->
    <div class="modal fade" id="completeModal" tabindex="-1" ref="completeModalRef">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Complete Appointment</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedAppointment" class="modal-info-box">
              <strong>Patient:</strong> {{ selectedAppointment.patient_name }}<br>
              <span class="text-muted">{{ formatDate(selectedAppointment.appointment_date) }} at {{ selectedAppointment.appointment_time }}</span>
            </div>
            <form @submit.prevent="completeAppointment">
              <div class="form-group">
                <label class="form-label">Diagnosis <span class="required">*</span></label>
                <textarea class="form-control" v-model="treatmentForm.diagnosis" rows="3" required placeholder="Enter diagnosis details..."></textarea>
              </div>
              <div class="form-group">
                <label class="form-label">Prescription</label>
                <textarea class="form-control" v-model="treatmentForm.prescription" rows="3" placeholder="Enter prescribed medications..."></textarea>
              </div>
              <div class="form-group">
                <label class="form-label">Notes</label>
                <textarea class="form-control" v-model="treatmentForm.notes" rows="2" placeholder="Additional notes..."></textarea>
              </div>
              <div class="form-group">
                <label class="form-label">Next Visit</label>
                <input type="date" class="form-control" v-model="treatmentForm.next_visit" :min="minDate">
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="completeAppointment">
              Complete & Save
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { doctorService } from '@/services/api'
import { Modal } from 'bootstrap'
import Sidebar from '@/components/shared/Sidebar.vue'
import StatCard from '@/components/shared/StatCard.vue'
import AppointmentsTab from '@/components/doctor/AppointmentsTab.vue'
import PatientsTab from '@/components/doctor/PatientsTab.vue'
import AvailabilityTab from '@/components/doctor/AvailabilityTab.vue'

export default {
  name: 'DoctorDashboard',
  components: {
    Sidebar,
    StatCard,
    AppointmentsTab,
    PatientsTab,
    AvailabilityTab
  },
  emits: ['show-toast', 'set-loading'],
  setup(props, { emit }) {
    const activeTab = ref('dashboard')
    const doctorInfo = ref({})
    const dashboardStats = ref({})
    const upcomingAppointments = ref([])
    const selectedAppointment = ref(null)
    const completeModalRef = ref(null)
    let completeModal = null

    const treatmentForm = reactive({
      diagnosis: '',
      prescription: '',
      notes: '',
      next_visit: ''
    })

    const sidebarItems = [
      { id: 'dashboard', name: 'Dashboard', icon: 'grid-1x2' },
      { id: 'appointments', name: 'Appointments', icon: 'calendar3' },
      { id: 'patients', name: 'My Patients', icon: 'people' },
      { id: 'availability', name: 'Availability', icon: 'clock' }
    ]

    const minDate = computed(() => new Date().toISOString().split('T')[0])

    const loadDashboard = async () => {
      try {
        emit('set-loading', true)
        const data = await doctorService.getDashboard()
        doctorInfo.value = data.doctor_info || {}
        dashboardStats.value = data.stats || {}
        upcomingAppointments.value = data.upcoming_appointments || []
      } catch (error) {
        emit('show-toast', { type: 'danger', message: error.response?.data?.error || 'Failed to load dashboard' })
      } finally {
        emit('set-loading', false)
      }
    }

    const handleTabChange = (tab) => {
      activeTab.value = tab
    }

    const openCompleteModal = (appointment) => {
      selectedAppointment.value = appointment
      Object.assign(treatmentForm, {
        diagnosis: '',
        prescription: '',
        notes: '',
        next_visit: ''
      })
      nextTick(() => {
        if (!completeModal) {
          completeModal = new Modal(completeModalRef.value)
        }
        completeModal.show()
      })
    }

    const completeAppointment = async () => {
      if (!treatmentForm.diagnosis) {
        emit('show-toast', { type: 'warning', message: 'Please enter diagnosis' })
        return
      }
      try {
        await doctorService.completeAppointment(selectedAppointment.value.id, treatmentForm)
        emit('show-toast', { type: 'success', message: 'Appointment completed successfully!' })
        completeModal.hide()
        loadDashboard()
      } catch (error) {
        emit('show-toast', { type: 'danger', message: error.response?.data?.error || 'Failed to complete appointment' })
      }
    }

    const cancelAppointment = async (appointment) => {
      if (!confirm(`Cancel appointment with ${appointment.patient_name}?`)) return
      try {
        await doctorService.cancelAppointment(appointment.id)
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
      doctorInfo,
      dashboardStats,
      upcomingAppointments,
      selectedAppointment,
      completeModalRef,
      treatmentForm,
      sidebarItems,
      minDate,
      loadDashboard,
      handleTabChange,
      openCompleteModal,
      completeAppointment,
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

.info-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 12px;
  margin-bottom: 24px;
}

.info-card-avatar {
  width: 56px;
  height: 56px;
  background: #5e5ce6;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 20px;
}

.info-card-content h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px;
}

.info-card-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #666;
}

.info-card-meta i {
  margin-right: 4px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
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

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar-sm {
  width: 28px;
  height: 28px;
  background: #5e5ce6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 11px;
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

.btn-action-success {
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
}

.btn-action-success:hover {
  background: #34c759;
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
  padding: 40px 16px !important;
  color: #999;
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
  .stats-grid {
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
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
