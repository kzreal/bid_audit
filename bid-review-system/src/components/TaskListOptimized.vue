<template>
  <div>
    <!-- 空状态 - Vercel 风格 -->
    <div v-if="tasks.length === 0" class="flex flex-col items-center justify-center p-12 text-center">
      <svg class="w-12 h-12 mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
      </svg>
      <p class="text-sm font-medium text-gray-500">暂无任务</p>
      <p class="text-xs text-gray-400 mt-2">请在左侧输入招标信息和投标文件后点击"开始分析"</p>
    </div>

    <!-- 任务列表 -->
    <div v-else class="space-y-2">
      <transition-group name="task-appear" tag="div">
        <div
          v-for="task in tasks"
          :key="task.id"
          :class="['task-card', { active: selectedTaskId === task.id }]"
          @click="selectTask(task)"
        >
          <!-- 状态垂直色条 -->
          <div
            class="status-bar"
            :class="getStatusBarClass(task)"
          ></div>

          <div class="flex items-start justify-between gap-3 mb-2.5">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-xs text-gray-400 font-medium">任务 {{ task.id }}</span>
                <span v-if="task.review" class="status-dot" :class="getStatusDotClass(task.review.conclusion)"></span>
              </div>
              <h3 class="text-sm font-semibold text-black leading-relaxed">{{ task.title }}</h3>
            </div>
            <span v-if="task.createdAt" class="text-xs text-gray-400 whitespace-nowrap flex-shrink-0">
              {{ formatDate(task.createdAt) }}
            </span>
          </div>

          <p v-if="task.description" class="text-xs text-gray-500 mb-2.5 line-clamp-2 leading-relaxed">
            {{ task.description }}
          </p>

          <!-- 状态标签 - Vercel 风格 -->
          <div class="flex items-center gap-2">
            <span v-if="!task.review" class="review-badge pending">
              待审核
            </span>
            <span v-else class="review-badge" :class="getStatusTagClass(task.review.conclusion)">
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

const getStatusBarClass = (task) => {
  if (!task.review) {
    return 'unreviewed'
  }
  const statusMap = {
    '通过': 'pass',
    '不通过': 'fail',
    '待确认': 'pending'
  }
  return statusMap[task.review.conclusion] || 'unreviewed'
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
/* 任务卡片 - Vercel 风格 */
.task-card {
  border: 1px solid #eaeaea;
  border-radius: 2px;
  padding: 0.875rem;
  background: white;
  transition: all 200ms ease-out;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  /* 左侧预留空间给状态色条 */
  padding-left: 1rem;
}

.task-card:hover {
  border-color: #0070f3;
}

.task-card.active {
  border-color: #0070f3;
  background: rgba(0, 112, 243, 0.05);
}

/* 状态垂直色条 */
.status-bar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  transition: all 200ms ease-out;
}

.status-bar.pass {
  background: #22c55e; /* 绿色 - 通过 */
}

.status-bar.fail {
  background: #ef4444; /* 红色 - 不通过 */
}

.status-bar.pending {
  background: #f59e0b; /* 黄色 - 待确认 */
}

.status-bar.unreviewed {
  background: #eaeaea; /* 极浅灰 - 待审核 */
}

/* 状态标签 */
.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-dot.pass {
  background: #22c55e;
}

.status-dot.fail {
  background: #ef4444;
}

.status-dot.pending {
  background: #f59e0b;
}

/* 状态标签 - 与垂直色条颜色统一 */
.review-badge.pass {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.review-badge.fail {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.review-badge.pending {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
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
  transition: all 200ms ease-out;
}

.task-appear-leave-active {
  transition: all 150ms ease-in;
}

.task-appear-enter-from {
  opacity: 0;
  transform: translateX(-12px);
}

.task-appear-leave-to {
  opacity: 0;
  transform: translateX(12px);
}

.task-appear-move {
  transition: transform 200ms ease-out;
}
</style>
