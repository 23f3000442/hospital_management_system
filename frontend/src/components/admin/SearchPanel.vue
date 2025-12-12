<template>
  <div>
    <h3 class="mb-4">
      <i class="bi bi-search me-2 text-primary"></i>
      Search
    </h3>

    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-8">
            <input
              type="text"
              class="form-control form-control-lg"
              placeholder="Search for doctors or patients..."
              v-model="searchQuery"
              @keyup.enter="performSearch"
            >
          </div>
          <div class="col-md-2">
            <select class="form-select form-select-lg" v-model="searchType">
              <option value="all">All</option>
              <option value="doctor">Doctors</option>
              <option value="patient">Patients</option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn btn-gradient-primary btn-lg w-100" @click="performSearch">
              <i class="bi bi-search"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Search Results -->
    <div v-if="results" class="row">
      <div class="col-md-6 mb-4" v-if="searchType !== 'patient'">
        <div class="card h-100">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0"><i class="bi bi-person-badge me-2"></i>Doctors</h5>
          </div>
          <div class="card-body">
            <div v-if="results.doctors?.length">
              <div class="list-group list-group-flush">
                <div v-for="doc in results.doctors" :key="doc.id" class="list-group-item">
                  <div class="d-flex justify-content-between">
                    <div>
                      <h6 class="mb-1">{{ doc.name }}</h6>
                      <small class="text-muted">{{ doc.specialization }} - {{ doc.department_name }}</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="text-muted text-center py-3">No doctors found</p>
          </div>
        </div>
      </div>
      <div class="col-md-6 mb-4" v-if="searchType !== 'doctor'">
        <div class="card h-100">
          <div class="card-header bg-success text-white">
            <h5 class="mb-0"><i class="bi bi-people me-2"></i>Patients</h5>
          </div>
          <div class="card-body">
            <div v-if="results.patients?.length">
              <div class="list-group list-group-flush">
                <div v-for="pat in results.patients" :key="pat.id" class="list-group-item">
                  <div class="d-flex justify-content-between">
                    <div>
                      <h6 class="mb-1">{{ pat.name }}</h6>
                      <small class="text-muted">{{ pat.phone }} - {{ pat.email }}</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="text-muted text-center py-3">No patients found</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { adminService } from '@/services/api'

export default {
  name: 'SearchPanel',
  emits: ['show-toast'],
  setup(props, { emit }) {
    const searchQuery = ref('')
    const searchType = ref('all')
    const results = ref(null)

    const performSearch = async () => {
      if (!searchQuery.value.trim()) return
      try {
        results.value = await adminService.search(searchQuery.value, searchType.value)
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Search failed' })
      }
    }

    return {
      searchQuery,
      searchType,
      results,
      performSearch
    }
  }
}
</script>

