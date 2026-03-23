<template>
  <div class="upload-tab p-5">
    <!-- 项目名称 -->
    <div class="mb-5">
      <label class="block text-sm font-medium text-black mb-2">项目名称</label>
      <input
        v-model="projectName"
        type="text"
        placeholder="请输入项目名称"
        class="w-full border border-gray-300 rounded-vercel-sm px-4 py-2.5 text-sm focus:outline-none focus:border-black transition-colors"
      />
    </div>

    <!-- 文件上传区 -->
    <div class="mb-5">
      <label class="block text-sm font-medium text-black mb-2">投标文件</label>
      <div
        @drop.prevent="handleDrop"
        @dragover.prevent="dragOver = true"
        @dragleave.prevent="dragOver = false"
        @click="triggerFileInput"
        :class="[
          'upload-zone border-2 border-dashed rounded-vercel-sm p-8 text-center cursor-pointer transition-all duration-200',
          dragOver ? 'border-vercel-blue bg-blue-50' : 'border-gray-300 hover:border-vercel-blue'
        ]"
      >
        <input
          ref="fileInputRef"
          type="file"
          accept=".docx"
          @change="handleFileChange"
          class="hidden"
        />
        <svg class="w-10 h-10 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
        </svg>
        <p class="text-sm text-gray-600 mb-1">拖拽文件到此处，或点击上传</p>
        <p class="text-xs text-gray-400">支持 .docx 格式</p>
      </div>
    </div>

    <!-- 已上传文件信息 -->
    <div v-if="uploadedFile" class="mb-5 p-4 bg-gray-50 border border-gray-200 rounded-vercel-sm">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <svg class="w-5 h-5 text-vercel-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <div>
            <p class="text-sm font-medium text-black">{{ uploadedFile.name }}</p>
            <p class="text-xs text-gray-500">{{ formatFileSize(uploadedFile.size) }}</p>
          </div>
        </div>
        <button @click="removeFile" class="text-gray-400 hover:text-red-500 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    </div>

    <!-- 切片层级选择 -->
    <div class="mb-5">
      <label class="block text-sm font-medium text-black mb-2">切片层级</label>
      <div class="grid grid-cols-5 gap-2">
        <button
          v-for="level in sliceLevels"
          :key="level.value"
          @click="selectedSliceLevel = level.value"
          :class="[
            'py-2 px-3 text-xs font-medium rounded-vercel-sm border transition-all duration-200',
            selectedSliceLevel === level.value
              ? 'bg-vercel-blue text-white border-vercel-blue'
              : 'bg-white text-gray-700 border-gray-300 hover:border-vercel-blue'
          ]"
        >
          {{ level.label }}
        </button>
      </div>
    </div>

    <!-- 开始解析按钮 -->
    <button
      v-if="uploadedFile && !parsed"
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

    <!-- 解析结果提示 -->
    <div v-if="parsed" class="mb-5 p-4 bg-green-50 border border-green-200 rounded-vercel-sm">
      <div class="flex items-center gap-2 text-green-700">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 13l4 4L19 7"></path>
        </svg>
        <span class="text-sm font-medium">解析完成，已切分为 {{ sliceCount }} 个切片</span>
      </div>
    </div>

    <!-- 消息通知区 -->
    <transition name="fade">
      <div v-if="message" :class="['mb-5 p-4 rounded-vercel-sm border', messageType === 'error' ? 'bg-red-50 border-red-200 text-red-700' : 'bg-green-50 border-green-200 text-green-700']">
        <p class="text-sm">{{ message }}</p>
      </div>
    </transition>

    <!-- 创建项目按钮 -->
    <button
      @click="createProject"
      :disabled="!canCreate || loading"
      class="w-full bg-vercel-blue text-white py-2.5 px-6 rounded-vercel-sm text-sm font-semibold transition-all duration-200 disabled:bg-gray-200 disabled:text-gray-500 disabled:cursor-not-allowed hover:bg-vercel-blue-hover focus:outline-none focus:ring-2 focus:ring-vercel-blue-light"
    >
      <span v-if="loading" class="inline-flex items-center justify-center">
        <span class="loading-dots mr-2">
          <span></span>
          <span></span>
          <span></span>
        </span>
        处理中...
      </span>
      <span v-else class="flex items-center justify-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
        </svg>
        创建项目
      </span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAppStore } from '../stores/appStore'

const store = useAppStore()

const projectName = ref('')
const uploadedFile = ref(null)
const selectedSliceLevel = ref(0)
const dragOver = ref(false)
const loading = ref(false)
const parsing = ref(false)
const parsed = ref(false)
const sliceCount = ref(0)
const message = ref('')
const messageType = ref('info')
const fileInputRef = ref(null)

const sliceLevels = [
  { value: 0, label: '零级' },
  { value: 1, label: '一级' },
  { value: 2, label: '二级' },
  { value: 3, label: '三级' },
  { value: -1, label: '全部' }
]

const canCreate = computed(() => {
  return projectName.value.trim() && uploadedFile.value && parsed.value
})

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
  uploadedFile.value = file
  store.setWordDocument(file)
  parsed.value = false
  sliceCount.value = 0
}

const startParsing = async () => {
  if (!uploadedFile.value) return

  parsing.value = true
  message.value = ''
  try {
    const level = selectedSliceLevel.value === -1 ? 999 : selectedSliceLevel.value
    const slices = await store.sliceDocument(uploadedFile.value, level)

    if (slices && slices.length > 0) {
      sliceCount.value = slices.length
      parsed.value = true
      showMessage(`解析成功，已切分为 ${slices.length} 个切片`, 'success')
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

const createProject = async () => {
  if (!canCreate.value) return

  loading.value = true
  try {
    // 保存项目配置到 store
    store.setProjectName(projectName.value)
    store.setSliceLevel(selectedSliceLevel.value)
    showMessage('项目创建成功', 'success')

    // 切换到创建任务 Tab
    setTimeout(() => {
      store.setCurrentTab('create-task')
    }, 500)
  } catch (error) {
    showMessage('项目创建失败: ' + error.message, 'error')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.upload-zone {
  transition: all 0.2s ease;
}
</style>
