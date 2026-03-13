<template>
  <div v-if="!selectedTask" class="h-full flex items-center justify-center text-gray-500">
    <div class="text-center">
      <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
      </svg>
      <p>请从左侧选择一个任务进行审核</p>
    </div>
  </div>

  <div v-else-if="reviewing" class="flex justify-center items-center h-64">
    <div class="text-center">
      <div class="loading-ring mx-auto mb-4"></div>
      <p class="text-gray-600">正在审核任务...</p>
    </div>
  </div>

  <div v-else-if="selectedTask.review" class="space-y-6">
    <!-- 审核结论 -->
    <div class="bg-gray-50 rounded-lg p-4">
      <h3 class="font-medium text-gray-700 mb-3">审核结论</h3>
      <div class="flex items-center justify-between">
        <span class="text-xl">
          <span v-if="selectedTask.review.status === '通过'" class="text-green-600">
            ✅ 通过
          </span>
          <span v-else-if="selectedTask.review.status === '不通过'" class="text-red-600">
            ❌ 不通过
          </span>
          <span v-else class="text-yellow-600">
            ❓ 待确认
          </span>
        </span>
        <button
          @click="reviewTask"
          :disabled="store.loading"
          class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <span v-if="store.loading" class="inline-flex items-center">
            <div class="loader mr-2"></div>
            审核中...
          </span>
          <span v-else>重新审核</span>
        </button>
      </div>
    </div>

    <!-- 审核原因 -->
    <div class="bg-gray-50 rounded-lg p-4">
      <h3 class="font-medium text-gray-700 mb-3">审核原因</h3>
      <div class="prose prose-sm max-w-none">
        <p class="text-gray-700 whitespace-pre-wrap">{{ selectedTask.review.reason }}</p>
      </div>
    </div>

    <!-- 来源信息 -->
    <div class="bg-gray-50 rounded-lg p-4">
      <h3 class="font-medium text-gray-700 mb-3">来源信息</h3>
      <div class="space-y-3">
        <div class="flex items-start">
          <svg class="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <div>
            <p class="text-sm font-medium text-gray-700">需求来源</p>
            <p class="text-sm text-gray-600 mt-1">{{ selectedTask.review.requirementSource }}</p>
          </div>
        </div>
        <div class="flex items-start">
          <svg class="w-5 h-5 text-green-500 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <div class="flex-1">
            <p class="text-sm font-medium text-gray-700">投标来源</p>
            <!-- 原始来源 -->
            <p class="text-xs text-gray-500 mt-1">{{ parsedBidSource.original }}</p>
            <!-- 多个可折叠的解析内容 -->
            <div v-if="parsedBidSource.hasLineNumbers" class="mt-2 space-y-2">
              <div
                v-for="(segment, index) in parsedBidSource.segments"
                :key="index"
                class="border border-gray-200 rounded-md overflow-hidden"
              >
                <button
                  @click="toggleSegment(index)"
                  class="w-full flex items-center justify-between px-3 py-2 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
                >
                  <span class="text-xs font-medium text-gray-700">
                    {{ segment.type === 'range' ? '行' : '行' }} {{ segment.label }} ({{ segment.lineCount }} 行内容)
                  </span>
                  <svg
                    :class="['w-4 h-4 text-gray-500 transition-transform', expandedSegments[index] ? 'rotate-180' : '']"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                  </svg>
                </button>
                <div v-show="expandedSegments[index]" class="p-3 bg-green-50 border-t border-gray-200 max-h-64 overflow-y-auto">
                  <p class="text-sm text-gray-700 whitespace-pre-wrap font-mono">{{ segment.content }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 审核历史 -->
    <div v-if="selectedTask.review.createdAt" class="bg-gray-50 rounded-lg p-4 mt-4">
      <h3 class="font-medium text-gray-700 mb-2">审核信息</h3>
      <div class="text-sm text-gray-600 space-y-1">
        <p>审核时间: {{ formatDateTime(selectedTask.review.createdAt) }}</p>
        <p>任务创建时间: {{ formatDateTime(selectedTask.createdAt) }}</p>
        <p>最后更新: {{ formatDateTime(selectedTask.updatedAt) }}</p>
      </div>
    </div>
  </div>

  <div v-else>
    <div class="bg-gray-50 rounded-lg p-8 text-center">
      <!-- 审核中状态 -->
      <div v-if="store.loading">
        <div class="loading-ring mx-auto mb-4" style="width: 48px; height: 48px;"></div>
        <p class="text-gray-600">正在审核任务...</p>
      </div>
      <!-- 等待审核状态 -->
      <div v-else>
        <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
        </svg>
        <p class="text-gray-600">此任务尚未审核</p>
        <p class="text-sm text-gray-400 mt-2">请点击任务列表中的任务开始审核</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useAppStore } from '../stores/appStore'
import { parseSourceWithContext } from '../utils/lineParser'

const store = useAppStore()

const props = defineProps({
  selectedTask: {
    type: Object,
    default: null
  },
  reviewing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['review-task'])

const reviewTask = () => {
  emit('review-task')
}

// 控制每个分段的展开/折叠状态
const expandedSegments = ref({})

const toggleSegment = (index) => {
  expandedSegments.value = {
    ...expandedSegments.value,
    [index]: !expandedSegments.value[index]
  }
}

// 解析投标来源，提取行号对应的内容
const parsedBidSource = computed(() => {
  if (!props.selectedTask?.review?.bidSource) {
    return { original: '', segments: [], hasLineNumbers: false }
  }
  return parseSourceWithContext(props.selectedTask.review.bidSource, store.contextText)
})

// 监听任务变化，重置展开状态
watch(() => props.selectedTask?.review?.bidSource, () => {
  expandedSegments.value = {}
})

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleDateString('zh-CN')
}

const formatDateTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleString('zh-CN')
}
</script>

<style scoped>
/* 旋转环形加载动画 */
.loading-ring {
  border: 3px solid #e5e7eb;
  border-top: 3px solid #2563eb;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>