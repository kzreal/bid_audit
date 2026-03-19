# 投标文件审核系统 - MVP 快速启动指南

## 概述

MVP（最小化可行产品）版本的投标文件审核系统，基于 HiAgent API 实现，提供核心功能：
- 招标信息输入
- 投标文件多切片上传（最多 30 个文件）
- 任务自动生成
- 多切片智能审核
- 审核结果展示

## 快速启动

### 1. 环境准备

**系统要求：**
- Python 3.8+
- Node.js 16+
- npm 或 yarn

**依赖安装：**

后端依赖：
```bash
pip install flask flask-cors requests
```

前端依赖：
```bash
cd bid-review-system
npm install
```

### 2. 配置

确保 `.env` 文件存在于项目根目录：

```env
# HiAgent API 配置
VITE_API_BASE_URL=https://prd-ai-studio.chint.com/api/proxy/api/v1
VITE_TASK_CREATOR_API_KEY=d6ntpsf4piphvinbnmh0
VITE_TASK_AUDITOR_API_KEY=d6oo7pn4piphvinbrb6g
VITE_SUMMARY_API_KEY=d6oo7pn4piphvinbrb7g
VITE_HIAGENT_USER_ID=250701283
```

### 3. 启动服务

**启动后端：**
```bash
cd /Users/kyle/Projects/投标文件审核
python3 backend_server.py
```

后端将运行在：`http://localhost:8888`

**启动前端：**
```bash
cd /Users/kyle/Projects/投标文件审核/bid-review-system
npm run dev
```

前端将运行在：`http://localhost:5173`

### 4. 访问系统

在浏览器中打开：`http://localhost:5173`

## 使用流程

### 步骤 1：输入招标信息

1. 在左侧"招标要求类型"下拉框中选择类型：
   - 信息核对
   - 招标要求
   - 通用

2. 在"招标信息"文本框中输入或粘贴招标文件内容

### 步骤 2：上传投标文件切片

1. 拖拽多个 `.md` 或 `.txt` 文件到上传区域
2. 或点击"选择文件"按钮，选择多个文件（最多 30 个）

**注意：**
- 支持的文件格式：`.md`、`.txt`
- 文件数量限制：最多 30 个
- 已上传文件会显示在列表中，可以单独删除

### 步骤 3：开始分析

1. 点击"开始分析"按钮
2. 系统将调用 HiAgent API 生成审核任务
3. 任务列表会显示在中间栏

### 步骤 4：审核任务

1. 点击任务列表中的任务
2. 系统会自动开始审核（使用多切片审核）
3. 每个切片会依次调用 TaskAuditor API
4. 所有切片审核完成后，调用 SummaryAgent 生成最终结论
5. 审核结果显示在右侧

### 步骤 5：查看审核结果

右侧面板会显示：
- **审核结论**：通过/不通过/待确认
- **审核原因**：详细的审核说明
- **来源信息**：需求来源和投标来源
- **切片审核结果**：每个切片的审核详情

## MVP 接口列表

| 端点 | 方法 | 说明 | HiAgent API |
|------|------|------|-------------|
| `/health` | GET | 健康检查 | - |
| `/hiagent/status` | GET | 获取 API 服务状态 | - |
| `/hiagent/generate-tasks` | POST | 生成审核任务列表 | TaskCreator |
| `/hiagent/review-task` | POST | 审核单个任务 | TaskAuditor |
| `/hiagent/review-task-slices` | POST | 多切片审核并汇总 | TaskAuditor + SummaryAgent |
| `/hiagent/generate-conclusion` | POST | 生成最终审核结论 | SummaryAgent |

## MVP 功能特性

### 保留的核心功能
- ✅ 招标要求类型选择（信息核对/招标要求/通用）
- ✅ 招标信息文本输入
- ✅ 投标文件多切片上传（最多 30 个）
- ✅ 任务生成（基于 HiAgent API - TaskCreator）
- ✅ 任务列表展示（三栏布局）
- ✅ 多切片审核（基于 HiAgent API - TaskAuditor）
- ✅ 审核结论汇总（基于 HiAgent API - SummaryAgent）
- ✅ 审核结果展示（包含每个切片结果和最终结论）
- ✅ 错误提示（显示真实错误信息）

