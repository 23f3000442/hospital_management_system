<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="mb-0">
        <i class="bi bi-person-badge me-2 text-primary"></i>
        Manage Doctors
      </h3>
      <button class="btn btn-gradient-primary" @click="openModal()">
        <i class="bi bi-plus-lg me-2"></i>Add Doctor
      </button>
    </div>

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
            placeholder="Search by name or specialization..."
            v-model="searchQuery"
            @input="debouncedSearch"
          >
        </div>
      </div>
    </div>

    <!-- Doctors Table -->
    <div class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Specialization</th>
                <th>Department</th>
                <th>Phone</th>
                <th>Experience</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doctor in doctors" :key="doctor.id">
                <td>#{{ doctor.id }}</td>
                <td>
                  <div class="d-flex align-items-center">
                    <div class="avatar me-3" style="width: 40px; height: 40px; font-size: 1rem;">
                      {{ doctor.name.charAt(0) }}
                    </div>
                    {{ doctor.name }}
                  </div>
                </td>
                <td>{{ doctor.specialization }}</td>
                <td>{{ doctor.department_name }}</td>
                <td>{{ doctor.phone || '-' }}</td>
                <td>{{ doctor.experience_years ? `${doctor.experience_years} years` : '-' }}</td>
                <td>
                  <button class="btn btn-sm btn-outline-primary me-1" @click="openModal(doctor)">
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button class="btn btn-sm btn-outline-danger" @click="deleteDoctor(doctor)">
                    <i class="bi bi-trash"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="!doctors.length">
                <td colspan="7" class="text-center py-4 text-muted">
                  No doctors found
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Doctor Modal -->
    <div class="modal fade" id="doctorModal" tabindex="-1" ref="modalRef">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header modal-header-custom">
            <h5 class="modal-title">
              <i class="bi bi-person-badge me-2"></i>
              {{ editingDoctor ? 'Edit Doctor' : 'Add New Doctor' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveDoctor">
              <div class="row" v-if="!editingDoctor">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Username <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" v-model="form.username" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Password <span class="text-danger">*</span></label>
                  <input type="password" class="form-control" v-model="form.password" required>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Full Name <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" v-model="form.name" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Email <span class="text-danger">*</span></label>
                  <input type="email" class="form-control" v-model="form.email" required>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Specialization <span class="text-danger">*</span></label>
                  <input type="text" class="form-control" v-model="form.specialization" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Department <span class="text-danger">*</span></label>
                  <select class="form-select" v-model="form.department_id" required>
                    <option value="">Select Department</option>
                    <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                      {{ dept.name }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="row">
                <div class="col-md-4 mb-3">
                  <label class="form-label">Phone</label>
                  <input type="tel" class="form-control" v-model="form.phone">
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label">Experience (Years)</label>
                  <input type="number" class="form-control" v-model="form.experience_years" min="0">
                </div>
                <div class="col-md-4 mb-3">
                  <label class="form-label">Qualification</label>
                  <input type="text" class="form-control" v-model="form.qualification">
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-gradient-primary" @click="saveDoctor">
              <i class="bi bi-check-lg me-2"></i>
              {{ editingDoctor ? 'Update' : 'Create' }}
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
  name: 'DoctorManagement',
  props: {
    departments: {
      type: Array,
      default: () => []
    }
  },
  emits: ['show-toast', 'refresh-stats'],
  setup(props, { emit }) {
    const doctors = ref([])
    const searchQuery = ref('')
    const editingDoctor = ref(null)
    const modalRef = ref(null)
    let modal = null
    let searchTimeout = null

    const form = reactive({
      username: '',
      password: '',
      email: '',
      name: '',
      specialization: '',
      department_id: '',
      phone: '',
      experience_years: '',
      qualification: ''
    })

    const loadDoctors = async () => {
      try {
        doctors.value = await adminService.getDoctors(searchQuery.value)
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to load doctors' })
      }
    }

    const debouncedSearch = () => {
      clearTimeout(searchTimeout)
      searchTimeout = setTimeout(loadDoctors, 300)
    }

    const openModal = (doctor = null) => {
      editingDoctor.value = doctor
      if (doctor) {
        Object.assign(form, {
          name: doctor.name,
          email: '',
          specialization: doctor.specialization,
          department_id: doctor.department_id,
          phone: doctor.phone || '',
          experience_years: doctor.experience_years || '',
          qualification: doctor.qualification || ''
        })
      } else {
        Object.assign(form, {
          username: '',
          password: '',
          email: '',
          name: '',
          specialization: '',
          department_id: '',
          phone: '',
          experience_years: '',
          qualification: ''
        })
      }
      nextTick(() => {
        if (!modal) {
          modal = new Modal(modalRef.value)
        }
        modal.show()
      })
    }

    const saveDoctor = async () => {
      try {
        if (editingDoctor.value) {
          await adminService.updateDoctor(editingDoctor.value.id, form)
          emit('show-toast', { type: 'success', message: 'Doctor updated successfully!' })
        } else {
          await adminService.createDoctor(form)
          emit('show-toast', { type: 'success', message: 'Doctor created successfully!' })
        }
        modal.hide()
        loadDoctors()
        emit('refresh-stats')
      } catch (error) {
        emit('show-toast', { type: 'danger', message: error.response?.data?.error || 'Operation failed' })
      }
    }

    const deleteDoctor = async (doctor) => {
      if (!confirm(`Are you sure you want to deactivate Dr. ${doctor.name}?`)) return
      try {
        await adminService.deleteDoctor(doctor.id)
        emit('show-toast', { type: 'success', message: 'Doctor deactivated successfully!' })
        loadDoctors()
        emit('refresh-stats')
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to deactivate doctor' })
      }
    }

    onMounted(loadDoctors)

    return {
      doctors,
      searchQuery,
      editingDoctor,
      modalRef,
      form,
      loadDoctors,
      debouncedSearch,
      openModal,
      saveDoctor,
      deleteDoctor
    }
  }
}
</script>

