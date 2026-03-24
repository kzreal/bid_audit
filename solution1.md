# docx-preview 行号注入与跳转方案

## 1. 问题背景

系统后端使用 python-docx 解析 Word 文档，按「段落 → 表格行 → 图片」的出现顺序为每个元素编号（`<!-- 1 -->`, `<!-- 2 -->` ...）。前端使用 docx-preview 渲染同一份 .docx 文件，但 docx-preview **不会自动生成行号**，导致审核结果中的"第x行"按钮无法定位到预览中的对应位置。

**核心思路**：在 docx-preview 渲染完成后，用与后端完全相同的规则遍历 DOM，为每个块级元素注入 `data-line` 属性，从而建立行号到 DOM 元素的映射。

---

## 2. 后端编号规则（对齐基准）

后端 python-docx 的编号逻辑如下，前端必须严格复刻：

```python
# backend/slice_builder.py
from docx import Document
from lxml import etree

WPML_NS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def build_line_numbers(doc_path: str) -> list[dict]:
    """
    按顺序遍历文档 body 的直接子元素，生成行号映射。
    规则：
      - 段落（w:p）  → 计为 1 行
      - 表格（w:tbl） → 每个 w:tr 计为 1 行
      - 其他元素      → 跳过不计
    """
    doc = Document(doc_path)
    line_map = []
    line_number = 1

    for element in doc.element.body:
        tag = etree.QName(element.tag).localname

        if tag == 'p':
            text = element.text or ''
            for t in element.iter(f'{WPML_NS}t'):
                text += (t.text or '')
            line_map.append({
                'line': line_number,
                'type': 'paragraph',
                'text_preview': text[:50].strip(),
            })
            line_number += 1

        elif tag == 'tbl':
            for row in element.iter(f'{WPML_NS}tr'):
                cells_text = []
                for cell in row.iter(f'{WPML_NS}tc'):
                    cell_text = ''
                    for t in cell.iter(f'{WPML_NS}t'):
                        cell_text += (t.text or '')
                    cells_text.append(cell_text.strip())
                line_map.append({
                    'line': line_number,
                    'type': 'table_row',
                    'text_preview': ' | '.join(cells_text)[:50],
                })
                line_number += 1

    return line_map
关键约定：空段落也计数、嵌套表格只数最内层 <tr>、页眉页脚不计入。

3. 前端实现
3.1 docx-preview 渲染入口
复制
// src/utils/docxRenderer.js
import { renderAsync } from 'docx-preview'
import { injectLineNumbersToDocxPreview } from './lineNumberInjector'

/**
 * 渲染 docx 文件并注入行号
 * @param {ArrayBuffer} arrayBuffer - docx 文件的二进制数据
 * @param {HTMLElement} container - 渲染容器 DOM 元素
 * @returns {Promise<number>} 注入的总行数
 */
export async function renderDocxWithLineNumbers(arrayBuffer, container) {
  // 1. 渲染 docx
  await renderAsync(arrayBuffer, container, null, {
    className: 'docx',
    inWrapper: true,
    ignoreWidth: false,
    ignoreHeight: false,
    ignoreFonts: false,
    breakPages: true,
  })

  // 2. 渲染完成后注入行号
  const totalLines = injectLineNumbersToDocxPreview(container)
  console.log(`[docx-preview] 渲染完成，共注入 ${totalLines} 个行号`)

  return totalLines
}
3.2 行号注入核心逻辑
复制
// src/utils/lineNumberInjector.js

/**
 * 遍历 docx-preview 渲染后的 DOM，为每个块级元素注入 data-line 属性。
 * 
 * 规则（必须与后端 python-docx 编号逻辑完全一致）：
 *   - 段落（<p>, <h1>~<h6> 等）→ 计为 1 行
 *   - 表格 <table> → 每个 <tr> 计为 1 行（表格本身不计）
 *   - 其他元素 → 跳过
 *
 * @param {HTMLElement} containerEl - docx-preview 的渲染容器
 * @returns {number} 注入的总行数
 */
export function injectLineNumbersToDocxPreview(containerEl) {
  let lineNumber = 1

  // docx-preview 渲染结构：.docx-wrapper > section.docx > 子元素
  const sections = containerEl.querySelectorAll('section.docx')

  if (sections.length === 0) {
    console.warn('[lineNumberInjector] 未找到 section.docx，检查 docx-preview 是否渲染完成')
    return 0
  }

  sections.forEach((section) => {
    const children = section.children

    for (const child of children) {
      lineNumber = processElement(child, lineNumber)
    }
  })

  return lineNumber - 1
}

/**
 * 处理单个元素，返回更新后的行号
 */
function processElement(element, lineNumber) {
  const tag = element.tagName?.toUpperCase()

  if (tag === 'TABLE') {
    // 表格：遍历所有 <tr>，每行计 1
    const rows = element.querySelectorAll(':scope > tbody > tr, :scope > thead > tr, :scope > tr')
    rows.forEach((row) => {
      row.setAttribute('data-line', lineNumber)
      lineNumber++
    })
  } else if (isBlockElement(tag)) {
    // 段落/标题/div 等块级元素：计 1 行
    element.setAttribute('data-line', lineNumber)
    lineNumber++
  }
  // 其他元素（如 <br>, <span> 等内联元素）跳过

  return lineNumber
}

/**
 * 判断是否为需要计数的块级元素
 */
function isBlockElement(tag) {
  const BLOCK_TAGS = new Set([
    'P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6',
    'DIV', 'BLOCKQUOTE', 'PRE', 'FIGURE',
    'UL', 'OL', 'LI',
  ])
  return BLOCK_TAGS.has(tag)
}
3.3 跳转与高亮
复制
// src/utils/lineScroller.js

/**
 * 滚动到指定行号并高亮
 * @param {HTMLElement} container - docx-preview 渲染容器
 * @param {number} lineNumber - 目标行号
 * @param {Object} options - 可选配置
 * @param {number} options.highlightDuration - 高亮持续时间（ms），默认 2000
 * @param {string} options.scrollBehavior - 滚动行为，默认 'smooth'
 * @returns {boolean} 是否成功找到并跳转
 */
export function scrollToLine(container, lineNumber, options = {}) {
  const {
    highlightDuration = 2000,
    scrollBehavior = 'smooth',
  } = options

  const target = container.querySelector(`[data-line="${lineNumber}"]`)

  if (!target) {
    console.warn(`[scrollToLine] 未找到行号 ${lineNumber} 对应的元素`)
    return false
  }

  // 滚动到目标元素
  target.scrollIntoView({
    behavior: scrollBehavior,
    block: 'center',
  })

  // 添加高亮效果
  target.classList.add('docx-line-highlight')
  setTimeout(() => {
    target.classList.remove('docx-line-highlight')
  }, highlightDuration)

  return true
}

/**
 * 带重试的跳转（应对异步渲染延迟）
 * @param {HTMLElement} container
 * @param {number} lineNumber
 * @param {number} maxRetries - 最大重试次数，默认 5
 * @param {number} retryInterval - 重试间隔（ms），默认 200
 * @returns {Promise<boolean>}
 */
export function scrollToLineWithRetry(container, lineNumber, maxRetries = 5, retryInterval = 200) {
  return new Promise((resolve) => {
    let attempts = 0

    const tryScroll = () => {
      attempts++
      const success = scrollToLine(container, lineNumber)

      if (success) {
        resolve(true)
      } else if (attempts < maxRetries) {
        setTimeout(tryScroll, retryInterval)
      } else {
        console.error(`[scrollToLine] 重试 ${maxRetries} 次后仍未找到行号 ${lineNumber}`)
        resolve(false)
      }
    }

    tryScroll()
  })
}
3.4 高亮样式
复制
/* src/styles/docx-line-highlight.css */

/* 行高亮动画 */
.docx-line-highlight {
  background-color: #fef08a !important; /* 黄色高亮 */
  outline: 2px solid #facc15 !important;
  outline-offset: 2px;
  border-radius: 2px;
  transition: background-color 0.3s ease, outline-color 0.3s ease;
}

/* 高亮消退动画（通过 JS 移除 class 触发） */
[data-line] {
  transition: background-color 0.5s ease, outline 0.5s ease;
}

/* 可选：鼠标悬停时显示行号（调试用） */
[data-line]:hover::before {
  content: 'L' attr(data-line);
  position: absolute;
  left: -40px;
  font-size: 10px;
  color: #9ca3af;
  background: #f3f4f6;
  padding: 1px 4px;
  border-radius: 2px;
  pointer-events: none;
}
4. 在 Vue 组件中集成
4.1 Word 预览组件
复制
<!-- src/components/DocxPreview.vue -->
<template>
  <div class="docx-preview-wrapper">
    <div ref="docxContainer" class="docx-container"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { renderDocxWithLineNumbers } from '@/utils/docxRenderer'
import { scrollToLineWithRetry } from '@/utils/lineScroller'
import { useDocStore } from '@/stores/docStore'

const props = defineProps({
  /** 需要跳转到的目标行号，由父组件传入 */
  targetLine: {
    type: Number,
    default: null,
  },
})

const docxContainer = ref(null)
const store = useDocStore()
const totalLines = ref(0)

// 加载并渲染文档
async function loadDocument(fileUrl) {
  if (!docxContainer.value) return

  const response = await fetch(fileUrl)
  const arrayBuffer = await response.arrayBuffer()

  // 清空容器
  docxContainer.value.innerHTML = ''

  // 渲染 + 注入行号
  totalLines.value = await renderDocxWithLineNumbers(arrayBuffer, docxContainer.value)
}

// 监听目标行号变化，自动跳转
watch(
  () => props.targetLine,
  async (newLine) => {
    if (newLine && docxContainer.value) {
      await scrollToLineWithRetry(docxContainer.value, newLine)
    }
  }
)

// 初始加载
onMounted(() => {
  if (store.currentFileUrl) {
    loadDocument(store.currentFileUrl)
  }
})

// 暴露方法供父组件调用
defineExpose({
  scrollToLine: (lineNumber) => {
    if (docxContainer.value) {
      return scrollToLineWithRetry(docxContainer.value, lineNumber)
    }
    return Promise.resolve(false)
  },
})
</script>

<style scoped>
.docx-preview-wrapper {
  width: 100%;
  height: 100%;
  overflow: auto;
  position: relative;
}

.docx-container {
  min-height: 100%;
}
</style>
4.2 审核结果面板（跳转触发方）
复制
<!-- src/components/ReviewPanel.vue -->
<template>
  <div class="review-panel">
    <div v-for="issue in reviewIssues" :key="issue.id" class="issue-card">
      <p>{{ issue.description }}</p>
      <button
        class="jump-btn"
        @click="handleJumpToLine(issue.lineNumber)"
      >
        第{{ issue.lineNumber }}行
      </button>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['jump-to-line'])

function handleJumpToLine(lineNumber) {
  emit('jump-to-line', lineNumber)
}
</script>
4.3 父组件组装
复制
<!-- src/views/AuditView.vue -->
<template>
  <div class="audit-layout">
    <DocxPreview ref="docxPreviewRef" :target-line="targetLine" />
    <ReviewPanel @jump-to-line="onJumpToLine" />
  </div>
</template>

<script setup>
import { ref } from 'vue'

const docxPreviewRef = ref(null)
const targetLine = ref(null)

function onJumpToLine(lineNumber) {
  targetLine.value = lineNumber
  // 也可以直接调用 ref 方法：
  // docxPreviewRef.value?.scrollToLine(lineNumber)
}
</script>
5. 对齐校验（调试工具）
为确保前后端编号一致，提供一个校验工具：

复制
// src/utils/lineNumberValidator.js

/**
 * 校验前端注入的行号与后端映射表是否一致
 * @param {HTMLElement} container - docx-preview 容器
 * @param {Array} backendLineMap - 后端返回的行号映射 [{line, type, text_preview}]
 * @returns {Object} 校验结果
 */
export function validateLineNumbers(container, backendLineMap) {
  const results = {
    total: backendLineMap.length,
    matched: 0,
    mismatched: [],
    missing: [],
  }

  backendLineMap.forEach((entry) => {
    const el = container.querySelector(`[data-line="${entry.line}"]`)

    if (!el) {
      results.missing.push(entry)
      return
    }

    const domText = el.textContent?.slice(0, 50).trim() || ''
    const backendText = entry.text_preview || ''

    // 模糊匹配：去除空白后比较前30个字符
    const normalize = (s) => s.replace(/\s+/g, '').slice(0, 30)

    if (normalize(domText) === normalize(backendText)) {
      results.matched++
    } else {
      results.mismatched.push({
        line: entry.line,
        type: entry.type,
        backend: backendText,
        frontend: domText.slice(0, 50),
      })
    }
  })

  // 输出报告
  console.group('[行号校验报告]')
  console.log(`总行数: ${results.total}`)
  console.log(`匹配: ${results.matched}`)
  console.log(`不匹配: ${results.mismatched.length}`)
  console.log(`缺失: ${results.missing.length}`)

  if (results.mismatched.length > 0) {
    console.table(results.mismatched)
  }
  if (results.missing.length > 0) {
    console.table(results.missing)
  }
  console.groupEnd()

  return results
}
在开发环境中使用：

复制
// 在 DocxPreview.vue 的 loadDocument 方法末尾添加
if (import.meta.env.DEV) {
  const { validateLineNumbers } = await import('@/utils/lineNumberValidator')
  const response = await fetch(`/api/documents/${docId}/line-map`)
  const backendLineMap = await response.json()
  validateLineNumbers(docxContainer.value, backendLineMap)
}
6. 边界情况处理清单
边界情况	python-docx 行为	docx-preview 行为	处理方式
空段落	包含在 doc.paragraphs 中	渲染为空 <p>	前端也计数空 <p>
嵌套表格	需递归遍历	渲染为嵌套 <table>	使用 :scope > tr 只选直接子行
文本框 / Shape	python-docx 不直接暴露	可能渲染为额外元素	跳过不编号
分节符 / 分页符	不算段落	产生新 <section>	不计数，跨 section 连续编号
页眉页脚	需单独 API 访问	会渲染在页面顶部/底部	排除不编号
图片独占段落	算 1 个段落	渲染为含 <img> 的 <p>	正常计数
合并单元格	<tr> 数量不变	<tr> 数量不变	正常按 <tr> 计数
7. 文件结构总览
复制
src/
├── components/
│   ├── DocxPreview.vue          # Word 预览组件
│   └── ReviewPanel.vue          # 审核结果面板
├── utils/
│   ├── docxRenderer.js          # docx-preview 渲染入口
│   ├── lineNumberInjector.js    # 行号注入核心逻辑
│   ├── lineScroller.js          # 跳转与高亮
│   └── lineNumberValidator.js   # 对齐校验工具（仅开发环境）
├── styles/
│   └── docx-line-highlight.css  # 高亮样式
├── stores/
│   └── docStore.js              # Pinia 状态管理
└── views/
    └── AuditView.vue            # 审核页面（组装组件）
复制

这份文档已经整理好了，包含完整的实现代码和集成说明。你可以直接复制上方的 Markdown 内容保存为 `.md` 文件使用。

整体方案的执行路径很清晰：**docx-preview 渲染完成 → 遍历 DOM 注入 `data-line` → 点击按钮时 `querySelector + scrollIntoView`**。第 5 节的校验工具是个保险绳——开发阶段打开它，能立刻发现前后端编号不一致的地方，上线前关掉即可。