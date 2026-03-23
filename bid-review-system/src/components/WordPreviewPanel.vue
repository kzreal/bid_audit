<template>
  <div class="word-preview-panel h-full flex flex-col">
    <!-- 工具栏 -->
    <div class="toolbar border-b border-gray-200 px-4 py-3 flex-shrink-0">
      <div class="flex items-center justify-end gap-4">
        <!-- 搜索框 -->
        <div class="flex items-center gap-2">
          <div class="relative">
            <input
              v-model="searchText"
              type="text"
              placeholder="搜索..."
              class="w-48 border border-gray-300 rounded-vercel-sm pl-8 pr-3 py-1.5 text-xs focus:outline-none focus:border-black transition-colors"
              @keyup.enter="handleSearch"
            />
            <svg class="w-4 h-4 absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
          <span v-if="searchResultCount > 0" class="text-xs text-gray-500">
            {{ searchResultIndex + 1 }} / {{ searchResultCount }}
          </span>
          <button
            v-if="searchResultCount > 0"
            @click="prevSearchResult"
            class="p-1 text-gray-400 hover:text-black transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 15l7-7 7 7"></path>
            </svg>
          </button>
          <button
            v-if="searchResultCount > 0"
            @click="nextSearchResult"
            class="p-1 text-gray-400 hover:text-black transition-colors"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 9l-7 7-7-7"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- 预览区域 -->
    <div class="preview-container flex-1 overflow-hidden relative">
      <!-- 空状态 -->
      <div v-if="!wordDocument" class="h-full flex items-center justify-center bg-gray-50">
        <div class="text-center">
          <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <p class="text-gray-500 text-sm mb-2">暂无文档预览</p>
          <p class="text-gray-400 text-xs">请上传 .docx 文件</p>
        </div>
      </div>

      <!-- Word 预览 -->
      <div
        v-else
        id="word-preview-container"
        class="h-full overflow-y-auto p-6"
        ref="previewContainerRef"
      >
        <div
          id="word-preview"
          class="docx-preview"
          ref="previewRef"
        ></div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="absolute inset-0 bg-white/80 flex items-center justify-center">
        <div class="text-center">
          <span class="loading-dots inline-flex">
            <span></span>
            <span></span>
            <span></span>
          </span>
          <p class="text-sm text-gray-500 mt-2">文档渲染中...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import { renderAsync } from 'docx-preview'

