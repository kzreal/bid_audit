<template>
  <div class="mb-6">
    <label class="block text-gray-700 text-sm font-medium mb-2">
      投标文件 (Markdown)
    </label>

    <!-- 文件上传区域 -->
    <div
      class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors mb-3"
      @drop="handleDrop"
      @dragover.prevent
      @dragenter.prevent
    >
      <input
        type="file"
        ref="fileInput"
        accept=".md,.txt"
        @change="handleFileSelect"
        class="hidden"
      />
      <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
      </svg>
      <p class="text-sm text-gray-600">
        拖拽文件到此处或
        <button @click="$refs.fileInput.click()" class="text-blue-600 hover:underline">
          选择文件
        </button>
      </p>
      <p class="text-xs text-gray-500 mt-1">支持 .md, .txt 格式</p>
    </div>

    <!-- 可编辑文本区域 -->
    <textarea
      class="text-editor w-full h-64 resize-none"
      v-model="store.bidText"
      placeholder="在此粘贴或输入投标文件内容..."
    ></textarea>

    <!-- 底部操作栏 -->
    <div class="mt-2 flex justify-between items-center">
      <span class="text-xs text-gray-500">
        字符数: {{ store.bidText.length }}
      </span>
      <button v-if="store.bidText" @click="clearBidText"
              class="text-xs text-red-600 hover:text-red-800">
        清空
      </button>
    </div>

    <!-- 文件信息 -->
    <div v-if="store.currentFile" class="mt-2 text-xs text-gray-600">
      <p>当前文件: {{ store.currentFile.name }}</p>
      <p>大小: {{ formatFileSize(store.currentFile.size) }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAppStore } from '../stores/appStore'

const store = useAppStore()
const fileInput = ref(null)
const currentFile = ref(null)

const clearBidText = () => {
  store.clearBidFile()
  currentFile.value = null
}

const handleDrop = (event) => {
  event.preventDefault()
  const files = event.dataTransfer.files
  if (files.length > 0) {
    processFile(files[0])
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    processFile(file)
  }
}

const processFile = (file) => {
  if (!file.name.match(/\.(md|txt)$/)) {
    alert('请选择 .md 或 .txt 文件')
    return
  }

  const reader = new FileReader()
  reader.onload = (e) => {
    const content = e.target.result
    store.setBidFile(content, file)
    currentFile.value = file
  }
  reader.readAsText(file)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>