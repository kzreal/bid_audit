"""
HiAgent API 测试脚本
测试 TaskCreator、TaskAuditor、SummaryAgent 三个接口，并记录输入输出到日志
"""

import json
import os
import sys
from datetime import datetime

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hiagent_client import TaskCreator, TaskAuditor, SummaryAgent

# 日志文件路径
LOG_FILE = "hiagent_test_log.txt"

def log_separator():
    """记录分隔线"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n{'=' * 80}\n")
        f.write(f"时间: {timestamp}\n")
        f.write(f"{'=' * 80}\n\n")

def log_request(title, api_name, input_data):
    """记录请求"""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"【{title} - {api_name}】\n")
        f.write(f"请求时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"请求数据:\n")
        f.write(json.dumps(input_data, ensure_ascii=False, indent=2))
        f.write("\n\n")

def log_response(output, raw_output=None):
    """记录响应"""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"响应时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"响应数据:\n")
        if raw_output:
            f.write("原始输出 (raw_output):\n")
            f.write(raw_output)
            f.write("\n\n")
        f.write("解析后输出:\n")
        f.write(json.dumps(output, ensure_ascii=False, indent=2))
        f.write("\n")

def log_error(error_msg):
    """记录错误"""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"错误: {error_msg}\n")
        f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n")

def clear_log():
    """清空日志文件"""
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# HiAgent API 测试日志\n")
        f.write(f"# 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# " + "=" * 70 + "\n\n")

def get_config():
    """从 .env 读取配置"""
    api_url = None
    task_creator_api_key = None
    task_auditor_api_key = None
    summary_api_key = None
    user_id = 'user001'

    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('VITE_API_BASE_URL='):
                    api_url = line.split('=', 1)[1]
                elif line.startswith('VITE_TASK_CREATOR_API_KEY='):
                    task_creator_api_key = line.split('=', 1)[1]
                elif line.startswith('VITE_TASK_AUDITOR_API_KEY='):
                    task_auditor_api_key = line.split('=', 1)[1]
                elif line.startswith('VITE_SUMMARY_API_KEY='):
                    summary_api_key = line.split('=', 1)[1]
                elif line.startswith('VITE_HIAGENT_USER_ID='):
                    user_id = line.split('=', 1)[1]
    except:
        pass

    # 如果本地文件没有设置，尝试从环境变量读取
    if not api_url:
        api_url = os.getenv('VITE_API_BASE_URL')
    if not task_creator_api_key:
        task_creator_api_key = os.getenv('VITE_TASK_CREATOR_API_KEY', 'd6ntpsf4piphvinbnmh0')
    if not task_auditor_api_key:
        task_auditor_api_key = os.getenv('VITE_TASK_AUDITOR_API_KEY', 'd6oo7pn4piphvinbrb6g')
    if not summary_api_key:
        summary_api_key = os.getenv('VITE_SUMMARY_API_KEY', 'd6oo7pn4piphvinbrb7g')
    if user_id == 'user001':
        user_id = os.getenv('VITE_HIAGENT_USER_ID', '250701283')

    # 如果都失败，使用默认值
    if not api_url:
        api_url = 'https://prd-ai-studio.chint.com/api/proxy/api/v1'

    return api_url, task_creator_api_key, task_auditor_api_key, summary_api_key, user_id

def test_task_creator():
    """测试 TaskCreator"""
    print("\n" + "=" * 60)
    print("测试 TaskCreator（任务创建器）")
    print("=" * 60)

    api_url, task_creator_api_key, _, _, user_id = get_config()
    creator = TaskCreator(api_url, task_creator_api_key, user_id)

    # 测试输入：招标要求
    requirement = """项目名称：某市公共安全视频监控建设项目
