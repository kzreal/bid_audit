<template>
  <div class="create-task-tab p-5">
    <!-- 模板库区域 -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-3">
        <label class="text-sm font-medium text-black">模板库</label>
        <button
          @click="store.openTemplateDrawer()"
          class="text-xs text-vercel-blue hover:text-vercel-blue-hover font-medium transition-colors"
        >
          管理模板
        </button>
      </div>

      <!-- 模板卡片网格 -->
      <div v-if="templates.length > 0" class="grid grid-cols-2 gap-3 mb-4">
        <div
          v-for="template in templates"
          :key="template.id"
          @click="toggleTemplateSelection(template.id)"
          :class="[
            'template-card p-3 border rounded-vercel-sm cursor-pointer transition-all duration-200',
            selectedTemplateIds.includes(template.id)
              ? 'border-vercel-blue bg-blue-50'
              : 'border-gray-200 hover:border-gray-300'
          ]"
        >
          <div class="flex items-start gap-2">
            <input
              type="checkbox"
              :checked="selectedTemplateIds.includes(template.id)"
              class="mt-1 w-4 h-4 rounded border-gray-300 text-vercel-blue focus:ring-vercel-blue"
            />
            <div class="flex-1 min-w-0">
              <h4 class="text-sm font-medium text-black truncate">{{ template.name }}</h4>
              <p class="text-xs text-gray-500 mt-1 line-clamp-2">{{ template.description }}</p>
              <div class="flex flex-wrap gap-1 mt-2">
                <span
                  v-for="tag in template.tags?.slice(0, 2)"
                  :key="tag"
                  class="inline-block px-1.5 py-0.5 text-xs bg-gray-100 text-gray-600 rounded"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="mb-4 p-6 border border-dashed border-gray-300 rounded-vercel-sm text-center">
        <svg class="w-8 h-8 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
        </svg>
        <p class="text-sm text-gray-500">暂无模板</p>
        <p class="text-xs text-gray-400 mt-1">点击上方按钮创建模板</p>
      </div>

      <!-- 加载选中模板按钮 -->
      <button
        v-if="selectedTemplateIds.length > 0"
        @click="loadSelectedTemplates"
        class="w-full bg-white text-black border border-gray-300 py-2 px-4 rounded-vercel-sm text-sm font-medium transition-all duration-200 hover:bg-gray-50 hover:border-black mb-3"
      >
        加载选中模板 ({{ selectedTemplateIds.length }})
      </button>
    </div>

    <!-- 分隔线 -->
    <div class="divider border-t border-gray-200 my-5"></div>

    <!-- 自然语言输入区 -->
    <div class="mb-5">
      <label class="block text-sm font-medium text-black mb-2">
        或输入审核要求
        <span class="text-xs text-gray-400 font-normal ml-2">AI 将自动转换为任务</span>
      </label>
      <textarea
        v-model="requirementText"
        rows="4"
        placeholder="例如：检查投标文件中的资质证书是否完整、有效期是否合法..."
        class="w-full border border-gray-300 rounded-vercel-sm px-4 py-2.5 text-sm focus:outline-none focus:border-black transition-colors resize-none"
      ></textarea>
    </div>

    <!-- 消息通知区 -->
    <transition name="fade">
      <div v-if="message" :class="['mb-5 p-4 rounded-vercel-sm border', messageType === 'error' ? 'bg-red-50 border-red-200 text-red-700' : 'bg-green-50 border-green-200 text-green-700']">
        <p class="text-sm">{{ message }}</p>
      </div>
    </transition>

    <!-- AI转换按钮 -->
    <button
      @click="convertToTasks"
      :disabled="!canConvert || loading"
      class="w-full bg-vercel-blue text-white py-2.5 px-6 rounded-vercel-sm text-sm font-semibold transition-all duration-200 disabled:bg-gray-200 disabled:text-gray-500 disabled:cursor-not-allowed hover:bg-vercel-blue-hover focus:outline-none focus:ring-2 focus:ring-vercel-blue-light"
    >
      <span v-if="loading" class="inline-flex items-center justify-center">
        <span class="loading-dots mr-2">
          <span></span>
          <span></span>
          <span></span>
        </span>
        AI 转换中...
      </span>
      <span v-else class="flex items-center justify-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
        </svg>
        AI 转换为任务
      </span>
    </button>

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

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useAppStore } from '../stores/appStore'
import { getAllTemplates, saveTemplate, getTemplateById, deleteTemplate } from '../services/templateService'
import TemplateDrawer from './TemplateDrawer.vue'
import TemplateEditor from './TemplateEditor.vue'

const store = useAppStore()

const requirementText = ref('')
const selectedTemplateIds = ref([])
const loading = ref(false)
const message = ref('')
const messageType = ref('info')
const editorOpen = ref(false)
const allTemplates = reactive([])

// 加载模板列表
const loadTemplates = () => {
  allTemplates.splice(0, allTemplates.length)
  allTemplates.push(...getAllTemplates())
}

onMounted(() => {
  loadTemplates()
})

const templates = computed(() => {
  return store.tasks.length > 0 ? [] : allTemplates
})

const canConvert = computed(() => {
  return requirementText.value.trim() || selectedTemplateIds.value.length > 0
})

const toggleTemplateSelection = (templateId) => {
  const index = selectedTemplateIds.value.indexOf(templateId)
  if (index === -1) {
    selectedTemplateIds.value.push(templateId)
  } else {
    selectedTemplateIds.value.splice(index, 1)
  }
}

const loadSelectedTemplates = () => {
  selectedTemplateIds.value.forEach(id => {
    const template = getTemplateById(id)
    if (template) {
      store.applyTemplate(template)
    }
  })
  showMessage(`已加载 ${selectedTemplateIds.value.length} 个模板`, 'success')
  selectedTemplateIds.value = []
  // 切换到任务列表 Tab
  setTimeout(() => {
    store.setCurrentTab('task-list')
  }, 500)
}

const convertToTasks = async () => {
  if (!canConvert.value) return

  loading.value = true
  try {
    if (requirementText.value.trim()) {
      store.setRequirement(requirementText.value)
      await store.generateTasks()
      showMessage('任务生成成功', 'success')
      // 切换到任务列表 Tab
      setTimeout(() => {
        store.setCurrentTab('task-list')
      }, 500)
    }
  } catch (error) {
    showMessage('任务生成失败: ' + error.message, 'error')
  } finally {
    loading.value = false
  }
}

const showMessage = (msg, type = 'info') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 3000)
}

// 模板相关处理
function handleCreateTemplate() {
  store.clearCurrentEditingTemplate()
  editorOpen.value = true
}

function handleEditTemplate(id) {
  const template = getTemplateById(id)
  if (template) {
    store.setCurrentEditingTemplate(template)
    editorOpen.value = true
  }
}

function handleSaveTemplate(templateData) {
  saveTemplate(templateData)
  editorOpen.value = false
  store.clearCurrentEditingTemplate()
  loadTemplates()
}

function handleApplyTemplate(id) {
  const template = getTemplateById(id)
  if (template) {
    store.applyTemplate(template)
    store.closeTemplateDrawer()
    showMessage('模板应用成功', 'success')
  }
}

function handleDeleteTemplate(id) {
  if (confirm('确定要删除这个模板吗？')) {
    deleteTemplate(id)
    loadTemplates()
  }
}
</script>
