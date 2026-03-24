# 投标文件审核系统 — Word 预览行号定位方案

**技术栈**: Vue 3 + Pinia + Flask + python-docx + docx-preview  
**文档格式**: Word (.docx)  
**更新日期**: 2026-03-24

---

## 一、核心需求

点击审核结果中的"第 x 行"按钮，跳转到 Word 预览中对应的段落/行，并高亮闪烁提示用户。

---

## 二、方案原理

将定位信息以 **Word 原生书签（Bookmark）** 的形式写入 .docx 文件本身。前端使用 docx-preview 渲染时，书签会被解析为 DOM 元素，前端直接通过元素查找实现精准跳转。

**书签与内容物理绑定，不依赖 DOM 渲染顺序，不存在对齐问题。**

### 数据流

后端 python-docx 写入书签 (line_1, line_2, ...)
↓
带书签的 .docx 文件发给前端
↓
前端 docx-preview 渲染，书签被解析为 DOM 元素
↓
点击"第 x 行" → DOM 中查找书签元素 → scrollIntoView

复制

---

## 三、方案对比与排除记录

| 方案 | 思路 | 结论 | 排除原因 |
|------|------|------|----------|
| A: docx-preview + 渲染后 DOM 注入 | 渲染完成后按顺序给 `<p>` `<tr>` 注入 `data-line` 属性 | ❌ 排除 | 后端遍历顺序 ≠ 前端 DOM 顺序，嵌套表格/空段落/页眉页脚均会导致错位 |
| B: @vue-office/docx 替换 | 换用 Vue 封装组件 | ❌ 排除 | 底层就是 docx-preview，换壳不换芯，且组件封装使 DOM 访问更困难 |
| **C: python-docx 书签 + docx-preview 渲染** | **书签内嵌于 .docx 文件，渲染器忠实输出** | **✅ 采用** | **书签与内容物理绑定，不存在对齐问题** |

### 方案 C 与方案 A 的本质区别

| | 方案 A（DOM 注入） | 方案 C（书签） |
|---|---|---|
| 编号来源 | 渲染后从外部注入 | **内嵌在 .docx 文件本身** |
| 对齐可靠性 | 依赖 DOM 顺序猜测，脆弱 | 书签与内容物理绑定，**不会错位** |
| 渲染器要求 | 需要输出顺序与后端一致 | 只需能识别书签即可 |

---

## 四、后端实现

### 4.1 书签写入函数

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_bookmark(paragraph, bookmark_id, bookmark_name):
    """在段落开头插入 Word 书签"""
    bookmark_start = OxmlElement('w:bookmarkStart')
    bookmark_start.set(qn('w:id'), str(bookmark_id))
    bookmark_start.set(qn('w:name'), bookmark_name)

    bookmark_end = OxmlElement('w:bookmarkEnd')
    bookmark_end.set(qn('w:id'), str(bookmark_id))

    paragraph._p.insert(0, bookmark_start)
    paragraph._p.append(bookmark_end)
4.2 文档元素遍历器
doc.paragraphs 只返回 body 直属段落，不包含表格内段落。必须使用自定义遍历器覆盖所有块级元素：

复制
from docx.table import Table
from docx.text.paragraph import Paragraph

def iter_block_items(doc):
    """
    按文档顺序遍历所有块级元素（段落 + 表格行）
    此函数必须与切片编号逻辑保持一致，建议切片和书签写入共用此函数
    """
    for child in doc.element.body.iterchildren():
        if child.tag == qn('w:p'):
            yield Paragraph(child, doc)
        elif child.tag == qn('w:tbl'):
            table = Table(child, doc)
            for row in table.rows:
                # 表格行：取第一个单元格的第一个段落作为书签锚点
                yield row.cells[0].paragraphs[0]
4.3 完整书签写入流程
复制
from docx import Document

def inject_bookmarks(input_path, output_path):
    doc = Document(input_path)

    # 避免与原有书签 ID 冲突
    existing_ids = [
        int(el.get(qn('w:id')))
        for el in doc.element.body.iter(qn('w:bookmarkStart'))
    ]
    start_id = max(existing_ids, default=0) + 1

    # 遍历所有块级元素，写入书签 line_1, line_2, ...
    for offset, para in enumerate(iter_block_items(doc)):
        add_bookmark(para, start_id + offset, f'line_{offset + 1}')

    doc.save(output_path)
    return output_path
4.4 关键约束
切片编号逻辑与书签编号逻辑必须完全同源。

切片时生成 <!-- 1 --> <!-- 2 --> ... 的遍历逻辑，和书签写入时的遍历逻辑，
必须调用同一个 iter_block_items() 函数，从源头杜绝编号漂移。

五、前端实现
5.1 docx-preview 渲染
复制
import { renderAsync } from 'docx-preview'

const container = ref(null)