招标编号：ZJ-2024-001
招标内容：
1. 投标单位必须具备一级安防工程资质证书
2. 项目编号必须为 ad1231313
3. 投标报价不超过 500 万元
4. 项目交付周期不超过 90 天
"""

    input_data = {
        "extraction": requirement,
        "type": 1
    }

    log_request("测试1", "TaskCreator", input_data)

    result = creator.sync_run_workflow(input_data)

    if result:
        raw_output = result.get('output', result.get('content', ''))
        parsed = TaskCreator.parse_tasks(raw_output)

        log_response(parsed, raw_output)

        print(f"✓ 任务创建成功")
        print(f"  生成任务数量: {len(parsed)}")
        for i, task in enumerate(parsed[:3], 1):
            print(f"  [{i}] {task['content'][:50]}...")
    else:
        log_error("TaskCreator 调用失败")
        print("✗ 任务创建失败")

def test_task_auditor():
    """测试 TaskAuditor"""
    print("\n" + "=" * 60)
    print("测试 TaskAuditor（任务审核器）")
    print("=" * 60)

    api_url, _, task_auditor_api_key, _, user_id = get_config()
    auditor = TaskAuditor(api_url, task_auditor_api_key, user_id)

    # 测试输入
    task = "请核实投标文件中项目编号是否为 ad1231313"
    context = """# 第3章 项目概况

## 3.1 项目编号

本项目编号为 **ad1231313**，符合招标文件要求。

## 3.2 项目范围

本项目涵盖全市公共安全视频监控系统的设计与建设...
"""

    input_data = {
        "task": task,
        "context": context
    }

    log_request("测试2", "TaskAuditor", input_data)

    result_text = auditor.audit_task(task, context, use_sync=True)

    if result_text:
        parsed = TaskAuditor.parse_audit_result(result_text)

        log_response(parsed, result_text)

        print(f"✓ 任务审核成功")
        print(f"  建议: {parsed.get('suggestion', 'N/A')[:50]}...")
        print(f"  证据: {parsed.get('evidence', 'N/A')}")
    else:
        log_error("TaskAuditor 调用失败")
        print("✗ 任务审核失败")

def test_summary_agent():
    """测试 SummaryAgent"""
    print("\n" + "=" * 60)
    print("测试 SummaryAgent（总结 Agent）")
    print("=" * 60)

    api_url, _, _, summary_api_key, user_id = get_config()
    summary = SummaryAgent(api_url, summary_api_key, user_id)

    # 测试输入
    task = "请核实投标文件中投标人是否为生产制造商"
    reviews = [
        {
            "chunk_id": "chapter_3",
            "suggestion": "投标文件在第3章明确声明为制造商，并提供了生产资质证明。",
            "evidence": "276, 684-713"
        },
        {
            "chunk_id": "chapter_5",
            "suggestion": "本切片与当前审核任务无关。",
            "evidence": None
        },
        {
            "chunk_id": "chapter_7",
            "suggestion": "技术方案中详细说明了生产能力和设备来源。",
            "evidence": "892-945"
        }
    ]

    input_data = {
        "task": task,
        "reviews": reviews
    }

    log_request("测试3", "SummaryAgent", input_data)

    result_text = summary.generate_conclusion(task, reviews, use_sync=True)

    if result_text:
        parsed = summary.parse_conclusion(result_text)

        log_response(parsed, result_text)

        print(f"✓ 结论生成成功")
        print(f"  结论: {parsed.get('conclusion', 'N/A')}")
        print(f"  原因: {parsed.get('reason', 'N/A')[:80]}...")
        print(f"  证据: {parsed.get('evidence', 'N/A')}")
    else:
        log_error("SummaryAgent 调用失败")
        print("✗ 结论生成失败")

def main():
    """主函数"""
    print("HiAgent API 测试脚本")
    print("=" * 60)
    print(f"日志文件: {LOG_FILE}")
    print("=" * 60)

    # 清空并初始化日志
    clear_log()

    try:
        # 测试 TaskCreator
        test_task_creator()

        log_separator()

        # 测试 TaskAuditor
        test_task_auditor()

        log_separator()

        # 测试 SummaryAgent
        test_summary_agent()

        log_separator()

        print("\n" + "=" * 60)
        print("所有测试完成！")
        print(f"日志已保存到: {LOG_FILE}")
        print("=" * 60 + "\n")

    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
