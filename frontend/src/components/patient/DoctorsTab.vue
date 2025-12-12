<template>
  <div>
    <h3 class="mb-4">
      <i class="bi bi-person-badge me-2 text-primary"></i>
      Find Doctors
    </h3>

    <!-- Search & Filter -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <input
              type="text"
              class="form-control"
              placeholder="Search by name or specialization..."
              v-model="searchQuery"
              @input="debouncedSearch"
            >
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="selectedDepartment" @change="loadDoctors">
              <option value="">All Departments</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                {{ dept.name }}
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <input
              type="text"
              class="form-control"
              placeholder="Specialization..."
              v-model="specializationFilter"
              @input="debouncedSearch"
            >
          </div>
          <div class="col-md-2">
            <button class="btn btn-outline-secondary w-100" @click="clearFilters">
              <i class="bi bi-x-lg me-1"></i>Clear
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Doctors Grid -->
    <div class="row">
      <div class="col-md-6 col-lg-4 mb-4" v-for="doctor in doctors" :key="doctor.id">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="avatar avatar-lg me-3">
                {{ doctor.name.charAt(0) }}
              </div>
              <div>
                <h5 class="mb-0">Dr. {{ doctor.name }}</h5>
                <small class="text-muted">{{ doctor.specialization }}</small>
              </div>
            </div>
            <div class="mb-3">
              <p class="mb-1">
                <i class="bi bi-building me-2 text-primary"></i>
                {{ doctor.department_name }}
              </p>
              <p class="mb-1" v-if="doctor.experience_years">
                <i class="bi bi-award me-2 text-success"></i>
                {{ doctor.experience_years }} years experience
              </p>
              <p class="mb-0" v-if="doctor.qualification">
                <i class="bi bi-mortarboard me-2 text-info"></i>
                {{ doctor.qualification }}
              </p>
            </div>

            <!-- Availability -->
            <div v-if="doctor.availability?.length" class="mb-3">
              <small class="text-muted d-block mb-2">Available:</small>
              <div class="d-flex flex-wrap gap-1">
                <span v-for="slot in doctor.availability.slice(0, 3)" :key="slot.date" class="badge bg-light text-dark">
                  {{ formatShortDate(slot.date) }}
                </span>
                <span v-if="doctor.availability.length > 3" class="badge bg-secondary">
                  +{{ doctor.availability.length - 3 }} more
                </span>
              </div>
            </div>
            <div v-else class="mb-3">
              <small class="text-muted">Check availability when booking</small>
            </div>

            <button class="btn btn-gradient-primary w-100" @click="openBookingModal(doctor)">
              <i class="bi bi-calendar-plus me-2"></i>Book Appointment
            </button>
          </div>
        </div>
      </div>
      <div v-if="!doctors.length" class="col-12">
        <div class="card">
          <div class="card-body text-center py-5 text-muted">
            <i class="bi bi-person-x display-4 mb-3"></i>
            <p>No doctors found matching your criteria</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking Modal -->
    <div class="modal fade" id="bookingModal" tabindex="-1" ref="bookingModalRef">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header modal-header-custom">
            <h5 class="modal-title">
              <i class="bi bi-calendar-plus me-2"></i>Book Appointment
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="selectedDoctor" class="mb-4 p-3 bg-light rounded d-flex align-items-center">
              <div class="avatar me-3">
                {{ selectedDoctor.name.charAt(0) }}
              </div>
              <div>
                <h6 class="mb-0">Dr. {{ selectedDoctor.name }}</h6>
                <small class="text-muted">{{ selectedDoctor.specialization }}</small>
              </div>
            </div>

            <form @submit.prevent="bookAppointment">
              <div class="mb-3">
                <label class="form-label">Date <span class="text-danger">*</span></label>
                <input type="date" class="form-control" v-model="bookingForm.appointment_date" :min="minDate" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Time <span class="text-danger">*</span></label>
                <select class="form-select" v-model="bookingForm.appointment_time" required>
                  <option value="">Select time</option>
                  <option v-for="time in timeSlots" :key="time" :value="time">{{ time }}</option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Reason for Visit</label>
                <textarea class="form-control" v-model="bookingForm.reason" rows="3" placeholder="Describe your symptoms or reason for consultation..."></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-gradient-primary" @click="bookAppointment">
              <i class="bi bi-check-lg me-2"></i>Confirm Booking
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

export default {
  name: 'DoctorsTab',
  props: {
    departments: {
      type: Array,
      default: () => []
    }
  },
  emits: ['show-toast', 'refresh'],
  setup(props, { emit }) {
    const doctors = ref([])
    const searchQuery = ref('')
    const selectedDepartment = ref('')
    const specializationFilter = ref('')
    const selectedDoctor = ref(null)
    const bookingModalRef = ref(null)
    let bookingModal = null
    let searchTimeout = null

    const bookingForm = reactive({
      doctor_id: '',
      appointment_date: '',
      appointment_time: '',
      reason: ''
    })

    const timeSlots = [
      '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
      '12:00', '12:30', '14:00', '14:30', '15:00', '15:30',
      '16:00', '16:30', '17:00'
    ]

    const minDate = computed(() => new Date().toISOString().split('T')[0])

    const loadDoctors = async () => {
      try {
        const params = {}
        if (searchQuery.value) params.search = searchQuery.value
        if (selectedDepartment.value) params.department_id = selectedDepartment.value
        if (specializationFilter.value) params.specialization = specializationFilter.value
        doctors.value = await patientService.getDoctors(params)
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to load doctors' })
      }
    }

    const debouncedSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(loadDoctors, 300)
    }

    const clearFilters = () => {
      searchQuery.value = ''
      selectedDepartment.value = ''
      specializationFilter.value = ''
      loadDoctors()
    }

    const openBookingModal = (doctor) => {
      selectedDoctor.value = doctor
      Object.assign(bookingForm, {
        doctor_id: doctor.id,
        appointment_date: '',
        appointment_time: '',
        reason: ''
      })
      nextTick(() => {
        if (!bookingModal) bookingModal = new Modal(bookingModalRef.value)
        bookingModal.show()
      })
    }

    const bookAppointment = async () => {
      if (!bookingForm.appointment_date || !bookingForm.appointment_time) {
        emit('show-toast', { type: 'warning', message: 'Please select date and time' })
        return
      }
      try {
        await patientService.bookAppointment(bookingForm)
        emit('show-toast', { type: 'success', message: 'Appointment booked successfully!' })
        bookingModal.hide()
        emit('refresh')
      } catch (error) {
        emit('show-toast', { type: 'danger', message: error.response?.data?.error || 'Failed to book appointment' })
      }
    }

    const formatShortDate = (dateStr) => {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }

    onMounted(loadDoctors)

    return {
      doctors,
      searchQuery,
      selectedDepartment,
      specializationFilter,
      selectedDoctor,
      bookingModalRef,
      bookingForm,
      timeSlots,
      minDate,
      loadDoctors,
      debouncedSearch,
      clearFilters,
      openBookingModal,
      bookAppointment,
      formatShortDate
    }
  }
}
</script>

