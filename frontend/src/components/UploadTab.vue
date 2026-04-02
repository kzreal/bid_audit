<template>
  <div class="upload-tab h-full flex flex-col">
    <!-- 上方可滚动区域 -->
    <div class="flex-1 overflow-y-auto min-h-0">
      <div class="p-5">
        <!-- 历史项目 -->
        <div class="mb-5">
          <label class="block text-sm font-medium text-black mb-2">历史项目</label>
          <div class="flex gap-2">
            <select
              v-model="selectedProjectId"
              @change="onProjectChange"
              class="flex-1 border border-gray-300 rounded-vercel-sm px-4 py-2.5 text-sm focus:outline-none focus:border-black transition-colors bg-white"
            >
              <option value="">无</option>
              <option v-for="project in projects" :key="project.id" :value="project.id">
                {{ project.name }} ({{ project.fileName }})
              </option>
            </select>
            <button
              v-if="selectedProjectId"
              @click="confirmDeleteProject"
              class="px-3 py-2 border border-gray-300 rounded-vercel-sm text-sm text-gray-600 hover:text-red-500 hover:border-red-500 transition-colors"
              title="删除项目"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
          <p v-if="selectedProjectId && selectedProject" class="mt-1 text-xs text-gray-500">
            最后打开: {{ formatDate(selectedProject.lastOpenedAt) }}
          </p>
        </div>

        <!-- 投标文件上传 -->
        <div class="mb-5">
          <label class="block text-sm font-medium text-black mb-2">投标文件</label>
          <input
            ref="fileInputRef"
            type="file"
            accept=".docx"
            @change="handleFileChange"
            class="hidden"
          />
          <button
            v-if="!uploadedFile"
            @click="triggerFileInput"
            class="inline-flex items-center gap-1.5 text-sm text-vercel-blue hover:text-vercel-blue-hover font-medium transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            选择 .docx 文件
          </button>
        </div>

        <!-- 已上传文件信息（紧凑单行） -->
        <div v-if="uploadedFile" class="mb-4 flex items-center gap-2 text-xs">
          <svg class="w-3.5 h-3.5 text-vercel-blue flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <span class="text-black font-medium truncate">{{ uploadedFile.name }}</span>
          <span class="text-gray-400 flex-shrink-0">{{ formatFileSize(uploadedFile.size) }}</span>
          <button @click="removeFile" class="text-gray-300 hover:text-red-500 transition-colors flex-shrink-0 ml-auto">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <!-- 渐进式：文件上传后且未解析时，显示切片配置 -->
        <template v-if="uploadedFile && !parsed">
          <div class="mb-4 flex items-center gap-3">
            <label class="text-sm font-medium text-black flex-shrink-0">切片层级</label>
            <select
              v-model="selectedSliceLevel"
              class="border border-gray-300 rounded-vercel-sm px-3 py-1.5 text-sm focus:outline-none focus:border-black transition-colors bg-white"
            >
              <option v-for="level in sliceLevels" :key="level.value" :value="level.value">
                {{ level.label }}
              </option>
            </select>
          </div>

          <!-- 开始解析按钮（同时创建项目） -->
          <button
            @click="startParsing"
            :disabled="parsing"
            class="w-full bg-white text-black border border-gray-300 py-2.5 px-6 rounded-vercel-sm text-sm font-semibold transition-all duration-200 disabled:bg-gray-200 disabled:text-gray-500 disabled:cursor-not-allowed hover:bg-gray-50 hover:border-black mb-5"
          >
            <span v-if="parsing" class="inline-flex items-center justify-center">
              <span class="loading-dots mr-2">
                <span></span>
                <span></span>
                <span></span>
              </span>
              解析中...
            </span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              开始解析
            </span>
          </button>
        </template>

        <!-- 解析结果提示 + 保存项目 -->
        <div v-if="parsed" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-vercel-sm">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 text-green-700">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7"></path>
              </svg>
              <span class="text-xs font-medium">已切分为 {{ sliceCount }} 个切片</span>
            </div>
            <button
              @click="saveProjectManual"
              class="text-xs text-green-700 hover:text-black font-medium transition-colors"
            >
              保存项目
            </button>
          </div>
        </div>

        <!-- 消息通知区 -->
        <transition name="fade">
          <div v-if="message" :class="['p-4 rounded-vercel-sm border', messageType === 'error' ? 'bg-red-50 border-red-200 text-red-700' : 'bg-green-50 border-green-200 text-green-700']">
            <p class="text-sm">{{ message }}</p>
          </div>
        </transition>
      </div>
    </div>

    <!-- ═══ 审核要求区（固定在底部，不随上方内容滚动） ═══ -->
    <div v-if="showRequirementSection" class="flex-shrink-0 border-t border-gray-200 bg-white">
      <div class="p-5">
        <h3 class="text-sm font-semibold text-black mb-3">审核要求</h3>

        <!-- 模板库区域 -->
        <div class="mb-3">
          <div class="flex items-center justify-between mb-2">
            <label class="text-xs font-medium text-gray-700">模板库</label>
            <button
              @click="store.openTemplateDrawer()"
              class="text-xs text-vercel-blue hover:text-vercel-blue-hover font-medium transition-colors"
            >
              管理模板
            </button>
          </div>

          <!-- 模板卡片网格 -->
          <div v-if="templates.length > 0" class="grid grid-cols-2 gap-2 mb-2">
            <div
              v-for="template in templates"
              :key="template.id"
              @click="toggleTemplateSelection(template.id)"
              :class="[
                'template-card p-2.5 border rounded-vercel-sm cursor-pointer transition-all duration-200',
                selectedTemplateIds.includes(template.id)
                  ? 'border-vercel-blue bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              ]"
            >
              <div class="flex items-start gap-2">
                <input
                  type="checkbox"
                  :checked="selectedTemplateIds.includes(template.id)"
                  class="mt-0.5 w-3.5 h-3.5 rounded border-gray-300 text-vercel-blue focus:ring-vercel-blue"
                />
                <div class="flex-1 min-w-0">
                  <h4 class="text-xs font-medium text-black truncate">{{ template.name }}</h4>
                  <p class="text-xs text-gray-500 mt-0.5 line-clamp-1">{{ template.description }}</p>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="mb-2 p-3 border border-dashed border-gray-300 rounded-vercel-sm text-center">
            <p class="text-xs text-gray-400">暂无模板，请在下方输入审核要求</p>
          </div>

          <!-- 加载选中模板按钮 -->
          <button
            v-if="selectedTemplateIds.length > 0"
            @click="loadSelectedTemplates"
            class="w-full bg-white text-black border border-gray-300 py-1.5 px-4 rounded-vercel-sm text-xs font-medium transition-all duration-200 hover:bg-gray-50 hover:border-black mb-2"
          >
            加载选中模板 ({{ selectedTemplateIds.length }})
          </button>
        </div>

        <!-- 审核要求输入 -->
        <div class="mb-3">
          <textarea
            v-model="requirementText"
            rows="3"
            placeholder="例如：检查投标文件中的资质证书是否完整、有效期是否合法..."
            class="w-full border border-gray-300 rounded-vercel-sm px-4 py-2.5 text-sm focus:outline-none focus:border-black transition-colors resize-none"
          ></textarea>
        </div>

        <!-- 生成审核任务按钮 -->
        <button
          @click="convertToTasks"
          :disabled="!canConvert || taskLoading"
          class="w-full bg-vercel-blue text-white py-2.5 px-6 rounded-vercel-sm text-sm font-semibold transition-all duration-200 disabled:bg-gray-200 disabled:text-gray-500 disabled:cursor-not-allowed hover:bg-vercel-blue-hover"
        >
          <span v-if="taskLoading" class="inline-flex items-center justify-center">
            <span class="loading-dots mr-2">
              <span></span>
              <span></span>
              <span></span>
            </span>
            生成中...
          </span>
          <span v-else class="flex items-center justify-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
            生成审核任务
          </span>
        </button>
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

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useAppStore } from '../stores/appStore'
import { getAllProjects, getProjectById, saveProject, deleteProject, updateLastOpened } from '../services/projectService'
import { getAllTemplates, saveTemplate, getTemplateById, deleteTemplate as deleteTemplateService } from '../services/templateService'
import TemplateDrawer from './TemplateDrawer.vue'
import TemplateEditor from './TemplateEditor.vue'

