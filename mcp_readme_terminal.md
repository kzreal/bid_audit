# MCP 服务器配置说明 - Claude 终端版本

## 概述

此 MCP 服务器将前端页面通过 **URI 资源** 暴露给终端版本的 Claude。

---

## 安装依赖

```bash
pip install mcp
```

---

## 配置方式

### 方式一：环境变量（推荐）

在启动 Claude 终端时设置环境变量：

```bash
# 设置 MCP 服务器
export ANTHROPIC_MCP_SERVERS='[{"name":"bid-review-frontend","command":"python3","args":["/Users/kyle/Projects/投标文件审核/mcp_server.py"]}'
```

然后启动 Claude：
```bash
claude
```

### 方式二：配置文件

创建或编辑 Claude 配置文件：

**macOS/Linux:**
```bash
# 创建配置文件
cat > ~/.config/claude/mcp_config.json << 'EOF'
{
  "servers": [
    {
      "name": "bid-review-frontend",
      "command": "python3",
      "args": ["/Users/kyle/Projects/投标文件审核/mcp_server.py"]
    }
  ]
}
EOF
```

**Windows (PowerShell):**
```powershell
$configPath = "$env:USERPROFILE\.config\claude\mcp_config.json"
$configDir = Split-Path $configPath
if (!(Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force
}

@'
{
  "servers": [
    {
      "name": "bid-review-frontend",
      "command": "python",
      "args": ["C:\\Users\\kyle\\Projects\\投标文件审核\\mcp_server.py"]
    }
  ]
}
'@ | Out-File -FilePath $configPath -Encoding UTF8
```

---

## 启动 MCP 服务器

### 手动启动（独立运行）

如果不想通过 Claude 配置，可以单独运行 MCP 服务器：

```bash
python3 /Users/kyle/Projects/投标文件审核/mcp_server.py
```

这样 MCP 服务器会以 stdio 模式运行，可以手动测试连接。

---

## 使用方式

### 在 Claude 对话中访问

启动 Claude 后，使用以下命令：

```
调用 MCP 工具 get_page_info
```

或者直接访问资源：
```
访问 URI 资源 http://localhost:5173
```

---

## 测试 MCP 连接

### 测试命令 1：列出资源

在 Claude 中输入：
```
列出所有可用的 MCP 资源
```

或发送：
```
发送 MCP 请求给 bid-review-frontend 服务器，方法：list_resources
```

**预期结果：**
- 前端页面: http://localhost:5173
- 后端健康检查: http://localhost:8888/health
- 后端API状态: http://localhost:8888/hiagent/status

### 测试命令 2：获取页面信息

在 Claude 中输入：
```
使用 get_page_info 工具
```

**预期结果：** 返回完整的访问指南，包括：
- 前端和后端 URL
- 页面元素选择器
- 操作流程示例
- Chrome DevTools 操作代码

---

## 常用操作示例

### 1. 访问前端页面

在 Claude 对话中：
```
访问前端页面 http://localhost:5173
```

### 2. 使用 get_page_info 工具

在 Claude 对话中：
```
调用 bid-review-frontend MCP 服务器的 get_page_info 工具
```

### 3. 结合浏览器调试

虽然 MCP 服务器本身不控制浏览器，但你可以：

1. **打开浏览器访问前端**
   ```
   http://localhost:5173
   ```

2. **使用 Chrome DevTools (F12)**
   - **Elements**: 查看页面结构和元素
   - **Console**: 执行 JavaScript 操作
   - **Network**: 监控 API 请求
   - **Application**: 查看本地存储和 Cookies

3. **推荐操作流程**

```
# 1. 查看任务列表
const tasks = document.querySelectorAll('[role="list"] > div');
tasks.forEach(t => console.log(t.textContent));

# 2. 点击"开始分析"按钮
const btn = document.querySelector('button:has-text("开始分析")');
btn.click();

# 3. 填写招标信息
const input = document.querySelector('textarea[name="requirement"]');
input.value = '招标文件内容...';
input.dispatchEvent(new Event('input', { bubbles: true }));

# 4. 上传文件
const uploadArea = document.querySelector('[role="upload"]');
// 拖拽文件到该区域
```

