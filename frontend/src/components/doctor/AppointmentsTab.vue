<template>
  <div>
    <h3 class="mb-4">
      <i class="bi bi-calendar-check me-2 text-primary"></i>
      My Appointments
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
                <th>Phone</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th>Treatment</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="apt in appointments" :key="apt.id">
                <td>#{{ apt.id }}</td>
                <td>{{ apt.patient_name }}</td>
                <td>{{ apt.patient_phone || '-' }}</td>
                <td>{{ formatDate(apt.appointment_date) }}</td>
                <td>{{ apt.appointment_time }}</td>
                <td>
                  <span class="badge-status" :class="`badge-${apt.status.toLowerCase()}`">
                    {{ apt.status }}
                  </span>
                </td>
                <td>
                  <span v-if="apt.has_treatment" class="badge bg-success">
                    <i class="bi bi-check"></i> Added
                  </span>
                  <span v-else class="badge bg-secondary">Pending</span>
                </td>
                <td>
                  <button
                    v-if="apt.status === 'Booked'"
                    class="btn btn-sm btn-success me-1"
                    @click="openCompleteModal(apt)"
                  >
                    <i class="bi bi-check-lg"></i>
                  </button>
                  <button
                    v-if="apt.status === 'Booked'"
                    class="btn btn-sm btn-danger"
                    @click="cancelAppointment(apt)"
                  >
                    <i class="bi bi-x-lg"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="!appointments.length">
                <td colspan="8" class="text-center py-4 text-muted">
                  No appointments found
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Complete Modal -->
    <div class="modal fade" id="aptCompleteModal" tabindex="-1" ref="modalRef">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header modal-header-custom">
            <h5 class="modal-title">Complete Appointment</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="completeAppointment">
              <div class="mb-3">
                <label class="form-label">Diagnosis <span class="text-danger">*</span></label>
                <textarea class="form-control" v-model="treatmentForm.diagnosis" rows="3" required></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Prescription</label>
                <textarea class="form-control" v-model="treatmentForm.prescription" rows="3"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Notes</label>
                <textarea class="form-control" v-model="treatmentForm.notes" rows="2"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Next Visit</label>
                <input type="date" class="form-control" v-model="treatmentForm.next_visit">
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-gradient-success" @click="completeAppointment">
              <i class="bi bi-check-lg me-2"></i>Complete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { doctorService } from '@/services/api'
import { Modal } from 'bootstrap'

export default {
  name: 'AppointmentsTab',
  emits: ['show-toast', 'refresh'],
  setup(props, { emit }) {
    const appointments = ref([])
    const statusFilter = ref('')
    const selectedAppointment = ref(null)
    const modalRef = ref(null)
    let modal = null

    const treatmentForm = reactive({
      diagnosis: '',
      prescription: '',
      notes: '',
      next_visit: ''
    })

    const loadAppointments = async () => {
      try {
        appointments.value = await doctorService.getAppointments(statusFilter.value)
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to load appointments' })
      }
    }

    const openCompleteModal = (apt) => {
      selectedAppointment.value = apt
      Object.assign(treatmentForm, { diagnosis: '', prescription: '', notes: '', next_visit: '' })
      nextTick(() => {
        if (!modal) modal = new Modal(modalRef.value)
        modal.show()
      })
    }

    const completeAppointment = async () => {
      if (!treatmentForm.diagnosis) {
        emit('show-toast', { type: 'warning', message: 'Please enter diagnosis' })
        return
      }
      try {
        await doctorService.completeAppointment(selectedAppointment.value.id, treatmentForm)
        emit('show-toast', { type: 'success', message: 'Appointment completed!' })
        modal.hide()
        loadAppointments()
        emit('refresh')
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to complete appointment' })
      }
    }

    const cancelAppointment = async (apt) => {
      if (!confirm(`Cancel appointment with ${apt.patient_name}?`)) return
      try {
        await doctorService.cancelAppointment(apt.id)
        emit('show-toast', { type: 'success', message: 'Appointment cancelled' })
        loadAppointments()
        emit('refresh')
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to cancel' })
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    }

    onMounted(loadAppointments)

    return {
      appointments,
      statusFilter,
      modalRef,
      treatmentForm,
      loadAppointments,
      openCompleteModal,
      completeAppointment,
      cancelAppointment,
      formatDate
    }
  }
}
</script>

