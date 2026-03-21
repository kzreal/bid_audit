<template>
  <div class="main-container h-screen flex bg-gray-50">
    <!-- 左侧：招标信息输入 -->
    <div class="w-[35%] bg-white border border-gray-200 flex flex-col">
      <header class="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-5">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-vercel-sm bg-white/20 flex items-center justify-center backdrop-blur-sm">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div>
            <h1 class="text-lg font-semibold tracking-tight">投标文件审核系统</h1>
            <p class="text-blue-100 text-xs mt-0.5">智能分析 · 精准审核 · 高效决策</p>
          </div>
        </div>
      </header>

      <div class="p-5 flex-1 overflow-y-auto">
        <!-- 模版库入口 - Vercel 风格 -->
        <button
          @click="store.openTemplateDrawer()"
          class="w-full mb-5 bg-white text-black border border-gray-300 py-2.5 px-4 rounded-vercel-sm text-sm font-semibold transition-all duration-200 flex items-center justify-center gap-2 hover:bg-gray-50 hover:border-black"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
          </svg>
          模版库
        </button>

        <!-- 错误提示 - Vercel 风格 -->
        <transition name="fade">
          <div v-if="store.error" class="mb-5 p-4 bg-white border border-gray-200 rounded-vercel-sm">
            <div class="flex items-start gap-3">
              <svg class="w-5 h-5 text-black flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-black font-medium">{{ store.error }}</p>
                <button @click="store.clearError()" class="mt-2 text-xs text-gray-500 hover:text-black font-medium transition-colors">
                  关闭
                </button>
              </div>
            </div>
          </div>
        </transition>

        <!-- 招标信息输入区域 -->
        <bid-requirement-input />

        <!-- 投标文件输入区域 -->
        <bid-file-input />

        <!-- 分析按钮 - Vercel 风格 -->
        <button
          @click="startAnalysis"
          :disabled="!store.canAnalyze || store.loading"
          class="w-full bg-vercel-blue text-white py-2.5 px-6 rounded-vercel-sm text-sm font-semibold transition-all duration-200 disabled:bg-gray-200 disabled:text-gray-500 disabled:cursor-not-allowed hover:bg-vercel-blue-hover focus:outline-none focus:ring-2 focus:ring-vercel-blue-light"
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
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
            创建任务
          </span>
        </button>
      </div>
    </div>

    <!-- 中间：任务列表 -->
    <div class="w-[30%] bg-gray-50 border-l border-gray-200 flex flex-col">
      <header class="bg-white border-b border-gray-200 px-5 py-4 sticky top-0 z-10">
        <div class="flex items-center justify-between gap-3">
          <div class="flex-1 min-w-0">
            <h2 class="text-sm font-semibold text-black">任务列表</h2>
            <p class="text-gray-500 text-xs mt-0.5">
              <span class="font-medium text-black">{{ tasks.length }}</span> 个任务
              <span v-if="store.taskStats.reviewed" class="ml-2 text-gray-400">
                · 已审核 <span class="text-vercel-blue font-medium">{{ store.taskStats.reviewed }}</span>
              </span>
            </p>
          </div>
          <!-- 操作按钮 -->
          <div class="flex items-center gap-2">
            <!-- 撤销按钮 - Vercel 风格 -->
            <button
              v-if="store.canUndoTemplateApplication"
              @click="handleUndoTemplate"
              class="bg-white text-black border border-gray-300 px-3 py-1.5 rounded-vercel-sm text-xs font-medium transition-all duration-200 hover:bg-gray-50 hover:border-black focus:outline-none focus:ring-2 focus:ring-vercel-blue-light flex items-center gap-1.5 whitespace-nowrap"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"></path>
              </svg>
              撤销
            </button>
            <!-- 全部审核按钮 - Vercel 风格 -->
            <button
              @click="handleReviewAll"
              :disabled="store.loading || tasks.filter(t => !t.review).length === 0"
              class="bg-vercel-blue text-white px-3 py-1.5 rounded-vercel-sm text-xs font-semibold transition-all duration-200 disabled:bg-gray-200 disabled:text-gray-500 disabled:cursor-not-allowed hover:bg-vercel-blue-hover focus:outline-none focus:ring-2 focus:ring-vercel-blue-light flex items-center gap-1.5 whitespace-nowrap"
            >
              <span v-if="store.loading" class="inline-flex items-center">
                <span class="loading-dots-mini mr-1.5">
                  <span></span>
                  <span></span>
                  <span></span>
                </span>
                审核中...
              </span>
              <span v-else class="flex items-center gap-1.5">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                </svg>
                全部审核 ({{ tasks.filter(t => !t.review).length }})
              </span>
            </button>
          </div>
        </div>
      </header>

      <div class="flex-1 overflow-y-auto p-3">
        <task-list
          :tasks="tasks"
          :selected-task-id="store.selectedTaskId"
          @select-task="handleSelectTask"
        />
      </div>
    </div>

    <!-- 右侧：审核详情 -->
    <div class="flex-1 bg-white border-l border-gray-200 flex flex-col">
      <header class="bg-white border-b border-gray-200 px-5 py-4 sticky top-0 z-10 flex-shrink-0 flex justify-between items-center gap-3">
        <div v-if="selectedTask" class="flex-1 min-w-0">
          <h2 class="text-sm font-semibold text-black leading-relaxed">{{ selectedTask.title }}</h2>
          <p v-if="selectedTask.description" class="text-gray-500 text-xs mt-1 leading-relaxed">{{ selectedTask.description }}</p>
        </div>
        <div v-if="selectedTask && selectedTask.review && selectedTask.review.createdAt" class="flex-shrink-0 text-right">
          <p class="text-xs text-gray-400 font-medium">{{ formatDateTime(selectedTask.review.createdAt) }}</p>
        </div>
        <div v-else class="flex-1">
          <h2 class="text-sm font-semibold text-gray-400">审核详情</h2>
        </div>
      </header>

      <!-- 空状态 - Vercel 风格 -->
      <div v-if="!selectedTask" class="flex-1 flex items-center justify-center p-8">
        <div class="text-center">
          <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
          </svg>
          <p class="text-gray-400 text-sm">请从任务列表中选择一个任务查看详情</p>
        </div>
      </div>

      <div v-if="selectedTask" class="flex-1 overflow-y-auto p-5">
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
/* 滑动淡入淡出过渡 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 200ms ease-out;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
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
