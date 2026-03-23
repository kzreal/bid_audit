<template>
  <div class="review-result-tab p-5">
    <!-- 审核概览 -->
    <div class="mb-6">
      <h3 class="text-sm font-semibold text-black mb-4">审核概览</h3>

      <!-- 进度条 -->
      <div class="mb-4">
        <div class="flex items-center justify-between text-xs text-gray-600 mb-2">
          <span>审核进度</span>
          <span>{{ reviewedCount }} / {{ totalCount }}</span>
        </div>
        <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            class="h-full bg-vercel-blue transition-all duration-300"
            :style="{ width: progressPercent + '%' }"
          ></div>
        </div>
      </div>

      <!-- 统计卡片 -->
      <div class="grid grid-cols-4 gap-3">
        <div class="p-3 border border-gray-200 rounded-vercel-sm text-center">
          <p class="text-xl font-bold text-black">{{ totalCount }}</p>
          <p class="text-xs text-gray-500">总计</p>
        </div>
        <div class="p-3 border border-gray-200 rounded-vercel-sm text-center">
          <p class="text-xl font-bold text-green-600">{{ passedCount }}</p>
          <p class="text-xs text-gray-500">通过</p>
        </div>
        <div class="p-3 border border-gray-200 rounded-vercel-sm text-center">
          <p class="text-xl font-bold text-red-600">{{ failedCount }}</p>
          <p class="text-xs text-gray-500">不通过</p>
        </div>
        <div class="p-3 border border-gray-200 rounded-vercel-sm text-center">
          <p class="text-xl font-bold text-yellow-600">{{ pendingCount }}</p>
          <p class="text-xs text-gray-500">待确认</p>
        </div>
      </div>
    </div>

    <!-- 分隔线 -->
    <div class="divider border-t border-gray-200 my-5"></div>

    <!-- 结果列表 -->
    <div class="mb-4 flex items-center justify-between">
      <h3 class="text-sm font-semibold text-black">审核结果</h3>
      <button
        v-if="reviewedTasks.length > 0"
        @click="sortByFailedFirst = !sortByFailedFirst"
        class="text-xs text-gray-500 hover:text-black transition-colors"
      >
        {{ sortByFailedFirst ? '按顺序' : '不通过优先' }}
      </button>
    </div>

    <!-- 空状态 -->
    <div v-if="reviewedTasks.length === 0" class="text-center py-12">
      <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <p class="text-gray-500 text-sm mb-4">暂无审核结果</p>
      <button
        @click="store.setCurrentTab('task-list')"
        class="text-sm text-vercel-blue hover:text-vercel-blue-hover font-medium transition-colors"
      >
        去审核任务
      </button>
    </div>

    <!-- 结果列表 -->
    <div v-else class="space-y-3">
      <transition-group name="result-list">
        <div
          v-for="(task, index) in sortedTasks"
          :key="task.id"
          class="result-item p-4 border border-gray-200 rounded-vercel-sm bg-white hover:border-gray-300 transition-all duration-200"
        >
          <!-- 头部 -->
          <div class="flex items-start justify-between gap-3 mb-3">
            <div class="flex items-start gap-2">
              <!-- 状态图标 -->
              <span
                :class="[
                  'inline-flex items-center justify-center w-6 h-6 rounded-full flex-shrink-0',
                  task.review?.conclusion === '通过' ? 'bg-green-100 text-green-600' :
                  task.review?.conclusion === '不通过' ? 'bg-red-100 text-red-600' :
                  'bg-yellow-100 text-yellow-600'
                ]"
              >
                <svg v-if="task.review?.conclusion === '通过'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                <svg v-else-if="task.review?.conclusion === '不通过'" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </span>
              <div>
                <h4 class="text-sm font-medium text-black leading-relaxed">{{ task.title }}</h4>
                <p class="text-xs text-gray-400 mt-1">{{ index + 1 }}</p>
              </div>
            </div>

            <!-- 状态标签 -->
            <span
              :class="[
                'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium flex-shrink-0',
                task.review?.conclusion === '通过' ? 'bg-green-100 text-green-700' :
                task.review?.conclusion === '不通过' ? 'bg-red-100 text-red-700' :
                'bg-yellow-100 text-yellow-700'
              ]"
            >
              {{ task.review?.conclusion }}
            </span>
          </div>

          <!-- 审核说明 -->
          <div v-if="task.review?.reason" class="mb-3 pl-8">
            <p class="text-xs text-gray-600 leading-relaxed">{{ task.review.reason }}</p>
          </div>

          <!-- 证据/来源 -->
          <div v-if="task.review?.bidSource && !isNaN(parseInt(task.review.bidSource))" class="pl-8">
            <button
              @click="handleJumpToLine(parseInt(task.review.bidSource))"
              class="text-xs text-vercel-blue hover:text-vercel-blue-hover font-medium transition-colors flex items-center gap-1"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
              </svg>
              查看来源
            </button>
          </div>

          <!-- 切片详情（如果有） -->
          <div v-if="task.review?.slices_reviews?.length > 0" class="mt-3 pl-8">
            <p class="text-xs text-gray-500 mb-2">切片详情 ({{ task.review.slices_reviews.length }})</p>
            <div class="space-y-2">
              <div
                v-for="(slice, sliceIndex) in task.review.slices_reviews"
                :key="sliceIndex"
                class="p-2 bg-gray-50 rounded text-xs"
              >
                <div class="flex items-center justify-between mb-1">
                  <span class="text-gray-600 font-medium">切片 {{ sliceIndex + 1 }}<template v-if="slice.sliceTitle"> - {{ slice.sliceTitle }}</template></span>
                  <button
                    v-if="slice.lineNumber"
                    @click="handleJumpToLine(slice.lineNumber)"
                    class="text-vercel-blue hover:text-vercel-blue-hover transition-colors"
                  >
                    第 {{ slice.lineNumber }} 行
                  </button>
                  <button
                    v-else-if="task.review?.bidSource && !isNaN(parseInt(task.review.bidSource))"
                    @click="handleJumpToLine(parseInt(task.review.bidSource))"
                    class="text-vercel-blue hover:text-vercel-blue-hover transition-colors"
                  >
                    查看来源
                  </button>
                </div>
                <p class="text-gray-600 leading-relaxed">{{ slice.suggestion }}</p>
              </div>
            </div>
          </div>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAppStore } from '../stores/appStore'

