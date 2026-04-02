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
                    if "workflow" in error_text.lower() and "not found" in error_text.lower():
                        print("❌ 工作流可能不存在或名称错误！")
                    elif "invalid input" in error_text.lower():
                        print("❌ 输入参数格式可能不正确！")

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

    def sync_run_review_workflow(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        同步运行审核工作流

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
                print(f"审核工作流运行失败: {result.get('message', '未知错误')}")
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
            原始响应文本
        """
        input_data = {
            "extraction": requirement,
            "type": 1  # 1 表示信息核对
        }

        if use_sync:
            print("使用同步方式创建任务...")
            result = self.sync_run_workflow(input_data)
            if result and isinstance(result, dict):
                # 返回完整的 JSON 字符串，供 parse_tasks 解析
                return json.dumps(result, ensure_ascii=False)
        else:
            # 异步调用 + 轮询
            print("使用异步方式创建任务...")
            run_id = self.async_run_workflow(input_data)
            if run_id:
                print(f"任务已提交，runId: {run_id}")
                result = self.query_workflow_process(run_id)
                if result:
                    # 获取 output 字段
                    output = result.get('output', '')
                    print(f"任务创建成功，输出长度: {len(output)}")
                    # 返回完整的 JSON 字符串，保持格式一致
                    return json.dumps(result, ensure_ascii=False)

        return None

    @staticmethod
    def parse_tasks(tasks_text: str) -> List[Dict[str, Any]]:
        """
        解析任务文本，提取每条任务

        HiAgent API 输出格式：
        {"output": [{"id": "1", "task": "..."}]}

        Args:
            tasks_text: HiAgent API 返回的原始响应文本

        Returns:
            任务列表，每个元素包含 id, content 和 subtasks
        """
        final_tasks = []
        try:
            # 解析外层 JSON
            outer_json = json.loads(tasks_text)
            print(f"DEBUG - tasks_text: {tasks_text[:500]}")
            # 获取 output 字段（列表或字符串）
            tasks_output = outer_json.get('output', [])

            # 如果 output 是字符串，尝试再次解析它（HiAgent 有时会嵌套 JSON 字符串）
            if isinstance(tasks_output, str):
                try:
                    tasks_list = json.loads(tasks_output)
                except:
                    tasks_list = []
            else:
                tasks_list = tasks_output

            print(f"DEBUG - tasks_list type: {type(tasks_list)}, content: {tasks_list}")

            if isinstance(tasks_list, list):
                for item in tasks_list:
                    if isinstance(item, dict):
                        task_id = item.get('id', '')
                        task_content = item.get('task', '')
                        if task_content:
                            final_tasks.append({
                                'id': task_id,
                                'content': task_content,
                                'subtasks': []
                            })
            elif isinstance(tasks_list, dict):
                # 检查是否有 'tasks' 键（HiAgent 返回格式：{"tasks": [{"id": "1", "task": "..."}]}）
                if 'tasks' in tasks_list:
                    tasks_inner = tasks_list.get('tasks', [])
                    for item in tasks_inner:
                        if isinstance(item, dict):
                            task_id = item.get('id', '')
                            task_content = item.get('task', '')
                            if task_content:
                                final_tasks.append({
                                    'id': task_id,
                                    'content': task_content,
                                    'subtasks': []
                                })
                elif 'output' in tasks_list:
                    # 兼容可能的双层 output
                    return TaskCreator.parse_tasks(json.dumps(tasks_list))

        except Exception as e:
            print(f"解析任务失败: {e}, 原始文本: {tasks_text[:200]}...")
            # 兜底：尝试正则解析旧格式
            task_pattern = re.compile(r'(\d+)[\.\、\s]+(.+)')
            for line in tasks_text.split('\n'):
                match = task_pattern.search(line)
                if match:
                    final_tasks.append({
                        'id': match.group(1),
                        'content': match.group(2).strip(),
                        'subtasks': []
                    })

        return final_tasks


class TaskAuditor(HiAgentClient):
    """任务审核器 - 调用第二个接口审核任务"""

    def audit_task(self, task: str, context: str, use_sync: bool = True) -> Optional[str]:
        """
        审核单个任务

        Args:
            task: 任务描述
            context: 上下文文本（文件内容）
            use_sync: 是否使用同步调用

        Returns:
            原始响应文本
        """
        input_data = {
            "task": task,
            "context": context
        }

        print(f"\n=== 审核任务 ===")
        print(f"任务: {str(task)[:50]}...")
        print(f"上下文长度: {len(context)} 字符")

        print("使用同步方式审核...")
        # 优先使用专门的审核工作流
        result = self.sync_run_review_workflow(input_data)
        if not result:
            # 如果审核工作流失败，尝试使用通用工作流
            print("审核工作流失败，尝试使用通用工作流...")
            result = self.sync_run_workflow(input_data)

        if result and isinstance(result, dict):
            # 返回完整的 JSON 字符串，供 parse_audit_result 解析
            return json.dumps(result, ensure_ascii=False)

        return None

    @staticmethod
    def parse_audit_result(result_text: str) -> Dict[str, str]:
        """
        解析单切片或多切片审核结果

        HiAgent API 输出格式：
        {"output": [{"suggestion": "...", "evidence": "..."}]}

        Args:
            result_text: HiAgent 返回的原始响应文本

        Returns:
            包含 suggestion, evidence 的字典
        """
        result = {
            'suggestion': '',
            'evidence': ''
        }

        try:
            # 解析外层 JSON
            outer_json = json.loads(result_text)
            # 获取 output 字段（列表或字符串）
            reviews_output = outer_json.get('output', [])

            # 如果 output 是字符串，尝试再次解析它
            if isinstance(reviews_output, str):
                try:
                    reviews_list = json.loads(reviews_output)
                except:
                    reviews_list = []
            else:
                reviews_list = reviews_output

            # 如果解析后是 dict 且包含 'output' 键（嵌套结构），提取内部列表
            if isinstance(reviews_list, dict) and 'output' in reviews_list:
                inner = reviews_list['output']
                if isinstance(inner, list):
                    reviews_list = inner
                elif isinstance(inner, str):
                    try:
                        reviews_list = json.loads(inner)
                    except:
                        reviews_list = []

            if isinstance(reviews_list, list) and len(reviews_list) > 0:
                # 对于单任务，通常只取第一个
                item = reviews_list[0]
                if isinstance(item, dict):
                    result['suggestion'] = item.get('suggestion', '')
                    result['evidence'] = str(item.get('evidence', ''))
            elif isinstance(reviews_list, dict):
                # 兼容直接的字典格式 {"suggestion": "...", "evidence": "..."}
                result['suggestion'] = reviews_list.get('suggestion', '')
                result['evidence'] = str(reviews_list.get('evidence', ''))

        except Exception as e:
            print(f"解析审核结果失败: {e}, 原始文本: {result_text[:200]}...")
            # 兜底：直接把整个文本作为建议
            result['suggestion'] = result_text

        return result


class SummaryAgent(HiAgentClient):
    """汇总审核结果并生成最终结论"""

    def generate_conclusion(self, task: str, reviews: List[Dict[str, Any]], use_sync: bool = True) -> Optional[str]:
        """
        汇总审核结果并生成最终结论

        Args:
            task: 任务描述
            reviews: 所有切片的审核结果
            use_sync: 是否使用同步调用

        Returns:
            原始响应文本
        """
        # 将 task 和 reviews 包装在 context 字段中（JSON 对象格式，不再是双重 JSON 字符串）
        input_data = {
            "context": {
                "task": task,
                "reviews": reviews
            }
        }

        print("使用同步方式生成结论...")
        result = self.sync_run_workflow(input_data)

        if result and isinstance(result, dict):
            # 返回完整的 JSON 字符串，因为外部 parse_conclusion 会解析它
            return json.dumps(result, ensure_ascii=False)

        return None

    @staticmethod
    def parse_conclusion(result_text: str) -> Dict[str, Any]:
        """
        解析总结结果

        HiAgent API 输出格式：
        {"results": [{"conclusion": "通过/不通过/待确认", "reasons": [{"suggestion": "...", "evidence": "..."}]}]}

        Args:
            result_text: HiAgent 返回的原始响应文本

        Returns:
            包含 conclusion, reasons 的字典
            reasons 是数组，每条包含 suggestion 和 evidence（不合并）
        """
        result = {
            "conclusion": '',
            "reason": []  # 不再是字符串，而是数组
        }

        try:
            # 解析外层 JSON
            outer_json = json.loads(result_text)

            # 获取 output 字段（HiAgent 返回格式：{"output": "{\"output\": \"{\\\"results\\\": [...]}\"}"}
            output_str = outer_json.get('output', '')

            # 如果 output 是字符串，尝试再次解析它
            if isinstance(output_str, str):
                try:
                    output_data = json.loads(output_str)
                except:
                    output_data = {}
            else:
                output_data = output_str

            # 如果 output_data 还有 output 键，需要再解析一层（三层嵌套）
            if 'output' in output_data:
                inner_output_str = output_data.get('output', '')
                if isinstance(inner_output_str, str):
                    try:
                        output_data = json.loads(inner_output_str)
                    except:
                        pass

            # 获取 results 字段
            results_list = output_data.get('results', [])

            if isinstance(results_list, list) and len(results_list) > 0:
                item = results_list[0]
                if isinstance(item, dict):
                    result['conclusion'] = item.get('conclusion', '')
                    reasons = item.get('reasons', [])

                    if isinstance(reasons, list) and len(reasons) > 0:
                        for r in reasons:
                            if isinstance(r, dict):
                                reason_item = {
                                    "suggestion": r.get('suggestion', '') or r.get('reason', ''),
                                    "evidence": str(r.get('evidence', '')) if r.get('evidence') and r.get('evidence') != "null" else ''
                                }
                                result['reason'].append(reason_item)

        except Exception as e:
            print(f"解析总结结果失败: {e}, 原始文本: {result_text[:200]}...")
            # 兜底
            result['reason'] = [{"suggestion": result_text, "evidence": ""}]

        return result
