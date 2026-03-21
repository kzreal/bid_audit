<template>
  <div class="main-container h-screen flex bg-gray-50">
    <!-- 左侧：招标信息输入 -->
    <div class="w-[35%] bg-white border-r border-gray-100 flex flex-col shadow-sm">
      <header class="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 shadow-sm">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-lg bg-white/20 flex items-center justify-center backdrop-blur-sm">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div>
            <h1 class="text-xl font-semibold tracking-tight">投标文件审核系统</h1>
            <p class="text-blue-100 text-sm mt-0.5">智能分析 · 精准审核 · 高效决策</p>
          </div>
        </div>
      </header>

      <div class="p-6 flex-1 overflow-y-auto">
        <!-- 模版库入口 -->
        <button
          @click="store.openTemplateDrawer()"
          class="w-full mb-6 bg-gradient-to-r from-blue-50 to-blue-100 border-2 border-blue-200 text-blue-700 py-3 px-4 rounded-xl font-semibold shadow-sm hover:shadow-md hover:border-blue-300 transition-all duration-300 flex items-center justify-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
          </svg>
          模版库
        </button>

        <!-- 错误提示 -->
        <transition name="slide-fade">
          <div v-if="store.error" class="mb-6 p-4 bg-red-50 border border-red-100 rounded-xl shadow-sm">
            <div class="flex items-start gap-3">
              <div class="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
                <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-red-700 font-medium">{{ store.error }}</p>
                <button @click="store.clearError()" class="mt-2 text-xs text-red-600 hover:text-red-800 font-medium transition-colors">
                  关闭提示
                </button>
              </div>
            </div>
          </div>
        </transition>

        <!-- 招标信息输入区域 -->
        <bid-requirement-input />

        <!-- 投标文件输入区域 -->
        <bid-file-input />

        <!-- 分析按钮 -->
        <button
          @click="startAnalysis"
          :disabled="!store.canAnalyze || store.loading"
          class="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3.5 px-6 rounded-xl font-semibold shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-300 disabled:from-gray-300 disabled:to-gray-400 disabled:shadow-none disabled:cursor-not-allowed hover:-translate-y-0.5 active:translate-y-0"
        >
          <span v-if="store.loading" class="inline-flex items-center justify-center">
            <span class="loading-dots mr-2">
              <span></span>
              <span></span>
              <span></span>
            </span>
            分析中...
          </span>
          <span v-else class="flex items-center justify-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
            创建任务
          </span>
        </button>
      </div>
    </div>

    <!-- 中间：任务列表 -->
    <div class="w-[30%] bg-gray-50 border-r border-gray-100 flex flex-col">
      <header class="bg-white border-b border-gray-100 p-6 shadow-sm sticky top-0 z-10 min-h-[98px]">
        <div class="flex items-center justify-between gap-4">
          <div class="flex-1 min-w-0">
            <h2 class="text-base font-semibold text-gray-800">任务列表</h2>
            <p class="text-gray-500 text-sm mt-0.5">
              <span class="font-medium text-gray-700">{{ tasks.length }}</span> 个任务
              <span v-if="store.taskStats.reviewed" class="ml-2 text-gray-400">
                · 已审核 <span class="text-green-600 font-medium">{{ store.taskStats.reviewed }}</span>
              </span>
            </p>
          </div>
          <!-- 操作按钮 -->
          <div class="flex items-center gap-2">
            <!-- 撤销按钮 -->
            <button
              v-if="store.canUndoTemplateApplication"
              @click="handleUndoTemplate"
              class="bg-white border-2 border-gray-200 text-gray-600 px-3 py-2 rounded-xl text-sm font-medium hover:bg-gray-50 transition-all duration-300 disabled:border-gray-200 disabled:text-gray-400 disabled:bg-gray-50 disabled:cursor-not-allowed flex items-center gap-1.5 shadow-sm whitespace-nowrap"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"></path>
              </svg>
              撤销
            </button>
            <!-- 全部审核按钮 -->
            <button
              @click="handleReviewAll"
              :disabled="store.loading || tasks.filter(t => !t.review).length === 0"
              class="bg-white border-2 border-blue-600 text-blue-600 px-4 py-2 rounded-xl text-sm font-semibold hover:bg-blue-50 transition-all duration-300 disabled:border-gray-200 disabled:text-gray-400 disabled:bg-gray-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm whitespace-nowrap"
            >
              <span v-if="store.loading" class="inline-flex items-center">
                <span class="loading-dots-mini mr-2">
                  <span></span>
                  <span></span>
                  <span></span>
                </span>
                审核中...
              </span>
              <span v-else class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                </svg>
                全部审核 ({{ tasks.filter(t => !t.review).length }})
              </span>
            </button>
          </div>
        </div>
      </header>

      <div class="flex-1 overflow-y-auto p-4">
        <task-list
          :tasks="tasks"
          :selected-task-id="store.selectedTaskId"
          @select-task="handleSelectTask"
        />
      </div>
    </div>

    <!-- 右侧：审核详情 -->
    <div class="flex-1 bg-white flex flex-col overflow-hidden">
      <header class="bg-white border-b border-gray-100 p-6 flex-shrink-0 flex justify-between items-center gap-4 shadow-sm sticky top-0 z-10 min-h-[98px]">
        <div v-if="selectedTask" class="flex-1 min-w-0">
          <h2 class="text-base font-semibold text-gray-800 leading-relaxed">{{ selectedTask.title }}</h2>
          <p v-if="selectedTask.description" class="text-gray-500 text-sm mt-1.5 leading-relaxed">{{ selectedTask.description }}</p>
        </div>
        <div v-if="selectedTask && selectedTask.review && selectedTask.review.createdAt" class="flex-shrink-0 text-right">
          <p class="text-xs text-gray-400 font-medium">{{ formatDateTime(selectedTask.review.createdAt) }}</p>
        </div>
        <div v-else class="flex-1">
          <h2 class="text-base font-semibold text-gray-400">审核详情</h2>
        </div>
      </header>

      <!-- 空状态 -->
      <div v-if="!selectedTask" class="flex-1 flex items-center justify-center p-8">
        <div class="text-center">
          <div class="w-20 h-20 mx-auto mb-4 rounded-2xl bg-gray-50 flex items-center justify-center">
            <svg class="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
            </svg>
          </div>
          <p class="text-gray-400 text-sm">请从任务列表中选择一个任务查看详情</p>
        </div>
      </div>

      <div v-if="selectedTask" class="flex-1 overflow-y-auto p-6">
        <review-detail
          :selected-task="selectedTask"
          :reviewing="store.reviewing"
          @review-task="handleReviewTask"
        />
      </div>
    </div>

    <!-- 模版库抽屉 -->
    <template-drawer
      key="template-drawer"
      :open="store.templateDrawerOpen"
      :templates="allTemplates"
      @close="store.closeTemplateDrawer"
      @create-template="handleCreateTemplate"
      @apply="handleApplyTemplate"
      @edit="handleEditTemplate"
      @delete="handleDeleteTemplate"
    />

    <!-- 模版编辑器 -->
    <template-editor
      :open="editorOpen"
      :template="store.currentEditingTemplate"
      @save="handleSaveTemplate"
      @cancel="editorOpen = false"
    />
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
  background: white;
  border-radius: 50%;
  animation: loading-pulse 1.4s ease-in-out infinite both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

