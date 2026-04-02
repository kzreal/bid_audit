"""
HiAgent API 客户端
参考文档: hiagent_api.md
"""

import json
import re
import time
from typing import Optional, Dict, Any, List

import requests


class HiAgentClient:
    """HiAgent API 客户端基类"""

    def __init__(self, api_url: str, api_key: str, user_id: str = "user001"):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.user_id = user_id
        self.headers = {
            'Apikey': api_key,
            'Content-Type': 'application/json'
        }

    def _make_request(self, url: str, data: dict, max_retries: int = 3) -> Optional[dict]:
        print(f"\n=== 发送请求 ===")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, ensure_ascii=False)}")

        for i in range(max_retries):
            try:
                response = requests.post(url, headers=self.headers, data=json.dumps(data))
                print(f"HTTP Status: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    print(f"Response: {json.dumps(result, ensure_ascii=False)[:500]}...")
                    return result
                else:
                    error_text = response.text
                    print(f"HTTP Error {response.status_code}: {error_text}")

            except Exception as e:
                print(f"请求失败，重试 {i + 1}/{max_retries}: {e}")
                if i < max_retries - 1:
                    time.sleep(1)
        return None

    def sync_run_workflow(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """同步运行工作流，返回完整响应 dict"""
        url = f"{self.api_url}/sync_run_app_workflow"
        data = {
            "UserID": self.user_id,
            "InputData": json.dumps(input_data),
            "NoDebug": True
        }
        result = self._make_request(url, data)
        if result and result.get('status') == 'success':
            return result
        elif result:
            print(f"工作流运行失败: {result.get('message', '未知错误')}")
        return None


def _extract_output(result: Dict) -> Any:
    """从 HiAgent 响应中提取 output，处理可能的嵌套字符串"""
    output = result.get('output', [])

    # HiAgent 有时返回嵌套的 JSON 字符串，逐层解析
    if isinstance(output, str):
        try:
            output = json.loads(output)
        except (json.JSONDecodeError, ValueError):
            return output

    # 二层嵌套
    if isinstance(output, dict) and 'output' in output:
        inner = output['output']
        if isinstance(inner, str):
            try:
                output = json.loads(inner)
            except (json.JSONDecodeError, ValueError):
                pass
        elif isinstance(inner, (list, dict)):
            output = inner

    return output


class TaskCreator(HiAgentClient):
    """任务创建器"""

    @staticmethod
    def parse_tasks(result: Dict) -> List[Dict[str, Any]]:
        """
        从 HiAgent 响应 dict 中提取任务列表

        期望格式: {"output": [{"id": "1", "task": "..."}]}
        """
        output = _extract_output(result)
        tasks = []

        items = []
        if isinstance(output, list):
            items = output
        elif isinstance(output, dict):
            items = output.get('tasks', output.get('output', []))
            if isinstance(items, dict):
                items = []

        for item in items:
            if isinstance(item, dict):
                content = item.get('task', '')
                if content:
                    tasks.append({
                        'id': item.get('id', ''),
                        'content': content,
                        'subtasks': []
                    })

        # 兜底：正则解析纯文本
        if not tasks and isinstance(result.get('output'), str):
            task_pattern = re.compile(r'(\d+)[\.\、\s]+(.+)')
            for line in result['output'].split('\n'):
                match = task_pattern.search(line)
                if match:
                    tasks.append({
                        'id': match.group(1),
                        'content': match.group(2).strip(),
                        'subtasks': []
                    })

        return tasks


class TaskAuditor(HiAgentClient):
    """任务审核器"""

    @staticmethod
    def parse_audit_result(result: Dict) -> Dict[str, str]:
        """
        从 HiAgent 响应 dict 中提取审核结果

        期望格式: {"output": [{"suggestion": "...", "evidence": "..."}]}
        """
        output = _extract_output(result)
        parsed = {'suggestion': '', 'evidence': ''}

        if isinstance(output, list) and len(output) > 0:
            item = output[0]
            if isinstance(item, dict):
                parsed['suggestion'] = item.get('suggestion', '')
                parsed['evidence'] = str(item.get('evidence', ''))
        elif isinstance(output, dict):
            parsed['suggestion'] = output.get('suggestion', '')
            parsed['evidence'] = str(output.get('evidence', ''))

        return parsed


class SummaryAgent(HiAgentClient):
    """汇总审核结果并生成最终结论"""

    @staticmethod
    def parse_conclusion(result: Dict) -> Dict[str, Any]:
        """
        从 HiAgent 响应 dict 中提取结论

        期望格式: {"output": {"results": [{"conclusion": "通过/不通过", "reasons": [...]}]}}
        """
        output = _extract_output(result)
        parsed = {"conclusion": '', "suggestions": []}

        results_list = output.get('results', []) if isinstance(output, dict) else []

        if isinstance(results_list, list) and len(results_list) > 0:
            item = results_list[0]
            if isinstance(item, dict):
                parsed['conclusion'] = item.get('conclusion', '')
                reasons = item.get('reasons', [])
                if isinstance(reasons, list):
                    for r in reasons:
                        if isinstance(r, dict):
                            parsed['suggestions'].append({
                                "suggestion": r.get('suggestion', '') or r.get('reason', ''),
                                "evidence": str(r.get('evidence', '')) if r.get('evidence') and r.get('evidence') != "null" else ''
                            })

        return parsed
