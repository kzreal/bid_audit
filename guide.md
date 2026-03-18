# 投标文件审核系统开发指南

## 项目概述

这是一个基于 **HiAgent API** 的投标文件智能审核系统，使用 Vue3 + Vite（前端）+ Flask + Python（后端）实现。

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         浏览器                               │
│                    (http://localhost:5173)                   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        前端服务                               │
│                   Vite Dev Server (5173)                     │
│  ┌─────────────┬─────────────┬──────────────────────────────┐   │
│  │  Vue 3     │  Pinia      │  Axios HTTP Client          │   │
│  │  (Composition│  (状态管理)  │  (请求封装)                │   │
│  │   API)      │             │                            │   │
│  └─────────────┴─────────────┴──────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
         Vite Proxy 配置转发 │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        后端服务                               │
│                  Flask Server (8888)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  hiagent_client.py (HiAgent API 客户端封装)        │   │
│  │  ├── HiAgentClient (基类)                            │   │
│  │  ├── TaskCreator (任务创建器)                         │   │
│  │  └── TaskAuditor (任务审核器)                         │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   HiAgent API (远程 AI 服务)                    │
│              https://prd-ai-studio.chint.com                 │
│                                                              │
│  工作流 API:                                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  POST /sync_run_app_workflow (同步运行工作流)        │   │
│  │  POST /run_app_workflow (异步运行工作流)             │   │
│  │  POST /query_run_app_process (查询异步运行状态)       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 核心组件说明

#### 1. 前端 (bid-review-system/)

**技术栈：**
- Vue 3 (Composition API)
- Vite (构建工具)
- Pinia (状态管理)
- Axios (HTTP 客户端)
- Tailwind CSS (样式框架)

**主要功能：**
- 招标信息输入
- 投标文件输入
- 任务列表展示
- 审核结果展示

#### 2. 后端 (backend_server.py)

**技术栈：**
- Flask (Web 框架)
- Flask-CORS (跨域支持)
- requests (HTTP 客户端)

**主要功能：**
- 作为前端和 HiAgent API 的中间层
- 处理配置管理（从 .env 读取）
- 提供 REST API 接口

#### 3. HiAgent 客户端 (hiagent_client.py)

**核心类：**

| 类名 | 功能 | API Key |
|------|------|---------|
| `HiAgentClient` | 基类，封装通用 API 调用逻辑 | - |
| `TaskCreator` | 根据招标要求生成审核任务 | TASK_CREATOR_API_KEY |
| `TaskAuditor` | 审核单个任务 | TASK_AUDITOR_API_KEY |
| `SummaryAgent` | 汇总审核结果并生成最终结论 | SUMMARY_API_KEY |

## HiAgent LLM 节点输入输出对齐

### HiAgent API 请求格式（统一）

```json
{
  "UserID": "250701283",           // 用户ID，必填，1-20字符，仅字母数字
  "InputData": "{...}",             // 输入数据JSON字符串，必填
  "NoDebug": true                    // 非debug模式，必填（推荐true）
}
```

### 1. TaskCreator（任务创建器）

**API Key**: `VITE_TASK_CREATOR_API_KEY`

#### InputData 结构

```json
{
  "extraction": "招标文件信息内容",  // string, 必填
  "type": 1                           // int, 必填
}
```

**type 参数值：**

| 值 | 含义 |
|----|-----|
| 0 | 核实信息 |
| 1 | 招标要求 |

#### HiAgent API 输出格式

```json
{
  "content": "{\n  \"tasks\": [\n    \"请核实投标文件中项目编号是否为\\\"ad1231313\\\"\"\n  ]\n}"
}
```

**解析说明：**
- `content` 字段包含一个 JSON 字符串
- 需要再次解析 `content` 获取内部的 `tasks` 数组
- `tasks` 数组中每个元素是一个任务字符串

**后端解析后标准格式：**

```json
{
  "code": 200,
  "message": "任务生成成功",
  "data": [
    {
      "id": 1,
      "content": "请核实投标文件中项目编号是否为\"ad1231313\"",
      "subtasks": []
    }
  ],
  "raw_text": "{...}"
}
```

---

### 2. TaskAuditor（任务审核器）

**API Key**: `VITE_TASK_AUDITOR_API_KEY`

#### InputData 结构

```json
{
  "task": "任务描述",           // string, 必填
  "context": "投标文件切片MD内容"  // string, 必填
}
```

**参数说明：**

| 参数名 | 数据类型 | 是否必填 | 说明 |
|--------|----------|----------|------|
| `task` | string | 是 | 当前要审核的任务描述 |
| `context` | string | 是 | 投标文件的一个切片的 MD 内容 |

#### HiAgent API 输出格式

```json
{
  "content": "{\n  \"result\": {\n    \"suggestion\": \"本切片与当前审核任务无关。\",\n    \"evidence\": \"null\"\n  }\n}"
}
```

**解析说明：**
- `content` 字段包含一个 JSON 字符串
- 需要再次解析 `content` 获取内部的 `result` 对象
- `result` 对象包含：
  - `suggestion`: 建议
  - `evidence`: 证据

**后端解析后标准格式：**

```json
{
  "code": 200,
  "message": "任务审核成功",
  "data": {
    "results": [
      {"suggestion": "本切片与当前审核任务无关。"},
      {"evidence": "null"}
    ]
  },
  "status": "待确认",
  "raw_text": "{...}"
}
```

**status 字段判断规则：**
- 如果 suggestion 包含"通过"、"符合"、"合格"、"满足" → 状态 = "通过"
- 如果 suggestion 包含"不通过"、"不符合"、"不合格"、"未通过" → 状态 = "不通过"
- 否则 → 状态 = "待确认"

---

### 3. SummaryAgent（总结 Agent）

**API Key**: `VITE_SUMMARY_API_KEY`

#### InputData 结构

```json
{
  "task": "请核实投标文件中投标人是否为生产制造商",
  "reviews": [
    {
      "chunk_id": "chapter_3",
      "suggestion": "投标文件在第3章明确声明为制造商，并提供了生产资质证明。",
      "evidence": "276, 684-713"
    },
    {
      "chunk_id": "chapter_5",
      "suggestion": "本切片与当前审核任务无关。",
      "evidence": null
    }
  ]
}
```

**参数说明：**

| 参数名 | 数据类型 | 是否必填 | 说明 |
|--------|----------|----------|------|
| `task` | string | 是 | 当前要总结的任务描述 |
| `reviews` | array | 是 | 所有切片的审核结果数组 |
| `reviews[].chunk_id` | string | 是 | 切片标识 |
| `reviews[].suggestion` | string | 是 | 该切片的建议 |
| `reviews[].evidence` | string/null | 是 | 该切片的证据 |

#### HiAgent API 输出格式

```json
{
  "content": "{\"conclusion\": \"通过\", \"reason\": \"投标文件在第3章明确声明为制造商，并提供了生产资质证明。\", \"evidence\": \"276, 684-713\"}"
}
```

**解析说明：**
- `content` 字段包含一个 JSON 字符串
- 需要再次解析 `content` 获取内部的 JSON 对象
- 解析后得到：
  - `conclusion`: 最终结论（"通过"、"不通过"、"待确认"）
  - `reason`: 原因说明
  - `evidence`: 证据

**后端解析后标准格式：**

```json
{
  "code": 200,
  "message": "总结成功",
  "data": {
    "conclusion": "通过",
    "reason": "投标文件在第3章明确声明为制造商，并提供了生产资质证明。",
    "evidence": "276, 684-713"
  },
  "raw_text": "{...}"
}
```

---

## 后端接口说明

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/hiagent/status` | GET | 获取 API 服务状态 |
| `/hiagent/debug` | POST | 生成任务并返回调试信息 |
| `/hiagent/generate-tasks` | POST | 生成审核任务列表 |
| `/hiagent/review-task` | POST | 审核单个任务 |
| `/hiagent/generate-conclusion` | POST | 生成最终审核结论 |

### POST /hiagent/generate-tasks

**请求：**
```json
{
  "requirement": "招标文件信息",
  "type": 1  // 可选，0: 核实信息, 1: 招标要求
}
```

**响应：**
```json
{
  "code": 200,
  "message": "任务生成成功",
  "data": [
    {
      "id": 1,
      "content": "请核实投标文件中项目编号是否为\"ad1231313\"",
      "subtasks": []
    }
  ],
  "raw_text": "{...}"
}
```

### POST /hiagent/review-task

**请求：**
```json
{
  "task": "任务描述（可以是对象或字符串）",
  "context": "投标文件切片MD内容"
}
```

**响应：**
```json
{
  "code": 200,
  "message": "任务审核成功",
  "data": {
    "results": [
      {"suggestion": "本切片与当前审核任务无关。"},
      {"evidence": "null"}
    ]
  },
  "status": "待确认",
  "raw_text": "{...}"
}
```

### POST /hiagent/generate-conclusion

**请求：**
```json
{
  "task": "请核实投标文件中投标人是否为生产制造商",
  "reviews": [
    {
      "chunk_id": "chapter_3",
      "suggestion": "投标文件在第3章明确声明为制造商，并提供了生产资质证明。",
      "evidence": "276, 684-713"
    },
    {
      "chunk_id": "chapter_5",
      "suggestion": "本切片与当前审核任务无关。",
      "evidence": null
    }
  ]
}
```

**响应：**
```json
{
  "code": 200,
  "message": "总结成功",
  "data": {
    "conclusion": "通过",
    "reason": "投标文件在第3章明确声明为制造商，并提供了生产资质证明。",
    "evidence": "276, 684-713"
  },
  "raw_text": "{...}"
}
```

---

## 配置说明

### 环境变量 (.env)

```env
# HiAgent API 配置
VITE_API_BASE_URL=https://prd-ai-studio.chint.com/api/proxy/api/v1
VITE_TASK_CREATOR_API_KEY=d6ntpsf4piphvinbnmh0
VITE_TASK_AUDITOR_API_KEY=d6oo7pn4piphvinbrb6g
VITE_SUMMARY_API_KEY=d6oo7pn4piphvinbrb7g
VITE_HIAGENT_USER_ID=250701283
```

### 前端配置 (vite.config.js)

```javascript
export default defineConfig({
  server: {
    host: '0.0.0.0',  // 允许局域网访问
    port: 5173,
    proxy: {
      '/hiagent': {
        target: 'http://localhost:8888',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8888',
        changeOrigin: true,
      }
    }
  }
})
```

---

## 端口说明

| 端口 | 服务 | 说明 |
|------|------|------|
| 5173 | 前端服务 | Vite 开发服务器默认端口 |
| 8888 | 后端服务 | Flask API 服务器 |

---

## 启动服务

### 方法一：分别启动

```bash
# 启动后端
python3 backend_server.py

# 启动前端（新终端）
cd bid-review-system
npm run dev
```

### 方法二：使用操作指南

详见 `操作指南.md` 文件，包含：
- 一键启动脚本
- 关闭服务命令
- 查看服务状态
- 常见问题排查

---

## 项目结构

```
投标文件审核/
├── backend_server.py       # Flask 后端服务
├── hiagent_client.py      # HiAgent API 客户端封装
├── config.py             # 配置文件
├── .env                  # 环境变量
├── bid-review-system/     # 前端项目
│   ├── src/
│   │   ├── App.vue
│   │   ├── services/
│   │   │   └── hiagentService.js
│   │   ├── utils/
│   │   │   ├── http.js
│   │   │   ├── taskParser.js
│   │   │   └── reviewParser.js
│   │   └── ...
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── guide.md             # 本文档
├── 操作指南.md           # 服务启动运维指南
└── hiagent_api.md       # HiAgent 官方 API 文档
```

---

## 常见问题

### Q1: 后端启动失败？
检查 .env 文件是否存在且配置正确。

### Q2: 前端无法连接后端？
- 检查后端是否在 8888 端口运行
- 检查 vite.config.js 的 proxy 配置
- 修改配置后需要重启服务

### Q3: HiAgent API 调用失败？
- 检查 API Key 是否正确
- 检查网络连接
- 查看后端日志了解详细错误

---

## 开发建议

1. **修改代码后**：前端修改后 Vite 会自动热更新，后端修改后需要手动重启
2. **调试**：可以使用 `/hiagent/debug` 端点查看详细的调试信息
3. **日志**：后端会输出详细的日志，包括请求和响应内容
