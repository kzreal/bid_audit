<template>
  <!-- 审核中状态 -->
  <div v-if="reviewing" class="flex flex-col items-center justify-center h-full p-8">
    <div class="loading-ring mb-6"></div>
    <p class="text-gray-600 font-medium">正在审核任务...</p>
    <p class="text-xs text-gray-400 mt-2">这可能需要几秒钟</p>
  </div>

  <!-- 审核完成状态 -->
  <div v-else-if="selectedTask.review" class="space-y-3">
    <!-- 审核结论卡片 -->
    <div class="bg-white border border-gray-100 rounded-xl p-4 shadow-sm">
      <div class="flex flex-col items-center justify-center gap-3">
        <div class="w-12 h-12 rounded-full flex items-center justify-center" :class="getConclusionIconBg(selectedTask.review.conclusion)">
          <svg v-if="selectedTask.review.conclusion === '通过'" class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <svg v-else-if="selectedTask.review.conclusion === '不通过'" class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <svg v-else class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <span :class="['text-xl font-bold', getConclusionTextClass(selectedTask.review.conclusion)]">
          {{ selectedTask.review.conclusion }}
        </span>
        <button
          @click="reviewTask"
          :disabled="store.loading"
          class="mt-1 bg-white border border-blue-600 text-blue-600 px-3 py-1.5 rounded-lg text-sm font-semibold hover:bg-blue-50 transition-all duration-300 disabled:border-gray-200 disabled:text-gray-400 disabled:bg-gray-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <span v-if="store.loading" class="inline-flex items-center">
            <div class="loader-mini mr-2"></div>
            审核中...
          </span>
          <span v-else class="flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            重新审核
          </span>
        </button>
      </div>
    </div>

    <!-- 审核原因 -->
    <div v-if="selectedTask.review.reason" class="bg-white border border-gray-100 rounded-2xl overflow-hidden shadow-sm">
      <div class="px-6 py-4 border-b border-gray-100 bg-gray-50/50">
        <div class="flex items-center gap-2 text-sm font-semibold text-gray-700">
          <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          审核原因
        </div>
      </div>
      <div class="p-6">
        <p class="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{{ selectedTask.review.reason }}</p>
      </div>
    </div>

    <!-- 投标来源 - 可折叠 -->
    <div v-if="selectedTask.review.bidSource" class="bg-white border border-gray-100 rounded-2xl overflow-hidden shadow-sm">
      <button
        @click="bidSourceExpanded = !bidSourceExpanded"
        class="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-gray-50/50 transition-colors"
      >
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <span class="text-sm font-semibold text-gray-700">投标来源</span>
          <span class="text-xs text-gray-400">({{ parseLineNumbersAndGetContent(selectedTask.review.bidSource).length }})</span>
        </div>
        <svg
          class="w-5 h-5 text-gray-400 transition-transform duration-200"
          :class="{ 'rotate-180': bidSourceExpanded }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </button>
      <div v-show="bidSourceExpanded" class="border-t border-gray-100">
        <div v-if="parseLineNumbersAndGetContent(selectedTask.review.bidSource).length > 0" class="p-4 space-y-2">
          <div
            v-for="(item, idx) in parseLineNumbersAndGetContent(selectedTask.review.bidSource)"
            :key="idx"
            class="bg-green-50 border border-green-100 rounded-xl p-3"
          >
            <div class="max-h-32 overflow-y-auto">
              <p class="text-xs text-gray-700 font-mono leading-relaxed whitespace-pre">{{ item.originalLine }}</p>
            </div>
          </div>
        </div>
        <div v-else class="p-4">
          <p class="text-sm text-gray-600">{{ selectedTask.review.bidSource }}</p>
        </div>
      </div>
    </div>

    <!-- 多切片审核结果 - 可折叠 -->
    <div v-if="selectedTask.review.slices_reviews && selectedTask.review.slices_reviews.length > 0" class="bg-white border border-gray-100 rounded-2xl overflow-hidden shadow-sm">
      <button
        @click="slicesExpanded = !slicesExpanded"
        class="w-full flex items-center justify-between px-6 py-4 text-left hover:bg-gray-50/50 transition-colors"
      >
        <div class="flex items-center gap-2">
          <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
          </svg>
          <span class="text-sm font-semibold text-gray-700">切片审核结果</span>
          <span class="text-xs text-gray-400">({{ selectedTask.review.slices_reviews.length }})</span>
        </div>
        <svg
          class="w-5 h-5 text-gray-400 transition-transform duration-200"
          :class="{ 'rotate-180': slicesExpanded }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </button>
      <div v-show="slicesExpanded" class="border-t border-gray-100">
        <div class="p-4 space-y-2">
          <div
            v-for="(sliceReview, index) in selectedTask.review.slices_reviews"
            :key="index"
            class="border border-gray-100 rounded-xl p-3 hover:bg-gray-50/50 transition-colors"
          >
            <div class="flex items-center gap-2 mb-2">
              <span class="px-2 py-1 bg-gray-100 text-gray-600 rounded-md text-xs font-medium">切片 {{ index + 1 }}</span>
            </div>
            <div v-if="sliceReview.suggestion" class="mb-2">
              <p class="text-sm text-gray-700 leading-relaxed">{{ sliceReview.suggestion }}</p>
            </div>
            <div v-if="sliceReview.evidence" class="flex items-start gap-2 text-xs text-gray-500">
              <svg class="w-3.5 h-3.5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              <span>证据: {{ sliceReview.evidence }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 未审核状态 -->
  <div v-else class="flex flex-col items-center justify-center h-full p-8">
    <div class="w-20 h-20 mb-4 rounded-2xl bg-gray-50 flex items-center justify-center">
      <svg class="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
      </svg>
    </div>
    <p class="text-sm font-medium text-gray-600">此任务尚未审核</p>
    <p class="text-xs text-gray-400 mt-2">请点击任务列表中的任务开始审核</p>
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

// 获取结论图标背景色
const getConclusionIconBg = (conclusion) => {
  const bgMap = {
    '通过': 'bg-green-100',
    '不通过': 'bg-red-100',
    '待确认': 'bg-yellow-100'
  }
  return bgMap[conclusion] || 'bg-gray-100'
}

// 获取结论文本颜色
const getConclusionTextClass = (conclusion) => {
  const colorMap = {
    '通过': 'text-green-600',
    '不通过': 'text-red-600',
    '待确认': 'text-yellow-600'
  }
  return colorMap[conclusion] || 'text-gray-600'
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
      // 单个行号（不是范围格式）
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
          // 保留原行，包括 <!-- 行号 --> 标记
          const content = matchedLine.trim()
          rangeLines.push(content)
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
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  animation: spin 1s linear infinite;
}

.loader-mini {
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
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
