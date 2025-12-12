<template>
  <div>
    <h3 class="mb-4">
      <i class="bi bi-clock me-2 text-primary"></i>
      Set Availability
    </h3>

    <div class="row">
      <div class="col-md-6">
        <div class="card mb-4">
          <div class="card-header bg-white">
            <h5 class="mb-0">Add Availability Slot</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="saveAvailability">
              <div class="mb-3">
                <label class="form-label">Date <span class="text-danger">*</span></label>
                <input
                  type="date"
                  class="form-control"
                  v-model="form.date"
                  :min="minDate"
                  :max="maxDate"
                  required
                >
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Start Time <span class="text-danger">*</span></label>
                  <input type="time" class="form-control" v-model="form.start_time" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">End Time <span class="text-danger">*</span></label>
                  <input type="time" class="form-control" v-model="form.end_time" required>
                </div>
              </div>
              <div class="form-check mb-3">
                <input type="checkbox" class="form-check-input" id="isAvailable" v-model="form.is_available">
                <label class="form-check-label" for="isAvailable">Available for appointments</label>
              </div>
              <button type="submit" class="btn btn-gradient-primary w-100">
                <i class="bi bi-plus-lg me-2"></i>Save Availability
              </button>
            </form>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-white">
            <h5 class="mb-0">Current Availability (Next 7 Days)</h5>
          </div>
          <div class="card-body p-0">
            <div class="list-group list-group-flush">
              <div v-for="slot in availability" :key="slot.id" class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="mb-1">{{ formatDate(slot.date) }}</h6>
                    <small class="text-muted">
                      <i class="bi bi-clock me-1"></i>
                      {{ slot.start_time }} - {{ slot.end_time }}
                    </small>
                  </div>
                  <span :class="slot.is_available ? 'badge bg-success' : 'badge bg-danger'">
                    {{ slot.is_available ? 'Available' : 'Not Available' }}
                  </span>
                </div>
              </div>
              <div v-if="!availability.length" class="list-group-item text-center py-4 text-muted">
                No availability set
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { doctorService } from '@/services/api'

export default {
  name: 'AvailabilityTab',
  emits: ['show-toast'],
  setup(props, { emit }) {
    const availability = ref([])

    const form = reactive({
      date: '',
      start_time: '09:00',
      end_time: '17:00',
      is_available: true
    })

    const minDate = computed(() => new Date().toISOString().split('T')[0])
    const maxDate = computed(() => {
      const d = new Date()
      d.setDate(d.getDate() + 7)
      return d.toISOString().split('T')[0]
    })

    const loadAvailability = async () => {
      try {
        availability.value = await doctorService.getAvailability()
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to load availability' })
      }
    }

    const saveAvailability = async () => {
      try {
        await doctorService.setAvailability(form)
        emit('show-toast', { type: 'success', message: 'Availability saved!' })
        loadAvailability()
        form.date = ''
        form.start_time = '09:00'
        form.end_time = '17:00'
        form.is_available = true
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to save availability' })
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
    }

    onMounted(loadAvailability)

    return {
      availability,
      form,
      minDate,
      maxDate,
      saveAvailability,
      formatDate
    }
  }
}
</script>