const store = useAppStore()

// === 项目相关状态 ===
const projectName = ref('')
const uploadedFile = ref(null)
const selectedSliceLevel = ref(1)
const dragOver = ref(false)
const parsing = ref(false)
const parsed = ref(false)
const sliceCount = ref(0)
const message = ref('')
const messageType = ref('info')
const fileInputRef = ref(null)
const selectedProjectId = ref('')
const projects = ref([])

// === 任务相关状态 ===
const requirementText = ref('')
const selectedTemplateIds = ref([])
const taskLoading = ref(false)
const editorOpen = ref(false)
const allTemplates = reactive([])

const sliceLevels = [
  { value: 0, label: '零级' },
  { value: 1, label: '一级' },
  { value: 2, label: '二级' },
  { value: 3, label: '三级' },
  { value: -1, label: '全部' }
]

// 是否显示审核要求区（项目存在且解析完成）
const showRequirementSection = computed(() => {
  return store.currentProjectId && parsed.value
})

// 模板列表（有任务时隐藏模板）
const templates = computed(() => {
  return store.tasks.length > 0 ? [] : allTemplates
})

const canConvert = computed(() => {
  return requirementText.value.trim() || selectedTemplateIds.value.length > 0
})

// 选中的项目对象
const selectedProject = computed(() => {
  if (!selectedProjectId.value) return null
  return projects.value.find(p => p.id === selectedProjectId.value) || null
})

