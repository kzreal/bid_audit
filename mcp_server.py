"""
MCP 服务器 - 将前端页面通过 URI 模板暴露给 Claude 访问
使用方式：https://spec.modelcontextprotocol.io/specification/resources

安装依赖: pip install mcp
配置方式: 在 Claude Desktop 中添加 MCP 服务器配置
"""

from mcp.server import Server
from mcp.types import Resource, TextContent
import asyncio


async def main():
    """主函数"""
    server = Server("bid-review-frontend")

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """列出 URI 资源 - 将前端页面 URL 暴露给 Claude"""
        return [
            Resource(
                uri="http://localhost:5173",
                name="前端页面",
                description="投标文件审核系统前端页面 - 可通过浏览器直接访问",
                mimeType="text/html"
            ),
            Resource(
                uri="http://localhost:8888/health",
                name="后端健康检查",
                description="后端服务健康检查接口",
                mimeType="application/json"
            ),
            Resource(
                uri="http://localhost:8888/hiagent/status",
                name="后端API状态",
                description="后端 API 服务状态",
                mimeType="application/json"
            ),
        ]

    @server.list_tools()
    async def list_tools() -> list:
        """列出可用工具 - 前端页面相关操作指南"""
        return []

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """调用工具 - 返回操作指南"""
        if name == "get_page_info":
            return [TextContent(
                type="text",
                text="""
📱 前端页面访问指南
═══════════════════════════════

🌐 页面URL:
   http://localhost:5173

🔧 后端API地址:
   http://localhost:8888

───────────────────────────────────────────────

📋 推荐的页面元素选择器:

1. 开始分析按钮:
   button:has-text('开始分析')

2. 类型选择器:
   select[aria-label*='类型']

3. 招标信息输入框:
   textarea[name='requirement']

4. 任务列表:
   [role='list'] > div

5. 审核结果区域:
   [role='review'] > div

───────────────────────────────────────────────

🎯 完整操作流程示例:

1. 访问 http://localhost:5173
2. 等待页面加载完成
3. 使用 Chrome DevTools (F12) 查看元素
4. 在 Console 中执行交互代码
5. 查看网络请求 (Network 标签)
6. 检查接口返回数据

───────────────────────────────────────────────

📝 Chrome DevTools 常用操作:

// 获取元素
const btn = document.querySelector('button:has-text("开始分析")');
const input = document.querySelector('textarea[name="requirement"]');

// 点击按钮
btn.click();

// 输入文本
input.value = '招标文件内容';
input.dispatchEvent(new Event('input', { bubbles: true }));

// 获取文本内容
const listItems = document.querySelectorAll('[role="list"] > div');
listItems.forEach(item => console.log(item.textContent));

───────────────────────────────────────────────

💡 提示:
- MCP 协议主要通过 URI 资源暴露页面访问
- 复杂的浏览器交互建议使用 Chrome DevTools 直接操作
- 我可以指导你在 DevTools Console 中执行操作
- 使用 Network 标签可以监控 API 请求和响应
"""
            )]

        return [TextContent(
            type="text",
            text=f"未知工具: {name}\n\n使用 'get_page_info' 工具查看页面访问指南"
        )]

    # 启动服务器
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
