<template>
  <div>
    <h3 class="mb-4">
      <i class="bi bi-people me-2 text-primary"></i>
      My Patients
    </h3>

    <div class="row">
      <div class="col-md-4" v-for="patient in patients" :key="patient.id">
        <div class="card mb-4">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="avatar me-3">
                {{ patient.name.charAt(0) }}
              </div>
              <div>
                <h5 class="mb-0">{{ patient.name }}</h5>
                <small class="text-muted">{{ patient.email }}</small>
              </div>
            </div>
            <div class="mb-3">
              <p class="mb-1"><i class="bi bi-telephone me-2 text-muted"></i>{{ patient.phone || '-' }}</p>
              <p class="mb-1"><i class="bi bi-droplet me-2 text-muted"></i>{{ patient.blood_group || '-' }}</p>
              <p class="mb-0"><i class="bi bi-calendar-event me-2 text-muted"></i>{{ patient.total_appointments }} appointments</p>
            </div>
            <button class="btn btn-outline-primary btn-sm w-100" @click="viewHistory(patient)">
              <i class="bi bi-clock-history me-1"></i>View History
            </button>
          </div>
        </div>
      </div>
      <div v-if="!patients.length" class="col-12">
        <div class="card">
          <div class="card-body text-center py-5 text-muted">
            <i class="bi bi-people display-4 mb-3"></i>
            <p>No patients assigned yet</p>
          </div>
        </div>
      </div>
    </div>

    <!-- History Modal -->
    <div class="modal fade" id="historyModal" tabindex="-1" ref="historyModalRef">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header modal-header-custom">
            <h5 class="modal-title">Patient History</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div v-if="patientHistory" class="mb-4">
              <h5>{{ patientHistory.patient.name }}</h5>
              <p class="text-muted">
                <i class="bi bi-telephone me-2"></i>{{ patientHistory.patient.phone || '-' }}
                <span class="mx-2">|</span>
                <i class="bi bi-droplet me-2"></i>{{ patientHistory.patient.blood_group || '-' }}
              </p>
            </div>

            <div v-if="patientHistory?.history?.length" class="accordion" id="historyAccordion">
              <div class="accordion-item" v-for="(record, index) in patientHistory.history" :key="record.appointment_id">
                <h2 class="accordion-header">
                  <button
                    class="accordion-button"
                    :class="{ collapsed: index !== 0 }"
                    type="button"
                    data-bs-toggle="collapse"
                    :data-bs-target="`#collapse${record.appointment_id}`"
                  >
                    {{ formatDate(record.appointment_date) }} at {{ record.appointment_time }}
                  </button>
                </h2>
                <div
                  :id="`collapse${record.appointment_id}`"
                  class="accordion-collapse collapse"
                  :class="{ show: index === 0 }"
                >
                  <div class="accordion-body">
                    <p><strong>Diagnosis:</strong> {{ record.diagnosis || '-' }}</p>
                    <p><strong>Prescription:</strong> {{ record.prescription || '-' }}</p>
                    <p><strong>Notes:</strong> {{ record.notes || '-' }}</p>
                    <p><strong>Next Visit:</strong> {{ record.next_visit ? formatDate(record.next_visit) : '-' }}</p>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-4 text-muted">
              <i class="bi bi-clipboard-x display-4 mb-3"></i>
              <p>No treatment history available</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { doctorService } from '@/services/api'
import { Modal } from 'bootstrap'

export default {
  name: 'PatientsTab',
  emits: ['show-toast'],
  setup(props, { emit }) {
    const patients = ref([])
    const patientHistory = ref(null)
    const historyModalRef = ref(null)
    let historyModal = null

    const loadPatients = async () => {
      try {
        patients.value = await doctorService.getPatients()
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to load patients' })
      }
    }

    const viewHistory = async (patient) => {
      try {
        patientHistory.value = await doctorService.getPatientHistory(patient.id)
        nextTick(() => {
          if (!historyModal) historyModal = new Modal(historyModalRef.value)
          historyModal.show()
        })
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to load history' })
      }
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    }

    onMounted(loadPatients)

    return {
      patients,
      patientHistory,
      historyModalRef,
      viewHistory,
      formatDate
    }
  }
}
</script>

