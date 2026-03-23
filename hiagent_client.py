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

        HiAgent API 新输出格式：
        {"output": "{\"tasks\": [\"任务1\", \"任务2\"]}"}

        支持多种格式：
        1. 新格式（推荐）: {"output": "{\"tasks\": [\"任务1\", \"任务2\"]}"}
        2. 嵌套JSON格式: {"content": "{\"tasks\": [...]}"}
        3. 原有文本格式: "1. 任务1\n2. 任务2"

        Args:
            tasks_text: HiAgent API 返回的 output 字段内容

        Returns:
            任务列表，每个元素包含 id, content 和 subtasks
        """
        # 第一步：尝试解析为 JSON，获取 inner output 字段
        content_to_parse = tasks_text

        try:
            # 新格式：先解析外层 {"output": "..."}
            outer_json = json.loads(tasks_text)
            if 'output' in outer_json:
                output_str = outer_json['output']
                if output_str:
                    # output 是 JSON 字符串，再解析一次
                    try:
                        inner_json = json.loads(output_str)
                        # 找到了内层 JSON，继续处理
                        content_to_parse = inner_json
                    except:
                        # output 不是 JSON 字符串，直接使用
                        content_to_parse = output_str
            elif 'content' in outer_json:
                # 兼容旧格式 content 字段
                content_str = outer_json['content']
                if content_str:
                    # 如果 content 是 JSON 字符串，再解析一次
                    try:
                        inner_json = json.loads(content_str)
                        content_to_parse = inner_json
                    except:
                        content_to_parse = content_str
            else:
                # 没有 output 或 content 字段，直接使用原始数据
                content_to_parse = outer_json
        except:
            # 不是 JSON 格式，使用原始文本
            content_to_parse = tasks_text

        # 第二步：根据解析结果生成任务列表
        tasks = []

        # 处理字典类型的解析结果
        if isinstance(content_to_parse, dict):
            # 新格式: {"tasks": ["任务1", "任务2"]}
            if 'tasks' in content_to_parse and isinstance(content_to_parse['tasks'], list):
                tasks_list = content_to_parse['tasks']
                for idx, task_item in enumerate(tasks_list, start=1):
                    task_content = ''

                    # 尝试获取任务内容，支持多种类型
                    if isinstance(task_item, str):
                        task_content = task_item
                    elif isinstance(task_item, dict):
                        # 兼容对象格式: {"id": 1, "task": "..."} 或 {"task": "..."}
                        if 'task' in task_item:
                            task_content = task_item['task']
                        elif 'description' in task_item:
                            task_content = task_item['description']
                        elif 'content' in task_item:
                            task_content = task_item['content']
                        else:
                            # 如果没有标准键，取第一个值
                            if task_item:
                                first_value = next(iter(task_item.values()))
                                task_content = str(first_value)

                    if task_content and str(task_content).strip():
                        tasks.append({
                            'id': int(idx),
                            'content': str(task_content).strip(),
                            'subtasks': []
                        })

            # 兼容旧格式: {"task": "任务描述"}
            elif 'task' in content_to_parse:
                task_content = content_to_parse['task']
                if task_content and task_content.strip():
                    tasks.append({
                        'id': 1,
                        'content': task_content.strip(),
                        'subtasks': []
                    })

            # 兼容旧格式: {"tasks": "任务字符串"} (tasks是字符串)
            elif 'tasks' in content_to_parse and isinstance(content_to_parse['tasks'], str):
                task_content = content_to_parse['tasks']
                if task_content and task_content.strip():
                    tasks.append({
                        'id': 1,
                        'content': task_content.strip(),
                        'subtasks': []
                    })

            # 兼容其他格式，检查 content 字段
            elif 'content' in content_to_parse:
                content_value = content_to_parse['content']
                if content_value and str(content_value).strip():
                    tasks.append({
                        'id': 1,
                        'content': str(content_value).strip(),
                        'subtasks': []
                    })

        # 处理原有的文本格式（1. 任务1\n2. 任务2）
        elif isinstance(content_to_parse, str):
            lines = content_to_parse.split('\n')
            current_task = None
            task_pattern = re.compile(r'^(\d+)[.、]\s*(.*)$')
            continue_pattern = re.compile(r'^\s+(.*)$')

            for line in lines:
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

                if current_task:
                    continue_match = continue_pattern.match(line)
                    if continue_match:
                        sub_content = continue_match.group(1).strip()
                        if sub_content:
                            sub_match = re.match(r'^(\d+)[.、](.*)$', sub_content)
                            if sub_match:
                                sub_id = sub_match.group(1)
                                sub_content = sub_match.group(2).strip()
                                current_task['subtasks'].append({
                                    'id': f"{current_task['id']}.{sub_id}",
                                    'content': sub_content
                                })
                            else:
                                if current_task['content']:
                                    current_task['content'] += '\n' + sub_content
                                else:
                                    current_task['content'] = sub_content

            # 如果没有匹配到任何编号任务，但文本不为空
            if len(tasks) == 0 and content_to_parse.strip():
                tasks = [{
                    'id': 1,
                    'content': content_to_parse.strip(),
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
            context: 上下文文本（文件内容）
            use_sync: 是否使用同步调用

        Returns:
            审核结果文本，格式为 #结论#原因#来源
        """
        input_data = {
            "task": task,
            "context": context
        }

        print(f"\n=== 审核任务 ===")
        print(f"任务: {str(task)[:50]}...")
        print(f"上下文长度: {len(context)} 字符")

        if use_sync:
            # 同步调用
            print("使用同步方式审核...")
            result = self.sync_run_review_workflow(input_data)
            if not result:
                # 如果审核工作流失败，尝试使用普通工作流
                print("审核工作流失败，尝试使用普通工作流...")
                result = self.sync_run_workflow(input_data)

            if result:
                # 检查返回的是字符串还是对象
                if isinstance(result, dict):
                    # 如果是对象，尝试从 content 或 output 字段获取
                    output = result.get('content', result.get('output', ''))
                else:
                    # 如果是字符串，直接使用
                    output = str(result)

                print(f"审核结果:\n{output}")
                return output
        else:
            # 异步调用 + 轮询
            print("使用异步方式审核...")
            run_id = self.async_run_workflow(input_data)
            if run_id:
                print(f"审核任务已提交，runId: {run_id}")
                result = self.query_workflow_process(run_id)
                if result:
                    output = result.get('output', '')
                    print(f"审核结果:\n{output}")
                    return output

        print("审核失败")
        return None

    @staticmethod
    def parse_audit_result(result_text: str) -> Dict[str, str]:
        """
        解析审核结果

        HiAgent API 新输出格式：
        {"output": "{\"result\": {\"suggestion\": \"...\", \"evidence\": \"...\"}}"}

        Args:
            result_text: HiAgent 返回的 output 字段内容

        Returns:
            包含 suggestion, evidence 的字典
        """
        result = {
            'suggestion': '',
            'evidence': ''
        }

        # 尝试解析为 JSON
        try:
            result_json = json.loads(result_text)

            # 尝试从 content 或 output 字段解析
            content = result_json.get('content', result_json.get('output', ''))

            if not content:
                raise json.JSONDecodeError("No content found")

            # content 可能是一个 JSON 字符串，尝试解析
            try:
                inner_json = json.loads(content)

                # 处理 result 包装层格式: {"result": {"suggestion": "...", "evidence": "..."}}
                if isinstance(inner_json, dict) and 'result' in inner_json:
                    result_obj = inner_json['result']
                    if isinstance(result_obj, dict):
                        if 'suggestion' in result_obj:
                            result['suggestion'] = result_obj['suggestion']
                        if 'evidence' in result_obj:
                            result['evidence'] = result_obj['evidence']
                        return result

                # 处理单对象格式（中文字段名）
                # 格式: {"conclusion": "通过", "reason": "...", "来源": "..."}
                if isinstance(inner_json, dict):
                    if 'conclusion' in inner_json:
                        result['conclusion'] = inner_json['conclusion']
                    if 'reason' in inner_json:
                        result['reason'] = inner_json['reason']
                    # 检查中文或英文字段名
                    if '来源' in inner_json:
                        result['evidence'] = inner_json['来源']
                    elif 'evidence' in inner_json:
                        result['evidence'] = inner_json['evidence']

                    # 处理 suggestion 和 evidence 格式
                    if 'suggestion' in inner_json:
                        result['suggestion'] = inner_json['suggestion']
                    if 'evidence' in inner_json:
                        result['evidence'] = inner_json['evidence']
                    if result['suggestion'] or result['evidence']:
                        return result

                    # 如果成功提取到所有字段，直接返回
                    if result['conclusion'] or result['reason'] or result['evidence']:
                        return result
                if 'results' in inner_json:
                    results_list = inner_json['results']
                    if isinstance(results_list, list) and len(results_list) > 0:
                        # 检查第一个对象是否同时包含 conclusion, reason, evidence
                        first_item = results_list[0]
                        if isinstance(first_item, dict):
                            if 'conclusion' in first_item and 'reason' in first_item and 'evidence' in first_item:
                                # 单对象格式，直接提取
                                result['conclusion'] = first_item['conclusion']
                                result['reason'] = first_item['reason']
                                result['evidence'] = first_item['evidence']
                                return result
                            # 尝试解析三个独立对象的格式
                            for item in results_list:
                                if isinstance(item, dict):
                                    if 'conclusion' in item:
                                        result['conclusion'] = item['conclusion']
                                    elif 'reason' in item:
                                        result['reason'] = item['reason']
                                    elif 'evidence' in item:
                                        result['evidence'] = item['evidence']
                            if result['conclusion'] or result['reason'] or result['evidence']:
                                return result
            except:
                pass

            # 兼容旧格式（包含 #结论、#原因、#来源 等关键词）
            lines = content.split('\n')
            standard_format_count = 0
            for line in lines:
                line = line.strip()
                if line.startswith('#结论') or line.startswith('#原因') or line.startswith('#来源'):
                    standard_format_count += 1
                elif re.match(r'^#\s*结论', line, re.IGNORECASE) or \
                     re.match(r'^#\s*原因', line, re.IGNORECASE) or \
                     re.match(r'^#\s*来源', line, re.IGNORECASE):
                    standard_format_count += 1

            if standard_format_count >= 1:
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    conclusion_match = re.match(r'^#\s*结论[：:]?\s*(.*)', line, re.IGNORECASE)
                    reason_match = re.match(r'^#\s*原因[：:]?\s*(.*)', line, re.IGNORECASE)
                    source_match = re.match(r'^#\s*来源[：:]?\s*(.*)', line, re.IGNORECASE)

                    if conclusion_match:
                        result['conclusion'] = conclusion_match.group(1).strip()
                    elif reason_match:
                        result['reason'] = reason_match.group(1).strip()
                    elif source_match:
                        result['evidence'] = source_match.group(1).strip()
            else:
                # 如果不是标准格式，将整个内容作为结论
                result['conclusion'] = content
                result['reason'] = '核对清单'
                result['evidence'] = 'HiAgent 工作流返回'

        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")

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
            结论文本，格式为 {"content": "{"conclusion": "...", "reason": "...", "evidence": "..."}"}
        """
        # 将 task 和 reviews 包装在 information 字段中（JSON 字符串格式）
        information = json.dumps({"task": task, "reviews": reviews}, ensure_ascii=False)

        input_data = {
            "information": information
        }

        if use_sync:
            print("使用同步方式生成结论...")
            url = f"{self.api_url}/sync_run_app_workflow"
            data = {
                "UserID": self.user_id,
                "InputData": json.dumps(input_data),
                "NoDebug": True
            }
            result = self._make_request(url, data)
        else:
            print("使用异步方式生成结论...")
            run_id = self.async_run_workflow(input_data)
            if run_id:
                result = self.query_workflow_process(run_id)

        if result:
            if isinstance(result, dict):
                output = result.get('content', result.get('output', ''))
            else:
                output = str(result)

        return output

    def parse_conclusion(self, result_text: str) -> Dict[str, str]:
        """
        解析总结结果

        HiAgent API 新输出格式：
        {"output": "{\"conclusion\": \"...\", \"reason\": \"...\", \"evidence\": \"...\"}"}

        Args:
            result_text: HiAgent 返回的 output 字段内容

        Returns:
            包含 conclusion, reason, evidence 的字典
        """
        result = {
            "conclusion": '',
            "reason": '',
            "evidence": ''
        }

        try:
            # 解析外层 JSON
            outer_json = json.loads(result_text)

            # 优先获取 output 字段，兼容 content 字段
            content_str = outer_json.get('output', outer_json.get('content', ''))

            if content_str:
                # 解析 inner_json
                try:
                    inner_data = json.loads(content_str)

                    # 尝试直接提取字段
                    result['conclusion'] = inner_data.get('conclusion', '')
                    result['reason'] = inner_data.get('reason', '')
                    result['evidence'] = inner_data.get('evidence', '')
                except json.JSONDecodeError:
                    # content_str 不是 JSON，直接使用
                    result['reason'] = content_str
                    result['evidence'] = content_str

        except json.JSONDecodeError:
            print(f"JSON 解析失败: {result_text}")

        return result
