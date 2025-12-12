<template>
  <div class="stat-card" :class="color">
    <div class="stat-header">
      <span class="stat-label">{{ title }}</span>
      <div class="stat-icon" :class="`icon-${color}`">
        <i :class="`bi bi-${icon}`"></i>
      </div>
    </div>
    <div class="stat-value">{{ value }}</div>
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    icon: {
      type: String,
      default: 'graph-up'
    },
    color: {
      type: String,
      default: 'purple'
    }
  }
}
</script>

<style scoped>
.stat-card {
  transition: all 0.15s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.stat-label {
  font-size: 12px;
  font-weight: 500;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.icon-purple {
  background: rgba(94, 92, 230, 0.1);
  color: #5e5ce6;
}

.icon-green {
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
}

.icon-orange {
  background: rgba(255, 159, 10, 0.1);
  color: #ff9f0a;
}

.icon-blue {
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1;
}
</style>
