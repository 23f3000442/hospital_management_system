<template>
  <div class="sidebar">
    <div class="sidebar-section">
      <div class="sidebar-section-title">Menu</div>
      <nav class="sidebar-nav">
        <a
          v-for="item in items"
          :key="item.name"
          href="#"
          class="sidebar-link"
          :class="{ active: activeTab === item.id }"
          @click.prevent="$emit('tab-change', item.id)"
        >
          <i :class="`bi bi-${item.icon}`"></i>
          <span>{{ item.name }}</span>
        </a>
      </nav>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Sidebar',
  props: {
    items: {
      type: Array,
      required: true
    },
    activeTab: {
      type: String,
      default: ''
    }
  },
  emits: ['tab-change']
}
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
}

.sidebar-section {
  padding: 8px 0;
}

.sidebar-section-title {
  padding: 8px 12px;
  font-size: 11px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 6px;
  color: #666;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.1s ease;
}

.sidebar-link:hover {
  background: #f0f0f0;
  color: #1a1a1a;
  text-decoration: none;
}

.sidebar-link.active {
  background: #ebebeb;
  color: #1a1a1a;
}

.sidebar-link i {
  font-size: 15px;
  width: 18px;
  text-align: center;
  opacity: 0.6;
}

.sidebar-link:hover i,
.sidebar-link.active i {
  opacity: 1;
}
</style>
