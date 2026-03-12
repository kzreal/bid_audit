"""
测试审核工作流返回格式
"""
import requests
import json

# 测试审核接口
url = 'http://localhost:8888/hiagent/review-task'

test_data = {
    'task': '核实投标文件中招标人名称是否为"正泰集团"',
    'context': '本投标文件由正泰集团提交，公司成立于1984年，总部位于浙江省杭州市...'
}

print('发送审核请求...')
print(f'URL: {url}')
print(f'Task: {test_data["task"]}')
print(f'Context: {test_data["context"][:50]}...\n')

try:
    response = requests.post(url, json=test_data, timeout=60)
    print(f'HTTP Status: {response.status_code}\n')
    result = response.json()

    print('=== API 返回结果 ===')
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 检查 raw_text 中的格式
    if 'raw_text' in result:
        print(f'\n=== raw_text (HiAgent 原始返回) ===')
        print(result['raw_text'])

        # 尝试解析 raw_text
        print(f'\n=== 解析 raw_text ===')
        try:
            parsed = json.loads(result['raw_text'])
            print(json.dumps(parsed, ensure_ascii=False, indent=2))
        except:
            print('无法解析为 JSON，显示原始内容')

    # 检查期望格式
    print(f'\n=== 格式检查 ===')
    if 'data' in result and 'results' in result['data']:
        results = result['data']['results']
        print(f'results 数组长度: {len(results)}')
        if len(results) >= 3:
            print(f'conclusion: {results[0].get("conclusion", "未找到")}')
            print(f'reason: {results[1].get("reason", "未找到")}')
            print(f'evidence: {results[2].get("evidence", "未找到")}')

            # 检查 conclusion 是否是期望格式
            conclusion = results[0].get('conclusion', '')
            if conclusion in ['通过', '不通过', '待确认']:
                print(f'\n✓ 结论格式正确: {conclusion}')
            else:
                print(f'\n✗ 结论格式可能不正确，实际值: {conclusion[:100] if len(conclusion) > 100 else conclusion}')

except requests.exceptions.ConnectionError:
    print('❌ 连接失败：后端服务器未运行，请先启动: python3 backend_server.py')
except Exception as e:
    print(f'请求失败: {e}')
    import traceback
    traceback.print_exc()
