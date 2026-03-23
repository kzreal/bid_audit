<template>
  <div class="tab-navigator border-b border-gray-200 flex-shrink-0">
    <nav class="flex">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="$emit('change-tab', tab.id)"
        :class="[
          'tab-item px-5 py-3 text-sm font-medium transition-all duration-200 relative',
          currentTab === tab.id
            ? 'text-vercel-blue'
            : 'text-gray-500 hover:text-black'
        ]"
      >
        {{ tab.label }}
        <!-- 选中指示条 -->
        <span
          v-if="currentTab === tab.id"
          class="absolute bottom-0 left-0 right-0 h-0.5 bg-vercel-blue"
        ></span>
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
.tab-item {
  border-bottom: 2px solid transparent;
}
</style>
