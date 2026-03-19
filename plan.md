# 投标文件审核系统 - 最小化 MVP 开发计划

## Context

当前项目已有较完整的投标文件审核系统代码，但功能较为复杂。用户希望开发一个最小化 MVP 版本，能够快速运行并验证核心功能。

**用户需求确认：**
1. 保留类型选择功能（信息核对/招标要求/通用）
2. 支持多切片文件上传（最多 30 个 .md 文件）
3. 保持三栏布局（但简化内部组件）
4. API 失败时显示真实错误（不使用模拟数据）
5. 保留三个 HiAgent LLM API 调用（TaskCreator、TaskAuditor、SummaryAgent）

---

## 实施方案

### Phase 1: 后端简化

**目标：** 简化后端代码，移除调试功能，保留 5 个核心接口（包含三个 HiAgent LLM API 调用），新增多切片审核接口。

**需要修改的文件：**
- `/Users/kyle/Projects/投标文件审核/backend_server.py`

**具体修改：**

1. **保留三个 HiAgent 客户端**（核心功能，不删除）
   - `TaskCreator` - 生成审核任务
   - `TaskAuditor` - 审核单个任务
   - `SummaryAgent` - 生成最终审核结论

2. **移除调试接口**
   - 移除 `/hiagent/debug` 路由及其处理函数

3. **简化日志输出**
   - 移除详细的调试 print 语句
   - 保留关键错误日志

4. **保留的核心接口（4个）：**
   - `GET /health` - 健康检查
   - `GET /hiagent/status` - API 状态
   - `POST /hiagent/generate-tasks` - 生成审核任务（TaskCreator）
   - `POST /hiagent/review-task` - 审核单个任务（TaskAuditor，可选）

5. **新增接口（1个）：**
   - `POST /hiagent/review-task-slices` - 多切片审核并汇总（仅 TaskAuditor，不调用 SummaryAgent）

**新增接口代码：**

```python
@app.route('/hiagent/review-task-slices', methods=['POST'])
def review_task_slices():
    """
    多切片审核：对一个任务，用多个切片文件分别审核，然后汇总
    """
    try:
        data = request.get_json()
        task_input = data.get('task')
        slices = data.get('slices', [])  # 切片内容数组

        # 验证切片数量（最多 30 个）
        if len(slices) > 30:
            return jsonify({'code': 400, 'message': '切片数量不能超过 30 个'}), 400

        if not task_input:
            return jsonify({'code': 400, 'message': '任务不能为空'}), 400

        if not slices:
            return jsonify({'code': 400, 'message': '切片不能为空'}), 400

        # 提取任务描述
        if isinstance(task_input, dict):
            task = task_input.get('description', task_input.get('title', ''))
        else:
            task = str(task_input)

        print(f"开始多切片审核，任务：{str(task)[:50]}...，切片数：{len(slices)}")

        # 对每个切片调用 TaskAuditor
        reviews = []
        for idx, slice_text in enumerate(slices):
            print(f"正在审核切片 {idx+1}/{len(slices)}...")
            result_text = task_auditor.audit_task(task, slice_text, use_sync=True)
            parsed = TaskAuditor.parse_audit_result(result_text)
            reviews.append({
                'suggestion': parsed.get('suggestion', ''),
                'evidence': parsed.get('evidence', '')
            })

        # 直接返回汇总结果（不调用 SummaryAgent）
        return jsonify({
            'code': 200,
            'message': '多切片审核成功',
            'data': {
                'task': task,
                'reviews': reviews
            }
        })
    except Exception as e:
        import traceback
        error_msg = f"多切片审核失败：{str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({
            'code': 500,
            'message': '多切片审核失败',
            'error': str(e)
        }), 500
```

---

### Phase 2: 前端组件简化

**目标：** 简化前端组件，保持三栏布局，支持多切片文件上传。

**需要修改的文件：**

#### 2.1 简化 BidRequirementInput.vue
- **文件路径：** `/Users/kyle/Projects/投标文件审核/bid-review-system/src/components/BidRequirementInput.vue`
- **保留内容：**
  - 类型选择下拉框（信息核对/招标要求/通用）
  - 招标信息文本输入框
  - 字符计数
  - 清空按钮
- **无需修改：** 当前组件已经比较简洁

