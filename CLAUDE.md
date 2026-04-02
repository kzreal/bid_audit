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
├── hiagent_client.py         # HiAgent API 客户端封装
├── data_structure.md         # 数据流结构文档
├── .env                      # 环境变量（API Key 等）
├── CLAUDE.md                 # 本文档
├── frontend/                # 前端项目
│   ├── src/
│   │   ├── main.js           # Vue 入口
│   │   ├── App.vue           # 根组件
│   │   ├── style.css         # 全局样式
│   │   ├── components/       # Vue 组件
│   │   │   ├── Layout.vue                # 主布局（三栏）
│   │   │   ├── BidRequirementInput.vue   # 招标信息输入
│   │   │   ├── BidFileInput.vue          # 投标文件输入
│   │   │   ├── TaskListOptimized.vue     # 任务列表
│   │   │   ├── ReviewDetail.vue           # 审核详情
│   │   │   ├── TemplateDrawer.vue         # 模版库抽屉
│   │   │   ├── TemplateCard.vue           # 模版卡片
│   │   │   ├── TemplateEditor.vue         # 模版编辑器
│   │   │   └── TemplateTagSelector.vue    # 标签选择器
│   │   ├── services/
│   │   │   ├── hiagentService.js  # HiAgent API 调用
│   │   │   └── templateService.js  # 模版数据服务
│   │   ├── stores/
│   │   │   └── appStore.js        # Pinia 状态管理
│   │   └── utils/
│   │       └── http.js             # Axios 封装
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
  "task": {
    "id": 1,
    "title": "任务描述"
  },
  "reviews": [
    {
      "suggestion": "切片1审核建议",
      "evidence": "切片1证据"
    }
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
    "conclusion": "通过/不通过/待确认",
    "suggestions": [
      {"suggestion": "原因说明", "evidence": "证据"}
    ]
  },
  "status": "通过"
}
```

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
  suggestions: Array<{ suggestion: string; evidence: string }>;  // 审核发现列表
  bidSource?: string;         // 投标来源
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
  bidSlices: [],           // 投标文件切片数组
  contextText: '',         // 单个文本输入（兼容性保留）
  tasks: [],               // 任务列表
  selectedTaskId: null,     // 当前选中任务ID
  reviewing: false,         // 审核中状态
  apiStatus: null,          // API状态
  loading: false,           // 加载状态
  error: null,             // 错误信息
  templateDrawerOpen: false,       // 模版库抽屉开关
  currentEditingTemplate: null,     // 当前编辑的模版
  appliedTemplateHistory: []        // 应用历史（用于撤销）
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

// 多切片审核任务
reviewTaskSlices({ task: Task, slices: string[] })

// 生成最终审核结论
generateConclusion({ task: Task|string, reviews: SliceReview[] })

// 获取 API 状态
getApiStatus()
```

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
**三栏布局（35% + 30% + 35%）**：
- **左侧（35%）**：招标信息输入 + 文件上传
- **中间（30%）**：任务列表
- **右侧（35%）**：审核详情

---

## 组件说明

| 组件 | 说明 |
|------|------|
| `Layout.vue` | 主布局容器，包含头部和三栏内容区 |
| `BidRequirementInput.vue` | 招标文件信息输入区 |
| `BidFileInput.vue` | 投标文件输入区，支持多切片 |
| `TaskListOptimized.vue` | 任务列表，支持状态筛选和动画 |
| `ReviewDetail.vue` | 审核详情展示 |
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
2. **代理**：前端 Vite 开发服务器配置了代理，将 `/hiagent/*` 请求转发到 `http://localhost:8888`
3. **重试机制**：前端 `http.js` 实现了请求重试机制（指数退避）
4. **模版存储**：模版数据存储在浏览器 `localStorage`，键名为 `bid_review_templates`
