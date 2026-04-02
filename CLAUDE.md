# 投标文件审核系统 - 项目文档

## 项目概述

这是一个基于 HiAgent API 的投标文件智能审核系统，使用 Vue3 + Vite（前端）+ Flask + Python（后端）实现。

**核心功能**：
1. 输入招标文件信息，AI 自动生成审核任务列表
2. 支持单文件或多切片文件审核
3. 模版库功能：保存和复用常用审核任务
4. 实时审核状态展示（通过/不通过/待确认）

---

## 技术栈

### 前端
- **Vue 3** (Composition API)
- **Vite** (构建工具)
- **Pinia** (状态管理)
- **Tailwind CSS** (样式框架)
- **Axios** (HTTP 客户端)

### 后端
- **Flask** (Web 框架)
- **Flask-CORS** (跨域支持)
- **requests** (HTTP 客户端)

### 外部 API
- **HiAgent API** (智能审核服务)

---

## 目录结构

```
投标文件审核/
├── backend_server.py          # Flask 后端服务（入口）
├── hiagent_client.py          # HiAgent API 客户端封装
├── data_structure.md          # 数据流结构文档
├── .env                       # 环境变量（API Key 等）
├── CLAUDE.md                  # 本文档
├── frontend/                  # 前端项目
│   ├── src/
│   │   ├── main.js            # Vue 入口
│   │   ├── App.vue            # 根组件
│   │   ├── style.css          # 全局样式
│   │   ├── components/        # Vue 组件
│   │   │   ├── MainLayout.vue           # 主布局（Tab导航+左右分栏）
│   │   │   ├── TabNavigator.vue         # 顶部Tab导航
│   │   │   ├── UploadTab.vue            # 项目创建/文件上传Tab
│   │   │   ├── CreateTaskTab.vue        # 创建任务Tab
│   │   │   ├── TaskListTab.vue          # 任务列表Tab
│   │   │   ├── TaskListOptimized.vue    # 任务卡片组件
│   │   │   ├── ReviewResultTab.vue      # 审核结果Tab（逐条suggestion+evidence）
│   │   │   ├── ReviewDetail.vue         # 审核详情（suggestion+可点击evidence）
│   │   │   ├── WordPreviewPanel.vue     # Word文档预览（带书签跳转）
│   │   │   ├── BidRequirementInput.vue  # 招标信息输入
│   │   │   ├── BidFileInput.vue         # 投标文件输入（多切片）
│   │   │   ├── TemplateDrawer.vue       # 模版库抽屉
│   │   │   ├── TemplateCard.vue         # 模版卡片
│   │   │   ├── TemplateEditor.vue       # 模版编辑器
│   │   │   └── TemplateTagSelector.vue  # 标签选择器
│   │   ├── services/
│   │   │   ├── hiagentService.js  # HiAgent API 调用封装
│   │   │   ├── templateService.js # 模版数据服务
│   │   │   └── projectService.js  # 项目管理服务（localStorage）
│   │   ├── stores/
│   │   │   └── appStore.js        # Pinia 状态管理
│   │   └── utils/
│   │       └── http.js            # Axios 封装
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
```

---

## 启动方式

### 后端服务
```bash
cd /Users/kyle/Projects/投标文件审核
python3 backend_server.py
```
- 地址：`http://localhost:8888`
- 局域网访问：`http://10.128.228.194:8888`

### 前端服务
```bash
cd /Users/kyle/Projects/投标文件审核/frontend
npm run dev
```
- 开发服务器自动代理 `/hiagent/*` 请求到后端
- 局域网访问：`http://10.128.228.194:5174`

---

## API 接口文档

### 后端 Flask API

基础路径：`http://localhost:8888`

#### 1. 生成审核任务
```
POST /hiagent/generate-tasks
```

**请求体**：
```json
{
  "requirement": "招标文件内容文本...",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "任务生成成功",
  "data": [
    {
      "id": 1,
      "content": "任务描述1",
      "subtasks": []
    },
    {
      "id": 2,
      "content": "任务描述2",
      "subtasks": []
    }
  ]
}
```

#### 2. 审核任务（单文件）
```
POST /hiagent/review-task
```

**请求体**：
```json
{
  "task": {
    "id": 1,
    "title": "任务描述"
  },
  "context": "投标文件内容...",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "任务审核成功",
  "data": {
    "suggestion": "审核建议文本",
    "evidence": "证据/来源文本"
  }
}
```

#### 3. 多切片审核任务
```
POST /hiagent/review-task-slices
```

