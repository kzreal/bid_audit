<template>
  <teleport to="body">
    <!-- 遮罩层 -->
    <transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 bg-black/30 backdrop-blur-sm z-40"
        @click="$emit('cancel')"
      ></div>
    </transition>

    <!-- 编辑器弹窗 -->
    <transition name="zoom">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
          <!-- 头部 -->
          <header class="border-b border-gray-100 p-6 flex-shrink-0">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-xl font-semibold text-gray-800">
                  {{ template ? '编辑模版' : '新建模版' }}
                </h2>
                <p class="text-sm text-gray-500 mt-1">
                  {{ template ? '修改模版内容和设置' : '创建新的审核模版' }}
                </p>
              </div>
              <button
                @click="$emit('cancel')"
                class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>

            <!-- 模式切换 -->
            <div v-if="!template" class="mt-6 flex items-center gap-2">
              <button
                @click="mode = 'manual'"
                :class="mode === 'manual' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
                class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
                手动创建
              </button>
              <button
                @click="mode = 'from-project'"
                :class="mode === 'from-project' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
                class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                :disabled="existingTasks.length === 0"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path>
                </svg>
                从项目生成
              </button>
            </div>
          </header>

          <!-- 内容区域 -->
          <div class="flex-1 overflow-y-auto p-6">
            <!-- 手动创建模式 -->
            <div v-if="mode === 'manual'" class="space-y-6">
              <!-- 基本信息 -->
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">模版名称 *</label>
                  <input
                    v-model="templateData.name"
                    type="text"
                    placeholder="例如：基础审核模版"
                    class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                  >
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">描述</label>
                  <textarea
                    v-model="templateData.description"
                    rows="2"
                    placeholder="简要描述这个模版的用途"
                    class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all resize-none"
                  ></textarea>
                </div>
              </div>

              <!-- 标签选择 -->
              <template-tag-selector
                v-model="templateData.tags"
                :tags="allTags"
                :show-suggestions="true"
              />

              <!-- 任务列表 -->
              <div>
                <div class="flex items-center justify-between mb-3">
                  <label class="block text-sm font-medium text-gray-700">审核任务</label>
                  <button
                    @click="addTask"
                    class="flex items-center gap-1.5 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                    </svg>
                    添加任务
                  </button>
                </div>
                <div class="space-y-2">
                  <div
                    v-for="(task, index) in templateData.tasks"
                    :key="task.id"
                    :draggable="true"
                    @dragstart="handleDragStart(index)"
                    @dragover="handleDragOver"
                    @drop="handleDrop(index)"
                    class="group flex items-start gap-3 p-4 bg-gray-50 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
                  >
                    <!-- 拖拽手柄 -->
                    <div class="cursor-move p-1 text-gray-400 hover:text-gray-600 transition-colors">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16"></path>
                      </svg>
                    </div>

                    <!-- 任务内容 -->
                    <div class="flex-1">
                      <input
                        v-model="task.title"
                        type="text"
                        placeholder="输入审核任务"
                        class="w-full px-3 py-2 bg-white border border-gray-200 rounded text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                      >
                    </div>

                    <!-- 删除按钮 -->
                    <button
                      @click="removeTask(index)"
                      class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 从项目生成模式 -->
            <div v-else-if="mode === 'from-project'" class="space-y-6">
              <!-- 基本信息 -->
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">模版名称 *</label>
                  <input
                    v-model="templateData.name"
                    type="text"
                    placeholder="例如：基础审核模版"
                    class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
                  >
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">描述</label>
                  <textarea
                    v-model="templateData.description"
                    rows="2"
                    placeholder="简要描述这个模版的用途"
                    class="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all resize-none"
                  ></textarea>
                </div>
              </div>

              <!-- 标签选择 -->
              <template-tag-selector
                v-model="templateData.tags"
                :tags="allTags"
                :show-suggestions="true"
              />

              <!-- 选择任务 -->
              <div>
                <div class="flex items-center justify-between mb-3">
                  <label class="block text-sm font-medium text-gray-700">选择要保存的任务</label>
                  <button
                    @click="toggleAllTasks"
                    class="text-sm text-blue-600 hover:text-blue-700 font-medium"
                  >
                    {{ allTasksSelected ? '取消全选' : '全选' }}
                  </button>
                </div>

                <div v-if="existingTasks.length === 0" class="text-center py-8 bg-gray-50 rounded-lg">
                  <svg class="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  <p class="text-sm text-gray-400">暂无任务可选</p>
                  <p class="text-xs text-gray-400 mt-1">先生成或添加一些任务</p>
                </div>

                <div v-else class="space-y-2 max-h-[300px] overflow-y-auto">
                  <label
                    v-for="task in existingTasks"
                    :key="task.id"
                    class="flex items-start gap-3 p-3 bg-gray-50 border border-gray-200 rounded-lg cursor-pointer hover:border-blue-300 transition-colors"
                  >
                    <input
                      type="checkbox"
                      v-model="selectedTaskIds"
                      :value="task.id"
                      class="mt-1 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    >
                    <div class="flex-1">
                      <p class="text-sm font-medium text-gray-800">{{ task.title }}</p>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- 底部按钮 -->
          <footer class="border-t border-gray-100 p-6 flex justify-end gap-3 flex-shrink-0">
            <button
              @click="$emit('cancel')"
              class="px-6 py-2.5 text-gray-600 hover:bg-gray-100 rounded-lg text-sm font-medium transition-colors"
            >
              取消
            </button>
            <button
              @click="handleSave"
              :disabled="!canSave"
              class="px-6 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed"
            >
              保存
            </button>
          </footer>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { getAllTags, createTemplateFromTasks } from '../services/templateService'
