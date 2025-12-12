<template>
  <div class="dashboard-layout">
    <!-- Sidebar -->
    <aside class="dashboard-sidebar">
      <Sidebar :items="sidebarItems" :activeTab="activeTab" @tab-change="activeTab = $event" />
    </aside>

    <!-- Main Content -->
    <main class="dashboard-main">
      <!-- Dashboard Tab -->
      <div v-if="activeTab === 'dashboard'" class="fade-in">
        <div class="page-header">
          <h1>Dashboard</h1>
          <p>Overview of hospital statistics</p>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid">
          <StatCard title="Total Doctors" :value="stats.total_doctors || 0" icon="person-badge" color="purple" />
          <StatCard title="Total Patients" :value="stats.total_patients || 0" icon="people" color="green" />
          <StatCard title="Total Appointments" :value="stats.total_appointments || 0" icon="calendar-check" color="orange" />
          <StatCard title="Upcoming" :value="stats.upcoming_appointments || 0" icon="clock" color="blue" />
        </div>

        <!-- Recent Appointments -->
        <div class="content-section">
          <div class="section-header">
            <h2>Recent Appointments</h2>
          </div>
          <div class="card">
            <div class="table-container">
              <table class="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Patient</th>
                    <th>Doctor</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="apt in stats.recent_appointments" :key="apt.id">
                    <td class="text-muted">#{{ apt.id }}</td>
                    <td>{{ apt.patient_name }}</td>
                    <td>{{ apt.doctor_name }}</td>
                    <td>{{ formatDate(apt.date) }}</td>
                    <td>{{ apt.time }}</td>
                    <td>
                      <span class="status-badge" :class="`status-${apt.status.toLowerCase()}`">
                        {{ apt.status }}
                      </span>
                    </td>
                  </tr>
                  <tr v-if="!stats.recent_appointments?.length">
                    <td colspan="6" class="empty-state">
                      No recent appointments
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Doctors Tab -->
      <div v-if="activeTab === 'doctors'" class="fade-in">
        <DoctorManagement 
          :departments="departments" 
          @show-toast="$emit('show-toast', $event)"
          @refresh-stats="loadDashboard"
        />
      </div>

      <!-- Patients Tab -->
      <div v-if="activeTab === 'patients'" class="fade-in">
        <PatientManagement @show-toast="$emit('show-toast', $event)" />
      </div>

      <!-- Appointments Tab -->
      <div v-if="activeTab === 'appointments'" class="fade-in">
        <AppointmentList @show-toast="$emit('show-toast', $event)" />
      </div>

      <!-- Search Tab -->
      <div v-if="activeTab === 'search'" class="fade-in">
        <SearchPanel @show-toast="$emit('show-toast', $event)" />
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { adminService } from '@/services/api'
import Sidebar from '@/components/shared/Sidebar.vue'
import StatCard from '@/components/shared/StatCard.vue'
import DoctorManagement from '@/components/admin/DoctorManagement.vue'
import PatientManagement from '@/components/admin/PatientManagement.vue'
import AppointmentList from '@/components/admin/AppointmentList.vue'
import SearchPanel from '@/components/admin/SearchPanel.vue'

export default {
  name: 'AdminDashboard',
  components: {
    Sidebar,
    StatCard,
    DoctorManagement,
    PatientManagement,
    AppointmentList,
    SearchPanel
  },
  emits: ['show-toast', 'set-loading'],
  setup(props, { emit }) {
    const activeTab = ref('dashboard')
    const stats = ref({})
    const departments = ref([])

    const sidebarItems = [
      { id: 'dashboard', name: 'Dashboard', icon: 'grid-1x2' },
      { id: 'doctors', name: 'Doctors', icon: 'person-badge' },
      { id: 'patients', name: 'Patients', icon: 'people' },
      { id: 'appointments', name: 'Appointments', icon: 'calendar3' },
      { id: 'search', name: 'Search', icon: 'search' }
    ]

    const loadDashboard = async () => {
      try {
        emit('set-loading', true)
        stats.value = await adminService.getDashboard()
      } catch (error) {
        emit('show-toast', { type: 'danger', message: error.response?.data?.error || 'Failed to load dashboard' })
      } finally {
        emit('set-loading', false)
      }
    }

    const loadDepartments = async () => {
      try {
        departments.value = await adminService.getDepartments()
      } catch (error) {
        console.error('Failed to load departments:', error)
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

    onMounted(() => {
      loadDashboard()
      loadDepartments()
    })

    return {
      activeTab,
      stats,
      departments,
      sidebarItems,
      loadDashboard,
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
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 4px;
  color: #1a1a1a;
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

.content-section {
  margin-bottom: 32px;
}

.section-header {
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0;
}

.table-container {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th {
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

.table td {
  padding: 14px 16px;
  font-size: 13px;
  color: #1a1a1a;
  border-bottom: 1px solid #e8e8e8;
}

.table tbody tr:hover {
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

.status-completed {
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
}

.status-cancelled {
  background: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
}

.empty-state {
  text-align: center;
  padding: 40px 16px !important;
  color: #999;
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
