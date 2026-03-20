<template>
  <div class="space-y-4">
    <!-- 任务筛选 -->
    <div class="bg-white rounded-lg p-4 shadow-sm">
      <h3 class="font-medium text-gray-700 mb-3">任务筛选</h3>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="status in filterOptions"
          :key="status.value"
          @click="selectedFilter = status.value"
          :class="[
            'px-3 py-1 rounded-full text-sm transition-colors',
            selectedFilter === status.value
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          ]"
        >
          {{ status.label }}
          <span class="ml-1 text-xs">({{ getStatusCount(status.value) }})</span>
        </button>
      </div>
    </div>

    <!-- 任务统计 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg p-4 shadow-sm">
        <p class="text-sm text-gray-600">总任务数</p>
        <p class="text-2xl font-semibold text-gray-800">{{ taskStats.total }}</p>
      </div>
      <div class="bg-white rounded-lg p-4 shadow-sm">
        <p class="text-sm text-gray-600">已审核</p>
        <p class="text-2xl font-semibold text-green-600">{{ taskStats.reviewed }}</p>
      </div>
      <div class="bg-white rounded-lg p-4 shadow-sm">
        <p class="text-sm text-gray-600">通过</p>
        <p class="text-2xl font-semibold text-green-600">{{ taskStats.passed }}</p>
      </div>
      <div class="bg-white rounded-lg p-4 shadow-sm">
        <p class="text-sm text-gray-600">不通过</p>
        <p class="text-2xl font-semibold text-red-600">{{ taskStats.failed }}</p>
      </div>
    </div>

    <!-- 批量操作 -->
    <div v-if="hasUnreviewedTasks" class="bg-white rounded-lg p-4 shadow-sm">
      <h3 class="font-medium text-gray-700 mb-3">批量操作</h3>
      <div class="flex gap-2">
        <button
          @click="batchReview"
          :disabled="store.loading"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <span v-if="store.loading" class="inline-flex items-center">
            <span class="loading-dots mr-2">
              <span></span>
              <span></span>
              <span></span>
            </span>
            审核中...
          </span>
          <span v-else>批量审核未审核任务</span>
        </button>
        <button
          @click="clearReviews"
          class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
        >
          清除审核结果
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useAppStore } from '../stores/appStore'

const store = useAppStore()

// 筛选选项
const filterOptions = [
  { value: 'all', label: '全部' },
  { value: 'pending', label: '待审核' },
  { value: 'reviewed', label: '已审核' },
  { value: 'pass', label: '通过' },
  { value: 'fail', label: '不通过' },
  { value: 'pending-review', label: '待确认' }
]

const selectedFilter = ref('all')

// 计算属性
const taskStats = computed(() => store.taskStats)

const hasUnreviewedTasks = computed(() => {
  return store.tasks.some(task => !task.review)
})

// 获取状态数量
const getStatusCount = (status) => {
  switch (status) {
    case 'all':
      return store.tasks.length
    case 'pending':
      return store.tasks.filter(task => !task.review).length
    case 'reviewed':
      return store.tasks.filter(task => task.review).length
    case 'pass':
      return store.tasks.filter(task => task.review?.conclusion === '通过').length
    case 'fail':
      return store.tasks.filter(task => task.review?.conclusion === '不通过').length
    case 'pending-review':
      return store.tasks.filter(task => task.review?.conclusion === '待确认').length
    default:
      return 0
  }
}

// 批量审核
const batchReview = async () => {
  const unreviewedTasks = store.tasks.filter(task => !task.review)

  for (const task of unreviewedTasks) {
    try {
      await store.reviewTask(task.id, true)
    } catch (error) {
      console.error(`审核任务 ${task.id} 失败:`, error)
    }
  }
}

// 清除审核结果
const clearReviews = () => {
  if (confirm('确定要清除所有审核结果吗？')) {
    store.tasks.forEach(task => {
      store.updateTask(task.id, { review: null })
    })
  }
}
</script>

<style scoped>
/* 加载动画 - 三脉冲点 */
.loading-dots {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  border-radius: 50%;
  animation: loading-pulse 1.4s ease-in-out infinite both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loading-pulse {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>