**请求体**：
```json
{
  "task": {
    "id": 1,
    "title": "任务描述"
  },
  "slices": ["切片1内容", "切片2内容", "切片3内容"],
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "多切片审核成功",
  "data": {
    "task": "任务描述",
    "reviews": [
      {
        "suggestion": "切片1审核建议",
        "evidence": "切片1证据"
      },
      {
        "suggestion": "切片2审核建议",
        "evidence": "切片2证据"
      }
    ]
  }
}
```

#### 4. 生成最终结论
```
POST /hiagent/generate-conclusion
```

**请求体**：
```json
{
  "task": "任务描述文本",
  "reviews": [
    {"title": "切片标题", "suggestion": "切片审核建议", "evidence": "4, 12-15"}
  ],
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

**响应**：
```json
{
  "code": 200,
  "message": "总结成功",
  "data": {
    "conclusion": "不通过",
    "suggestions": [
      {"suggestion": "在'第一章'中，发现招标编号错误。", "evidence": "4"},
      {"suggestion": "在'授权委托书'中，未发现有效印章。", "evidence": ""}
    ]
  },
  "status": "不通过"
}
```

> **注意**：`data.suggestions` 是审核原因数组，每项包含 `suggestion`（原因描述）和 `evidence`（行号定位）。前端 `hiagentService.js` 将 `suggestions` 映射为 `reason` 字段。

#### 5. 获取 API 状态
```
GET /hiagent/status
```

**响应**：
```json
{
  "code": 200,
  "message": "API 服务正常",
  "data": {
    "api_url": "https://prd-ai-studio.chint.com/api/proxy/api/v1",
    "user_id": "250701283",
    "status": "running"
  }
}
```

#### 6. 健康检查
```
GET /health
```

**响应**：
```json
{
  "status": "ok",
  "message": "HiAgent Backend Server is running"
}
```

---

## 前端数据结构

### 任务对象 (Task)
```typescript
interface Task {
  id: number | string;      // 唯一标识
  title: string;             // 任务标题
  description: string;       // 任务描述（可空）
  subtasks: SubTask[];       // 子任务
  review?: Review;           // 审核结果
  createdAt: Date;           // 创建时间
  updatedAt: Date;           // 更新时间
}
```

### 审核结果对象 (Review)
```typescript
interface Review {
  conclusion: '通过' | '不通过' | '待确认';  // 审核结论
  reason: Array<{ suggestion: string; evidence: string }>;  // 审核原因数组（来自后端 suggestions）
  bidSource?: string;         // 行号定位字符串，如 "4, 12-15, 23"（从 reason 中收集）
  requirementSource?: string;  // 招标要求来源
  slices_reviews?: SliceReview[];  // 切片审核结果
  createdAt: Date;           // 创建时间
}
```

### 切片审核对象 (SliceReview)
```typescript
interface SliceReview {
  suggestion: string;  // 审核建议
  evidence: string;    // 证据
}
```

### 模版对象 (Template)
```typescript
interface Template {
  id: string;           // 模版ID
  name: string;         // 模版名称
  description: string;  // 模版描述
  tags: string[];       // 标签
  tasks: string[];      // 任务列表（字符串数组）
  createdAt: string;    // 创建时间
  updatedAt?: string;   // 更新时间
}
```

---

## 前端 Pinia Store

### useAppStore 状态
```javascript
state: {
  requirementText: '',      // 招标信息
  bidSlices: [],           // 投标文件切片数组 [{index, title, level, content, startLine, endLine}]
  sliceMetadata: [],       // 切片元数据 [{index, title, level, startLine, endLine}]
  contextText: '',         // 单个文本输入（兼容性保留）
  tasks: [],               // 任务列表
  selectedTaskId: null,    // 当前选中任务ID
  reviewing: false,        // 审核中状态
  apiStatus: null,         // API状态
  loading: false,          // 加载状态
  error: null,             // 错误信息
  templateDrawerOpen: false,       // 模版库抽屉开关
  currentEditingTemplate: null,    // 当前编辑的模版
  appliedTemplateHistory: [],      // 应用历史（用于撤销）
  currentTab: 'upload',            // 当前Tab (upload/create-task/task-list/review-result)
  wordDocument: null,              // Word文档文件对象
  wordDocumentWithBookmarks: null, // 带书签的Word文档（预览用）
  highlightLine: null,             // 高亮行号
  previewMode: 'original',        // 预览模式 (original/slice)
  projectName: '',                 // 项目名称
  sliceLevel: 0,                   // 切片层级
  selectedSliceIndex: null,        // 当前选中的切片索引
  currentProjectId: null,          // 当前项目ID
  projects: []                     // 项目列表
}
```

### 关键 Getters
```javascript
selectedTask      // 当前选中的任务对象
taskStats         // { total, reviewed, passed, failed, pending }
canAnalyze        // 是否可以开始分析（requirementText 非空）
canReview         // 是否可以开始审核
useSliceReview    // 是否使用多切片审核（bidSlices.length > 0）
canUndoTemplateApplication  // 是否可以撤销模版应用
```

---

## 前端 API 服务 (hiagentService.js)

```javascript
// 生成审核任务
generateTasks({ requirement: string })

