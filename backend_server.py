"""
HiAgent API 后端服务器
连接前端 Vue 应用和 HiAgent API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加当前目录到 Python 路径，以便导入 hiagent_client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hiagent_client import TaskCreator, TaskAuditor, SummaryAgent

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 从环境变量或配置文件读取配置
def get_config():
    # 首先尝试从本地 .env 文件读取
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

API_URL, TASK_CREATOR_API_KEY, TASK_AUDITOR_API_KEY, SUMMARY_API_KEY, USER_ID = get_config()
print(f"Config: API_URL={API_URL}, TASK_CREATOR_API_KEY={TASK_CREATOR_API_KEY}, TASK_AUDITOR_API_KEY={TASK_AUDITOR_API_KEY}, SUMMARY_API_KEY={SUMMARY_API_KEY}, USER_ID={USER_ID}")

# 初始化 HiAgent 客户端，使用不同的 API key
task_creator = TaskCreator(API_URL, TASK_CREATOR_API_KEY, USER_ID)
task_auditor = TaskAuditor(API_URL, TASK_AUDITOR_API_KEY, USER_ID)
summary_agent = SummaryAgent(API_URL, SUMMARY_API_KEY, USER_ID)


@app.route('/hiagent/generate-tasks', methods=['POST'])
def generate_tasks():
    """生成审核任务"""
    try:
        data = request.get_json()
        requirement = data.get('requirement')
        # 检查是否明确传递了 type 参数
        task_type = data.get('type') if 'type' in data else None

        if not requirement:
            return jsonify({
                'code': 400,
                'message': '招标文件信息不能为空'
            }), 400

        # type=0（核实信息）和 type=1（招标要求）都需要调用 HiAgent API
        if task_type in [0, 1]:
            result = task_creator.sync_run_workflow({
                "extraction": requirement,
                "type": task_type
            })

            if not result or result.get('status') != 'success':
                return jsonify({
                    'code': 500,
                    'message': '任务生成失败'
                }), 500

            # 获取 output 字段（HiAgent API 新格式）
            output = result.get('output', '')

            # 将 output 传递给 TaskCreator.parse_tasks 进行解析
            # 新格式: {"output": "{\"tasks\": [\"任务1\", \"任务2\"]}"}
            tasks = TaskCreator.parse_tasks(output)

            return jsonify({
                'code': 200,
                'message': '任务生成成功',
                'data': tasks,
                'raw_text': output
            })

        # 通用要求（type=None），直接复制为任务
        tasks = [{
            'id': 1,
            'content': requirement,
            'subtasks': []
        }]
        return jsonify({
            'code': 200,
            'message': '任务生成成功',
            'data': tasks,
            'raw_text': requirement
        })

    except Exception as e:
        import traceback
        error_msg = f"生成任务时发生错误：{str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({
            'code': 500,
            'message': '任务生成失败',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/hiagent/generate-conclusion', methods=['POST'])
def generate_conclusion():
    """生成最终审核结论"""
    try:
        data = request.get_json()
        task_input = data.get('task')
        reviews = data.get('reviews', [])

        if not task_input:
            return jsonify({
                'code': 400,
                'message': '任务不能为空'
            }), 400

        # 如果 task 是对象，从中提取任务描述
        if isinstance(task_input, dict):
            # 优先使用 description，其次使用 title
            task = task_input.get('description', task_input.get('title', ''))
        else:
            # 如果是字符串，直接使用
            task = str(task_input)

        if not isinstance(reviews, list):
            return jsonify({
                'code': 400,
                'message': '审核结果必须是数组格式'
            }), 400

        # 调用 SummaryAgent 生成结论
        result_text = summary_agent.generate_conclusion(task, reviews, use_sync=True)

        if not result_text:
            return jsonify({
                'code': 500,
                'message': '结论生成失败'
            }), 500

        # 使用 SummaryAgent.parse_conclusion 解析总结结果
        parsed = summary_agent.parse_conclusion(result_text)
        conclusion = parsed.get('conclusion', '')
        reason = parsed.get('reason', '')
        evidence = parsed.get('evidence', '')

        # 根据结论内容判断状态
        status = '待确认'  # 默认状态
        if conclusion:
            # 检查是否包含"通过"、"符合"等关键词
            if any(keyword in conclusion for keyword in ['通过', '符合', '合格', '满足']):
                status = '通过'
            elif any(keyword in conclusion for keyword in ['不通过', '不符合', '不合格', '未通过']):
                status = '不通过'

        # 使用 Python 的 datetime 获取当前时间
        from datetime import datetime

        # 返回符合 guide.md 定义的格式
        return jsonify({
            'code': 200,
            'message': '总结成功',
            'data': {
                'conclusion': conclusion,
                'reason': reason,
                'evidence': evidence
            },
            'status': status,
            'raw_text': result_text
        })

    except Exception as e:
        print(f"生成结论时发生错误：{str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误：{str(e)}'
        }), 500


@app.route('/hiagent/review-task', methods=['POST'])
def review_task():
    """审核任务"""
    try:
        data = request.get_json()
        task_input = data.get('task')
        context = data.get('context')

        if not task_input:
            return jsonify({
                'code': 400,
                'message': '任务不能为空'
            }), 400

        # 如果 task 是对象，从中提取任务描述
        if isinstance(task_input, dict):
            # 优先使用 description，其次使用 title
            task = task_input.get('description', task_input.get('title', ''))
        else:
            # 如果是字符串，直接使用
            task = str(task_input)

        if not context:
            return jsonify({
                'code': 400,
                'message': '投标文件内容不能为空'
            }), 400

        # 调用 HiAgent API 审核任务
        result_text = task_auditor.audit_task(task, context, use_sync=True)

        if not result_text:
            return jsonify({
                'code': 500,
                'message': '任务审核失败'
            }), 500

        # 使用 TaskAuditor.parse_audit_result 解析审核结果
        # 新格式: {"result": {"suggestion": "...", "evidence": "..."}}
        parsed = TaskAuditor.parse_audit_result(result_text)
        suggestion = parsed.get('suggestion', '')
        evidence = parsed.get('evidence', '')

        # 返回符合格式
        return jsonify({
            'code': 200,
            'message': '任务审核成功',
            'data': {
                'suggestion': suggestion,
                'evidence': evidence
            },
            'raw_text': result_text
        })

    except Exception as e:
        print(f"审核任务时发生错误：{str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误：{str(e)}'
        }), 500


@app.route('/hiagent/review-task-slices', methods=['POST'])
def review_task_slices():
    """
    多切片审核：对一个任务，用多个切片文件分别审核，然后汇总结果（不调用 LLM）
    """
    try:
        data = request.get_json()
        task_input = data.get('task')
        slices = data.get('slices', [])  # 切片内容数组

        # 验证切片数量（最多 30 个）
        if len(slices) > 30:
            return jsonify({'code': 400, 'message': '切片数量不能超过 30 个'}), 400

        if not task_input:
            return jsonify({'code': 400, 'message': '任务不能为空'}), 400

        if not slices:
            return jsonify({'code': 400, 'message': '切片不能为空'}), 400

        # 提取任务描述
        if isinstance(task_input, dict):
            task = task_input.get('description', task_input.get('title', ''))
        else:
            task = str(task_input)

        print(f"开始多切片审核，任务：{str(task)[:50]}...，切片数：{len(slices)}")

        # 对每个切片调用 TaskAuditor
        reviews = []
        for idx, slice_text in enumerate(slices):
            print(f"正在审核切片 {idx+1}/{len(slices)}...")
            result_text = task_auditor.audit_task(task, slice_text, use_sync=True)
            parsed = TaskAuditor.parse_audit_result(result_text)

            # 处理 evidence，如果是字符串 "null" 则转为 null
            evidence = parsed.get('evidence', '')
            if evidence == 'null' or evidence == '""':
                evidence = None

            reviews.append({
                'suggestion': parsed.get('suggestion', ''),
                'evidence': evidence
            })

        # 调用 SummaryAgent 汇总所有切片的审核结果
        # 只返回原始切片审核结果，不做整合处理
        print(f"\n切片审核完成，共 {len(reviews)} 个切片")

        # 返回简化格式（只包含 task 和 reviews）
        return jsonify({
            'code': 200,
            'message': '多切片审核成功',
            'data': {
                'task': task,
                'reviews': reviews
            }
        })

    except Exception as e:
        import traceback
        error_msg = f"多切片审核失败：{str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({
            'code': 500,
            'message': '多切片审核失败',
            'error': str(e)
        }), 500


@app.route('/hiagent/status', methods=['GET'])
def get_status():
    """获取 API 状态"""
    return jsonify({
        'code': 200,
        'message': 'API 服务正常',
        'data': {
            'api_url': API_URL,
            'user_id': USER_ID,
            'status': 'running'
        }
    })


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'message': 'HiAgent Backend Server is running'
    })


@app.route('/hiagent/summarize-reviews', methods=['POST'])
def summarize_reviews():
    """
    汇总切片审核结果：将各个切片的审核结果整合为统一格式
    """
    try:
        data = request.get_json()
        task_input = data.get('task')
        reviews_input = data.get('reviews', [])

        if not task_input:
            return jsonify({'code': 400, 'message': '任务不能为空'}), 400

        # 提取任务描述
        if isinstance(task_input, dict):
            task = task_input.get('description', task_input.get('title', ''))
        else:
            task = str(task_input)

        # 检查 reviews 格式
        if not isinstance(reviews_input, list):
            return jsonify({'code': 400, 'message': 'reviews 必须是数组'}), 400

        print(f"\n开始汇总审核结果，任务：{str(task)[:50]}...，审核结果数：{len(reviews_input)}")

        # 构建 reviews 数组
        reviews = []
        for review in reviews_input:
            # 处理每个 review 对象
            suggestion = review.get('suggestion', '')
            evidence = review.get('evidence', '')

            # 如果 evidence 是字符串 "null"，则转为 null
            if evidence == 'null' or evidence == '""':
                evidence = None

            reviews.append({
                'suggestion': suggestion,
                'evidence': evidence
            })

        print(f"汇总完成，生成 reviews 数组：{len(reviews)} 条")

        # 返回结果
        return jsonify({
            'code': 200,
            'message': '汇总成功',
            'data': {
                'task': task,
                'reviews': reviews
            }
        })

    except Exception as e:
        import traceback
        error_msg = f"汇总失败：{str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({
            'code': 500,
            'message': '汇总失败',
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("HiAgent Backend Server 启动中...")
    print(f"API URL: {API_URL}")
    print(f"User ID: {USER_ID}")
    print("服务器地址: http://localhost:8888")

    app.run(
        host='0.0.0.0',
        port=8888,
        debug=True,
        threaded=True
    )