<template>
  <div>
    <!-- 空状态 -->
    <div v-if="tasks.length === 0" class="flex flex-col items-center justify-center p-12 text-center">
      <div class="w-20 h-20 mb-4 rounded-2xl bg-gray-50 flex items-center justify-center">
        <svg class="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
        </svg>
      </div>
      <p class="text-sm font-medium text-gray-500">暂无任务</p>
      <p class="text-xs text-gray-400 mt-2">请在左侧输入招标信息和投标文件后点击"开始分析"</p>
    </div>

    <!-- 任务列表 -->
    <div v-else class="space-y-3">
      <transition-group name="task-appear" tag="div">
        <div
          v-for="task in tasks"
          :key="task.id"
          :class="['task-card', { active: selectedTaskId === task.id }]"
          @click="selectTask(task)"
        >
          <div class="flex items-start justify-between gap-3 mb-3">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-xs text-gray-400 font-medium">任务 {{ task.id }}</span>
                <span v-if="task.review" class="status-dot" :class="getStatusDotClass(task.review.conclusion)"></span>
              </div>
              <h3 class="text-sm font-semibold text-gray-800 leading-relaxed">{{ task.title }}</h3>
            </div>
            <span v-if="task.createdAt" class="text-xs text-gray-400 whitespace-nowrap flex-shrink-0">
              {{ formatDate(task.createdAt) }}
            </span>
          </div>

          <p v-if="task.description" class="text-xs text-gray-500 mb-3 line-clamp-2 leading-relaxed">
            {{ task.description }}
          </p>

          <!-- 状态标签 -->
          <div class="flex items-center gap-2">
            <span v-if="!task.review" class="status-tag pending">
              <svg class="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              待审核
            </span>
            <span v-else class="status-tag" :class="getStatusTagClass(task.review.conclusion)">
              <svg class="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              {{ task.review.conclusion }}
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

const getStatusDotClass = (status) => {
  const statusMap = {
    '通过': 'pass',
    '不通过': 'fail',
    '待确认': 'pending'
  }
  return statusMap[status] || 'pending'
}

const getStatusTagClass = (status) => {
  const statusMap = {
    '通过': 'pass',
    '不通过': 'fail',
    '待确认': 'pending'
  }
  return statusMap[status] || 'pending'
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
/* 任务卡片 */
.task-card {
  border: 1.5px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1rem;
  background: white;
  transition: all 0.2s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.task-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: transparent;
  transition: background 0.2s ease;
}

.task-card:hover {
  border-color: #bfdbfe;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);
  transform: translateY(-1px);
}

.task-card.active {
  border-color: #3b82f6;
  background: linear-gradient(to right, #eff6ff, #ffffff);
}

.task-card.active::before {
  background: #3b82f6;
}

/* 状态点 */
.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-dot.pass {
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.4);
}

.status-dot.fail {
  background: #ef4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.4);
}

.status-dot.pending {
  background: #f59e0b;
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.4);
}

/* 状态标签 */
.status-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.625rem;
  border-radius: 0.5rem;
  font-size: 0.6875rem;
  font-weight: 500;
  line-height: 1;
  letter-spacing: 0.0125em;
}

.status-tag.pending {
  background: #fef3c7;
  color: #92400e;
}

.status-tag.pass {
  background: #d1fae5;
  color: #065f46;
}

.status-tag.fail {
  background: #fee2e2;
  color: #991b1b;
}

/* 文本截断 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 任务出现动画 */
.task-appear-enter-active {
  transition: all 0.2s ease-out;
}

.task-appear-leave-active {
  transition: all 0.15s ease-in;
}

.task-appear-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.task-appear-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.task-appear-move {
  transition: transform 0.2s ease;
}
</style>
