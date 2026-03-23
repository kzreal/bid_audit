<template>
  <div class="word-preview-panel h-full flex flex-col">
    <!-- 工具栏 -->
    <div class="toolbar border-b border-gray-200 px-4 py-3 flex-shrink-0">
      <div class="flex items-center justify-between">
        <!-- 左侧：预览模式切换 -->
        <div class="flex items-center gap-2">
          <button
            v-if="wordDocument || sliceContent"
            @click="previewMode = 'original'"
            :class="['px-3 py-1.5 text-xs rounded-vercel-sm transition-colors', previewMode === 'original' ? 'bg-black text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']"
          >
            原文预览
          </button>
          <button
            v-if="sliceContent"
            @click="previewMode = 'slice'"
            :class="['px-3 py-1.5 text-xs rounded-vercel-sm transition-colors', previewMode === 'slice' ? 'bg-black text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200']"
          >
            切片预览
          </button>
        </div>

        <!-- 右侧：搜索框 -->
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
      <div v-if="!wordDocument && !sliceContent" class="h-full flex items-center justify-center bg-gray-50">
        <div class="text-center">
          <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <p class="text-gray-500 text-sm mb-2">暂无文档预览</p>
          <p class="text-gray-400 text-xs">请上传 .docx 文件</p>
        </div>
      </div>

      <!-- Word 预览 (原文模式) -->
      <div
        v-if="previewMode === 'original' && wordDocument"
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

      <!-- 切片预览模式 -->
      <div
        v-if="previewMode === 'slice' && sliceContent"
        id="slice-preview-container"
        class="h-full overflow-y-auto p-6"
        ref="slicePreviewRef"
      >
        <!-- 切片内容会通过 v-html 渲染 -->
      </div>

      <!-- 有文档但未选择模式 -->
      <div
        v-if="wordDocument && !previewMode"
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
import { ref, watch, onMounted, nextTick, computed } from 'vue'
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
  },
  // 切片内容（带 <!-- id --> 标记的 Markdown 文本）
  sliceContent: {
    type: [String, null],
    default: null
  }
})

const emit = defineEmits(['line-clicked'])

const previewMode = ref('original') // 'original' | 'slice'
const slicePreviewRef = ref(null)

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

// 监听切片内容变化
watch(() => props.sliceContent, async (newContent) => {
  if (newContent && previewMode.value === 'slice') {
    await nextTick()
    renderSliceContent(newContent)
  }
})