#### 2.2 简化并扩展 BidFileInput.vue
- **文件路径：** `/Users/kyle/Projects/投标文件审核/bid-review-system/src/components/BidFileInput.vue`
- **修改内容：**
  - **保留文件拖拽上传区域**（支持多文件选择）
  - **保留文件选择按钮**（允许选择多个文件）
  - 添加文件数量限制（最多 30 个）
  - 添加已上传文件列表显示
  - 移除文本输入框（只使用文件上传）
  - 只支持 .md 格式文件
  - 显示已上传的切片文件列表

#### 2.3 简化 Layout.vue
- **文件路径：** `/Users/kyle/Projects/投标文件审核/bid-review-system/src/components/Layout.vue`
- **保留内容：**
  - 三栏布局结构（左中右）
  - 错误提示区域
- **简化内容：**
  - 简化加载动画（可保留）
  - 简化"全部审核"按钮逻辑

#### 2.4 简化 TaskList 组件
- **文件路径：** `/Users/kyle/Projects/投标文件审核/bid-review-system/src/components/TaskListOptimized.vue`
- **简化内容：**
  - 移除虚拟滚动相关逻辑
  - 简化筛选功能（保留基本筛选）
  - 移除复杂的性能优化

#### 2.5 简化 ReviewDetail 组件
- **文件路径：** `/Users/kyle/Projects/投标文件审核/bid-review-system/src/components/ReviewDetail.vue`
- **修改内容：**
  - 简化审核结果展示 UI
  - **展示每个切片的审核结果列表**
  - **展示汇总后的最终结论**
  - 移除不必要的交互功能

---

### Phase 3: 前端服务和状态简化

**目标：** 简化 API 服务层和状态管理，移除模拟数据和复杂解析逻辑，添加多切片审核逻辑。

**新增：多切片文件上传和审核逻辑**

#### 3.1 简化 appStore.js
- **文件路径：** `/Users/kyle/Projects/投标文件审核/bid-review-system/src/stores/appStore.js`
- **修改内容：**
  - 保留核心状态：`requirementType`、`requirementText`、`slices`（替换 bidText）、`tasks`、`selectedTaskId`、`loading`、`error`
  - 保留核心 actions：`setRequirement`、`setSlices`（替换 setBidFile）、`generateTasks`、`reviewTaskSlices`（替换 reviewTask）、`selectTask`
  - 添加 `slices` 状态：存储上传的切片内容数组
  - 添加 `reviewTaskSlices` action：调用多切片审核接口
  - 移除模拟数据相关代码（`useMock` 参数和逻辑）
  - 移除复杂的验证逻辑

#### 3.2 简化 hiagentService.js
- **文件路径：** `/Users/kyle/Projects/投标文件审核/bid-review-system/src/services/hiagentService.js`
- **修改内容：**
  - 保留 `generateTasks` 函数（TaskCreator）
  - 保留 `reviewTask` 函数（TaskAuditor，可选）
  - **保留 `generateConclusion` 函数**（SummaryAgent - 核心功能）
  - **新增 `reviewTaskSlices` 函数**：调用多切片审核接口
  - 移除复杂的解析函数（`parseTaskText`、`parseBackendTasks`、`parseReviewText`）
  - 简化错误处理，直接显示真实错误
  - 移除模拟数据返回逻辑

**新增函数：**

```javascript
export const reviewTaskSlices = async (params) => {
  const { task, slices } = params

  if (!task) {
    throw new Error('任务不能为空')
  }

  if (!Array.isArray(slices) || slices.length === 0) {
    throw new Error('切片不能为空')
  }

  if (slices.length > 30) {
    throw new Error('切片数量不能超过 30 个')
  }

  const requestData = {
    task,
    slices,
    timestamp: new Date().toISOString()
  }

  return retryRequest(() =>
    http.post('/hiagent/review-task-slices', requestData)
  ).then(response => {
    return {
      conclusion: response.data?.conclusion || '',
      reason: response.data?.reason || '',
      evidence: response.data?.evidence || '',
      slicesReviews: response.data?.slices_reviews || [],
      createdAt: new Date()
    }
  }).catch(error => {
    console.error('多切片审核失败:', error)
    throw error
  })
}
```

