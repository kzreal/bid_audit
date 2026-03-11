# HiAgent API 客户端使用说明

## 概述

本目录包含了调用 HiAgent API 的 Python 客户端代码，用于实现投标文件审核的两个主要功能：
1. **创建任务**：根据需求文本创建审核任务列表
2. **审核任务**：对每个任务进行审核并返回结果

## 文件说明

- `hiagent_client.py` - 核心客户端代码，包含 API 调用和结果解析
- `config.py` - 配置文件，管理不同环境的配置
- `usage_example.py` - 使用示例

## 获取 API 配置

在使用前，需要从 HiAgent 平台获取以下信息：

1. 登录 HiAgent 平台，进入智能体预览页
2. 在右侧找到 API 调用的配置：
   - **API URL**：API 基础地址，格式为 `http://域名:端口/api/proxy/api/v1`
   - **ApiKey**：鉴权密钥
3. 打开 API 访问开关

## 配置

编辑 `config.py` 文件，设置你的配置：

```python
# 基础配置
API_URL = "http://your-server:port/api/proxy/api/v1"
API_KEY = "your_api_key_here"
USER_ID = "user001"  # 1-20字符，仅支持字母和数字
```

## 快速开始

### 步骤1：创建审核任务

```python
from hiagent_client import TaskCreator
from config import config

# 从配置文件读取
task_creator = TaskCreator(config.API_URL, config.API_KEY, config.USER_ID)

# 需求文本
requirement = """
请根据招标文件，创建以下审核任务：
1. 审核项目资质是否满足要求
2. 审核技术方案是否符合技术规格
3. 审核报价是否在预算范围内
"""

# 创建任务（同步调用）
tasks_text = task_creator.create_tasks(requirement, use_sync=True)

# 解析任务
tasks = TaskCreator.parse_tasks(tasks_text)
for task in tasks:
    print(f"任务 {task['id']}: {task['content']}")
```

### 步骤2：审核任务

```python
from hiagent_client import TaskAuditor
from config import config

# 初始化
task_auditor = TaskAuditor(config.API_URL, config.API_KEY, config.USER_ID)

# 上下文文本
context = "招标文件的相关内容..."

# 审核任务
result_text = task_auditor.audit_task(task['content'], context, use_sync=True)

# 解析审核结果
result = TaskAuditor.parse_audit_result(result_text)
print(f"结论: {result['conclusion']}")
print(f"原因: {result['reason']}")
print(f"来源: {result['source']}")
```

## 数据格式说明

### 任务格式（1、2、3 编号）

HiAgent 返回的任务文本格式示例：
```
1、审核投标单位的资质文件
  1.1、检查营业执照
  1.2、检查资质证书
2、审核技术方案
  2.1、检查技术规格符合性
3、审核报价
```

解析后得到：
```python
[
    {
        'id': 1,
        'content': '审核投标单位的资质文件',
        'subtasks': [
            {'id': '1.1', 'content': '检查营业执照'},
            {'id': '1.2', 'content': '检查资质证书'}
        ]
    },
    {'id': 2, 'content': '审核技术方案', ...},
    {'id': 3, 'content': '审核报价', ...}
]
```

### 审核结果格式（#结论#原因#来源）

HiAgent 返回的审核结果格式示例：
```
通过#投标单位具备一级资质证书#招标文件第3.1条
```

解析后得到：
```python
{
    'conclusion': '通过',
    'reason': '投标单位具备一级资质证书',
    'source': '招标文件第3.1条'
}
```

## API 方法说明

### HiAgentClient 基类

| 方法 | 说明 |
|------|------|
| `sync_run_workflow(input_data)` | 同步运行工作流 |
| `async_run_workflow(input_data)` | 异步运行工作流，返回 runId |
| `query_workflow_process(run_id)` | 查询异步工作流运行状态 |

### TaskCreator 任务创建器

| 方法 | 说明 |
|------|------|
| `create_tasks(requirement, use_sync=True)` | 创建审核任务 |
| `parse_tasks(tasks_text)` | 解析任务文本 |

### TaskAuditor 任务审核器

| 方法 | 说明 |
|------|------|
| `audit_task(task, context, use_sync=True)` | 审核单个任务 |
| `parse_audit_result(result_text)` | 解析审核结果 |

## 同步 vs 异步调用

- **同步调用** (`use_sync=True`)：等待任务完成返回结果，简单直接（推荐）
- **异步调用** (`use_sync=False`)：提交任务后立即返回 runId，通过轮询获取结果

建议使用同步调用，除非任务执行时间较长。

## 错误处理

代码内置了重试机制：
- 默认重试次数：3 次
- 异步查询最大重试次数：10 次
- 采用指数退避策略

## 注意事项

1. **UserID** 必须是 1-20 个字符，且仅支持字母和数字
2. **InputData** 需要转换为 JSON 字符串格式
3. 所有接口都需要在 Header 中设置 `Apikey`
4. 调用工作流接口时，建议设置 `NoDebug=true` 以提升性能

## 环境配置

在 `config.py` 中可以通过修改 `environment` 变量来切换环境：

```python
environment = "production"  # 可选: "development", "test", "production"
```

各环境的配置分别定义在：
- `DevelopmentConfig`：开发环境
- `TestConfig`：测试环境
- `ProductionConfig`：生产环境

## 运行示例

```bash
# 配置好 config.py 后
python usage_example.py
```

## 完整流程示例

```python
from hiagent_client import TaskCreator, TaskAuditor
from config import config

# 初始化
task_creator = TaskCreator(config.API_URL, config.API_KEY, config.USER_ID)
task_auditor = TaskAuditor(config.API_URL, config.API_KEY, config.USER_ID)

# 需求和上下文
requirement = "创建审核任务..."
context = "招标文件内容..."

# 步骤1：创建任务
tasks_text = task_creator.create_tasks(requirement)
tasks = TaskCreator.parse_tasks(tasks_text)

# 步骤2：逐个审核
results = []
for task in tasks:
    result_text = task_auditor.audit_task(task['content'], context)
    result = TaskAuditor.parse_audit_result(result_text)
    results.append({'task': task, 'result': result})

# 步骤3：输出结果
for item in results:
    print(f"任务: {item['task']['content']}")
    print(f"结论: {item['result']['conclusion']}")
```