# 投标文件审核系统数据流结构文档 (2026-04-02)

本文档记录了 HiAgent 工作流各节点输出与后端解析器（`hiagent_client.py`）之间的数据流结构。

## 核心数据流模式

```
前端 → backend_server.py 路由 → HiAgentClient.sync_run_workflow(input_dict)
                                         ↓
                                    HiAgent API 返回 dict
                                         ↓
                                   parse_* 静态方法提取字段
                                         ↓
                                    返回 JSON 给前端
```

所有 parse 方法**直接接收 dict**，不经过 json.dumps/json.loads 中转。

---

## 1. 任务生成阶段 (Task Generation)

### HiAgent 输出
```json
{
  "output": [
    {"id": "1", "task": "请核实投标文件中投标人名称是否为'正泰电气股份有限公司'。"},
    {"id": "2", "task": "请核对投标文件中所有涉及金额的表述..."}
  ]
}
```

### 解析: `TaskCreator.parse_tasks(result: Dict) -> List[Dict]`
- **输入**: HiAgent 响应 dict
- **逻辑**: `_extract_output(result)` 提取 output 列表中的 `id` 和 `task` 字段
- **返回**:
  ```python
  [
    {"id": "1", "content": "...", "subtasks": []},
    {"id": "2", "content": "...", "subtasks": []}
  ]
  ```

---

## 2. 审核阶段 (Audit/Review)

### HiAgent 输出
```json
{
  "output": [
    {"suggestion": "发现招标编号不一致：标准值为'ADB...'，实际为'AFD'...", "evidence": "4, 12-15"}
  ]
}
```

### 解析: `TaskAuditor.parse_audit_result(result: Dict) -> Dict`
- **输入**: HiAgent 响应 dict
- **逻辑**: 提取 `output` 列表中第一个元素的 `suggestion` 和 `evidence`
- **返回**:
  ```python
  {"suggestion": "...", "evidence": "4, 12-15"}
  ```

---

## 3. 汇总/总结阶段 (Summary/Conclusion)

### HiAgent 输出
```json
{
  "output": {
    "results": [
      {
        "conclusion": "不通过",
        "reasons": [
          {"reason": "在'第一章'中，发现招标编号错误。", "evidence": "4"},
          {"reason": "在'授权委托书'中，未发现有效印章。", "evidence": "null"}
        ]
      }
    ]
  }
}
```

### 解析: `SummaryAgent.parse_conclusion(result: Dict) -> Dict`
- **输入**: HiAgent 响应 dict
- **逻辑**:
  1. `_extract_output(result)` 提取 output
  2. 从 `results[0]` 取 `conclusion`
  3. 遍历 `reasons`，每个元素转为 `{suggestion, evidence}`
     - `suggestion`: 优先取 `suggestion`，否则取 `reason`
     - `evidence`: 有效值转字符串，`"null"` 或空值转为 `""`
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

### 后端 API 路由返回 (generate-conclusion)
```python
{
    "code": 200,
    "message": "总结成功",
    "data": {
        "conclusion": "不通过",
        "suggestions": [
            {"suggestion": "...", "evidence": "4"},
            {"suggestion": "...", "evidence": ""}
        ]
    },
    "status": "不通过"
}
```

---

## 4. 后端路由调用模式 (backend_server.py)

```python
# 1. 调用 HiAgent API（返回 dict）
result = client.sync_run_workflow(input_data)

# 2. 直接传 dict 给 parse 方法
parsed = XxxAgent.parse_xxx(result)

# 3. 返回给前端
return jsonify({"code": 200, "data": parsed})
```

## 5. `_extract_output` 工具函数

处理 HiAgent 可能的嵌套 JSON 字符串：
- `output` 是 list/dict → 直接返回
- `output` 是字符串 → `json.loads` 解析
- 嵌套 `{"output": {"output": ...}}` → 逐层展开