// 监听预览模式变化
watch(previewMode, async (newMode) => {
  if (newMode === 'slice' && props.sliceContent) {
    await nextTick()
    renderSliceContent(props.sliceContent)
  } else if (newMode === 'original' && props.wordDocument) {
    await nextTick()
    await renderDocument(props.wordDocument)
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

  // docx-preview 生成的结构是 .docx-preview > section > p
  const sections = previewRef.value.querySelectorAll('section')
  console.log('Found sections:', sections.length)

  // 用于存储 elementId -> displayLineNumber 的映射
  const lineNumberMap = new Map()
  let displayLineNumber = 1

  sections.forEach((section, sectionIndex) => {
    section.style.marginBottom = '8px'

    const elements = section.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th')
    elements.forEach((el) => {
      const text = el.textContent.trim()
      if (!text) return

      // 尝试解析 HTML 注释中的 id: <!-- xxx -->
      let elementId = null
      let displayNumber = null

      // 检查是否有 HTML 注释节点作为第一个子节点
      const childNodes = Array.from(el.childNodes)
      const commentNode = childNodes.find(node => node.nodeType === Node.COMMENT_NODE)
      if (commentNode) {
        const commentText = commentNode.textContent.trim()
        const match = commentText.match(/^(\d+)$/)
        if (match) {
          elementId = parseInt(match[1])
          displayNumber = elementId
          lineNumberMap.set(elementId, displayLineNumber)
          el.setAttribute('data-line', displayNumber)
          el.setAttribute('data-element-id', elementId)
        }
      }

      if (elementId === null) {
        // 没有标记的元素，使用递增行号
        el.setAttribute('data-line', displayLineNumber)
        displayNumber = displayLineNumber
      }

      el.style.cursor = 'pointer'
      el.addEventListener('click', () => {
        emit('line-clicked', displayNumber)
      })

      displayLineNumber++
    })
  })

  // 将映射暴露给外部，方便通过 elementId 查找行号
  previewRef.value._lineNumberMap = lineNumberMap
  console.log('Total lines:', displayLineNumber, 'Line number map size:', lineNumberMap.size)
}

// 渲染切片内容（带 <!-- id --> 标记的 Markdown）
const renderSliceContent = (content) => {
  if (!slicePreviewRef.value || !content) return

  loading.value = true
  console.log('Rendering slice content, length:', content.length)

  try {
    // 将 Markdown 转换为 HTML，同时保留 <!-- id --> 注释
    const htmlContent = convertMarkdownToHtml(content)
    slicePreviewRef.value.innerHTML = htmlContent

    // 为切片内容注入行号
    injectLineNumbersForSlice(slicePreviewRef.value)

    console.log('Slice content rendered')
  } catch (error) {
    console.error('切片内容渲染失败:', error)
  } finally {
    loading.value = false
  }
}

// 将 Markdown 转换为 HTML（保留 <!-- id --> 注释）
const convertMarkdownToHtml = (markdown) => {
  if (!markdown) return ''

  const lines = markdown.split('\n')
  let html = ''
  let inTable = false

  for (const line of lines) {
    // 处理表格
    if (line.trim().startsWith('|')) {
      if (!inTable) {
        html += '<table class="docx-table"><tbody>'
        inTable = true
      }
      // 解析表格行
      const cells = line.trim().split('|').filter(c => c.trim())
      if (cells.length > 0 && !line.includes('---')) {
        html += '<tr>'
        for (const cell of cells) {
          html += `<td>${cell.trim()}</td>`
        }
        html += '</tr>'
      } else if (line.includes('---')) {
        // 分隔行，跳过
      }
      continue
    } else {
      if (inTable) {
        html += '</tbody></table>'
        inTable = false
      }
    }

    // 处理标题
    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/)
    if (headingMatch) {
      const level = headingMatch[1].length
      const text = headingMatch[2]
      html += `<h${level}>${text}</h${level}>`
      continue
    }

    // 处理段落（保留 <!-- id --> 注释）
    if (line.trim()) {
      html += `<p>${line}</p>`
    }
  }

  // 关闭未关闭的表格
  if (inTable) {
    html += '</tbody></table>'
  }

  return html
}

// 为切片内容注入行号（解析 <!-- id --> 注释）
const injectLineNumbersForSlice = (container) => {
  if (!container) return

  // 用于存储 elementId -> displayLineNumber 的映射
  const lineNumberMap = new Map()
  let displayLineNumber = 1

  const elements = container.querySelectorAll('p, h1, h2, h3, h4, h5, h6, li, td, th')
  console.log('Found elements in slice:', elements.length)

  elements.forEach((el) => {
    const text = el.textContent.trim()
    if (!text) return

    // 尝试解析 HTML 注释中的 id: <!-- xxx -->
    let elementId = null
    let displayNumber = null

    // 检查是否有 HTML 注释节点作为第一个子节点
    const childNodes = Array.from(el.childNodes)
    const commentNode = childNodes.find(node => node.nodeType === Node.COMMENT_NODE)
    if (commentNode) {
      const commentText = commentNode.textContent.trim()
      const match = commentText.match(/^(\d+)$/)
      if (match) {
        elementId = parseInt(match[1])
        displayNumber = elementId
        lineNumberMap.set(elementId, displayLineNumber)
        el.setAttribute('data-line', displayNumber)
        el.setAttribute('data-element-id', elementId)
      }
    }

    if (elementId === null) {
      // 没有标记的元素，使用递增行号
      el.setAttribute('data-line', displayLineNumber)
      displayNumber = displayLineNumber
    }

    el.style.cursor = 'pointer'
    el.addEventListener('click', () => {
      emit('line-clicked', displayNumber)
    })

    displayLineNumber++
  })

  // 将映射暴露给外部
  container._lineNumberMap = lineNumberMap
  console.log('Slice total lines:', displayLineNumber, 'Line number map size:', lineNumberMap.size)
}

const scrollToLine = (lineNumber) => {
  // 根据预览模式选择目标容器
  const container = previewMode.value === 'slice' ? slicePreviewRef.value : previewRef.value
  if (!container) return

  const element = container.querySelector(`[data-line="${lineNumber}"]`)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'center' })

    // 添加高亮效果
    element.classList.add('highlight-line')
    setTimeout(() => {
      element.classList.remove('highlight-line')
    }, 3000)
  } else {
    console.log('scrollToLine: element not found for line', lineNumber, 'in mode', previewMode.value)
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

// 通过 elementId（如 summary agent 返回的 38）获取对应的行号
const getLineNumberByElementId = (elementId) => {
  const container = previewMode.value === 'slice' ? slicePreviewRef.value : previewRef.value
  if (!container || !container._lineNumberMap) return null
  return container._lineNumberMap.get(elementId) || null
}

// 暴露方法给父组件调用
defineExpose({
  scrollToLine,
  getLineNumberByElementId
})
</script>

<style>
/* docx-preview 样式调整 - 保持原始 Word 外观 */
.docx-preview {
  font-family: 'Times New Roman', SimSun, '宋体', serif;
  font-size: 12pt;
  line-height: 1.5;
  color: #000000;
}

.docx-preview section {
  position: relative;
  margin-bottom: 0;
  padding: 0;
}

.docx-preview p {
  margin: 0;
  text-align: justify;
}

.docx-preview h1 {
  font-size: 22pt;
  font-weight: bold;
  margin: 24pt 0 12pt 0;
  text-align: center;
}

.docx-preview h2 {
  font-size: 16pt;
  font-weight: bold;
  margin: 18pt 0 12pt 0;
}

.docx-preview h3 {
  font-size: 14pt;
  font-weight: bold;
  margin: 16pt 0 8pt 0;
}

.docx-preview table {
  border-collapse: collapse;
  width: 100%;
  margin: 8pt 0;
}

.docx-preview td,
.docx-preview th {
  border: 0.5pt solid #000;
  padding: 4pt 8pt;
  vertical-align: top;
}

.docx-preview th {
  background-color: #e6e6e6;
  font-weight: bold;
}

/* 切片预览样式 */
#slice-preview-container {
  font-family: 'Times New Roman', SimSun, '宋体', serif;
  font-size: 12pt;
  line-height: 1.5;
  color: #000000;
}

#slice-preview-container .docx-table {
  border-collapse: collapse;
  width: 100%;
  margin: 8pt 0;
}

#slice-preview-container td,
#slice-preview-container th {
  border: 0.5pt solid #000;
  padding: 4pt 8pt;
  vertical-align: top;
}

#slice-preview-container h1 {
  font-size: 22pt;
  font-weight: bold;
  margin: 24pt 0 12pt 0;
  text-align: center;
}

#slice-preview-container h2 {
  font-size: 16pt;
  font-weight: bold;
  margin: 18pt 0 12pt 0;
}

#slice-preview-container h3 {
  font-size: 14pt;
  font-weight: bold;
  margin: 16pt 0 8pt 0;
}

#slice-preview-container p {
  margin: 0 0 8pt 0;
  text-align: justify;
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