import { useAppStore } from '../stores/appStore'
import TemplateTagSelector from './TemplateTagSelector.vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  template: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['save', 'cancel'])

const store = useAppStore()

// 编辑模式：manual（手动创建）或 from-project（从项目生成）
const mode = ref('manual')

// 模版数据
const templateData = ref({
  name: '',
  description: '',
  tags: [],
  tasks: []
})

// 选中的任务 ID（从项目生成模式）
const selectedTaskIds = ref([])

// 拖拽相关
let draggedIndex = null

// 现有任务（从项目生成模式）
const existingTasks = computed(() => store.tasks)

// 所有可用标签
const allTags = computed(() => getAllTags())

// 是否全选
const allTasksSelected = computed(() => {
  return existingTasks.value.length > 0 &&
    selectedTaskIds.value.length === existingTasks.value.length
})

// 是否可以保存
const canSave = computed(() => {
  if (!templateData.value.name.trim()) return false

  if (mode.value === 'manual') {
    return templateData.value.tasks.some(t => t.title.trim())
  } else {
    return selectedTaskIds.value.length > 0
  }
})

// 监听 open 变化，重置表单
watch(() => props.open, (isOpen) => {
  if (isOpen) {
    if (props.template) {
      // 编辑模式：填充现有数据
      templateData.value = {
        name: props.template.name,
        description: props.template.description || '',
        tags: [...(props.template.tags || [])],
        tasks: (props.template.tasks || []).map(t => ({
          id: `task_${Date.now()}_${Math.random()}`,
          title: typeof t === 'string' ? t : t.title
        }))
      }
      mode.value = 'manual'
    } else {
      // 新建模式：重置表单
      templateData.value = {
        name: '',
        description: '',
        tags: [],
        tasks: []
      }
      selectedTaskIds.value = []
      // 如果没有现有任务，默认为手动创建
      if (existingTasks.value.length > 0) {
        mode.value = 'from-project'
      } else {
        mode.value = 'manual'
      }
    }
  }
})

// 添加任务
function addTask() {
  templateData.value.tasks.push({
    id: `task_${Date.now()}_${Math.random()}`,
    title: ''
  })
}

// 移除任务
function removeTask(index) {
  templateData.value.tasks.splice(index, 1)
}

// 全选/取消全选
function toggleAllTasks() {
  if (allTasksSelected.value) {
    selectedTaskIds.value = []
  } else {
    selectedTaskIds.value = existingTasks.value.map(t => t.id)
  }
}

// 拖拽开始
function handleDragStart(index) {
  draggedIndex = index
}

// 拖拽经过
function handleDragOver(e) {
  e.preventDefault()
}

// 拖拽放置
function handleDrop(index) {
  if (draggedIndex === null || draggedIndex === index) return

  const tasks = [...templateData.value.tasks]
  const [removed] = tasks.splice(draggedIndex, 1)
  tasks.splice(index, 0, removed)

  templateData.value.tasks = tasks
  draggedIndex = null
}

// 保存模版
function handleSave() {
  if (!canSave.value) return

  const saveData = {
    id: props.template?.id,
    name: templateData.value.name,
    description: templateData.value.description,
    tags: templateData.value.tags
  }

  if (mode.value === 'manual') {
    // 手动创建：使用编辑的任务
    saveData.tasks = templateData.value.tasks
      .filter(t => t.title.trim())
      .map(t => t.title.trim())
  } else {
    // 从项目生成：使用选中的任务
    const selectedTasks = existingTasks.value.filter(t => selectedTaskIds.value.includes(t.id))
    saveData.tasks = selectedTasks.map(t => t.title)
  }

  emit('save', saveData)
}
</script>

<style scoped>
/* 淡入淡出 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 缩放 */
.zoom-enter-active,
.zoom-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.zoom-enter-from,
.zoom-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* 焦点样式 */
input:focus,
textarea:focus {
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}
</style>
