# 投标文件审核系统数据流结构文档 (2026-04-02)

本文档记录了 HiAgent 工作流各节点输出、后端解析器（`hiagent_client.py`）、以及前端数据消费之间的数据流结构。

## 1. 任务生成阶段 (Task Generation)

### HiAgent 节点输出 (JSON)

```json
{
  "output": [
    {"id": "1", "task": "请核实投标文件中投标人名称是否为'正泰电气股份有限公司'。"},
    {"id": "2", "task": "请核对投标文件中所有涉及金额的表述..."}
  ]
}
```

### 后端解析器: `TaskCreator.parse_tasks(result: Dict)`
- **输入**: `sync_run_workflow` 返回的 dict
- **逻辑**: `_extract_output()` 提取 `output` 列表中的 `id` 和 `task` 字段
- **返回**: `[{id, content, subtasks}]`

### 前端消费 (`appStore.js`)
- `generateTasks()` 调用后 → `response.data` 映射为 `{id, title: task.task || task.content, description: '', subtasks}`

---

## 2. 审核阶段 (Audit/Review)

### HiAgent 节点输出 (JSON)

```json
{
  "output": [
    {"suggestion": "发现招标编号不一致：标准值为'ADB...'，实际为'AFD'...", "evidence": "4, 12-15"}
  ]
}
```

### 后端解析器: `TaskAuditor.parse_audit_result(result: Dict)`
- **输入**: `sync_run_workflow` 返回的 dict
- **逻辑**: 提取 `output[0]` 的 `suggestion` 和 `evidence`
- **返回**: `{suggestion: str, evidence: str}`

### 前端消费 (`hiagentService.js`)
- `reviewTaskSlices()` 返回: `{data: {slices_reviews: [{suggestion, evidence}], ...}}`

---

## 3. 汇总/总结阶段 (Summary/Conclusion)

### HiAgent 节点输出 (JSON)

```json
{
  "results": [
    {
      "conclusion": "不通过",
      "reasons": [
        {"suggestion": "在'第一章'中，发现招标编号错误。", "evidence": "4"},
        {"suggestion": "在'授权委托书'中，未发现有效印章。", "evidence": "null"}
      ]
    }
  ]
}
```

### 后端解析器: `SummaryAgent.parse_conclusion(result: Dict)`
- **输入**: `sync_run_workflow` 返回的 dict
- **逻辑**:
  1. `_extract_output()` 提取输出
  2. 从 `results[0]` 提取 `conclusion`
  3. 遍历 `reasons` 列表，每个元素清洗为 `{suggestion, evidence}`
- **返回**:
  ```python
  {
    "conclusion": "不通过",
    "suggestions": [
      {"suggestion": "在'第一章'中，发现招标编号错误。", "evidence": "4"},
      {"suggestion": "在'授权委托书'中，未发现有效印章。", "evidence": ""}
    ]
  }
  ```

### 后端 API 路由返回 (`POST /hiagent/generate-conclusion`)
```python
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

### 前端消费 (`hiagentService.js` → `appStore.js`)

**`generateConclusion()`** 将 `data.suggestions` 映射为 `reason`:
```javascript
return {
  data: {
    conclusion: data.conclusion || '待确认',
    reason: data.suggestions || [],   // 后端 suggestions → 前端 reason
    evidence: '',
    ...
  }
}
```

**`reviewTaskWithSlices()`** 组装最终 review 对象:
```javascript
review: {
  conclusion: conclusionResponse.data?.conclusion || '待确认',
  reason: conclusionResponse.data?.reason ?? [],     // [{suggestion, evidence}]
  bidSource: allEvidence,                              // 所有 evidence 拼接，如 "4, 12-15, 23"
  slices_reviews: reviewsWithLineNumbers,
  ...
}
```

### 前端 UI 渲染

**`ReviewResultTab.vue`** 遍历 `reason` 数组:
```
┌─────────────────────────────────────┐
│ 结论: 不通过                          │
├─────────────────────────────────────┤
│ ┌─ 原因 1 ────────────────────────┐ │
│ │ 在"第一章"中，发现招标编号错误...  │ │
│ │ 定位：[段落 4] [段落 12-15]      │ │  ← 可点击跳转到文档位置
│ └─────────────────────────────────┘ │
│ ┌─ 原因 2 ────────────────────────┐ │
│ │ 在"授权委托书"中，未发现有效印章。 │ │
│ │ 定位：[段落 23]                  │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**`ReviewDetail.vue`** 同样遍历 `reason` 数组，并解析 evidence 中的行号为可点击 token。

---

## 4. 数据流全景

```
HiAgent API
    ↓ sync_run_workflow() → Dict
    ↓
后端 parse_*() 静态方法
    ↓ 返回结构化 Dict
    ↓ jsonify() → HTTP Response
    ↓
前端 hiagentService.js
    ↓ 映射/转换字段名
    ↓
appStore.js (Pinia)
    ↓ 组装 review 对象
    ↓
Vue 组件渲染 (ReviewResultTab / ReviewDetail)
```

**关键字段映射**:

| 后端字段 | 前端字段 | 说明 |
|---------|---------|------|
| `suggestions` (parse_conclusion) | `reason` (service/store) | 审核原因数组 `[{suggestion, evidence}]` |
| 各 reason 项的 `evidence` | `bidSource` (拼接) | 所有 evidence 行号拼接为定位字符串 |
| `conclusion` | `conclusion` | 审核结论（通过/不通过/待确认） |
