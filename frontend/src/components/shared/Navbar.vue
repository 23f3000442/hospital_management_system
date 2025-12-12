<template>
  <nav class="navbar navbar-expand-lg navbar-custom">
    <div class="container-fluid">
      <router-link class="navbar-brand" to="/">
        <i class="bi bi-heart-pulse-fill"></i>
        <span>MediCare</span>
      </router-link>
      
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto align-items-center">
          <li class="nav-item dropdown">
            <a 
              class="nav-link user-dropdown" 
              href="#" 
              role="button" 
              ref="dropdownToggle"
              @click.prevent="toggleDropdown"
            >
              <div class="user-avatar">
                {{ getUserInitial }}
              </div>
              <span class="user-name">{{ user?.username || 'User' }}</span>
              <i class="bi bi-chevron-down chevron" :class="{ open: dropdownOpen }"></i>
            </a>
            <ul class="dropdown-menu dropdown-menu-end" :class="{ show: dropdownOpen }">
              <li class="dropdown-header-item">
                <div class="dropdown-user-info">
                  <span class="dropdown-user-name">{{ user?.username }}</span>
                  <span class="dropdown-user-role">{{ user?.role }}</span>
                </div>
              </li>
              <li><hr class="dropdown-divider"></li>
              <li>
                <a class="dropdown-item" href="#" @click.prevent="handleLogout">
                  <i class="bi bi-box-arrow-right"></i>
                  Sign out
                </a>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

export default {
  name: 'Navbar',
  props: {
    user: {
      type: Object,
      default: null
    }
  },
  emits: ['logout'],
  setup(props, { emit }) {
    const dropdownOpen = ref(false)
    const dropdownToggle = ref(null)

    const getUserInitial = computed(() => {
      return props.user?.username?.charAt(0)?.toUpperCase() || 'U'
    })

    const toggleDropdown = () => {
      dropdownOpen.value = !dropdownOpen.value
    }

    const handleLogout = () => {
      dropdownOpen.value = false
      emit('logout')
    }

    const closeDropdown = (event) => {
      if (dropdownToggle.value && !dropdownToggle.value.contains(event.target)) {
        dropdownOpen.value = false
      }
    }

    onMounted(() => {
      document.addEventListener('click', closeDropdown)
    })

    onBeforeUnmount(() => {
      document.removeEventListener('click', closeDropdown)
    })

    return {
      dropdownOpen,
      dropdownToggle,
      getUserInitial,
      toggleDropdown,
      handleLogout
    }
  }
}
</script>

<style scoped>
.navbar-custom {
  height: 52px;
  display: flex;
  align-items: center;
}

.navbar-brand {
  gap: 8px;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px !important;
  border-radius: 6px;
  cursor: pointer;
}

.user-dropdown:hover {
  background: #f0f0f0;
}

.user-avatar {
  width: 28px;
  height: 28px;
  background: #5e5ce6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 12px;
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: #1a1a1a;
}

.chevron {
  font-size: 10px;
  color: #999;
  transition: transform 0.2s ease;
}

.chevron.open {
  transform: rotate(180deg);
}

.dropdown-menu.show {
  display: block;
}

.dropdown-header-item {
  padding: 12px;
}

.dropdown-user-info {
  display: flex;
  flex-direction: column;
}

.dropdown-user-name {
  font-weight: 600;
  font-size: 13px;
  color: #1a1a1a;
}

.dropdown-user-role {
  font-size: 12px;
  color: #999;
  text-transform: capitalize;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dropdown-item i {
  font-size: 14px;
}
</style>
