<template>
  <div>
    <h3 class="mb-4">
      <i class="bi bi-person me-2 text-primary"></i>
      My Profile
    </h3>

    <div class="row">
      <div class="col-md-8">
        <div class="card">
          <div class="card-body">
            <form @submit.prevent="updateProfile">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Full Name</label>
                  <input type="text" class="form-control" v-model="form.name">
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Phone</label>
                  <input type="tel" class="form-control" v-model="form.phone">
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Date of Birth</label>
                  <input type="date" class="form-control" v-model="form.date_of_birth">
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Gender</label>
                  <select class="form-select" v-model="form.gender">
                    <option value="">Select</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Blood Group</label>
                  <select class="form-select" v-model="form.blood_group">
                    <option value="">Select</option>
                    <option v-for="bg in bloodGroups" :key="bg" :value="bg">{{ bg }}</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Email</label>
                  <input type="email" class="form-control" :value="patientInfo.email" disabled>
                  <small class="text-muted">Email cannot be changed</small>
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Address</label>
                <textarea class="form-control" v-model="form.address" rows="2"></textarea>
              </div>
              <button type="submit" class="btn btn-gradient-primary">
                <i class="bi bi-check-lg me-2"></i>Update Profile
              </button>
            </form>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card">
          <div class="card-body text-center">
            <div class="avatar avatar-lg mx-auto mb-3" style="width: 100px; height: 100px; font-size: 2.5rem;">
              {{ patientInfo.name ? patientInfo.name.charAt(0) : 'P' }}
            </div>
            <h5>{{ patientInfo.name }}</h5>
            <p class="text-muted">{{ patientInfo.email }}</p>
            <hr>
            <div class="text-start">
              <p class="mb-2"><i class="bi bi-telephone me-2 text-primary"></i>{{ form.phone || 'Not set' }}</p>
              <p class="mb-2"><i class="bi bi-droplet me-2 text-danger"></i>{{ form.blood_group || 'Not set' }}</p>
              <p class="mb-0"><i class="bi bi-gender-ambiguous me-2 text-info"></i>{{ form.gender || 'Not set' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, onMounted } from 'vue'
import { patientService } from '@/services/api'

export default {
  name: 'ProfileTab',
  props: {
    patientInfo: { type: Object, default: () => ({}) }
  },
  emits: ['show-toast', 'refresh'],
  setup(props, { emit }) {
    const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

    const form = reactive({
      name: '',
      phone: '',
      date_of_birth: '',
      gender: '',
      blood_group: '',
      address: ''
    })

    const loadProfile = async () => {
      try {
        const profile = await patientService.getProfile()
        Object.assign(form, {
          name: profile.name || '',
          phone: profile.phone || '',
          date_of_birth: profile.date_of_birth || '',
          gender: profile.gender || '',
          blood_group: profile.blood_group || '',
          address: profile.address || ''
        })
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to load profile' })
      }
    }

    const updateProfile = async () => {
      try {
        await patientService.updateProfile(form)
        emit('show-toast', { type: 'success', message: 'Profile updated successfully!' })
        emit('refresh')
      } catch (error) {
        emit('show-toast', { type: 'danger', message: 'Failed to update profile' })
      }
    }

    onMounted(loadProfile)

    return {
      bloodGroups,
      form,
      updateProfile
    }
  }
}
</script>

