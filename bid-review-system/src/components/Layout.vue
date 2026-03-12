<template>
  <div class="main-container h-screen flex">
    <!-- 左侧：招标信息输入 -->
    <div class="w-[35%] bg-white border-r border-gray-200 flex flex-col">
      <header class="bg-blue-600 text-white p-4">
        <h1 class="text-xl font-semibold">投标文件审核系统</h1>
        <p class="text-blue-100 text-sm mt-1">智能分析，精准审核</p>
      </header>

      <div class="p-4 flex-1 overflow-y-auto">
        <!-- 错误提示 -->
        <div v-if="store.error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-red-500 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div class="flex-1">
              <p class="text-sm text-red-700">{{ store.error }}</p>
              <button @click="store.clearError()" class="mt-1 text-xs text-red-600 hover:text-red-800">
                关闭
              </button>
            </div>
          </div>
        </div>

        <!-- 招标信息输入区域 -->
        <bid-requirement-input />

        <!-- 投标文件输入区域 -->
        <bid-file-input />

        <!-- 分析按钮 -->
        <button
          @click="startAnalysis"
          :disabled="!store.canAnalyze || store.loading"
          class="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <span v-if="store.loading" class="inline-flex items-center">
            <span class="loading-dots mr-2">
              <span></span>
              <span></span>
              <span></span>
            </span>
            分析中...
          </span>
          <span v-else>开始分析</span>
        </button>
      </div>
    </div>

    <!-- 中间：任务列表 -->
    <div class="w-[30%] bg-gray-50 border-r border-gray-200 flex flex-col">
      <header class="bg-white border-b border-gray-200 p-4">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-gray-800">任务列表</h2>
            <p class="text-gray-600 text-sm mt-1">
              共 {{ tasks.length }} 个任务
              <span v-if="store.taskStats.reviewed" class="ml-2">
                (已审核: {{ store.taskStats.reviewed }})
              </span>
            </p>
          </div>
          <!-- 全部审核按钮 -->
          <button
            @click="handleReviewAll"
            :disabled="store.loading"
            class="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
          >
            <span v-if="store.loading" class="inline-flex items-center">
              <span class="loading-dots mr-2">
                <span></span>
                <span></span>
                <span></span>
              </span>
              审核中...
            </span>
            <span v-else>全部审核 ({{ tasks.filter(t => !t.review).length }})</span>
          </button>
        </div>
      </header>

      <div class="flex-1 overflow-y-auto">
        <task-list
          :tasks="tasks"
          :selected-task-id="store.selectedTaskId"
          @select-task="handleSelectTask"
        />
      </div>
    </div>

    <!-- 右侧：审核详情 -->
    <div class="flex-1 bg-white flex flex-col overflow-hidden">
      <header v-if="selectedTask" class="bg-white border-b border-gray-200 p-4 flex-shrink-0">
        <h2 class="text-lg font-semibold text-gray-800">任务审核</h2>
        <p class="text-gray-600 text-sm mt-1">{{ selectedTask.title }}</p>
      </header>

      <div class="flex-1 overflow-y-auto p-6">
        <review-detail
          :selected-task="selectedTask"
          :reviewing="store.reviewing"
          @review-task="handleReviewTask"
        />
      </div>
    </div>
  </div>
</template>

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

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAppStore } from '../stores/appStore'
import BidRequirementInput from './BidRequirementInput.vue'
import BidFileInput from './BidFileInput.vue'
import TaskList from './TaskList.vue'
import ReviewDetail from './ReviewDetail.vue'

const store = useAppStore()

// 模拟任务数据（备用）
const mockTasks = ref([
  {
    id: 1,
    title: '技术方案完整性评估',
    description: '评估投标文件中的技术方案是否完整、可行，是否满足需求文档中的所有技术要求。',
    requirementSource: '需求文档第3章：技术要求',
    bidSource: '投标文件第4章：技术方案',
    review: null
  },
  {
    id: 2,
    title: '价格合理性分析',
    description: '分析投标报价是否合理，与市场平均水平相比是否存在偏差。',
    requirementSource: '需求文档第5章：预算要求',
    bidSource: '投标文件第6章：报价清单',
    review: null
  },
  {
    id: 3,
    title: '经验资质匹配度',
    description: '审核投标方的过往经验和资质是否满足项目要求。',
    requirementSource: '需求文档第2章：投标人资格',
    bidSource: '投标文件附件：公司资质证明',
    review: null
  }
])

// 组件挂载时检查 API 状态
onMounted(async () => {
  try {
    await store.checkApiStatus()
  } catch (error) {
    console.warn('无法获取 API 状态:', error)
  }
})

// 任务列表（从 store 获取）
const tasks = computed(() => store.tasks)

// 选中的任务（从 store 获取）
const selectedTask = computed(() => store.selectedTask)


// 开始分析
const startAnalysis = async () => {
  if (!store.canAnalyze) return

  try {
    await store.generateTasks(false)
  } catch (error) {
    console.error('生成任务失败:', error)
  }
}

// 处理选择任务（自动开始审核）
const handleSelectTask = async (taskId) => {
  store.selectTask(taskId)

  // 如果任务未审核，自动开始审核
  const task = store.tasks.find(t => t.id === taskId)
  if (task && !task.review && !store.loading) {
    try {
      store.startReviewing()
      await store.reviewTask(taskId, false)
    } catch (error) {
      console.error('审核任务失败:', error)
    }
  }
}

// 处理审核任务
const handleReviewTask = async () => {
  if (!store.selectedTaskId) return

  try {
    store.startReviewing()
    await store.reviewTask(store.selectedTaskId, false)
  } catch (error) {
    console.error('审核任务失败:', error)
  }
}

// 全部审核
const handleReviewAll = async () => {
  const unreviewedTasks = store.tasks.filter(task => !task.review)

  if (unreviewedTasks.length === 0) {
    return
  }

  for (const task of unreviewedTasks) {
    try {
      store.selectTask(task.id)
      await store.reviewTask(task.id, false)
    } catch (error) {
      console.error(`审核任务 ${task.id} 失败:`, error)
    }
  }
}
</script>