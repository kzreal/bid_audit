<template>
  <div>
    <!-- 空状态 -->
    <div v-if="filteredTasks.length === 0" class="p-8 text-center text-gray-500">
      <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
      </svg>
      <p>{{ tasks.length === 0 ? '暂无任务' : '没有符合条件的任务' }}</p>
      <p class="text-sm mt-2">{{ tasks.length === 0 ? '请在左侧输入招标信息和投标文件后点击"开始分析"' : '请调整筛选条件' }}</p>
    </div>

    <!-- 任务列表 -->
    <transition-group name="fade" tag="div" class="p-4 space-y-3">
      <div v-for="task in filteredTasks" :key="task.id"
           :class="['task-card', { active: selectedTaskId === task.id }]"
           @click="selectTask(task)">
        <!-- 任务标题和描述合并为一行 -->
        <div class="mb-3">
          <h3 class="font-medium text-gray-800 text-sm">
            任务{{ task.id }}: {{ task.description }}
          </h3>
        </div>

        <!-- 状态 -->
        <div class="flex justify-between items-center">
          <div class="flex items-center">
            <span v-if="!task.review" class="text-xs text-gray-500">
              <span class="inline-block w-2 h-2 bg-gray-400 rounded-full mr-1"></span>
              待审核
            </span>
            <span v-else :class="['text-xs', getStatusClass(task.review.status)]">
              <span class="inline-block w-2 h-2 rounded-full mr-1" :class="getStatusBg(task.review.status)"></span>
              {{ task.review.status }}
            </span>
          </div>

          <!-- 审核中状态 -->
          <span v-if="store.loading && store.selectedTaskId === task.id && !task.review" class="text-xs text-blue-600 flex items-center">
            <span class="loading-dots mr-2">
              <span></span>
              <span></span>
              <span></span>
            </span>
            审核中...
          </span>
          <span v-else-if="task.review" class="text-xs text-gray-400">
            已审核
          </span>
        </div>
      </div>
    </transition-group>

    <!-- 加载状态 -->
    <div v-if="false" class="p-4">
      <div class="animate-pulse">
        <div class="bg-gray-200 rounded-lg p-4 mb-3"></div>
        <div class="bg-gray-200 rounded-lg p-4 mb-3"></div>
        <div class="bg-gray-200 rounded-lg p-4"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue'
import { useAppStore } from '../stores/appStore'

const store = useAppStore()

const props = defineProps({
  tasks: {
    type: Array,
    required: true
  },
  selectedTaskId: {
    type: Number,
    default: null
  },
  selectedFilter: {
    type: String,
    default: 'all'
  }
})

const emit = defineEmits(['select-task'])

const selectTask = (task) => {
  emit('select-task', task.id)
}

const getStatusClass = (status) => {
  const statusMap = {
    '通过': 'text-green-600',
    '不通过': 'text-red-600',
    '待确认': 'text-yellow-600'
  }
  return statusMap[status] || 'text-gray-600'
}

const getStatusBg = (status) => {
  const statusMap = {
    '通过': 'bg-green-500',
    '不通过': 'bg-red-500',
    '待确认': 'bg-yellow-500'
  }
  return statusMap[status] || 'bg-gray-400'
}

// 筛选后的任务
const filteredTasks = computed(() => {
  if (!props.selectedFilter || props.selectedFilter === 'all') {
    return props.tasks
  }

  switch (props.selectedFilter) {
    case 'pending':
      return props.tasks.filter(task => !task.review)
    case 'reviewed':
      return props.tasks.filter(task => task.review)
    case 'pass':
      return props.tasks.filter(task => task.review?.status === '通过')
    case 'fail':
      return props.tasks.filter(task => task.review?.status === '不通过')
    case 'pending-review':
      return props.tasks.filter(task => task.review?.status === '待确认')
    default:
      return props.tasks
  }
})

// 任务统计
const taskStats = computed(() => {
  const total = props.tasks.length
  const reviewed = props.tasks.filter(task => task.review).length
  const passed = props.tasks.filter(task => task.review?.status === '通过').length
  const failed = props.tasks.filter(task => task.review?.status === '不通过').length
  const pending = props.tasks.filter(task => task.review?.status === '待确认').length

  return { total, reviewed, passed, failed, pending }
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

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