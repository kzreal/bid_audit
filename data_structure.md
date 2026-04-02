# 投标文件审核系统数据流结构文档 (2026-04-01)

本文档记录了系统重构后，HiAgent 工作流各节点输出与后端解析器（`hiagent_client.py`）之间的数据流结构。

## 1. 任务生成阶段 (Task Generation)

### HiAgent 节点输出 (JSON)
工作流节点直接输出包含任务列表的 JSON 对象。

```json
{
  "output": [
    {
      "id": "1",
      "task": "请核实投标文件中投标人名称是否为'正泰电气股份有限公司'。"
    },
    {
      "id": "2",
      "task": "请核对投标文件中所有涉及金额的表述..."
    }
  ]
}
```

### 后端解析器: `TaskCreator.parse_tasks(tasks_text)`
- **输入**: 上述原始 JSON 字符串。
- **逻辑**: 提取 `output` 列表中的 `id` 和 `task` 字段。
- **返回 (List[Dict])**:
  ```python
  [
    {"id": "1", "content": "...", "subtasks": []},
    {"id": "2", "content": "...", "subtasks": []}
  ]
  ```

---

## 2. 审核阶段 (Audit/Review)

### HiAgent 节点输出 (JSON)
支持单切片或多切片审核，输出结构一致。

```json
{
  "output": [
    {
      "suggestion": "发现招标编号不一致：标准值为'ADB...'，实际为'AFD...'。",
      "evidence": "4, 12-15"
    }
  ]
}
```

### 后端解析器: `TaskAuditor.parse_audit_result(result_text)`
- **输入**: 上述原始 JSON 字符串。
- **逻辑**: 提取 `output` 列表中第一个元素的 `suggestion` 和 `evidence`。
- **返回 (Dict)**:
  ```python
  {
    "suggestion": "...",
    "evidence": "4, 12-15"
  }
  ```

---

## 3. 汇总/总结阶段 (Summary/Conclusion)

### HiAgent 节点输出 (JSON)
汇总节点对多切片结果进行总结，采用嵌套的 `results` 和 `reasons` 结构。

```json
{
  "results": [
    {
      "conclusion": "不通过",
      "reasons": [
        {
          "reason": "在'第一章'中，发现招标编号错误。",
          "evidence": "4"
        },
        {
          "reason": "在'授权委托书'中，未发现有效印章。",
          "evidence": "null"
        }
      ]
    }
  ]
}
```

### 后端解析器: `SummaryAgent.parse_conclusion(result_text)`
- **输入**: 上述原始 JSON 字符串。
- **逻辑**:
  1. 提取第一个 `results` 对象的 `conclusion`。
  2. 将 `reasons` 列表中的所有 `reason` 字段合并为换行分隔的字符串。
  3. 将所有有效的 `evidence`（非 "null"）合并为逗号分隔的字符串。
- **返回 (Dict)**:
  ```python
  {
    "conclusion": "不通过",
    "reason": "在'第一章'中...\n在'授权委托书'中...",
    "evidence": "4"
  }
  ```

---

## 4. 后端 API 路由对接 (backend_server.py)

所有路由均采用以下模式：
1. 调用 `hiagent_client` 的 `sync_run_workflow` 获取结果字典。
2. 使用 `json.dumps(result)` 将结果转为字符串传给对应的 `parse` 静态方法。
3. 解析后的结构直接返回给前端，供 Vue 组件渲染。

**更新说明**：已移除旧版本中对嵌套字符串的二次 `json.loads` 操作，所有节点均按照标准 JSON 对象进行通信。