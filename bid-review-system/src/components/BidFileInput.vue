<template>
  <div class="mb-6">
    <label class="block text-gray-700 text-sm font-medium mb-2">
      投标文件切片 (Markdown) - 最多 30 个文件
    </label>

    <!-- 文件上传区域 -->
    <div
      class="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-gray-400 transition-colors mb-3"
      @drop="handleDrop"
      @dragover.prevent
      @dragenter.prevent
    >
      <input
        type="file"
        ref="fileInput"
        accept=".md,.txt"
        multiple
        @change="handleFileSelect"
        class="hidden"
      />
      <svg class="w-8 h-8 mx-auto mb-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
      </svg>
      <p class="text-xs text-gray-600">
        拖拽文件到此处或
        <button @click="$refs.fileInput.click()" class="text-blue-600 hover:underline">
          选择文件
        </button>
      </p>
      <p class="text-[10px] text-gray-500 mt-0.5">支持 .md, .txt 格式，最多 30 个文件</p>
    </div>

    <!-- 已上传文件列表 -->
    <div v-if="uploadedFiles.length > 0" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
      <div class="flex justify-between items-center mb-2">
        <span class="text-xs text-gray-700 font-medium">
          已上传文件 ({{ uploadedFiles.length }}/30)
        </span>
        <button @click="clearAllFiles" class="text-xs text-red-600 hover:text-red-800">
          清空全部
        </button>
      </div>
      <div class="max-h-48 overflow-y-auto">
        <div
          v-for="(file, index) in uploadedFiles"
          :key="index"
          class="flex items-center justify-between py-1 px-2 hover:bg-gray-100 rounded"
        >
          <div class="flex items-center flex-1 min-w-0">
            <span class="text-xs text-gray-600 truncate">{{ file.name }}</span>
            <span class="text-[10px] text-gray-400 ml-2">({{ formatFileSize(file.size) }})</span>
          </div>
          <button @click="removeFile(index)" class="text-red-500 hover:text-red-700 ml-2">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMessage" class="mt-2 text-xs text-red-600">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAppStore } from '../stores/appStore'

const store = useAppStore()
const fileInput = ref(null)
const uploadedFiles = ref([])
const errorMessage = ref('')

const clearAllFiles = () => {
  uploadedFiles.value = []
  store.setBidSlices([])
  errorMessage.value = ''
}

const removeFile = (index) => {
  uploadedFiles.value.splice(index, 1)
  updateStoreSlices()
}

const handleDrop = (event) => {
  event.preventDefault()
  errorMessage.value = ''
  const files = Array.from(event.dataTransfer.files)

  if (uploadedFiles.value.length + files.length > 30) {
    errorMessage.value = `文件数量不能超过 30 个，当前有 ${uploadedFiles.value.length} 个`
    return
  }

  files.forEach(file => {
    if (file.name.match(/\.(md|txt)$/)) {
      processFile(file)
    } else {
      errorMessage.value = `文件 ${file.name} 格式不支持，只支持 .md 和 .txt 文件`
    }
  })
}

const handleFileSelect = (event) => {
  errorMessage.value = ''
  const files = Array.from(event.target.files)

  if (uploadedFiles.value.length + files.length > 30) {
    errorMessage.value = `文件数量不能超过 30 个，当前有 ${uploadedFiles.value.length} 个`
    return
  }

  files.forEach(file => {
    processFile(file)
  })
}

const processFile = (file) => {
  if (!file.name.match(/\.(md|txt)$/)) {
    errorMessage.value = `文件 ${file.name} 格式不支持`
    return
  }

  // 检查是否已存在相同名称的文件
  if (uploadedFiles.value.some(f => f.name === file.name)) {
    errorMessage.value = `文件 ${file.name} 已存在`
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    const content = e.target.result
    uploadedFiles.value.push({
      name: file.name,
      size: file.size,
      content: content
    })
    updateStoreSlices()
  }
  reader.readAsText(file)
}

const updateStoreSlices = () => {
  store.setBidSlices(uploadedFiles.value.map(f => f.content))
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>