/* 迷你加载动画 */
.loading-dots-mini {
  display: inline-flex;
  align-items: center;
  gap: 3px;
}

.loading-dots-mini span {
  width: 4px;
  height: 4px;
  background: #2563eb;
  border-radius: 50%;
  animation: loading-pulse 1.4s ease-in-out infinite both;
}

.loading-dots-mini span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots-mini span:nth-child(2) {
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

/* 滑动淡入淡出过渡 */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 审核徽章样式 */
.review-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1;
}

.review-badge.pass {
  background-color: #d1fae5;
  color: #065f46;
}

.review-badge.fail {
  background-color: #fee2e2;
  color: #991b1b;
}

.review-badge.pending {
  background-color: #fef3c7;
  color: #92400e;
}

/* 滚动条美化 */
:deep(*)::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

:deep(*)::-webkit-scrollbar-track {
  background: transparent;
}

:deep(*)::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

:deep(*)::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useAppStore } from '../stores/appStore'
import { generateConclusion } from '../services/hiagentService'
import { getAllTemplates, saveTemplate, getTemplateById, deleteTemplate } from '../services/templateService'
import BidRequirementInput from './BidRequirementInput.vue'
import BidFileInput from './BidFileInput.vue'
import TaskList from './TaskListOptimized.vue'
import ReviewDetail from './ReviewDetail.vue'
import TemplateDrawer from './TemplateDrawer.vue'
import TemplateEditor from './TemplateEditor.vue'

const store = useAppStore()

// 模版编辑器开关
const editorOpen = ref(false)

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

// 所有模版
const allTemplates = reactive([])

// 加载模版列表
const loadTemplates = () => {
  // 使用 splice 和 push 确保响应式更新
  allTemplates.splice(0, allTemplates.length)
  allTemplates.push(...getAllTemplates())
}

// 初始化时加载模版
loadTemplates()

