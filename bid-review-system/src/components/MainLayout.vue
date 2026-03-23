<template>
  <div class="main-container h-screen flex bg-gray-50">
    <!-- 左侧：Tab操作区 40% -->
    <div class="w-[40%] bg-white border-r border-gray-200 flex flex-col">
      <!-- 头部 - 蓝色渐变 -->
      <header class="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-5 flex-shrink-0">
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

      <!-- Tab导航 -->
      <tab-navigator
        :tabs="tabs"
        :current-tab="store.currentTab"
        @change-tab="store.setCurrentTab"
      />

      <!-- Tab内容区 -->
      <div class="flex-1 overflow-y-auto">
        <upload-tab v-if="store.currentTab === 'upload'" />
        <create-task-tab v-if="store.currentTab === 'create-task'" />
        <task-list-tab v-if="store.currentTab === 'task-list'" />
        <review-result-tab v-if="store.currentTab === 'review-result'" @jump-to-line="handleJumpToLine" />
      </div>
    </div>

    <!-- 右侧：预览区 60% -->
    <div class="flex-1 bg-white flex flex-col">
      <word-preview-panel
        ref="wordPreviewRef"
        :word-document="store.wordDocument"
        :highlight-line="store.highlightLine"
        :slice-metadata="store.sliceMetadata"
        @line-clicked="handleLineClicked"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAppStore } from '../stores/appStore'
import TabNavigator from './TabNavigator.vue'
import UploadTab from './UploadTab.vue'
import CreateTaskTab from './CreateTaskTab.vue'
import TaskListTab from './TaskListTab.vue'
import ReviewResultTab from './ReviewResultTab.vue'
import WordPreviewPanel from './WordPreviewPanel.vue'

const store = useAppStore()
const wordPreviewRef = ref(null)

// Tab配置
const tabs = [
  { id: 'upload', label: '创建项目' },
  { id: 'create-task', label: '创建任务' },
  { id: 'task-list', label: '任务列表' },
  { id: 'review-result', label: '审核结果' }
]

// 组件挂载时检查 API 状态
onMounted(async () => {
  try {
    await store.checkApiStatus()
  } catch (error) {
    console.warn('无法获取 API 状态:', error)
  }
})

// 处理高亮跳转
const handleJumpToLine = (lineNumber) => {
  if (wordPreviewRef.value) {
    wordPreviewRef.value.scrollToLine(lineNumber)
  }
}

// 处理行点击
const handleLineClicked = (lineNumber) => {
  console.log('点击行号:', lineNumber)
}
</script>
