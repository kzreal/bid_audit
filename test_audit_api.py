#!/usr/bin/env python3
"""
测试审核 API 功能
"""

import json
import os
import sys

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hiagent_client import TaskAuditor
from config import Config

def test_audit_api():
    """测试审核 API"""
    print("=== 测试审核 API ===")

    # 使用配置文件中的设置
    api_url = Config.API_URL
    api_key = Config.API_KEY
    user_id = Config.USER_ID

    # 如果配置文件中没有设置，使用默认值
    if api_url == "http://your-server:port/api/proxy/api/v1":
        api_url = "https://prd-ai-studio.chint.com/api/proxy/api/v1"
        api_key = "d6ntpsf4piphvinbnmh0"
        user_id = "250701283"
        print("⚠️ 使用默认配置（来自代码硬编码）")

    print(f"API URL: {api_url}")
    print(f"API Key: {api_key}")
    print(f"User ID: {user_id}")

    # 创建审核器
    auditor = TaskAuditor(api_url, api_key, user_id)

    # 测试数据
    task = "评估投标文件中的技术方案是否完整"
    context = """
    投标文件内容：

    1. 技术方案概述
    我们公司采用最新的云计算架构，包括：
    - 前端：Vue.js 3.0 + TypeScript
    - 后端：Spring Boot + MySQL
    - 部署：Docker + Kubernetes

    2. 技术特点
    - 高可用性：99.9%可用性保证
    - 安全性：多层安全防护
    - 扩展性：支持水平扩展

    3. 实施计划
    - 第一阶段：需求分析和系统设计（2周）
    - 第二阶段：开发和单元测试（6周）
    - 第三阶段：集成测试和部署（2周）
    """

    print("\n--- 测试审核 ---")
    print(f"任务: {task}")
    print(f"上下文长度: {len(context)} 字符")

    # 调用审核 API
    result = auditor.audit_task(task, context, use_sync=True)

    if result:
        print(f"\n✅ 审核成功！")
        print(f"结果: {result}")

        # 尝试解析结果
        parsed = auditor.parse_audit_result(result)
        print(f"\n解析后的结果:")
        print(f"结论: {parsed['conclusion']}")
        print(f"原因: {parsed['reason']}")
        print(f"来源: {parsed['source']}")
    else:
        print("\n❌ 审核失败！")
        print("可能的原因：")
        print("1. 工作流名称不正确")
        print("2. 工作流不存在")
        print("3. 输入参数格式错误")
        print("4. API 权限问题")

if __name__ == "__main__":
    test_audit_api()