// 审核任务（单文件）
reviewTask({ task: Task, context: string })

// 多切片审核任务（返回 slices_reviews + 待确认状态）
reviewTaskSlices({ task: Task, slices: string[] })

// 生成最终审核结论
// 后端返回 data.suggestions 数组 → 前端映射为 reason 字段
generateConclusion({ task: Task|string, reviews: SliceReview[] })

// 获取 API 状态
getApiStatus()
```

### 数据字段映射说明

后端 `SummaryAgent.parse_conclusion()` 返回 `{conclusion, suggestions}`，其中 `suggestions` 为 `[{suggestion, evidence}]` 数组。

前端处理链路：
1. `hiagentService.js`: `data.suggestions` → `reason` 字段
2. `appStore.js`: 收集所有 `reason[].evidence` → `bidSource` 定位字符串
3. `ReviewResultTab.vue` / `ReviewDetail.vue`: 遍历 `reason` 数组逐条渲染，evidence 解析为可点击的行号按钮

---

## 设计规范

### 设计风格
**Vercel 风格 + Next.js 文档风格**
- 极简黑白配色为主
- 头部保留蓝色渐变作为品牌识别
- 1px 细边框，极小圆角 (2px)

### 状态色
```css
通过: #22c55e (绿色)
不通过: #ef4444 (红色)
待确认: #f59e0b (黄色)
```

### 布局结构
**Tab 导航 + 左右分栏**：
- **顶部 Tab 栏**：创建项目 | 创建任务 | 任务列表 | 审核结果
- **左侧**：任务列表 / 审核结果（根据当前 Tab 切换）
- **右侧**：Word 文档预览（带书签跳转）

---

## 组件说明

| 组件 | 说明 |
|------|------|
| `MainLayout.vue` | 主布局容器，Tab 导航 + 左右分栏 |
| `TabNavigator.vue` | 顶部 Tab 导航（创建项目/创建任务/任务列表/审核结果） |
| `UploadTab.vue` | 项目创建/加载 Tab（文件上传 + 切片） |
| `CreateTaskTab.vue` | 创建任务 Tab（输入招标信息 + 生成任务） |
| `TaskListTab.vue` | 任务列表 Tab（任务卡片 + 批量审核） |
| `ReviewResultTab.vue` | 审核结果 Tab（概览统计 + 逐条显示 suggestion + evidence 定位按钮） |
| `ReviewDetail.vue` | 单任务审核详情（结论 + reason 数组 + evidence 可点击跳转） |
| `TaskListOptimized.vue` | 任务卡片组件（状态色条 + 筛选） |
| `BidRequirementInput.vue` | 招标文件信息输入区 |
| `BidFileInput.vue` | 投标文件输入区，支持多切片 |
| `WordPreviewPanel.vue` | Word 文档预览面板（带书签跳转） |
| `TemplateDrawer.vue` | 模版库抽屉（侧边滑出） |
| `TemplateCard.vue` | 模版卡片组件 |
| `TemplateEditor.vue` | 模版编辑器 |
| `TemplateTagSelector.vue` | 模版标签选择器 |

---

## 环境变量 (.env)

```env
VITE_API_BASE_URL=https://prd-ai-studio.chint.com/api/proxy/api/v1
VITE_TASK_CREATOR_API_KEY=your_api_key_here
VITE_TASK_AUDITOR_API_KEY=your_api_key_here
VITE_SUMMARY_API_KEY=your_api_key_here
VITE_HIAGENT_USER_ID=250701283
```

---

## 注意事项

1. **CORS**：后端已配置 `CORS(app)`，允许所有来源的跨域请求
2. **代理**：前端 Vite 开发服务器配置了代理，将 `/hiagent/*` 和 `/document/*` 请求转发到 `http://localhost:8888`
3. **重试机制**：前端 `http.js` 实现了请求重试机制（指数退避）
4. **模版存储**：模版数据存储在浏览器 `localStorage`，键名为 `bid_review_templates`
5. **字段映射**：后端返回 `suggestions` 数组，前端统一映射为 `reason` 字段。UI 组件遍历 `reason` 数组逐条显示
6. **证据定位**：每个 reason 项的 `evidence` 字段包含行号（如 "4, 12-15"），前端解析为可点击按钮，点击跳转到 Word 文档对应段落
7. **书签预览**：`/document/preview-with-bookmarks` 接口在文档中插入 `line_N` 格式书签，与切片行号一一对应
8. **文件大小**：后端限制上传文件大小为 2GB
