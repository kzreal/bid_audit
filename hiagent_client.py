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
        """
        初始化客户端

        Args:
            api_url: API 基础地址，如 http://33.234.30.131:32300/api/proxy/api/v1
            api_key: API 密钥
            user_id: 用户ID，1-20字符，仅支持字母和数字
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.user_id = user_id
        self.headers = {
            'Apikey': api_key,
            'Content-Type': 'application/json'
        }

    def _make_request(self, url: str, data: dict, max_retries: int = 3) -> Optional[dict]:
        """
        发送 HTTP POST 请求并处理重试逻辑

        Args:
            url: 请求的 URL
            data: 请求体数据
            max_retries: 最大重试次数

        Returns:
            成功返回 JSON 响应，失败返回 None
        """
        for i in range(max_retries):
            try:
                response = requests.post(url, headers=self.headers, data=json.dumps(data))
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"请求失败，重试 {i + 1}/{max_retries}: {e}")
                if i < max_retries - 1:
                    time.sleep(1)
        return None

    def sync_run_workflow(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        同步运行工作流

        Args:
            input_data: 输入数据字典，会被转为 JSON 字符串

        Returns:
            工作流运行结果，包含 output 字段
        """
        url = f"{self.api_url}/sync_run_app_workflow"
        data = {
            "UserID": self.user_id,
            "InputData": json.dumps(input_data),
            "NoDebug": True
        }

        result = self._make_request(url, data)
        if result:
            if result.get('status') == 'success':
                return result
            else:
                print(f"工作流运行失败: {result.get('message', '未知错误')}")
        return None

    def async_run_workflow(self, input_data: Dict[str, Any]) -> Optional[str]:
        """
        异步运行工作流

        Args:
            input_data: 输入数据字典

        Returns:
            runId，用于后续查询运行结果
        """
        url = f"{self.api_url}/run_app_workflow"
        data = {
            "UserID": self.user_id,
            "InputData": json.dumps(input_data),
            "NoDebug": True
        }

        result = self._make_request(url, data)
        if result and 'runId' in result:
            return result['runId']
        return None

    def query_workflow_process(self, run_id: str, max_retries: int = 10) -> Optional[Dict[str, Any]]:
        """
        查询异步工作流运行进度

        Args:
            run_id: 工作流运行ID
            max_retries: 最大轮询次数

        Returns:
            工作流运行结果
        """
        url = f"{self.api_url}/query_run_app_process"
        data = {
            "UserID": self.user_id,
            "RunID": run_id
        }

        retry_count = 0
        while retry_count < max_retries:
            result = self._make_request(url, data)
            if result:
                if result.get('status') == 'success':
                    print(f"工作流运行成功，耗时 {result.get('costMs', 0)}ms")
                    return result
                else:
                    print(f"工作流状态: {result.get('status')}")
            else:
                print(f"查询结果为空")
            retry_count += 1
            if retry_count < max_retries:
                # 指数退避等待
                wait_time = min(2 ** retry_count, 30)
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)

        print("达到最大重试次数")
        return None