// 加载项目列表
const loadProjects = () => {
  projects.value = getAllProjects()
}

// 加载模板列表
const loadTemplates = () => {
  allTemplates.splice(0, allTemplates.length)
  allTemplates.push(...getAllTemplates())
}

// 选择项目时触发
const onProjectChange = () => {
  const projectId = selectedProjectId.value
  if (!projectId) {
    resetForm()
    return
  }

  const project = getProjectById(projectId)
  if (project) {
    projectName.value = project.name
    selectedSliceLevel.value = project.sliceLevel || 0
    sliceCount.value = project.sliceCount || 0

    if (project.slices && project.slices.length > 0) {
      store.setBidSlices(project.slices)
      store.setSliceMetadata(project.sliceMetadata || [])
      parsed.value = true
    }

    store.setCurrentProjectId(projectId)
    updateLastOpened(projectId)
    showMessage(`已加载项目: ${project.name}`, 'success')
  }
}

const resetForm = () => {
  projectName.value = ''
  uploadedFile.value = null
  selectedSliceLevel.value = 1
  parsed.value = false
  sliceCount.value = 0
  store.setBidSlices([])
  store.setSliceMetadata([])
  store.setWordDocument(null)
  store.setCurrentProjectId(null)
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

const confirmDeleteProject = () => {
  if (!selectedProjectId.value) return
  const project = selectedProject.value
  if (!project) return

  if (confirm(`确定要删除项目"${project.name}"吗？`)) {
    deleteProject(project.id)
    store.deleteProject(project.id)
    selectedProjectId.value = ''
    resetForm()
    loadProjects()
    showMessage('项目已删除', 'success')
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadProjects()
  loadTemplates()
  restoreFromStore()
})

watch(() => store.currentTab, (newTab) => {
  if (newTab === 'upload') {
    restoreFromStore()
  }
})

const restoreFromStore = () => {
  if (store.currentProjectId) {
    selectedProjectId.value = store.currentProjectId
    projectName.value = store.projectName || ''
    selectedSliceLevel.value = store.sliceLevel || 0
    sliceCount.value = store.bidSlices?.length || 0
    parsed.value = store.bidSlices?.length > 0
  }
}

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleDrop = (e) => {
  dragOver.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) {
    selectFile(files[0])
  }
}

const handleFileChange = (e) => {
  const files = e.target.files
  if (files.length > 0) {
    selectFile(files[0])
  }
}

const selectFile = (file) => {
  if (!file.name.endsWith('.docx')) {
    showMessage('请上传 .docx 格式的文件', 'error')
    return
  }

  // 新建项目时自动填充项目名称
  const fileNameWithoutExt = file.name.replace(/\.docx$/i, '')
  if (!selectedProjectId.value && !projectName.value.trim() && fileNameWithoutExt) {
    projectName.value = fileNameWithoutExt
  }

  uploadedFile.value = file
  store.setWordDocument(file)
  parsed.value = false
  sliceCount.value = 0
}

