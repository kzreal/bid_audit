"""测试 SummaryAgent 调用"""
import json
from hiagent_client import SummaryAgent

# 读取配置
import os

summary_api_key = None
try:
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('VITE_SUMMARY_API_KEY='):
                summary_api_key = line.split('=', 1)[1]
                break
except:
    pass

if not summary_api_key:
    print("ERROR: VITE_SUMMARY_API_KEY not found in .env")
    exit(1)

api_url = None
try:
    with open('.env', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('VITE_API_BASE_URL='):
                api_url = line.split('=', 1)[1]
                break
except:
    pass

if not api_url:
    print("ERROR: VITE_API_BASE_URL not found in .env")
    exit(1)

user_id = '250701283'

print(f"配置:")
print(f"  API URL: {api_url}")
print(f"  Summary API Key: {summary_api_key}")
print(f"  User ID: {user_id}")
print()

# 初始化 SummaryAgent
summary = SummaryAgent(api_url, summary_api_key, user_id)

# 测试数据
task = "请核实投标文件中投标人是否为生产制造商"
reviews = [
    {"chunk_id": "chapter_3", "suggestion": "投标文件在第3章明确声明为制造商，并提供了生产资质证明。", "evidence": "276, 684-713"},
    {"chunk_id": "chapter_5", "suggestion": "本切片与当前审核任务无关。", "evidence": None},
    {"chunk_id": "chapter_7", "suggestion": "技术方案中详细说明了生产能力和设备来源。", "evidence": "892-945"}
]

print("测试输入:")
print(f"  task: {task}")
print(f"  reviews: {json.dumps(reviews, ensure_ascii=False)}")
print()

print("开始调用 SummaryAgent.generate_conclusion()...")
result_text = summary.generate_conclusion(task, reviews, use_sync=True)

print()
print("原始返回:")
print(result_text)
print()

print("解析返回:")
parsed = summary.parse_conclusion(result_text)
print(json.dumps(parsed, ensure_ascii=False, indent=2))
print()

if parsed.get('conclusion'):
    print(f"结论: {parsed.get('conclusion')}")
if parsed.get('reason'):
    print(f"原因: {parsed.get('reason')[:80] if parsed.get('reason') else 'N/A'}")
if parsed.get('evidence'):
    print(f"证据: {parsed.get('evidence')}")
