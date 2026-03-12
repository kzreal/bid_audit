# HiAgent 后端 API

服务器地址: `http://localhost:8888`

## API 端点

### 1. POST `/hiagent/debug`
生成任务并返回调试信息

```json
{
  "requirement": "需求文本"
}
```

### 2. POST `/hiagent/generate-tasks`
生成审核任务列表

```json
{
  "requirement": "需求文本",
  "type": 0  // 0: 核实信息, 1: 招标要求
}
```

**type=0 输出格式:**
```json
{"tasks": "请核实投标文件中招标人名称是否为"xyz公司""}
```

**type=1 输出格式:**
```json
{"tasks": [{"task1": "核实招标人是否为国有企业"}, {"task2": "核实招标人注册地址是否位于上海市"}]}
```

### 3. POST `/hiagent/review-task`
审核任务，返回审核结果

```json
{
  "task": "任务描述",
  "context": "投标文件内容"
}
```

**输出结果:**
```json
{"results": [{"conclusion": "通过"}, {"reason": "..."}, {"evidence": "页码范围"}]}
```

### 4. GET `/hiagent/status`
获取 API 服务状态

### 5. GET `/health`
健康检查

