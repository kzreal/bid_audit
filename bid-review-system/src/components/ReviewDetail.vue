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
      <h3 class="font-medium text-gray-700 mb-3 flex items-center justify-between">
        <span class="flex items-center">
          <span>审核结论</span>
          <span class="text-xl ml-2">
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
      </h3>
    </div>

    <!-- 审核原因 -->
    <div v-if="selectedTask.review.reason" class="bg-gray-50 rounded-lg p-4">
      <h3 class="font-medium text-gray-700 mb-3">审核原因</h3>
      <p class="text-gray-700 whitespace-pre-wrap">{{ selectedTask.review.reason }}</p>
    </div>

    <!-- 投标来源 - 可折叠 -->
    <div class="bg-gray-50 rounded-lg">
      <button
        @click="bidSourceExpanded = !bidSourceExpanded"
        class="w-full flex items-center justify-between p-3 text-left hover:bg-gray-100 transition-colors rounded-lg"
      >
        <h3 class="font-medium text-gray-700">投标来源 ({{ parseLineNumbersAndGetContent(selectedTask.review.bidSource).length }})</h3>
        <svg
          class="w-5 h-5 text-gray-500 transition-transform duration-200"
          :class="{ 'rotate-180': bidSourceExpanded }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </button>
      <div v-show="bidSourceExpanded" class="px-3 pb-3">
        <div v-if="parseLineNumbersAndGetContent(selectedTask.review.bidSource).length > 0" class="space-y-2">
          <div
            v-for="(item, idx) in parseLineNumbersAndGetContent(selectedTask.review.bidSource)"
            :key="idx"
            class="bg-green-50 border border-green-200 rounded-md"
          >
            <div class="max-h-24 overflow-y-auto p-2">
              <p class="text-sm text-gray-700 font-mono whitespace-pre">{{ item.originalLine }}</p>
            </div>
          </div>
        </div>
        <p v-else class="text-sm text-gray-600">{{ selectedTask.review.bidSource || '-' }}</p>
      </div>
    </div>

    <!-- 多切片审核结果 - 可折叠 -->
    <div v-if="selectedTask.review.slices_reviews && selectedTask.review.slices_reviews.length > 0" class="bg-gray-50 rounded-lg">
      <button
        @click="slicesExpanded = !slicesExpanded"
        class="w-full flex items-center justify-between p-3 text-left hover:bg-gray-100 transition-colors rounded-lg"
      >
        <h3 class="font-medium text-gray-700">切片审核结果 ({{ selectedTask.review.slices_reviews.length }})</h3>
        <svg
          class="w-5 h-5 text-gray-500 transition-transform duration-200"
          :class="{ 'rotate-180': slicesExpanded }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </button>
      <div v-show="slicesExpanded" class="px-3 pb-3">
        <div class="space-y-2">
          <div
            v-for="(sliceReview, index) in selectedTask.review.slices_reviews"
            :key="index"
            class="border border-gray-200 rounded-md p-2 text-sm"
          >
            <p class="text-xs text-gray-500 mb-1">切片 {{ index + 1 }}</p>
            <div v-if="sliceReview.suggestion" class="mb-1">
              <p class="text-xs text-gray-600">{{ sliceReview.suggestion }}</p>
            </div>
            <div v-if="sliceReview.evidence" class="text-xs text-gray-500">
              证据: {{ sliceReview.evidence }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-else>
    <div class="bg-gray-50 rounded-lg p-8 text-center">
      <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
      </svg>
      <p class="text-gray-600">此任务尚未审核</p>
      <p class="text-sm text-gray-400 mt-2">请点击任务列表中的任务开始审核</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAppStore } from '../stores/appStore'

const store = useAppStore()

// 切片审核结果展开/收起状态
const slicesExpanded = ref(false)
// 投标来源展开/收起状态
const bidSourceExpanded = ref(false)

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

const formatDateTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleString('zh-CN')
}

// 解析行号范围
const parseLineRanges = (bidSource) => {
  if (!bidSource) return []

  const ranges = []
  const parts = bidSource.toString().split(/[,，]/)

  for (const part of parts) {
    const trimmed = part.trim()
    if (!trimmed) continue

    // 检查是否是范围格式（如 264-278）
    const rangeMatch = trimmed.match(/^(\d+)\s*[-—–]\s*(\d+)$/)
    if (rangeMatch) {
      ranges.push({
        start: parseInt(rangeMatch[1]),
        end: parseInt(rangeMatch[2])
      })
    } else {
      // 单个行号
      const num = parseInt(trimmed)
      if (!isNaN(num) && num > 0) {
        ranges.push({ start: num, end: num })
      }
    }
  }

  return ranges
}

// 解析行号并获取切片原文
const parseLineNumbersAndGetContent = (bidSource) => {
  if (!bidSource || bidSource === '待补充' || !Array.isArray(store.bidSlices)) {
    return []
  }

  const ranges = parseLineRanges(bidSource)
  if (ranges.length === 0) {
    return []
  }

  const results = []

  // 遍历所有切片，查找对应行号的内容
  for (const slice of store.bidSlices) {
    const lines = (slice.content || '').split('\n')

    for (const range of ranges) {
      // 为每个范围收集所有行
      const rangeLines = []
      for (let lineNumber = range.start; lineNumber <= range.end; lineNumber++) {
        // 查找该行号的切片内容
        // 行号格式：<!-- 行号 --> 内容
        const matchedLine = lines.find(line => {
          const match = line.match(/^<!--\s*(\d+)\s*-->/)
          return match && parseInt(match[1]) === lineNumber
        })

        if (matchedLine) {
          rangeLines.push(matchedLine.trim())
        }
      }

      // 如果找到该范围的行，作为一个片段添加到结果
      if (rangeLines.length > 0) {
        results.push({
          originalLine: rangeLines.join('\n')
        })
      }
    }
  }

  return results
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

.loader {
  border: 2px solid #f3f4f6;
  border-top: 2px solid #2563eb;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
