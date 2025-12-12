<template>
  <div>
    <h3 class="mb-4">
      <i class="bi bi-calendar-check me-2 text-primary"></i>
      My Appointments
    </h3>

    <!-- Upcoming -->
    <h5 class="mb-3">Upcoming Appointments</h5>
    <div class="card mb-4">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>Doctor</th>
                <th>Specialization</th>
                <th>Date</th>
                <th>Time</th>
                <th>Reason</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="apt in upcomingAppointments" :key="apt.id">
                <td>Dr. {{ apt.doctor_name }}</td>
                <td>{{ apt.specialization }}</td>
                <td>{{ formatDate(apt.appointment_date) }}</td>
                <td>{{ apt.appointment_time }}</td>
                <td>{{ apt.reason || '-' }}</td>
                <td>
                  <button class="btn btn-sm btn-outline-primary me-1" @click="openRescheduleModal(apt)">
                    <i class="bi bi-calendar"></i> Reschedule
                  </button>
                  <button class="btn btn-sm btn-outline-danger" @click="cancelAppointment(apt)">
                    <i class="bi bi-x-lg"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="!upcomingAppointments.length">
                <td colspan="6" class="text-center py-4 text-muted">
                  No upcoming appointments
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Past Appointments -->
    <h5 class="mb-3">Past Appointments</h5>
    <div class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>Doctor</th>
                <th>Specialization</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="apt in pastAppointments" :key="apt.id">
                <td>Dr. {{ apt.doctor_name }}</td>
                <td>{{ apt.specialization }}</td>
                <td>{{ formatDate(apt.appointment_date) }}</td>
                <td>{{ apt.appointment_time }}</td>
                <td>
                  <span class="badge-status" :class="`badge-${apt.status.toLowerCase()}`">
                    {{ apt.status }}
                  </span>
                </td>
              </tr>
              <tr v-if="!pastAppointments.length">
                <td colspan="5" class="text-center py-4 text-muted">
                  No past appointments
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Reschedule Modal -->
    <div class="modal fade" id="rescheduleAptModal" tabindex="-1" ref="modalRef">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header modal-header-custom">
            <h5 class="modal-title">Reschedule Appointment</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedAppointment" class="mb-4 p-3 bg-light rounded">
              <h6>Dr. {{ selectedAppointment.doctor_name }}</h6>
              <p class="mb-0 text-muted">Current: {{ formatDate(selectedAppointment.appointment_date) }} at {{ selectedAppointment.appointment_time }}</p>
            </div>
            <form @submit.prevent="rescheduleAppointment">
              <div class="mb-3">
                <label class="form-label">New Date <span class="text-danger">*</span></label>
                <input type="date" class="form-control" v-model="rescheduleForm.appointment_date" :min="minDate" required>
              </div>
              <div class="mb-3">
                <label class="form-label">New Time <span class="text-danger">*</span></label>
                <select class="form-select" v-model="rescheduleForm.appointment_time" required>
                  <option value="">Select time</option>
                  <option v-for="time in timeSlots" :key="time" :value="time">{{ time }}</option>
                </select>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-gradient-primary" @click="rescheduleAppointment">
              <i class="bi bi-check-lg me-2"></i>Reschedule
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, nextTick } from 'vue'
import { patientService } from '@/services/api'
import { Modal } from 'bootstrap'

export default {
  name: 'MyAppointmentsTab',
  props: {
    upcomingAppointments: { type: Array, default: () => [] },
    pastAppointments: { type: Array, default: () => [] }
  },
  emits: ['show-toast', 'refresh'],
  setup(props, { emit }) {
    const selectedAppointment = ref(null)
    const modalRef = ref(null)
    let modal = null

    const rescheduleForm = reactive({
      appointment_date: '',
      appointment_time: ''
    })

    const timeSlots = [
      '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
      '12:00', '12:30', '14:00', '14:30', '15:00', '15:30',
      '16:00', '16:30', '17:00'
    ]

    const minDate = computed(() => new Date().toISOString().split('T')[0])

    const openRescheduleModal = (apt) => {
      selectedAppointment.value = apt
      rescheduleForm.appointment_date = ''
      rescheduleForm.appointment_time = ''
      nextTick(() => {
        if (!modal) modal = new Modal(modalRef.value)
        modal.show()
      })
    }

    const rescheduleAppointment = async () => {
      if (!rescheduleForm.appointment_date || !rescheduleForm.appointment_time) {
        emit('show-toast', { type: 'warning', message: 'Please select date and time' })
        return
      }
      try {
        await patientService.rescheduleAppointment(selectedAppointment.value.id, rescheduleForm)
        emit('show-toast', { type: 'success', message: 'Appointment rescheduled!' })
        modal.hide()
        emit('refresh')
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to reschedule' })
      }
    }

    const cancelAppointment = async (apt) => {
      if (!confirm(`Cancel appointment with Dr. ${apt.doctor_name}?`)) return
      try {
        await patientService.cancelAppointment(apt.id)
        emit('show-toast', { type: 'success', message: 'Appointment cancelled' })
        emit('refresh')
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to cancel' })
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    }

    return {
      selectedAppointment,
      modalRef,
      rescheduleForm,
      timeSlots,
      minDate,
      openRescheduleModal,
      rescheduleAppointment,
      cancelAppointment,
      formatDate
    }
  }
}
</script>