---

## 前后端服务启动

### 启动后端

```bash
cd /Users/kyle/Projects/投标文件审核
python3 backend_server.py
```

### 启动前端

```bash
cd /Users/kyle/Projects/投标文件审核/bid-review-system
npm run dev
```

---

## 故障排查

### 问题：Claude 无法连接到 MCP 服务器

1. **检查 MCP 服务器是否运行**
   ```bash
   # 测试 MCP 服务器是否正常响应
   echo '{"jsonrpc":"2.0","id":1,"method":"resources/list"}' | python3 -c "import sys,json; data=json.load(sys.stdin); print(json.dumps(data))" | python3 /Users/kyle/Projects/投标文件审核/mcp_server.py
   ```

2. **检查配置文件路径**
   ```bash
   # macOS/Linux
   ls -la ~/.config/claude/mcp_config.json

   # Windows
   dir %USERPROFILE%\.config\claude\
   ```

3. **检查环境变量**
   ```bash
   echo $ANTHROPIC_MCP_SERVERS
   ```

### 问题：无法访问前端页面

1. **确认前端服务状态**
   ```bash
   curl http://localhost:5173
   ```

2. **确认端口占用**
   ```bash
   lsof -ti:5173  # macOS/Linux
   netstat -ano | findstr :5173  # Windows
   ```

---

## 高级配置

### 添加更多 MCP 服务器

如果需要添加多个 MCP 服务器，修改配置文件：

```json
{
  "servers": [
    {
      "name": "bid-review-frontend",
      "command": "python3",
      "args": ["/Users/kyle/Projects/投标文件审核/mcp_server.py"]
    },
    {
      "name": "another-mcp-server",
      "command": "node",
      "args": ["/path/to/another/server.js"]
    }
  ]
}
```

### 禁用特定服务器

在配置中设置 `"disabled": true`：

```json
{
  "servers": [
    {
      "name": "bid-review-frontend",
      "command": "python3",
      "args": ["/Users/kyle/Projects/投标文件审核/mcp_server.py"],
      "disabled": false
    }
  ]
}
```

---

## MCP 协议说明

### 为什么使用 URI 资源？

- **URI 资源** 将页面 URL 声明为可访问资源
- 终端版本的 Claude 可以通过内置的浏览器或 `open` 命令访问 URI
- 这比使用 Tools 更符合"在网页上调试"的需求

### 可用的资源类型

```json
{
  "uri": "http://localhost:5173",
  "name": "前端页面",
  "description": "...",
  "mimeType": "text/html"
}
```

---

## 注意事项

1. **绝对路径 vs 相对路径**
   - 配置文件中的路径最好是绝对路径
   - 相对路径可能导致 MCP 服务器找不到文件

2. **Python 解释器**
   - 确保使用 `python3` 而不是 `python`（某些系统上 python2 已过时）
   - Windows 上可能需要使用 `py` 而不是 `python3`

3. **权限问题**
   - 确保 Python 脚本有执行权限
   - 确保路径可读

4. **编码问题**
   - JSON 配置文件应使用 UTF-8 编码
   - 中文字符可能需要转义

---

## 快速参考

| 命令 | 说明 |
|------|------|
| `export ANTHROPIC_MCP_SERVERS='...'` | 临时设置环境变量 |
| `~/.config/claude/mcp_config.json` | 持久化配置文件位置 |
| `claude` | 启动 Claude 终端 |
| `访问 http://localhost:5173` | 直接打开前端页面 |
| `F12` | 打开 Chrome DevTools |

---

## 需要帮助？

如果遇到问题，请检查：

1. Claude 终端的官方文档
2. MCP 协议规范: https://spec.modelcontextprotocol.io
3. 本项目的配置文件和日志

---

## 更新日志

- 2026-03-19: 初始版本，支持 Claude 终端配置
- 支持环境变量和配置文件两种方式
- 提供 URI 资源暴露前端页面
