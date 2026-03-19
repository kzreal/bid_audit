# MCP 服务器配置说明

## 概述

此 MCP 服务器将前端页面通过 **URI 资源** 暴露给 Claude，使其能够通过浏览器访问页面进行调试。

---

## 安装步骤

### 1. 安装 Python 依赖

```bash
pip install mcp
```

### 2. 在 Claude Desktop 中配置 MCP 服务器

**方法一：通过 Claude Desktop 设置界面**

1. 打开 Claude Desktop
2. 点击左侧 "..." 菜单 > Settings
3. 在 "MCP Servers" 标签页，点击 "+" 按钮
4. 配置以下信息：

| 配置项 | 值 |
|--------|-----|
| Name | bid-review-frontend |
| Command | python3 |
| Arguments | /Users/kyle/Projects/投标文件审核/mcp_server.py |

5. 点击 "Add" 添加服务器

**方法二：通过配置文件**

编辑 Claude Desktop 配置文件（通常在 `~/Library/Application Support/Claude/claude_desktop_config.json`）：

```json
{
  "mcpServers": [
    {
      "name": "bid-review-frontend",
      "command": "python3",
      "args": ["/Users/kyle/Projects/投标文件审核/mcp_server.py"]
    }
  ]
}
```

---

## 启动服务

### 方式一：手动启动（测试用）

```bash
# 直接运行 MCP 服务器
python3 /Users/kyle/Projects/投标文件审核/mcp_server.py
```

### 方式二：通过 Claude Desktop（推荐）

配置完成后，重启 Claude Desktop，MCP 服务器会自动启动。

---

## 使用方式

### 在 Claude 对话中访问前端页面

**调用工具：**
```
使用 get_page_info 工具
```

**返回内容：**
- 前端页面 URL
- 后端 API 地址
- 页面元素选择器列表
- 完整操作流程示例
- Chrome DevTools 常用操作代码

### 直接浏览器访问

在 Claude 返回 URL 后，你也可以：

1. **直接复制 URL 到浏览器**
   ```
   http://localhost:5173
   ```

2. **使用浏览器扩展（如果安装了）**
   某些 MCP 客户端提供内置浏览器支持

---

## 可用资源

启动 MCP 服务器后，Claude 可以访问以下资源：

| 资源 | URI | 说明 |
|------|-----|------|
| 前端页面 | http://localhost:5173 | 可通过浏览器直接访问 |
| 后端健康检查 | http://localhost:8888/health | 后端服务健康检查 |
| 后端API状态 | http://localhost:8888/hiagent/status | 后端 API 服务状态 |

---

## 可用工具

| 工具名 | 说明 |
|--------|------|
| get_page_info | 获取前端页面访问指南和操作说明 |

---

## 注意事项

1. **确保前端服务已启动**
   ```bash
   cd /Users/kyle/Projects/投标文件审核/bid-review-system
   npm run dev
   ```

2. **确保后端服务已启动**
   ```bash
   cd /Users/kyle/Projects/投标文件审核
   python3 backend_server.py
   ```

3. **端口冲突**
   - 前端默认端口: 5173
   - 后端默认端口: 8888
   - 如果端口冲突，请修改对应服务的端口配置

4. **Chrome DevTools 访问**
   - 按 F12 打开开发者工具
   - 使用 Console 执行 JavaScript 操作
   - 使用 Network 标签查看 API 请求

---

## 故障排查

### 问题：MCP 服务器无法连接

1. 检查 Python mcp 包是否已安装
   ```bash
   pip show mcp
   ```

2. 检查文件路径是否正确
   ```bash
   ls -la /Users/kyle/Projects/投标文件审核/mcp_server.py
   ```

3. 查看 Claude Desktop 日志
   - macOS: ~/Library/Logs/Claude/
   - Windows: %APPDATA%\Claude\logs\

### 问题：无法访问前端页面

1. 确认前端服务是否正在运行
   ```bash
   lsof -ti:5173
   ```

2. 检查防火墙设置

---

## 技术说明

### 为什么使用 URI 资源而不是 Tools？

- **URI 资源** 将页面 URL 暴露为可访问链接
- Claude 可以通过内置浏览器功能直接访问该 URL
- 这样更符合"在网页上查看和调试"的需求
- Tools 主要用于在代码中执行操作，不适合网页交互场景

### Chrome DevTools 集成

虽然 MCP 服务器本身不提供浏览器控制，但结合 Chrome DevTools 可以实现完整的调试能力：

| 功能 | 实现方式 |
|------|----------|
| 查看页面元素 | Chrome Elements 面板 |
| 执行操作 | Chrome Console |
| 监控API | Chrome Network 面板 |
| 调试样式 | Chrome Sources/Elements |
| 性能分析 | Chrome Performance 面板 |

---

## 进阶功能（可选）

如果需要更深入的交互能力，可以考虑集成：

### Puppeteer MCP Server
```bash
npm install -g @modelcontextprotocol/server-puppeteer
```

### Playwright MCP Server
```bash
npm install -g @modelcontextprotocol/server-playwright
```

这些 MCP 服务器提供了完整的浏览器控制能力，包括：
- 点击元素
- 填写表单
- 截图
- 执行 JavaScript
- 页面导航
