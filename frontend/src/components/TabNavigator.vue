<template>
  <div class="tab-navigator flex-shrink-0">
    <nav class="tab-nav">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="$emit('change-tab', tab.id)"
        :class="[
          'tab-item',
          currentTab === tab.id ? 'tab-active' : 'tab-inactive'
        ]"
      >
        <span class="tab-label">{{ tab.label }}</span>
        <!-- 激活态底部发光条 -->
        <span v-if="currentTab === tab.id" class="tab-glow"></span>
      </button>
    </nav>
  </div>
</template>

<script setup>
defineProps({
  tabs: {
    type: Array,
    required: true
  },
  currentTab: {
    type: String,
    required: true
  }
})

defineEmits(['change-tab'])
</script>

<style scoped>
.tab-navigator {
  border-bottom: 1px solid #e5e7eb;
  background: #fff;
  position: relative;
  overflow: hidden;
}

.tab-nav {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  position: relative;
}

.tab-item {
  position: relative;
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.01em;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
  background: transparent;
  text-align: center;
  overflow: hidden;
}

/* ---- 非激活态 ---- */
.tab-inactive {
  color: #999;
}

.tab-inactive:hover {
  color: #333;
  background: rgba(0, 0, 0, 0.02);
}

/* ---- 激活态 ---- */
.tab-active {
  color: #0070f3;
  font-weight: 600;
  background: linear-gradient(
    180deg,
    rgba(0, 112, 243, 0.06) 0%,
    rgba(0, 112, 243, 0) 100%
  );
}

/* 底部发光条 */
.tab-glow {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #0070f3, transparent);
  border-radius: 2px 2px 0 0;
  animation: glow-in 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

@keyframes glow-in {
  from {
    width: 0%;
    opacity: 0;
  }
  to {
    width: 60%;
    opacity: 1;
  }
}
</style>
