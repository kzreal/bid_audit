<template>
  <div class="mb-5">
    <label class="flex items-center gap-2 text-black text-xs font-semibold mb-2.5">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
      </svg>
      投标文件切片 (Markdown)
    </label>

    <!-- 文件上传区域 - Vercel 风格 -->
    <div
      :class="[
        'border border-dashed rounded-vercel-sm p-5 text-center transition-all duration-200',
        isDragging ? 'border-vercel-blue bg-vercel-blue-light' : 'border-gray-300 bg-gray-50 hover:border-black hover:bg-gray-100'
      ]"
      @drop="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragenter.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @dragend="isDragging = false"
    >
      <input
        type="file"
        ref="fileInput"
        accept=".md,.txt"
        multiple
        @change="handleFileSelect"
        class="hidden"
      />
      <div class="w-12 h-12 mx-auto mb-2.5 rounded-vercel-sm bg-gray-50 flex items-center justify-center">
        <svg class="w-6 h-6 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
        </svg>
      </div>
      <p class="text-sm text-black font-medium mb-1">
        拖拽文件到此处或
        <button @click="$refs.fileInput.click()" class="text-black font-semibold hover:text-vercel-blue transition-colors underline">
          选择文件
        </button>
      </p>
      <p class="text-xs text-gray-500">支持 .md, .txt 格式，最多 100 个文件</p>
    </div>

    <!-- 已上传文件列表 - Vercel 风格 -->
    <transition name="fade">
      <div v-if="uploadedFiles.length > 0" class="mt-3 card-vercel overflow-hidden">
        <div class="flex justify-between items-center px-4 py-2.5 bg-gray-50 border-b border-gray-200 cursor-pointer" @click="fileListExpanded = !fileListExpanded">
          <span class="text-xs text-black font-semibold flex items-center gap-2">
            <svg class="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            已上传文件 ({{ uploadedFiles.length }}/100)
          </span>
          <div class="flex items-center gap-2">
            <svg
              class="w-4 h-4 text-gray-400 transition-transform duration-200"
              :class="{ 'rotate-180': fileListExpanded }"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 9l-7 7-7-7"></path>
            </svg>
            <button @click.stop="clearAllFiles" class="text-xs text-gray-500 hover:text-black transition-colors flex items-center gap-1">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
              清空全部
            </button>
          </div>
        </div>
        <div v-show="fileListExpanded" class="max-h-52 overflow-y-auto">
          <transition-group name="list-item">
            <div
              v-for="(file, index) in uploadedFiles"
              :key="index"
              class="flex items-center justify-between px-4 py-2 hover:bg-gray-50 transition-colors border-b border-gray-200 last:border-b-0"
            >
              <div class="flex items-center gap-2 flex-1 min-w-0">
                <div class="w-7 h-7 rounded-vercel-sm bg-gray-100 flex items-center justify-center flex-shrink-0">
                  <svg class="w-3.5 h-3.5 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-xs text-black font-medium truncate">{{ file.name }}</p>
                  <p class="text-[10px] text-gray-500">{{ formatFileSize(file.size) }}</p>
                </div>
              </div>
              <button @click="removeFile(index)" class="w-7 h-7 rounded-vercel-sm bg-gray-100 hover:bg-gray-200 text-gray-500 hover:text-black transition-all flex items-center justify-center flex-shrink-0">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </transition-group>
        </div>
      </div>
    </transition>

    <!-- 错误提示 - Vercel 风格 -->
    <transition name="shake">
      <div v-if="errorMessage" class="mt-2.5 p-3 bg-white border border-gray-200 rounded-vercel-sm text-xs text-black flex items-center gap-2">
        <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        {{ errorMessage }}
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* 上滑过渡 */
.slide-up-enter-active {
  transition: all 200ms ease-out;
}

.slide-up-leave-active {
  transition: all 150ms ease-in;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* 列表项过渡 */
.list-item-enter-active {
  transition: all 200ms ease-out;
}

.list-item-leave-active {
  transition: all 150ms ease-in;
}

.list-item-enter-from {
  opacity: 0;
  transform: translateX(-8px);
}

.list-item-leave-to {
  opacity: 0;
  transform: translateX(8px);
}

/* 抖动效果 */
.shake-enter-active {
  animation: shake 0.3s ease-in-out;
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  10%, 30%, 50%, 70%, 90% {
    transform: translateX(-3px);
  }
  20%, 40%, 60%, 80% {
    transform: translateX(3px);
  }
}
</style>

<script setup>
import { ref } from 'vue'
import { useAppStore } from '../stores/appStore'

const store = useAppStore()
const fileInput = ref(null)
const uploadedFiles = ref([])
const errorMessage = ref('')
const isDragging = ref(false)
const fileListExpanded = ref(false)

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

  if (uploadedFiles.value.length + files.length > 100) {
    errorMessage.value = `文件数量不能超过 100 个，当前有 ${uploadedFiles.value.length} 个`
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

  if (uploadedFiles.value.length + files.length > 100) {
    errorMessage.value = `文件数量不能超过 100 个，当前有 ${uploadedFiles.value.length} 个`
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
  store.setBidSlices(uploadedFiles.value.map(f => ({
    fileName: f.name,
    content: f.content
  })))
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>
