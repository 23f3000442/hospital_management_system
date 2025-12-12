<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="mb-0">
        <i class="bi bi-clock-history me-2 text-primary"></i>
        Treatment History
      </h3>
      <button class="btn btn-outline-primary" @click="exportTreatments">
        <i class="bi bi-download me-2"></i>Export CSV
      </button>
    </div>

    <div v-if="treatmentHistory.length">
      <div class="card mb-3" v-for="record in treatmentHistory" :key="record.appointment_id">
        <div class="card-header bg-white d-flex justify-content-between align-items-center">
          <div>
            <h6 class="mb-0">
              <i class="bi bi-calendar me-2"></i>
              {{ formatDate(record.appointment_date) }} at {{ record.appointment_time }}
            </h6>
          </div>
          <span class="badge bg-primary">Dr. {{ record.doctor_name }}</span>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <h6 class="text-muted mb-2">Diagnosis</h6>
              <p>{{ record.diagnosis || 'Not provided' }}</p>
            </div>
            <div class="col-md-6">
              <h6 class="text-muted mb-2">Prescription</h6>
              <p>{{ record.prescription || 'Not provided' }}</p>
            </div>
          </div>
          <div class="row" v-if="record.notes || record.next_visit">
            <div class="col-md-6" v-if="record.notes">
              <h6 class="text-muted mb-2">Notes</h6>
              <p>{{ record.notes }}</p>
            </div>
            <div class="col-md-6" v-if="record.next_visit">
              <h6 class="text-muted mb-2">Next Visit</h6>
              <p><i class="bi bi-calendar-event me-1"></i>{{ formatDate(record.next_visit) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="card">
      <div class="card-body text-center py-5 text-muted">
        <i class="bi bi-clipboard-x display-4 mb-3"></i>
        <p>No treatment history available</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { patientService } from '@/services/api'

export default {
  name: 'TreatmentHistoryTab',
  emits: ['show-toast'],
  setup(props, { emit }) {
    const treatmentHistory = ref([])

    const loadHistory = async () => {
      try {
        treatmentHistory.value = await patientService.getTreatmentHistory()
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to load history' })
      }
    }

    const exportTreatments = async () => {
      try {
        const data = await patientService.exportTreatments()
        if (data.csv_data) {
          const blob = new Blob([data.csv_data], { type: 'text/csv' })
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = 'treatment_history.csv'
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          window.URL.revokeObjectURL(url)
          emit('show-toast', { type: 'success', message: 'Export downloaded!' })
        }
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to export' })
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    }

    onMounted(loadHistory)

    return {
      treatmentHistory,
      exportTreatments,
      formatDate
    }
  }
}
</script>

