#!/usr/bin/env python3
"""
测试 HiAgent API 调用
"""

import sys
import json
sys.path.append('.')

from hiagent_client import TaskCreator, TaskAuditor

def test_hiagent():
    print("=== 测试 HiAgent API ===")

    # 测试配置
    api_url = 'https://prd-ai-studio.chint.com/api/proxy/api/v1'
    api_key = 'd6ntpsf4piphvinbnmh0'
    user_id = '250701283'

    print(f"API_URL: {api_url}")
    print(f"API_KEY: {api_key}")
    print(f"USER_ID: {user_id}")
    print()

    # 测试任务创建
    task_creator = TaskCreator(api_url, api_key, user_id)
    requirement = "请审核投标文件的资质和技术方案"

    print(f"需求文本: {requirement}")
    print()

    try:
        print("创建任务中...")
        tasks_text = task_creator.create_tasks(requirement, use_sync=True)

        if tasks_text:
            print("✅ 任务创建成功!")
            print(f"返回结果: {tasks_text}")
            print()

            # 解析任务
            tasks = TaskCreator.parse_tasks(tasks_text)
            print("解析后的任务:")
            for task in tasks:
                print(f"  任务 {task['id']}: {task['content']}")
                if task['subtasks']:
                    for subtask in task['subtasks']:
                        print(f"    - {subtask['id']}: {subtask['content']}")

            return True
        else:
            print("❌ 任务创建失败!")
            return False

    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_hiagent()

    if success:
        print("\n" + "="*50)
        print("✅ 测试成功！可以开始测试前端了。")
    else:
        print("\n" + "="*50)
        print("❌ 测试失败，请检查配置。")