class TaskCreator(HiAgentClient):
    """任务创建器 - 调用第一个接口创建任务"""

    def create_tasks(self, requirement: str, use_sync: bool = True) -> Optional[str]:
        """
        创建审核任务

        Args:
            requirement: 需求文本
            use_sync: 是否使用同步调用，True为同步，False为异步

        Returns:
            tasks 文本，格式为 1、2、3 编号
        """
        input_data = {
            "extraction": requirement,
            "type": 1  # 1 表示信息核对
        }

        if use_sync:
            # 同步调用
            print("使用同步方式创建任务...")
            result = self.sync_run_workflow(input_data)
            if result:
                # 检查返回的是字符串还是对象
                if isinstance(result, dict):
                    # 如果是对象，尝试从 content 或 output 字段获取
                    output = result.get('content', result.get('output', ''))
                else:
                    # 如果是字符串，直接使用
                    output = str(result)

                print(f"任务创建成功，输出:\n{output}")
                return output
        else:
            # 异步调用 + 轮询
            print("使用异步方式创建任务...")
            run_id = self.async_run_workflow(input_data)
            if run_id:
                print(f"任务已提交，runId: {run_id}")
                result = self.query_workflow_process(run_id)
                if result:
                    output = result.get('output', '')
                    print(f"任务创建成功，输出:\n{output}")
                    return output

        return None

    @staticmethod
    def parse_tasks(tasks_text: str) -> List[Dict[str, Any]]:
        """
        解析任务文本，提取每条任务

        Args:
            tasks_text: HiAgent 返回的任务文本，格式为 1、2、3 编号

        Returns:
            任务列表，每个元素包含 id, content 和 subtasks
        """
        tasks = []
        lines = tasks_text.split('\n')

        current_task = None
        task_pattern = re.compile(r'^(\d+)[.、]\s*(.*)$')
        continue_pattern = re.compile(r'^\s+(.*)$')

        for line in lines:
            # 匹配任务编号行，如 "1、审核项目资质"
            match = task_pattern.match(line)
            if match:
                task_id = match.group(1)
                content = match.group(2).strip()
                if content:
                    current_task = {
                        'id': int(task_id),
                        'content': content,
                        'subtasks': []
                    }
                    tasks.append(current_task)
                continue

            # 匹配续行（缩进的内容）
            if current_task:
                continue_match = continue_pattern.match(line)
                if continue_match:
                    sub_content = continue_match.group(1).strip()
                    if sub_content:
                        # 如果是子任务
                        sub_match = re.match(r'^(\d+)[.、](.*)$', sub_content)
                        if sub_match:
                            sub_id = sub_match.group(1)
                            sub_content = sub_match.group(2).strip()
                            current_task['subtasks'].append({
                                'id': f"{current_task['id']}.{sub_id}",
                                'content': sub_content
                            })
                        else:
                            # 续行，追加到主任务
                            if current_task['content']:
                                current_task['content'] += '\n' + sub_content
                            else:
                                current_task['content'] = sub_content

        # 如果没有匹配到任何编号任务，但文本不为空，则将整个文本作为单个任务
        if len(tasks) == 0 and tasks_text.strip():
            tasks = [{
                'id': 1,
                'content': tasks_text.strip(),
                'subtasks': []
            }]

        return tasks


class TaskAuditor(HiAgentClient):
    """任务审核器 - 调用第二个接口审核任务"""

    def audit_task(self, task: str, context: str, use_sync: bool = True) -> Optional[str]:
        """
        审核单个任务

        Args:
            task: 任务描述
            context: 上下文文本
            use_sync: 是否使用同步调用

        Returns:
            审核结果文本，格式为 #结论#原因#来源
        """
        input_data = {
            "task": task,
            "context": context
        }

        if use_sync:
            # 同步调用
            print(f"使用同步方式审核任务: {str(task)[:50]}...")
            result = self.sync_run_workflow(input_data)
            if result:
                # 检查返回的是字符串还是对象
                if isinstance(result, dict):
                    # 如果是对象，尝试从 content 或 output 字段获取
                    output = result.get('content', result.get('output', ''))
                else:
                    # 如果是字符串，直接使用
                    output = str(result)

                print(f"审核成功，输出:\n{output}")
                return output
        else:
            # 异步调用 + 轮询
            print(f"使用异步方式审核任务: {str(task)[:50]}...")
            run_id = self.async_run_workflow(input_data)
            if run_id:
                print(f"审核任务已提交，runId: {run_id}")
                result = self.query_workflow_process(run_id)
                if result:
                    output = result.get('output', '')
                    print(f"审核成功，输出:\n{output}")
                    return output

        return None

    @staticmethod
    def parse_audit_result(result_text: str) -> Dict[str, str]:
        """
        解析审核结果

        Args:
            result_text: HiAgent 返回的审核结果文本，格式为 #结论#原因#来源

        Returns:
            包含 conclusion, reason, source 的字典
        """
        parts = result_text.split('#')

        result = {
            'conclusion': '',
            'reason': '',
            'source': ''
        }

        # 去掉空的部分
        parts = [p.strip() for p in parts if p.strip()]

        if len(parts) >= 1:
            result['conclusion'] = parts[0]
        if len(parts) >= 2:
            result['reason'] = parts[1]
        if len(parts) >= 3:
            result['source'] = parts[2]

        return result