const renderDocx = async (arrayBuffer) => {
  await renderAsync(arrayBuffer, container.value, null, {
    className: 'docx-wrapper',
    inWrapper: true,
    ignoreWidth: false,
    ignoreHeight: false,
    ignoreFonts: false,
    breakPages: true,
    experimental: true  // 启用实验特性以获得更好的书签支持
  })
}
5.2 确认书签的 DOM 结构
docx-preview 渲染 w:bookmarkStart 时，会输出 DOM 元素。部署前必须用 F12 审查元素确认实际结构，常见形式：

复制
<!-- 可能的结构 1：带 id 的 span -->
<span id="line_1" class="docx-bookmark-start"></span>

<!-- 可能的结构 2：带 name 属性 -->
<a name="line_1"></a>

<!-- 可能的结构 3：带 data 属性 -->
<span data-bookmark="line_1"></span>
5.3 书签元素查找函数
兼容多种可能的 DOM 结构：

复制
/**
 * 在容器中查找书签对应的 DOM 元素
 * @param {HTMLElement} container - 预览容器
 * @param {number} lineNumber - 行号
 * @returns {HTMLElement|null}
 */
function findBookmarkElement(container, lineNumber) {
  const name = `line_${lineNumber}`

  // 按优先级依次尝试不同的查找方式
  return (
    container.querySelector(`#${name}`) ||
    container.querySelector(`[name="${name}"]`) ||
    container.querySelector(`[data-bookmark="${name}"]`) ||
    null
  )
}
5.4 跳转逻辑（完整版）
复制
import { nextTick } from 'vue'

const handleJumpToLine = async (lineNumber) => {
  const sliceMetadata = store.sliceMetadata

  // 1. 找到行号所在的切片
  const sliceIndex = sliceMetadata.findIndex(
    (s) => lineNumber >= s.startLine && lineNumber <= s.endLine
  )

  if (sliceIndex === -1) {
    console.warn(`行号 ${lineNumber} 不在任何切片范围内`)
    return
  }

  // 2. 切换到对应切片
  store.setPreviewMode('slice')
  store.setSelectedSliceIndex(sliceIndex)

  // 3. 等待 DOM 渲染完成
  await nextTick()

  // 4. 查找书签元素并滚动
  const container = document.querySelector('.preview-container')
  const target = findBookmarkElement(container, lineNumber)

  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'center' })

    // 5. 高亮闪烁提示（书签节点可能是空元素，高亮其相邻的可见元素）
    const visible =
      target.offsetHeight > 0 ? target : target.nextElementSibling
    if (visible) {
      visible.classList.add('highlight-flash')
      setTimeout(() => visible.classList.remove('highlight-flash'), 2000)
    }
  } else {
    console.warn(`未找到书签 line_${lineNumber} 对应的 DOM 元素`)
  }
}
5.5 高亮闪烁样式
复制
@keyframes flash-highlight {
  0%,
  100% {
    background-color: transparent;
  }
  50% {
    background-color: rgba(255, 213, 79, 0.4);
  }
}

.highlight-flash {
  animation: flash-highlight 0.6s ease-in-out 2;
  border-radius: 2px;
}
六、注意事项
6.1 书签 ID 唯一性
Word 规范要求同一文档内 w:id 全局唯一。招标文件可能已包含书签，后端写入时必须先扫描已有最大 ID，从其后开始编号（见 4.3 中的 existing_ids 处理）。

6.2 编号一致性（最重要）
以下三处的编号逻辑必须完全同源：

复制
后端切片编号 (<!-- id -->)        ← 使用 iter_block_items()
后端书签写入 (line_{id})          ← 使用 iter_block_items()
前端跳转查找 (findBookmarkElement) ← 使用相同的行号
6.3 大文档渲染延迟
切片切换后，如果文档较大，nextTick() 可能不足以等待 docx-preview 完成渲染。可加入 requestAnimationFrame 兜底：

复制
// 替换单纯的 await nextTick()
await nextTick()
await new Promise((resolve) => requestAnimationFrame(resolve))
6.4 特殊元素处理
场景	说明	处理方式
嵌套表格	表格内嵌套表格	iter_block_items 中按需递归处理内层表格
合并单元格	row.cells[0] 可能是合并后的单元格	不影响书签写入，书签打在段落上即可
图片段落	段落内包含图片	正常写入书签，docx-preview 会渲染图片所在的段落
空段落	内容为空的段落	后端不跳过，保持编号连续
七、验证清单
 后端：iter_block_items() 遍历顺序与切片编号一致
 后端：书签 ID 不与原文档已有书签冲突
 后端：空段落、表格行均正确编号
 前端：F12 确认 docx-preview 渲染书签的实际 DOM 结构
 前端：findBookmarkElement() 的选择器与实际 DOM 结构匹配
 前端：切片切换后等待渲染完成再查找元素
 集成：点击"第 x 行"能正确跳转到对应位置并高亮
 边界：测试首行、末行、表格行、图片行的跳转