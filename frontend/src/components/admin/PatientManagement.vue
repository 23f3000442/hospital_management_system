<template>
  <div>
    <h3 class="mb-4">
      <i class="bi bi-people me-2 text-primary"></i>
      Manage Patients
    </h3>

    <!-- Search -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="input-group">
          <span class="input-group-text bg-light">
            <i class="bi bi-search"></i>
          </span>
          <input
            type="text"
            class="form-control"
            placeholder="Search by name or phone..."
            v-model="searchQuery"
            @input="debouncedSearch"
          >
        </div>
      </div>
    </div>

    <!-- Patients Table -->
    <div class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Gender</th>
                <th>Blood Group</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="patient in patients" :key="patient.id">
                <td>#{{ patient.id }}</td>
                <td>{{ patient.name }}</td>
                <td>{{ patient.email }}</td>
                <td>{{ patient.phone || '-' }}</td>
                <td>{{ patient.gender || '-' }}</td>
                <td>{{ patient.blood_group || '-' }}</td>
                <td>
                  <button class="btn btn-sm btn-outline-primary me-1" @click="openModal(patient)">
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-danger" @click="deletePatient(patient)">
                    <i class="bi bi-trash"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="!patients.length">
                <td colspan="7" class="text-center py-4 text-muted">
                  No patients found
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Patient Modal -->
    <div class="modal fade" id="patientModal" tabindex="-1" ref="modalRef">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header modal-header-custom">
            <h5 class="modal-title">
              <i class="bi bi-person me-2"></i>Edit Patient
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="savePatient">
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input type="text" class="form-control" v-model="form.name">
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input type="email" class="form-control" v-model="form.email">
              </div>
              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input type="tel" class="form-control" v-model="form.phone">
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Gender</label>
                  <select class="form-select" v-model="form.gender">
                    <option value="">Select</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Blood Group</label>
                  <select class="form-select" v-model="form.blood_group">
                    <option value="">Select</option>
                    <option v-for="bg in bloodGroups" :key="bg" :value="bg">{{ bg }}</option>
                  </select>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Address</label>
                <textarea class="form-control" v-model="form.address" rows="2"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-gradient-primary" @click="savePatient">
              <i class="bi bi-check-lg me-2"></i>Update
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { adminService } from '@/services/api'
import { Modal } from 'bootstrap'

export default {
  name: 'PatientManagement',
  emits: ['show-toast'],
  setup(props, { emit }) {
    const patients = ref([])
    const searchQuery = ref('')
    const editingPatient = ref(null)
    const modalRef = ref(null)
    let modal = null
    let searchTimeout = null

    const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

    const form = reactive({
      name: '',
      email: '',
      phone: '',
      gender: '',
      blood_group: '',
      address: ''
    })

    const loadPatients = async () => {
      try {
        patients.value = await adminService.getPatients(searchQuery.value)
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to load patients' })
      }
    }

    const debouncedSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(loadPatients, 300)
    }

    const openModal = (patient) => {
      editingPatient.value = patient
      Object.assign(form, {
        name: patient.name,
        email: patient.email,
        phone: patient.phone || '',
        gender: patient.gender || '',
        blood_group: patient.blood_group || '',
        address: patient.address || ''
      })
      nextTick(() => {
        if (!modal) {
          modal = new Modal(modalRef.value)
        }
        modal.show()
      })
    }

    const savePatient = async () => {
      try {
        await adminService.updatePatient(editingPatient.value.id, form)
        emit('show-toast', { type: 'success', message: 'Patient updated successfully!' })
        modal.hide()
        loadPatients()
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to update patient' })
      }
    }

    const deletePatient = async (patient) => {
      if (!confirm(`Are you sure you want to deactivate ${patient.name}?`)) return
      try {
        await adminService.deletePatient(patient.id)
        emit('show-toast', { type: 'success', message: 'Patient deactivated successfully!' })
        loadPatients()
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to deactivate patient' })
      }
    }

    onMounted(loadPatients)

    return {
      patients,
      searchQuery,
      modalRef,
      form,
      bloodGroups,
      loadPatients,
      debouncedSearch,
      openModal,
      savePatient,
      deletePatient
    }
  }
}
</script>