// 格式化日期时间
const formatDateTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleString('zh-CN')
}

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
      // 根据是否使用切片审核调用不同的方法
      if (store.useSliceReview) {
        await store.reviewTaskWithSlices(taskId)
      } else {
        await store.reviewTask(taskId)
      }
    } catch (error) {
      console.error('审核任务失败:', error)
    }
  }
}

// 处理审核任务
const handleReviewTask = async () => {
  if (!store.selectedTaskId) return

  try {
    // 根据是否使用切片审核调用不同的方法
    if (store.useSliceReview) {
      await store.reviewTaskWithSlices(store.selectedTaskId)
    } else {
      await store.reviewTask(store.selectedTaskId)
    }
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
      // 根据是否使用切片审核调用不同的方法
      if (store.useSliceReview) {
        await store.reviewTaskWithSlices(task.id)
      } else {
        await store.reviewTask(task.id)
      }
    } catch (error) {
      console.error(`审核任务 ${task.id} 失败:`, error)
    }
  }

  // 所有任务审核完成后，调用汇总
  await summarizeReviews()
}

  // 汇总所有切片审核结果并生成最终结论
  const summarizeReviews = async () => {
    // 获取所有已审核的任务
    const reviewedTasks = store.tasks.filter(task => task.review && task.review.slices_reviews)

    if (reviewedTasks.length === 0) {
      console.log('没有已审核的任务需要汇总')
      return
    }

    console.log(`开始汇总 ${reviewedTasks.length} 个任务的切片审核结果...`)

    // 对每个任务调用汇总接口
    for (const task of reviewedTasks) {
      const slicesReviews = task.review.slices_reviews || []

      try {
        // 首先调用汇总接口（代码汇总）
        const response = await fetch('http://localhost:8888/hiagent/summarize-reviews', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            task: task,
            reviews: slicesReviews
          })
        })

        if (!response.ok) {
          console.error(`汇总任务 ${task.id} 失败: ${response.status}`)
          continue
        }

        const result = await response.json()

        if (result.code === 200) {
          console.log(`任务 ${task.id} 汇总完成`)

          // 然后调用 generateConclusion 生成最终结论
          try {
            const conclusionResponse = await generateConclusion({
              task: task,
              reviews: slicesReviews
            })

            if (conclusionResponse && conclusionResponse.data) {
              store.updateTask(task.id, {
                review: {
                  ...task.review,
                  conclusion: conclusionResponse.data.conclusion || '待确认',
                  reason: conclusionResponse.data.reason || '',
                  evidence: conclusionResponse.data.evidence || '待补充',
                  bidSource: conclusionResponse.data.evidence || '待补充',
                  requirementSource: conclusionResponse.data.requirementSource || '招标要求'
                }
              })
              console.log(`任务 ${task.id} 结论生成完成`)
            }
          } catch (error) {
            console.error(`任务 ${task.id} 结论生成失败:`, error)
            // 结论生成失败，使用汇总结果更新
            const summaryData = result.data || {}
            store.updateTask(task.id, {
              review: {
                ...task.review,
                conclusion: summaryData.conclusion || '待确认',
                reason: summaryData.reason || ''
              }
            })
          }
        } else {
          console.error(`汇总任务 ${task.id} 失败:`, result.message)
        }
      } catch (error) {
        console.error(`汇总任务 ${task.id} 失败:`, error)
      }
    }

    console.log('所有任务汇总完成')
  }

  // 获取 API key 的辅助函数
  async function getApiKey(url) {
    const response = await fetch(`http://localhost:8888${url}`)
    const result = await response.json()
    if (result.code === 200 && result.data && result.data.status) {
      return result.data.message  // 使用 message 字段作为 API key
    }
    return ''
  }

// ========== 模版功能相关 ==========

// 创建新模版
function handleCreateTemplate() {
  store.clearCurrentEditingTemplate()
  editorOpen.value = true
}

// 编辑模版
function handleEditTemplate(id) {
  const template = getTemplateById(id)
  if (template) {
    store.setCurrentEditingTemplate(template)
    editorOpen.value = true
  }
}

// 保存模版
function handleSaveTemplate(templateData) {
  saveTemplate(templateData)
  editorOpen.value = false
  store.clearCurrentEditingTemplate()
  loadTemplates()
}

// 应用模版
function handleApplyTemplate(id) {
  const template = getTemplateById(id)
  if (template) {
    store.applyTemplate(template)
    store.closeTemplateDrawer()
  }
}

// 删除模版
function handleDeleteTemplate(id) {
  if (confirm('确定要删除这个模版吗？')) {
    deleteTemplate(id)
    loadTemplates()
  }
}

// 撤销模版应用
function handleUndoTemplate() {
  store.undoTemplateApplication()
}
</script>