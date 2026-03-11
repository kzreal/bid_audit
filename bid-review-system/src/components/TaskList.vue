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
        <div class="flex justify-between items-start mb-2">
          <div class="flex-1">
            <h3 class="font-medium text-gray-800">{{ task.title }}</h3>
            <p class="text-xs text-gray-400 mt-1">任务 {{ task.id }}</p>
          </div>
          <span class="text-xs text-gray-400">
            {{ formatDate(task.createdAt) }}
          </span>
        </div>

        <p class="text-sm text-gray-600 mb-3 line-clamp-2">{{ task.description }}</p>

        <!-- 状态和操作 -->
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

          <div class="flex items-center gap-2">
            <button
              v-if="!task.review"
              @click.stop="startReview(task)"
              :disabled="store.loading && store.selectedTaskId === task.id"
              class="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              <span v-if="store.loading && store.selectedTaskId === task.id" class="inline-flex items-center">
                <div class="loader mr-1"></div>
                审核中
              </span>
              <span v-else>开始审核</span>
            </button>
            <span v-if="task.review" class="text-xs text-gray-400">
              已审核
            </span>
          </div>
        </div>

        <!-- 审核评分 -->
        <div v-if="task.review?.score" class="mt-3 pt-3 border-t border-gray-200">
          <div class="flex items-center justify-between text-xs">
            <span class="text-gray-600">评分详情</span>
            <span class="font-medium text-gray-700">
              平均分: {{ calculateAverageScore(task.review.score) }}
            </span>
          </div>
          <div class="mt-2 space-y-1">
            <div v-for="(score, key) in task.review.score" :key="key" class="flex items-center">
              <span class="text-xs text-gray-600 w-16">{{ getScoreLabel(key) }}</span>
              <div class="flex-1 bg-gray-200 rounded-full h-1.5 ml-2">
                <div class="bg-blue-600 h-1.5 rounded-full" :style="{ width: score + '%' }"></div>
              </div>
              <span class="text-xs text-gray-700 ml-2 w-8 text-right">{{ score }}</span>
            </div>
          </div>
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

const emit = defineEmits(['select-task', 'start-review'])

const selectTask = (task) => {
  emit('select-task', task.id)
}

const startReview = (task) => {
  emit('start-review', task)
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

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleDateString('zh-CN')
}

// 计算平均分
const calculateAverageScore = (score) => {
  if (!score || typeof score !== 'object') return 0
  const values = Object.values(score)
  if (values.length === 0) return 0
  return Math.round(values.reduce((sum, val) => sum + val, 0) / values.length)
}

// 获取评分标签
const getScoreLabel = (key) => {
  const labelMap = {
    technical: '技术',
    price: '价格',
    experience: '经验',
    quality: '质量',
    schedule: '进度',
    service: '服务',
    solution: '方案',
    innovation: '创新'
  }
  return labelMap[key] || key
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>