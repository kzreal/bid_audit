<template>
  <div>
    <!-- 空状态 -->
    <div v-if="tasks.length === 0" class="p-8 text-center text-gray-500">
      <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
      </svg>
      <p>暂无任务</p>
      <p class="text-sm mt-2">请在左侧输入招标信息和投标文件后点击"开始分析"</p>
    </div>

    <!-- 任务列表 -->
    <div v-else class="p-4 space-y-3">
      <transition-group name="fade" tag="div">
        <div
          v-for="task in tasks"
          :key="task.id"
          :class="['task-card', { active: selectedTaskId === task.id }]"
          @click="selectTask(task)"
        >
          <div class="flex justify-between items-start mb-2">
            <div class="flex-1 pr-4">
              <h3 class="font-medium text-gray-800">{{ task.title }}</h3>
              <p class="text-xs text-gray-400 mt-1">任务 {{ task.id }}</p>
            </div>
            <span class="text-xs text-gray-400 flex-shrink-0">
              {{ formatDate(task.createdAt) }}
            </span>
          </div>

          <p class="text-sm text-gray-600 mb-3 line-clamp-2">{{ task.description }}</p>

          <!-- 状态 -->
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
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/appStore'

const props = defineProps({
  tasks: {
    type: Array,
    required: true
  },
  selectedTaskId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['select-task'])

const store = useAppStore()

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

const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleDateString('zh-CN')
}

const selectTask = (task) => {
  emit('select-task', task.id)
}
</script>

<style scoped>
.task-card {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  background: white;
  transition: all 0.2s;
  cursor: pointer;
}

.task-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.task-card.active {
  border-color: #2563eb;
  background: #eff6ff;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
