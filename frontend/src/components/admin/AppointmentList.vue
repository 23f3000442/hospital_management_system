<template>
  <div>
    <h3 class="mb-4">
      <i class="bi bi-calendar-check me-2 text-primary"></i>
      All Appointments
    </h3>

    <!-- Filter -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row">
          <div class="col-md-4">
            <select class="form-select" v-model="statusFilter" @change="loadAppointments">
              <option value="">All Status</option>
              <option value="Booked">Booked</option>
              <option value="Completed">Completed</option>
              <option value="Cancelled">Cancelled</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Appointments Table -->
    <div class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Date</th>
                <th>Time</th>
                <th>Reason</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="apt in appointments" :key="apt.id">
                <td>#{{ apt.id }}</td>
                <td>{{ apt.patient_name }}</td>
                <td>{{ apt.doctor_name }}</td>
                <td>{{ formatDate(apt.appointment_date) }}</td>
                <td>{{ apt.appointment_time }}</td>
                <td>{{ apt.reason || '-' }}</td>
                <td>
                  <span class="badge-status" :class="`badge-${apt.status.toLowerCase()}`">
                    {{ apt.status }}
                  </span>
                </td>
              </tr>
              <tr v-if="!appointments.length">
                <td colspan="7" class="text-center py-4 text-muted">
                  No appointments found
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { adminService } from '@/services/api'

export default {
  name: 'AppointmentList',
  emits: ['show-toast'],
  setup(props, { emit }) {
    const appointments = ref([])
    const statusFilter = ref('')

    const loadAppointments = async () => {
      try {
        appointments.value = await adminService.getAppointments(statusFilter.value)
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to load appointments' })
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    onMounted(loadAppointments)

    return {
      appointments,
      statusFilter,
      loadAppointments,
      formatDate
    }
  }
}
</script>

