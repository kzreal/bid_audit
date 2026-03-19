#!/usr/bin/env python3
"""
测试后端 API 接口
"""

import requests
import json

# 后端地址
BASE_URL = "http://localhost:8888"

def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def print_result(response, title="响应结果"):
    """格式化打印响应结果"""
    print(f"\n{title}:")
    print(f"  HTTP Status: {response.status_code}")
    try:
        data = response.json()
        print(f"  Data: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except:
        print(f"  Raw: {response.text[:200]}")

def test_health():
    """测试健康检查接口"""
    print_section("1. 测试健康检查接口 (GET /health)")
    response = requests.get(f"{BASE_URL}/health")
    print_result(response)

def test_hiagent_status():
    """测试 API 状态接口"""
    print_section("2. 测试 API 状态接口 (GET /hiagent/status)")
    response = requests.get(f"{BASE_URL}/hiagent/status")
    print_result(response)

def test_generate_tasks():
    """测试生成任务接口"""
    print_section("3. 测试生成任务接口 (POST /hiagent/generate-tasks)")

    test_cases = [
        {
            "name": "信息核对 (type=0)",
            "data": {
                "requirement": "项目编号：ad1231313，项目名称：2025年集团统一采购项目",
                "type": 0
            }
        },
        {
            "name": "招标要求 (type=1)",
            "data": {
                "requirement": "投标人必须是制造商，注册资本不低于1000万元",
                "type": 1
            }
        },
        {
            "name": "通用要求 (type=None)",
            "data": {
                "requirement": "请检查投标文件的完整性和规范性"
            }
        }
    ]

    for case in test_cases:
        print(f"\n--- 测试用例: {case['name']} ---")
        response = requests.post(
            f"{BASE_URL}/hiagent/generate-tasks",
            json=case["data"],
            headers={"Content-Type": "application/json"}
        )
        print_result(response)

def test_review_task():
    """测试审核单个任务接口"""
    print_section("4. 测试审核单个任务接口 (POST /hiagent/review-task)")

    data = {
        "task": "请核实投标文件中项目编号是否为 ad1231313",
        "context": "# 投标文件\n\n## 第一章\n项目编号：ad1231313\n\n## 第二章\n投标人信息..."
    }

    response = requests.post(
        f"{BASE_URL}/hiagent/review-task",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print_result(response)

def test_review_task_slices():
    """测试多切片审核接口"""
    print_section("5. 测试多切片审核接口 (POST /hiagent/review-task-slices)")

    data = {
        "task": "请核实投标文件中项目编号是否为 ad1231313",
        "slices": [
            "# 切片1\n\n项目编号：ad1231313\n项目名称：2025年集团统一采购项目",
            "# 切片2\n\n投标人：某某有限公司\n注册资本：5000万元",
            "# 切片3\n\n本投标文件真实有效，如有虚假愿承担法律责任。"
        ]
    }

    response = requests.post(
        f"{BASE_URL}/hiagent/review-task-slices",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print_result(response)

def test_generate_conclusion():
    """测试生成结论接口"""
    print_section("6. 测试生成结论接口 (POST /hiagent/generate-conclusion)")

    data = {
        "task": "请核实投标文件中项目编号是否为 ad1231313",
        "reviews": [
            {
                "suggestion": "切片1中项目编号为 ad1231313，与要求一致",
                "evidence": "1"
            },
            {
                "suggestion": "切片2中未提及项目编号",
                "evidence": None
            },
            {
                "suggestion": "切片3为声明部分，不涉及项目编号",
                "evidence": None
            }
        ]
    }

    response = requests.post(
        f"{BASE_URL}/hiagent/generate-conclusion",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    print_result(response)

def test_error_handling():
    """测试错误处理"""
    print_section("7. 测试错误处理")

    test_cases = [
        {
            "name": "生成任务 - 缺少 requirement",
            "endpoint": "/hiagent/generate-tasks",
            "data": {}
        },
        {
            "name": "审核任务 - 缺少 task",
            "endpoint": "/hiagent/review-task",
            "data": {"context": "测试内容"}
        },
        {
            "name": "审核任务 - 缺少 context",
            "endpoint": "/hiagent/review-task",
            "data": {"task": "测试任务"}
        },
        {
            "name": "多切片审核 - 超过30个切片",
            "endpoint": "/hiagent/review-task-slices",
            "data": {
                "task": "测试任务",
                "slices": ["内容"] * 31
            }
        }
    ]

    for case in test_cases:
        print(f"\n--- 测试: {case['name']} ---")
        response = requests.post(
            f"{BASE_URL}{case['endpoint']}",
            json=case["data"],
            headers={"Content-Type": "application/json"}
        )
        print_result(response)

def main():
    """运行所有测试"""
    print(f"\n{'#'*60}")
    print(f"#  投标文件审核系统 - API 接口测试")
    print(f"#  后端地址: {BASE_URL}")
    print(f"{'#'*60}")

    # 测试所有接口
    test_health()
    test_hiagent_status()
    test_generate_tasks()
    test_review_task()
    test_review_task_slices()
    test_generate_conclusion()
    test_error_handling()

    print(f"\n{'#'*60}")
    print(f"#  测试完成")
    print(f"{'#'*60}\n")

if __name__ == "__main__":
    main()
