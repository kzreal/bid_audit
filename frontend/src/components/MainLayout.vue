<template>
  <div class="main-container h-screen flex bg-gray-50">
    <!-- 左侧：Tab操作区 30% -->
    <div class="w-[30%] bg-white border-r border-gray-200 flex flex-col">
      <!-- 头部 - Vercel 简约风格 -->
      <header class="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-vercel-sm bg-vercel-blue flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
          <div>
            <h1 class="text-base font-semibold tracking-tight text-black">投标文件审核系统</h1>
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
      <div class="flex-1 min-h-0 border-b-8 border-white">
        <upload-tab v-if="store.currentTab === 'upload'" />
        <task-list-tab v-if="store.currentTab === 'task-list'" />
        <review-result-tab v-if="store.currentTab === 'review-result'" @jump-to-line="handleJumpToLine" />
      </div>
    </div>

    <!-- 右侧：预览区 70% -->
    <div class="flex-1 bg-white flex flex-col border-b-8 border-white">
      <word-preview-panel
        ref="wordPreviewRef"
        :word-document="store.wordDocument"
        :word-document-with-bookmarks="store.wordDocumentWithBookmarks"
        :highlight-line="store.highlightLine"
        :slice-metadata="store.sliceMetadata"
        :slice-content="currentSliceContent"
        @line-clicked="handleLineClicked"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useAppStore } from '../stores/appStore'
import TabNavigator from './TabNavigator.vue'
import UploadTab from './UploadTab.vue'
import TaskListTab from './TaskListTab.vue'
import ReviewResultTab from './ReviewResultTab.vue'
import WordPreviewPanel from './WordPreviewPanel.vue'

const store = useAppStore()
const wordPreviewRef = ref(null)

// 当前选中切片的内容
const currentSliceContent = computed(() => {
  if (store.selectedSliceIndex === null || store.selectedSliceIndex === undefined) {
    return null
  }
  const slice = store.bidSlices[store.selectedSliceIndex]
  return slice?.content || null
})

// Tab配置 - 合并创建项目和创建任务为单个 Tab
const tabs = [
  { id: 'upload', label: '项目创建' },
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
const handleJumpToLine = async (lineNumber) => {
  if (!lineNumber) return

  console.log(`跳转到行号: ${lineNumber}`)

  // 优先使用原文预览模式进行定位（使用 Word 原生书签）
  store.setPreviewMode('original')

  // 等待预览模式切换和文档渲染完成
  await nextTick()
  await new Promise(resolve => requestAnimationFrame(resolve))

  // 使用原文行号直接定位（带书签的 Word 文档会处理书签查找）
  if (wordPreviewRef.value) {
    wordPreviewRef.value.scrollToLine(lineNumber)
  }
}

// 处理行点击
const handleLineClicked = (lineNumber) => {
  console.log('点击行号:', lineNumber)
}
</script>