#### 3.3 移除不需要的工具文件
- **删除文件：**
  - `/Users/kyle/Projects/投标文件审核/bid-review-system/src/utils/taskParser.js`
  - `/Users/kyle/Projects/投标文件审核/bid-review-system/src/utils/reviewParser.js`
  - `/Users/kyle/Projects/投标文件审核/bid-review-system/src/utils/mockData.js`
  - `/Users/kyle/Projects/投标文件审核/bid-review-system/src/utils/performance.js`
- **保留文件：**
  - `/Users/kyle/Projects/投标文件审核/bid-review-system/src/utils/http.js`

---

### Phase 4: 文档更新

**目标：** 创建 MVP 快速启动指南，更新现有文档。

#### 4.1 创建 MVP 快速启动指南
- **新建文件：** `/Users/kyle/Projects/投标文件审核/mvp-guide.md`
- **内容：**
  - MVP 功能说明
  - 快速启动步骤（简化版）
  - MVP 与完整版对比
  - 常见问题

#### 4.2 更新 guide.md
- **修改文件：** `/Users/kyle/Projects/投标文件审核/guide.md`
- **修改内容：**
  - 添加 MVP 版本说明
  - 更新项目结构图（标明 MVP 相关文件）
  - **更新多切片审核接口说明**
  - 更新 SummaryAgent 输入输出格式

---

### Phase 5: 验证测试

**目标：** 确保 MVP 能够正常运行。

#### 验证清单：

**后端验证：**
- [ ] 后端服务成功启动（端口 8888）
- [ ] `/health` 接口返回正常
- [ ] `/hiagent/status` 接口返回正常
- [ ] `/hiagent/generate-tasks` 接口可调用（TaskCreator）
- [ ] `/hiagent/review-task-slices` 接口可调用（多切片审核）

**前端验证：**
- [ ] 前端服务成功启动（端口 5173）
- [ ] 页面加载正常（无错误）
- [ ] 可以选择招标要求类型
- [ ] 可以输入招标信息
- [ ] 可以上传多个 .md 切片文件（最多 30 个）
- [ ] 点击"开始分析"能生成任务
- [ ] 任务列表能正确显示
- [ ] 点击任务能进行多切片审核
- [ ] 每个切片的审核结果能正确显示
- [ ] 最终汇总结论能正确显示
- [ ] API 失败时显示错误提示

**集成验证：**
- [ ] 前后端通信正常
- [ ] HiAgent API 调用成功
- [ ] 完整流程可用：输入 → 生成任务 → 多切片审核 → 汇总结果 → 查看最终结论

---

## 关键文件清单

### 需要修改的文件：

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend_server.py` | 修改 | 移除调试接口，新增多切片审核接口，保留三个 HiAgent LLM API |
| `BidFileInput.vue` | 修改 | 支持多文件上传（最多 30 个 .md 文件），显示文件列表 |
| `Layout.vue` | 修改 | 简化组件（可选） |
| `TaskListOptimized.vue` | 修改 | 移除虚拟滚动 |
| `ReviewDetail.vue` | 修改 | 简化 UI，展示多切片审核结果和最终结论 |
| `appStore.js` | 修改 | 添加 slices 状态，添加 reviewTaskSlices action，移除模拟数据逻辑 |
| `hiagentService.js` | 修改 | 添加 reviewTaskSlices 函数，移除复杂解析和模拟数据 |
| `guide.md` | 修改 | 用户会更新 HiAgent 接口输入输出说明 |

### 需要删除的文件：

| 文件 | 说明 |
|------|------|
| `src/utils/taskParser.js` | 任务解析工具 |
| `src/utils/reviewParser.js` | 审核结果解析工具 |
| `src/utils/mockData.js` | 模拟数据 |
| `src/utils/performance.js` | 性能优化工具 |

### 需要新建的文件：

| 文件 | 说明 |
|------|------|
| `mvp-guide.md` | MVP 快速启动指南 |

---

## 预估工作量

| 阶段 | 预估时间 | 优先级 |
|------|----------|--------|
| Phase 1: 后端简化 | 1.5 小时 | 高 |
| Phase 2: 前端组件简化 | 2 小时 | 高 |
| Phase 3: 服务和状态简化 + 多切片审核 | 2.5 小时 | 高 |
| Phase 4: 文档更新 | 0.5 小时 | 中 |
| Phase 5: 验证测试 | 1.5 小时 | 高 |
| **总计** | **8 小时** | - |

---

## MVP 功能特性

### 保留的核心功能：
1. 招标要求类型选择（信息核对/招标要求/通用）
2. 招标信息文本输入
3. 投标文件内容输入（多切片 .md 文件上传，最多 30 个）
4. 任务生成（基于 HiAgent API - TaskCreator）
5. 任务列表展示（三栏布局）
6. 多切片审核（基于 HiAgent API - TaskAuditor）
   - 支持上传多个 MD 格式切片文件（最多 30 个）
   - 每个切片单独审核
   - 汇总所有切片的审核结果
7. 审核结论生成（基于 HiAgent API - SummaryAgent）
   - 基于所有切片的审核结果生成最终结论
8. 审核结果展示（包含每个切片结果和最终结论）
9. 错误提示

### 移除的功能：
1. 虚拟滚动优化
2. 模拟数据
3. 复杂的任务/结果解析逻辑
4. 调试接口
5. 性能优化工具

---

## 启动方式（简化后）

```bash
# 启动后端
cd /Users/kyle/Projects/投标文件审核
python3 backend_server.py

