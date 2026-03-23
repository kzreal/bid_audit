<template>
  <div class="task-list-tab p-5">
    <!-- 头部操作区 -->
    <div class="mb-5 flex items-center justify-between gap-3">
      <div class="flex-1">
        <h3 class="text-sm font-semibold text-black">
          任务列表
          <span class="text-gray-400 font-normal ml-2">{{ tasks.length }} 个任务</span>
        </h3>
      </div>
      <div class="flex items-center gap-2">
        <!-- 撤销按钮 -->
        <button
          v-if="store.canUndoTemplateApplication"
          @click="handleUndoTemplate"
          class="bg-white text-black border border-gray-300 px-3 py-1.5 rounded-vercel-sm text-xs font-medium transition-all duration-200 hover:bg-gray-50 hover:border-black"
        >
          <svg class="w-3.5 h-3.5 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"></path>
          </svg>
          撤销
        </button>
        <!-- 全部审核按钮 -->
        <button
          @click="handleReviewAll"
          :disabled="loading || unreviewedTasks.length === 0"
          class="bg-vercel-blue text-white px-3 py-1.5 rounded-vercel-sm text-xs font-semibold transition-all duration-200 disabled:bg-gray-200 disabled:text-gray-500 disabled:cursor-not-allowed hover:bg-vercel-blue-hover"
        >
          <span v-if="loading" class="inline-flex items-center">
            <span class="loading-dots-mini mr-1.5">
              <span></span>
              <span></span>
              <span></span>
            </span>
            审核中...
          </span>
          <span v-else>
            全部审核 ({{ unreviewedTasks.length }})
          </span>
        </button>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="tasks.length === 0" class="text-center py-12">
      <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
      </svg>
      <p class="text-gray-500 text-sm mb-4">暂无任务</p>
      <button
        @click="store.setCurrentTab('create-task')"
        class="text-sm text-vercel-blue hover:text-vercel-blue-hover font-medium transition-colors"
      >
        去创建任务
      </button>
    </div>

    <!-- 任务列表 -->
    <div v-else class="space-y-2">
      <transition-group name="task-list">
        <div
          v-for="task in tasks"
          :key="task.id"
          @click="handleSelectTask(task.id)"
          :class="[
            'task-item p-4 border rounded-vercel-sm cursor-pointer transition-all duration-200',
            selectedTaskId === task.id
              ? 'border-vercel-blue bg-blue-50'
              : 'border-gray-200 hover:border-gray-300'
          ]"
        >
          <div class="flex items-start gap-3">
            <!-- 复选框 -->
            <input
              type="checkbox"
              :checked="selectedTaskIds.includes(task.id)"
              @click.stop
              @change="toggleTaskSelection(task.id)"
              class="mt-1 w-4 h-4 rounded border-gray-300 text-vercel-blue focus:ring-vercel-blue"
            />

            <!-- 任务内容 -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-2">
                <h4 class="text-sm font-medium text-black leading-relaxed">{{ task.title }}</h4>
                <!-- 状态标签 -->
                <span
                  v-if="task.review"
                  :class="[
                    'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium flex-shrink-0',
                    task.review.conclusion === '通过' ? 'bg-green-100 text-green-700' :
                    task.review.conclusion === '不通过' ? 'bg-red-100 text-red-700' :
                    'bg-yellow-100 text-yellow-700'
                  ]"
                >
                  {{ task.review.conclusion }}
                </span>
                <span
                  v-else
                  class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600 flex-shrink-0"
                >
                  待审核
                </span>
              </div>

              <!-- 审核原因（如果已审核） -->
              <p v-if="task.review?.reason" class="text-xs text-gray-500 mt-2 line-clamp-2">
                {{ task.review.reason }}
              </p>

              <!-- 时间 -->
              <p class="text-xs text-gray-400 mt-2">
                {{ formatTime(task.createdAt) }}
              </p>
            </div>
          </div>
        </div>
      </transition-group>
    </div>

    <!-- 底部操作栏 -->
    <div v-if="tasks.length > 0" class="mt-5 pt-4 border-t border-gray-200 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <label class="flex items-center gap-2 text-xs text-gray-600 cursor-pointer">
          <input
            type="checkbox"
            :checked="isAllSelected"
            :indeterminate="isPartiallySelected"
            @change="toggleSelectAll"
            class="w-4 h-4 rounded border-gray-300 text-vercel-blue focus:ring-vercel-blue"
          />
          全选
        </label>
        <span class="text-xs text-gray-400">{{ selectedTaskIds.length }} 已选</span>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="deleteSelectedTasks"
          :disabled="selectedTaskIds.length === 0"
          class="px-3 py-1.5 text-xs font-medium text-red-600 hover:text-red-700 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          删除选中
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAppStore } from '../stores/appStore'

const store = useAppStore()

const selectedTaskIds = ref([])
const loading = computed(() => store.loading)

const tasks = computed(() => store.tasks)
const selectedTaskId = computed(() => store.selectedTaskId)

const unreviewedTasks = computed(() => {
  return tasks.value.filter(t => !t.review)
})

const isAllSelected = computed(() => {
  return tasks.value.length > 0 && selectedTaskIds.value.length === tasks.value.length
})

const isPartiallySelected = computed(() => {
  return selectedTaskIds.value.length > 0 && selectedTaskIds.value.length < tasks.value.length
})

const formatTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleString('zh-CN')
}

const handleSelectTask = async (taskId) => {
  store.selectTask(taskId)

  // 如果任务未审核，自动开始审核
  const task = tasks.value.find(t => t.id === taskId)
  if (task && !task.review && !loading.value) {
    try {
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

const toggleTaskSelection = (taskId) => {
  const index = selectedTaskIds.value.indexOf(taskId)
  if (index === -1) {
    selectedTaskIds.value.push(taskId)
  } else {
    selectedTaskIds.value.splice(index, 1)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedTaskIds.value = []
  } else {
    selectedTaskIds.value = tasks.value.map(t => t.id)
  }
}

const deleteSelectedTasks = () => {
  if (selectedTaskIds.value.length === 0) return
  if (confirm(`确定要删除选中的 ${selectedTaskIds.value.length} 个任务吗？`)) {
    // 从 store 中删除选中的任务
    selectedTaskIds.value.forEach(id => {
      const index = store.tasks.findIndex(t => t.id === id)
      if (index !== -1) {
        store.tasks.splice(index, 1)
      }
    })
    selectedTaskIds.value = []
  }
}

const handleUndoTemplate = () => {
  store.undoTemplateApplication()
}

const handleReviewAll = async () => {
  const unreviewed = tasks.value.filter(t => !t.review)
  for (const task of unreviewed) {
    try {
      store.selectTask(task.id)
      if (store.useSliceReview) {
        await store.reviewTaskWithSlices(task.id)
      } else {
        await store.reviewTask(task.id)
      }
    } catch (error) {
      console.error(`审核任务 ${task.id} 失败:`, error)
    }
  }
}
</script>

<style scoped>
.task-list-enter-active,
.task-list-leave-active {
  transition: all 0.3s ease;
}

.task-list-enter-from,
.task-list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>