const store = useAppStore()
const sortByFailedFirst = ref(true)

const emit = defineEmits(['jump-to-line'])

const tasks = computed(() => store.tasks)

const reviewedTasks = computed(() => {
  return tasks.value.filter(t => t.review)
})

const totalCount = computed(() => tasks.value.length)
const reviewedCount = computed(() => reviewedTasks.value.length)
const passedCount = computed(() => reviewedTasks.value.filter(t => t.review?.conclusion === '通过').length)
const failedCount = computed(() => reviewedTasks.value.filter(t => t.review?.conclusion === '不通过').length)
const pendingCount = computed(() => reviewedTasks.value.filter(t => t.review?.conclusion === '待确认').length)

const progressPercent = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((reviewedCount.value / totalCount.value) * 100)
})

const sortedTasks = computed(() => {
  if (!sortByFailedFirst.value) return reviewedTasks.value
  return [...reviewedTasks.value].sort((a, b) => {
    const order = { '不通过': 0, '待确认': 1, '通过': 2 }
    return (order[a.review?.conclusion] || 3) - (order[b.review?.conclusion] || 3)
  })
})

const handleJumpToLine = (lineNumber) => {
  if (lineNumber) {
    emit('jump-to-line', lineNumber)
  }
}
</script>

<style scoped>
.result-list-enter-active,
.result-list-leave-active {
  transition: all 0.3s ease;
}

.result-list-enter-from,
.result-list-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