// 开始解析（同时自动创建项目）
const startParsing = async () => {
  if (!uploadedFile.value) return

  // 新建项目时弹出输入框确认名称
  if (!selectedProjectId.value) {
    const defaultName = projectName.value || uploadedFile.value.name.replace(/\.docx$/i, '') || '未命名项目'
    const inputName = prompt('请输入项目名称：', defaultName)
    if (!inputName || !inputName.trim()) return
    projectName.value = inputName.trim()
  }

  parsing.value = true
  message.value = ''
  try {
    const level = selectedSliceLevel.value === -1 ? 999 : selectedSliceLevel.value
    const slices = await store.sliceDocument(uploadedFile.value, level)

    if (slices && slices.length > 0) {
      sliceCount.value = slices.length
      parsed.value = true

      // 自动创建/更新项目
      store.setProjectName(projectName.value)
      store.setSliceLevel(selectedSliceLevel.value)

      const projectData = {
        id: selectedProjectId.value || undefined,
        name: projectName.value,
        fileName: uploadedFile.value?.name || '',
        fileSize: uploadedFile.value?.size || 0,
        sliceLevel: selectedSliceLevel.value,
        sliceCount: slices.length,
        slices: store.bidSlices,
        sliceMetadata: store.sliceMetadata
      }

      const saved = saveProject(projectData)
      selectedProjectId.value = saved.id
      store.setCurrentProjectId(saved.id)
      loadProjects()

      showMessage('解析完成，请在下方输入审核要求', 'success')
    } else {
      showMessage('解析成功，但未能提取切片内容', 'info')
      parsed.value = true
      sliceCount.value = 0
    }
  } catch (error) {
    console.error('解析 docx 文件失败:', error)
    showMessage('解析失败: ' + error.message, 'error')
    parsed.value = false
  } finally {
    parsing.value = false
  }
}

const removeFile = () => {
  uploadedFile.value = null
  parsed.value = false
  sliceCount.value = 0
  store.setWordDocument(null)
  store.setBidSlices([])
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

// 手动保存项目（弹出输入框让用户确认项目名称）
const saveProjectManual = () => {
  const defaultName = projectName.value || uploadedFile.value?.name?.replace(/\.docx$/i, '') || '未命名项目'
  const inputName = prompt('请输入项目名称：', defaultName)
  if (!inputName || !inputName.trim()) return

  projectName.value = inputName.trim()
  store.setProjectName(projectName.value)
  store.setSliceLevel(selectedSliceLevel.value)

  const projectData = {
    id: selectedProjectId.value || undefined,
    name: projectName.value,
    fileName: uploadedFile.value?.name || '',
    fileSize: uploadedFile.value?.size || 0,
    sliceLevel: selectedSliceLevel.value,
    sliceCount: sliceCount.value,
    slices: store.bidSlices,
    sliceMetadata: store.sliceMetadata
  }

  const saved = saveProject(projectData)
  selectedProjectId.value = saved.id
  store.setCurrentProjectId(saved.id)
  loadProjects()
  showMessage('项目已保存', 'success')
}

const showMessage = (msg, type = 'info') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 3000)
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// === 任务相关方法 ===

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
  setTimeout(() => {
    store.setCurrentTab('task-list')
  }, 500)
}

const convertToTasks = async () => {
  if (!canConvert.value) return

  taskLoading.value = true
  try {
    if (requirementText.value.trim()) {
      store.setRequirement(requirementText.value)
      await store.generateTasks()
      showMessage('任务生成成功', 'success')
      setTimeout(() => {
        store.setCurrentTab('task-list')
      }, 500)
    }
  } catch (error) {
    showMessage('任务生成失败: ' + error.message, 'error')
  } finally {
    taskLoading.value = false
  }
}

// === 模板管理方法 ===

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
    deleteTemplateService(id)
    loadTemplates()
  }
}
</script>

<style scoped>
.upload-zone {
  transition: all 0.2s ease;
}
</style>
