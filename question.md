# 投标文件审核系统 - 行号跳转问题

## 技术栈
- **前端**: Vue 3 + Pinia + Tailwind CSS
- **后端**: Flask + python-docx
- **测试**: Playwright E2E
- **文档格式**: Word (.docx) 预览，使用 docx-preview 库

## 问题描述

### 核心功能
系统需要实现：**点击审核结果中的"第x行"按钮，跳转到 Word 预览中对应的行**

### 数据流程

1. **后端切片时**：对每个 Word 元素（段落、表格行、图片）按出现顺序编号，生成 `<!-- id -->` 格式的标记

   切片内容示例：
   ```
   <!-- 1 --> # 投标函（适用于一步法开标方式）
   <!-- 2 --> ## 投标函
   <!-- 3 --> 华电（格尔木）能源有限公司(招标人名称)：
   ...
   <!-- 41 --> | 序号 | 条款名称 | ...
   ```

2. **切片元数据** (`sliceMetadata`)：
   ```js
   {
     index: 0,
     title: "投标函（适用于一步法开标方式）",
     startLine: 1,    // 原始行号
     endLine: 79      // 原始行号
   }
   ```

3. **前端渲染**：
   - 切片内容通过 `convertMarkdownToHtml()` 转换为 HTML
   - 通过 `injectLineNumbersForSlice()` 为元素添加 `data-line` 属性

4. **跳转逻辑** (`handleJumpToLine`)：
   ```js
   const handleJumpToLine = (lineNumber) => {
     // 1. 查找该行号属于哪个切片
     const sliceMetadata = store.sliceMetadata
     for (let i = 0; i < sliceMetadata.length; i++) {
       const slice = sliceMetadata[i]
       if (lineNumber >= slice.startLine && lineNumber <= slice.endLine) {
         // 2. 切换到切片预览模式
         store.setPreviewMode('slice')
         store.setSelectedSliceIndex(i)
         // 3. 没有调用 scrollToLine()！这是 bug
         return
       }
     }
   }
   ```

### 当前问题

1. **`handleJumpToLine` 找到切片后没有调用 `scrollToLine()`** - 这是主要 bug
2. **`convertMarkdownToHtml` 处理标题时丢失了 `<!-- id -->`** - 只提取了文本，丢失了注释
3. **`injectLineNumbersForSlice` 期望注释作为 DOM 注释节点，但 HTML 解析后是普通文本**

## 需要解决

1. 修复 `handleJumpToLine`，在切换切片后调用 `scrollToLine(targetLineInSlice)`
2. 确保 `convertMarkdownToHtml` 能正确将 `<!-- id -->` 转为 HTML 注释节点，或直接提取 ID 作为 data-line
3. 确保 `data-line` 属性使用原始行号（而非递增序号）

## 关键代码位置

- `MainLayout.vue:90` - `handleJumpToLine` 函数
- `WordPreviewPanel.vue:388` - `convertMarkdownToHtml` 函数
- `WordPreviewPanel.vue:446` - `injectLineNumbersForSlice` 函数
- `WordPreviewPanel.vue:498` - `scrollToLine` 函数

## 验证方法

打开 localStorage 中的 `bid_review_projects`，选择一个有切片的项目，点击审核结果中的"第x行"按钮，应跳转到正确的切片并高亮对应行。