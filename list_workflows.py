#!/usr/bin/env python3
"""
列出可用的 HiAgent 应用和工作流
"""

import json
import os
import sys

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
from hiagent_client import HiAgentClient

def list_apps():
    """列出 HiAgent 中的应用"""
    print("=== HiAgent 应用列表 ===")

    # 使用配置文件中的设置
    from config import Config
    api_url = Config.API_URL
    api_key = Config.API_KEY
    user_id = Config.USER_ID

    # 如果配置文件中没有设置，使用默认值
    if api_url == "http://your-server:port/api/proxy/api/v1":
        api_url = "https://prd-ai-studio.chint.com/api/proxy/api/v1"
        api_key = "d6ntpsf4piphvinbnmh0"
        user_id = "250701283"

    client = HiAgentClient(api_url, api_key, user_id)

    print(f"API URL: {api_url}")
    print(f"User ID: {user_id}")
    print()

    # 列出应用（需要根据实际 API 调整）
    try:
        # 尝试调用一些常见的接口来获取应用信息
        print("正在获取应用信息...")

        # 尝试获取应用配置
        url = f"{api_url}/get_app_config_preview"
        headers = {
            'Apikey': api_key,
            'Content-Type': 'application/json'
        }
        data = {"UserID": user_id}

        response = requests.post(url, headers=headers, json=data)
        print(f"get_app_config_preview 状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("应用配置:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"获取应用配置失败: {response.text}")

    except Exception as e:
        print(f"错误: {e}")
        print()
        print("可能需要：")
        print("1. 确认 API URL 是否正确")
        print("2. 确认 API Key 是否有效")
        print("3. 确认应用是否已发布并启用 API")

if __name__ == "__main__":
    list_apps()