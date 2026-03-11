# API 部分代码研究报告

## 文档信息

| 项目 | 内容 |
|------|------|
| 研究日期 | 2026-03-11 |
| 研究范围 | 投标文件审核系统 API 层代码 |
| 相关文件 | http.js, hiagentService.js, 环境配置, 类型定义 |

---

## 目录

1. [文件结构](#1-文件结构)
2. [HTTP 客户端 (http.js)](#2-http-客户端-httpjs)
3. [hiagent API 服务 (hiagentService.js)](#3-hiagent-api-服务-hiagentservicejs)
4. [环境变量配置](#4-环境变量配置)
5. [类型定义](#5-类型定义)
6. [API 端点说明](#6-api-端点说明)
7. [数据流向分析](#7-数据流向分析)
8. [发现的问题](#8-发现的问题)
9. [改进建议](#9-改进建议)

---

## 1. 文件结构

```
src/
├── services/
│   └── hiagentService.js      # hiagent API 服务层
├── utils/
│   └── http.js                # HTTP 客户端工具
└── types/
    └── index.js               # 类型常量定义

.env.development               # 开发环境配置
.env.production               # 生产环境配置
vite.config.js                # Vite 配置
```

---

## 2. HTTP 客户端 (http.js)

### 2.1 概述

`http.js` 封装了 Axios HTTP 客户端，提供了统一的请求/响应处理、错误处理和重试机制。

### 2.2 配置详情

```javascript
// Axios 实例配置
{
  baseURL: 'https://prd-ai-studio.chint.com/api/proxy/api/v1',
  timeout: 30000,              // 30秒超时
  headers: {
    'Content-Type': 'application/json'
  }
}
```

### 2.3 请求拦截器

| 功能 | 实现方式 |
|------|----------|
| API Key 注入 | 根据 URL 路径自动选择对应的 API Key |
| 防缓存 | GET 请求添加时间戳参数 `_t: Date.now()` |

**API Key 路由规则**:

```javascript
function getApiKey(url) {
  if (url.includes('/generate-tasks')) {
    return VITE_HIAGENT_API_KEY           // d6ntpsf4piphvinbnmh0
  } else if (url.includes('/review-task')) {
    return VITE_HIAGENT_REVIEW_API_KEY    // d6ntqaga61inpm569a3g
  }
  return VITE_HIAGENT_API_KEY
}
```

### 2.4 响应拦截器

**预期响应格式**:
```javascript
{
  code: 200,
  data: {},
  message: ''
}
```

**错误码映射**:

| HTTP 状态码 | 错误信息 |
|-------------|----------|
| 400 | 请求参数错误 |
| 401 | 认证失败，请检查 API key |
| 403 | 权限不足 |
| 404 | 请求的资源不存在 |
| 429 | 请求过于频繁，请稍后再试 |
| 500 | 服务器内部错误 |
| ECONNABORTED | 请求超时，请检查网络连接 |

### 2.5 重试机制

**实现细节**:

```javascript
retryRequest(requestFn, maxRetries = 3, delay = 1000)
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| maxRetries | 3 | 最大重试次数 |
| delay | 1000ms | 初始延迟时间 |

**重试策略**:
- 指数退避算法：`delay * Math.pow(2, i)`
- 不重试的错误：401（认证失败）
- 可重试的错误：NETWORK_ERROR, 500, 429

---

## 3. hiagent API 服务 (hiagentService.js)

### 3.1 导出模块

| 函数名 | 用途 |
|--------|------|
| `generateTasks` | 生成审核任务 |
| `reviewTask` | 执行任务审核 |
| `getApiStatus` | 获取 API 状态 |
| `API_ENDPOINTS` | API 端点常量 |

### 3.2 生成任务 API

**函数签名**:
```javascript
generateTasks({ requirement, bid, requirementType })
```

**参数说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requirement | string | ✅ | 招标信息文本 |
| bid | string | ✅ | 投标文件文本 |
| requirementType | string | ❌ | 要求类型 |

**请求数据结构**:
```javascript
{
  requirement: string,
  bid: string,
  requirementType: string,
  timestamp: string  // ISO 格式时间戳
}
```

**API 端点**: `POST /hiagent/generate-tasks`

**回退机制**: API 失败时返回模拟数据
```javascript
{
  tasks: [{
    id: 1,
    title: '技术方案评估',
    description: '评估投标文件中的技术方案是否完整、可行...',
    requirementSource: '需求文档',
    bidSource: '投标文件'
  }]
}
```

### 3.3 审核任务 API

**函数签名**:
```javascript
reviewTask({ taskId, requirement, bid, requirementType })
```

**参数说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| taskId | number | ✅ | 任务ID |
| requirement | string | ✅ | 招标信息文本 |
| bid | string | ✅ | 投标文件文本 |
| requirementType | string | ❌ | 要求类型 |

**请求数据结构**:
```javascript
{
  taskId: number,
  requirement: string,
  bid: string,
  requirementType: string,
  timestamp: string
}
```

**API 端点**: `POST /hiagent/review-task`

**回退机制**: API 失败时返回模拟数据
```javascript
{
  status: '待确认',
  reason: 'API 连接失败，返回模拟审核结果...',
  requirementSource: '需求文档',
  bidSource: '投标文件'
}
```

### 3.4 API 状态检查

**函数签名**: `getApiStatus()`

**API 端点**: `GET /hiagent/status`

**回退机制**: 失败返回
```javascript
{
  status: 'unknown',
  message: '无法连接到服务器'
}
```

---

## 4. 环境变量配置

### 4.1 开发环境 (.env.development)

```env
VITE_APP_TITLE=投标文件审核系统
VITE_API_BASE_URL=https://prd-ai-studio.chint.com/api/proxy/api/v1
VITE_HIAGENT_API_KEY=d6ntpsf4piphvinbnmh0
VITE_HIAGENT_REVIEW_API_KEY=d6ntqaga61inpm569a3g
```

### 4.2 生产环境 (.env.production)

```env
VITE_APP_TITLE=投标文件审核系统
VITE_API_BASE_URL=https://prd-ai-studio.chint.com/api/proxy/api/v1
VITE_HIAGENT_API_KEY=your_production_api_key_here
VITE_HIAGENT_REVIEW_API_KEY=your_production_review_api_key_here
```

### 4.3 配置说明

| 变量名 | 用途 | 开发环境值 |
|--------|------|------------|
| VITE_API_BASE_URL | API 基础 URL | prd-ai-studio.chint.com |
| VITE_HIAGENT_API_KEY | 任务生成 API 密钥 | d6ntpsf4piphvinbnmh0 |
| VITE_HIAGENT_REVIEW_API_KEY | 审核任务 API 密钥 | d6ntqaga61inpm569a3g |

**⚠️ 安全警告**: 生产环境 API Key 仍为占位符，需要配置真实密钥。

---

## 5. 类型定义

### 5.1 任务状态 (TaskStatus)

```javascript
{
  PENDING: 'pending',      // 待处理
  REVIEWING: 'reviewing',  // 审核中
  COMPLETED: 'completed'   // 已完成
}
```

### 5.2 审核状态 (ReviewStatus)

```javascript
{
  PASS: '通过',      // 符合要求
  FAIL: '不通过',    // 不符合要求
  PENDING: '待确认'  // 需要人工确认
}
```

### 5.3 招标要求类型 (RequirementType)

```javascript
{
  INFORMATION_CHECK: 'information-check',        // 信息核对
  BIDDING_REQUIREMENT: 'bidding-requirement',    // 招标要求
  GENERAL_REQUIREMENT: 'general-requirement'     // 通用要求
}
```

### 5.4 任务数据结构 (TaskSchema)

```javascript
{
  id: Number,
  title: String,
  description: String,
  requirementSource: String,
  bidSource: String,
  review: {
    status: String,
    reason: String,
    requirementSource: String,
    bidSource: String,
    score: Object
  },
  createdAt: Date,
  updatedAt: Date
}
```

### 5.5 审核结果数据结构 (ReviewSchema)

```javascript
{
  taskId: Number,
  status: String,
  reason: String,
  requirementSource: String,
  bidSource: String,
  score: Object,
  createdAt: Date
}
```

---

## 6. API 端点说明

### 6.1 端点列表

| 端点 | 方法 | 用途 | 认证 |
|------|------|------|------|
| `/hiagent/generate-tasks` | POST | 生成审核任务 | VITE_HIAGENT_API_KEY |
| `/hiagent/review-task` | POST | 执行任务审核 | VITE_HIAGENT_REVIEW_API_KEY |
| `/hiagent/status` | GET | 获取 API 状态 | - |

### 6.2 完整 URL 格式

```
开发环境:
https://prd-ai-studio.chint.com/api/proxy/api/v1/hiagent/generate-tasks
https://prd-ai-studio.chint.com/api/proxy/api/v1/hiagent/review-task
https://prd-ai-studio.chint.com/api/proxy/api/v1/hiagent/status

生产环境:
https://prd-ai-studio.chint.com/api/proxy/api/v1/hiagent/generate-tasks
https://prd-ai-studio.chint.com/api/proxy/api/v1/hiagent/review-task
https://prd-ai-studio.chint.com/api/proxy/api/v1/hiagent/status
```

---

## 7. 数据流向分析

### 7.1 生成任务流程

```
用户输入招标信息和投标文件
    ↓
generateTasks() 被调用
    ↓
参数验证
    ↓
retryRequest() 封装请求
    ↓
http.post('/hiagent/generate-tasks')
    ↓
请求拦截器注入 API Key
    ↓
发送到 API 服务器
    ↓
响应拦截器处理结果
    ↓
返回任务列表 或 回退到模拟数据
```

### 7.2 审核任务流程

```
用户选择任务并点击审核
    ↓
reviewTask() 被调用
    ↓
参数验证
    ↓
retryRequest() 封装请求
    ↓
http.post('/hiagent/review-task')
    ↓
请求拦截器注入 API Key
    ↓
发送到 API 服务器
    ↓
响应拦截器处理结果
    ↓
返回审核结果 或 回退到模拟数据
```

---

## 8. 发现的问题

### 8.1 安全问题

| 问题 | 严重性 | 说明 |
|------|--------|------|
| API Key 泄露风险 | 🔴 高 | 开发环境 API Key 直接写在 .env 文件中，可能被提交到代码仓库 |
| 生产环境密钥未配置 | 🔴 高 | 生产环境 API Key 仍为占位符 |
| 无 API Key 加密 | 🟡 中 | API Key 以明文形式存储和使用 |

### 8.2 架构问题

| 问题 | 严重性 | 说明 |
|------|--------|------|
| 硬编码 API 路径 | 🟡 中 | hiagentService.js 中 API 端点以字符串形式硬编码 |
| 响应格式假设 | 🟡 中 | 假设 API 返回 `{ code: 200, data: {}, message: '' }` 格式，未验证 |
| 缺少 API 文档 | 🟡 中 | 没有关于 hiagent API 的官方文档参考 |
| 类型定义不完整 | 🟡 中 | types/index.js 只定义了运行时常量，非 TypeScript 类型 |

### 8.3 错误处理问题

| 问题 | 严重性 | 说明 |
|------|--------|------|
| 静默失败 | 🟡 中 | API 失败时静默返回模拟数据，用户可能不知道 API 不可用 |
| 无错误上报 | 🟡 中 | 错误仅记录到 console.error，未上报到监控系统 |
| 回退数据单一 | 🟢 低 | 回退数据是固定的，无法模拟不同场景 |

### 8.4 代码质量问题

| 问题 | 严重性 | 说明 |
|------|--------|------|
| JSDoc 注释不完整 | 🟢 低 | 部分函数缺少详细注释 |
| 无单元测试 | 🔴 高 | API 层完全没有测试覆盖 |
| 缺少 TypeScript | 🟡 中 | 计划使用 TypeScript 但实际使用 JavaScript |

---

## 9. 改进建议

### 9.1 安全改进

1. **移除敏感信息**
   ```javascript
   // 使用 .gitignore 确保环境变量文件不被提交
   // 在项目 README 中说明如何配置环境变量
   ```

2. **配置真实生产密钥**
   ```env
   # .env.production
   VITE_HIAGENT_API_KEY=<真实的生产环境密钥>
   VITE_HIAGENT_REVIEW_API_KEY=<真实的生产环境审核密钥>
   ```

3. **添加 API 密钥轮换机制**
   ```javascript
   // 定期更换 API 密钥
   // 支持从后端服务获取临时 token
   ```

### 9.2 架构改进

1. **使用配置文件统一管理端点**
   ```javascript
   // config/api.js
   export const API_CONFIG = {
     BASE_URL: import.meta.env.VITE_API_BASE_URL,
     ENDPOINTS: {
       GENERATE_TASKS: '/hiagent/generate-tasks',
       REVIEW_TASK: '/hiagent/review-task',
       STATUS: '/hiagent/status'
     }
   }
   ```

2. **添加 API 响应验证**
   ```javascript
   // 验证 API 返回数据的格式和类型
   function validateApiResponse(response, schema) {
     // 实现响应验证逻辑
   }
   ```

3. **迁移到 TypeScript**
   ```typescript
   // 定义严格的类型接口
   interface GenerateTasksParams {
     requirement: string
     bid: string
     requirementType?: string
   }
   ```

### 9.3 错误处理改进

1. **添加错误提示组件**
   ```javascript
   // 当 API 失败时，向用户显示友好的错误提示
   showApiErrorToast('无法连接到服务器，正在使用离线模式')
   ```

2. **实现错误上报**
   ```javascript
   // 将错误信息发送到监控平台
   reportErrorToMonitoring(error, context)
   ```

3. **改进回退机制**
   ```javascript
   // 提供多种模拟数据场景
   const mockScenarios = {
     success: { /* 成功场景 */ },
     partialSuccess: { /* 部分成功场景 */ },
     failure: { /* 失败场景 */ }
   }
   ```

### 9.4 测试改进

1. **添加单元测试**
   ```javascript
   // 测试 hiagentService.js 的各个函数
   describe('hiagentService', () => {
     it('should generate tasks correctly', async () => {
       // 测试逻辑
     })
   })
   ```

2. **添加集成测试**
   ```javascript
   // 测试完整的 API 调用流程
   describe('API Integration', () => {
     it('should call generate-tasks endpoint', async () => {
       // 测试逻辑
     })
   })
   ```

3. **使用 Mock Server**
   ```javascript
   // 使用 MSW (Mock Service Worker) 模拟 API 响应
   import { setupServer } from 'msw/node'
   ```

---

## 附录

### A. API 调用示例

```javascript
// 生成任务
import { generateTasks } from '@/services/hiagentService'

const result = await generateTasks({
  requirement: '需要3年以上的项目管理经验',
  bid: '投标方拥有5年项目管理经验...',
  requirementType: 'bidding-requirement'
})

console.log(result.tasks)
```

```javascript
// 审核任务
import { reviewTask } from '@/services/hiagentService'

const result = await reviewTask({
  taskId: 1,
  requirement: '需要3年以上的项目管理经验',
  bid: '投标方拥有5年项目管理经验...',
  requirementType: 'bidding-requirement'
})

console.log(result.status)  // '通过' | '不通过' | '待确认'
console.log(result.reason)
```

### B. 错误处理示例

```javascript
import { generateTasks } from '@/services/hiagentService'

try {
  const result = await generateTasks({
    requirement: '...',
    bid: '...'
  })
  console.log(result.tasks)
} catch (error) {
  if (error.code === 'NETWORK_ERROR') {
    console.log('网络错误，请检查连接')
  } else if (error.code === 401) {
    console.log('认证失败，请检查 API Key')
  } else {
    console.log('未知错误:', error.message)
  }
}
```

---

## 总结

当前 API 层代码实现了基本的请求封装、错误处理和重试机制，能够满足核心功能需求。但存在以下主要问题：

1. **安全性不足**：API Key 管理不规范，生产环境密钥未配置
2. **缺少测试**：完全没有测试覆盖
3. **类型安全不足**：使用 JavaScript 而非 TypeScript
4. **错误处理不完善**：静默失败可能误导用户

建议优先解决安全问题和添加测试覆盖，然后逐步改进架构和类型安全。

---

**最后更新**: 2026-03-11