### 移除的功能
- ❌ 虚拟滚动优化
- ❌ 模拟数据
- ❌ 复杂的任务/结果解析逻辑
- ❌ 调试接口
- ❌ 性能优化工具
- ❌ 行号解析和分段展示

## MVP 与完整版对比

| 功能 | MVP | 完整版 |
|------|-----|--------|
| 文件上传 | 多切片上传（最多30个） | 单个文件上传 + 切片分割 |
| 虚拟滚动 | ❌ | ✅ |
| 模拟数据 | ❌ | ✅ |
| 调试接口 | ❌ | ✅ |
| 复杂解析 | ❌ | ✅ |
| 性能优化工具 | ❌ | ✅ |
| 行号解析 | ❌ | ✅ |
| 三栏布局 | ✅ | ✅ |
| 多切片审核 | ✅ | ✅ |
| 审核结论汇总 | ✅ | ✅ |

## 常见问题

### Q: 启动后端时提示端口被占用？
A: 修改 `backend_server.py` 最后一行的 `port` 参数，使用其他端口（如 8889）。

### Q: 前端无法连接后端？
A: 检查：
1. 后端是否正常运行（访问 `http://localhost:8888/health`）
2. `.env` 文件中的 API URL 是否正确
3. 防火墙是否阻止了连接

### Q: HiAgent API 调用失败？
A: 检查：
1. API Key 是否正确
2. API URL 是否可访问
3. 网络连接是否正常

### Q: 切片数量限制？
A: MVP 版本最多支持 30 个切片文件。如需更多，可以修改后端代码中的限制。

### Q: 如何查看详细错误信息？
A: MVP 版本会直接显示 API 返回的错误信息，不会使用模拟数据。查看错误提示或浏览器控制台。

### Q: 审核结果状态不正确？
A: 审核状态是基于 HiAgent API 返回的结论文本自动判断的：
- 包含"通过"、"符合"、"合格"、"满足" → 通过
- 包含"不通过"、"不符合"、"不合格"、"未通过" → 不通过
- 其他情况 → 待确认

## 项目结构

```
投标文件审核/
├── backend_server.py          # 后端服务（MVP 版本）
├── hiagent_client.py         # HiAgent API 客户端
├── .env                     # 配置文件
├── guide.md                 # 完整开发指南
├── mvp-guide.md            # 本文件 - MVP 快速启动指南
└── bid-review-system/        # 前端项目
    ├── src/
    │   ├── components/
    │   │   ├── BidRequirementInput.vue  # 招标信息输入
    │   │   ├── BidFileInput.vue         # 文件上传（多切片）
    │   │   ├── Layout.vue              # 主布局
    │   │   ├── TaskListOptimized.vue   # 任务列表
    │   │   └── ReviewDetail.vue       # 审核详情
    │   ├── stores/
    │   │   └── appStore.js            # 状态管理
    │   ├── services/
    │   │   └── hiagentService.js      # API 服务
    │   ├── utils/
    │   │   └── http.js               # HTTP 工具
    │   ├── types/
    │   │   └── index.js              # 类型定义
    │   └── main.js                   # 入口文件
    ├── package.json
    └── vite.config.js               # Vite 配置
```

## 开发说明

### MVP 版本特点
1. **代码简化**：移除了虚拟滚动、复杂解析、模拟数据等代码
2. **聚焦核心**：只保留多切片审核和结果展示的核心功能
3. **易于部署**：代码结构清晰，依赖少，便于快速部署
4. **真实数据**：所有 API 调用都使用真实数据，无模拟

### 扩展建议
如果需要扩展功能，可以考虑：
1. 添加虚拟滚动以支持大量任务
2. 添加模拟数据用于开发测试
3. 添加行号解析以支持精确引用
4. 添加更多筛选和排序功能
5. 添加审核历史记录功能

## 技术支持

如有问题，请参考 `guide.md` 获取更详细的开发文档。