# 启动前端（新终端）
cd /Users/kyle/Projects/投标文件审核/bid-review-system
npm run dev

# 访问地址
# 前端: http://localhost:5173
# 后端: http://localhost:8888
```

---

## 多切片审核数据流程

```
1. 用户上传多个 .md 切片文件（最多 30 个）
   ↓
2. 前端读取文件内容，构建 slices 数组
   ↓
3. 调用 /hiagent/review-task-slices 接口（传入 task + slices）
   ↓
4. 后端接收任务和切片数组
   ↓
5. 对每个切片调用 TaskAuditor API（单个任务，多个切片分别审核）
   ↓
6. 收集所有切片的审核结果（reviews 数组）
   ↓
7. 返回汇总结果（task + reviews）（不调用 LLM，代码直接汇总）
   ↓
8. 前端展示所有切片的审核结果
```

**关键说明：**
- 对每个任务，后端会对每个切片依次调用 TaskAuditor API 进行单独审核
- 所有切片审核完成后，汇总 reviews 数组
- **不调用 SummaryAgent API**，直接返回 reviews 数组作为汇总结果
- 前端负责对 reviews 数组进行进一步的展示或处理

---

## HiAgent 接口输入输出格式（更新版）

### TaskCreator 输入
```json
{
  "extraction": "招标文件信息内容",
  "type": 1
}
```

### TaskCreator 输出
```json
{
  "output": "{\n  \"tasks\": [\n    \"请核实投标文件中项目编号是否为\\\"ad1231313\\\"\"\n  ]\n}"
}
```
**解析说明：**
- HiAgent API 返回嵌套 JSON 结构
- 先解析外层 `{"output": "..."}`
- 再解析内部的 `tasks` 数组（字符串数组）

### TaskAuditor 输入（单切片）
```json
{
  "task": "任务描述",
  "context": "投标文件切片MD内容"
}
```

### TaskAuditor 输出
```json
{
  "output": "{\n  \"result\": {\n    \"suggestion\": \"本切片与当前审核任务无关。\",\n    \"evidence\": \"null\"\n  }\n}"
}
```
**解析说明：**
- HiAgent API 返回嵌套 JSON 结构
- 先解析外层 `{"output": "..."}`
- 再解析内部的 `result` 对象
- `result` 对象包含 `suggestion` 和 `evidence` 两个字段

### SummaryAgent 输入（汇总格式）
```json
{
  "task": "单条审核任务描述",
  "reviews": [
    {
      "suggestion": "该切片的审核建议",
      "evidence": "行号列表，或 null（表示本切片与任务无关）"
    },
    {
      "suggestion": "建议2",
      "evidence": "行号列表，或 null（表示本切片与任务无关）"
    }
  ]
}
```

### SummaryAgent 输出
```json
{
  "output": "{\"conclusion\": \"通过\", \"reason\": \"投标文件在第3章明确声明为制造商，并提供了生产资质证明。\", \"evidence\": \"276, 684-713\"}"
}
```
**解析说明：**
- HiAgent API 返回嵌套 JSON 结构
- 先解析外层 `{"output": "..."}`
- 再解析内部的结论对象
- 内部对象包含 `conclusion`、`reason`、`evidence` 三个字段