const props = defineProps({
  wordDocument: {
    type: [File, null],
    default: null
  },
  highlightLine: {
    type: [Number, null],
    default: null
  },
  sliceMetadata: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['line-clicked'])

const previewRef = ref(null)
const previewContainerRef = ref(null)
const loading = ref(false)
const searchText = ref('')
const searchResultIndex = ref(0)
const searchResultCount = ref(0)
const searchMatches = ref([])

// 监听文档变化
watch(() => props.wordDocument, async (newDoc) => {
  if (newDoc) {
    console.log('Word document changed, rendering...')
    await nextTick()
    await renderDocument(newDoc)
  }
}, { immediate: true })

// 监听高亮行变化
watch(() => props.highlightLine, (newLine) => {
  if (newLine) {
    scrollToLine(newLine)
  }
})

onMounted(async () => {
  console.log('WordPreviewPanel mounted, wordDocument:', props.wordDocument)
  await nextTick()
  if (props.wordDocument) {
    await renderDocument(props.wordDocument)
  }
})

const renderDocument = async (file) => {
  if (!file || !previewRef.value) {
    console.log('renderDocument: missing file or previewRef', { file: !!file, previewRef: !!previewRef.value })
    return
  }

  loading.value = true
  console.log('Starting to render document:', file.name)
  try {
    // 使用 docx-preview 渲染
    await renderAsync(file.arrayBuffer(), previewRef.value, undefined, {
      className: 'docx-preview',
      inWrapper: true,
      ignoreWidth: false,
      ignoreHeight: false,
      ignoreFonts: false,
      breakPages: true,
      useBase64URL: true,
      useMathMLPolyfill: false,
      renderHeaders: true,
      renderFooters: true,
      renderFootnotes: true,
      renderChanges: false,
      renderTrackedChanges: false,
      renderComments: false
    })

    console.log('RenderAsync completed, preview content:', previewRef.value.innerHTML.length, 'chars')

    // 渲染完成后注入行号
    await nextTick()
    injectLineNumbers()

    console.log('Line numbers injected')
  } catch (error) {
    console.error('文档渲染失败:', error)
  } finally {
    loading.value = false
  }
}

const injectLineNumbers = () => {
  if (!previewRef.value) return

  let lineNumber = 1
  // docx-preview 生成的结构是 .docx-preview > section > p
  const sections = previewRef.value.querySelectorAll('section')
  console.log('Found sections:', sections.length)

  // 切片背景色
  const sliceColors = [
    '#ffffff', // 零级 - 白色
    '#f0f9ff', // 一级 - 天蓝
    '#ecfdf5', // 二级 - 浅绿
    '#fef3c7', // 三级 - 浅黄
    '#fdf4ff', // 四级 - 浅紫
    '#ffe4e6', // 五级 - 浅粉
  ]

  sections.forEach((section, sectionIndex) => {
    // 为每个 section 添加切片背景色
    section.style.backgroundColor = sliceColors[sectionIndex % sliceColors.length]
    section.style.padding = '8px'
    section.style.marginBottom = '8px'

    const elements = section.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th')
    elements.forEach((el) => {
      if (el.textContent.trim()) {
        el.setAttribute('data-line', lineNumber)
        el.style.cursor = 'pointer'
        el.addEventListener('click', () => {
          emit('line-clicked', lineNumber)
        })
        lineNumber++
      }
    })
  })
  console.log('Total lines:', lineNumber)
}

const scrollToLine = (lineNumber) => {
  if (!previewRef.value) return

  const element = previewRef.value.querySelector(`[data-line="${lineNumber}"]`)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'center' })

    // 添加高亮效果
    element.classList.add('highlight-line')
    setTimeout(() => {
      element.classList.remove('highlight-line')
    }, 3000)
  }
}

const handleSearch = () => {
  if (!searchText.value.trim() || !previewRef.value) return

  // 清除之前的高亮
  clearSearchHighlights()

  // 查找匹配元素
  const walker = document.createTreeWalker(
    previewRef.value,
    NodeFilter.SHOW_TEXT,
    null,
    false
  )

  searchMatches.value = []
  let node
  while (node = walker.nextNode()) {
    if (node.textContent.toLowerCase().includes(searchText.value.toLowerCase())) {
      searchMatches.value.push(node.parentElement)
    }
  }

  searchResultCount.value = searchMatches.value.length
  searchResultIndex.value = 0

  if (searchMatches.value.length > 0) {
    highlightSearchResult()
  }
}

const highlightSearchResult = () => {
  searchMatches.value.forEach((el, index) => {
    if (index === searchResultIndex.value) {
      el.classList.add('search-highlight')
      el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  })
}

const clearSearchHighlights = () => {
  if (!previewRef.value) return
  previewRef.value.querySelectorAll('.search-highlight').forEach(el => {
    el.classList.remove('search-highlight')
  })
}

const prevSearchResult = () => {
  if (searchResultIndex.value > 0) {
    searchResultIndex.value--
    highlightSearchResult()
  }
}

const nextSearchResult = () => {
  if (searchResultIndex.value < searchResultCount.value - 1) {
    searchResultIndex.value++
    highlightSearchResult()
  }
}

// 暴露方法给父组件调用
defineExpose({
  scrollToLine
})
</script>

<style>
/* docx-preview 样式调整 */
.docx-preview {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 14px;
  line-height: 1.6;
}

.docx-preview section {
  position: relative;
  margin-bottom: 16px;
}

/* 高亮样式 */
.highlight-line {
  background-color: #fef3c7 !important;
  border-left: 3px solid #f59e0b !important;
  padding-left: 8px;
  transition: all 0.3s ease;
}

/* 搜索高亮 */
.search-highlight {
  background-color: #fef08a !important;
}

/* 加载动画 */
.loading-dots span {
  animation: loading-dots 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes loading-dots {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}
</style>
