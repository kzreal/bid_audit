"""
HiAgent API 后端服务器
连接前端 Vue 应用和 HiAgent API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# 添加当前目录到 Python 路径，以便导入 hiagent_client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hiagent_client import TaskCreator, TaskAuditor

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 从环境变量或配置文件读取配置
def get_config():
    # 首先尝试从环境变量读取
    api_url = os.getenv('VITE_API_BASE_URL')
    api_key = os.getenv('VITE_HIAGENT_API_KEY')
    user_id = os.getenv('VITE_HIAGENT_USER_ID', 'user001')

    # 如果环境变量没有设置，尝试从 frontend 的 .env.development 读取
    if not api_url or api_key == 'your_api_key_here':
        try:
            with open('../bid-review-system/.env.development', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('VITE_API_BASE_URL='):
                        api_url = line.split('=', 1)[1]
                    elif line.startswith('VITE_HIAGENT_API_KEY='):
                        api_key = line.split('=', 1)[1]
        except:
            # 如果都失败，使用默认值
            api_url = 'https://prd-ai-studio.chint.com/api/proxy/api/v1'
            api_key = 'd6ntpsf4piphvinbnmh0'
            user_id = '250701283'

    return api_url, api_key, user_id

API_URL, API_KEY, USER_ID = get_config()
print(f"Config: API_URL={API_URL}, API_KEY={API_KEY}, USER_ID={USER_ID}")

# 初始化 HiAgent 客户端
task_creator = TaskCreator(API_URL, API_KEY, USER_ID)
task_auditor = TaskAuditor(API_URL, API_KEY, USER_ID)


@app.route('/hiagent/debug', methods=['POST'])
def debug_tasks():
    """调试端点，显示详细错误信息"""
    try:
        data = request.get_json()
        requirement = data.get('requirement', '')

        print(f"=== DEBUG MODE ===")
        print(f"Requirement: {requirement}")
        print(f"Config - API_URL: {API_URL}")
        print(f"Config - API_KEY: {API_KEY}")
        print(f"Config - USER_ID: {USER_ID}")

        # 调用 HiAgent
        input_data = {"extraction": requirement, "type": 1}
        print(f"Input data: {input_data}")

        result = task_creator.sync_run_workflow(input_data)
        print(f"HiAgent result: {result}")

        if result and result.get('status') == 'success':
            # 解析 output 字段，它可能是 JSON 字符串
            output = result.get('output', '')
            print(f"Raw output: {output}")

            # 尝试解析 output 中的 JSON
            try:
                import json
                data = json.loads(output)
                content = data.get('content', '')
                print(f"Extracted content: {content}")
            except:
                # 如果解析失败，直接使用 output
                content = output

            # 解析任务
            tasks = TaskCreator.parse_tasks(content)
            return jsonify({
                'code': 200,
                'message': '任务生成成功',
                'data': tasks,
                'raw_text': content,
                'debug': 'success'
            })
        else:
            return jsonify({
                'code': 500,
                'message': 'HiAgent API 失败',
                'hiagent_result': result,
                'debug': 'hiagent_error'
            }), 500

    except Exception as e:
        import traceback
        error_msg = f"调试错误：{str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({
            'code': 500,
            'message': '调试失败',
            'error': str(e),
            'traceback': traceback.format_exc(),
            'debug': 'server_error'
        }), 500

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

        print(f"开始生成任务，需求：{requirement[:50]}..., type: {task_type}")

        # type=0（核实信息）和 type=1（招标要求）都需要调用 HiAgent API
        if task_type in [0, 1]:
            print(f"type={task_type}，调用 HiAgent API")
            result = task_creator.sync_run_workflow({
                "extraction": requirement,
                "type": task_type
            })

            if not result or result.get('status') != 'success':
                return jsonify({
                    'code': 500,
                    'message': '任务生成失败'
                }), 500

            # 解析 output 字段
            output = result.get('output', '')
            print(f"Raw output: {output}")

            # 尝试解析 output 中的 JSON
            try:
                import json
                json_data = json.loads(output)
                content = json_data.get('content', '')
                print(f"Extracted content: {content}")
            except:
                # 如果解析失败，直接使用 output
                content = output

            # 解析任务
            print(f"=== Debug Info ===")
            print(f"Type of content: {type(content)}")
            print(f"Length: {len(content)}")
            print(f"Starts with {{: {content.startswith('{')}")

            tasks = TaskCreator.parse_tasks(content)
            print(f"Parsed tasks count: {len(tasks)}")

            return jsonify({
                'code': 200,
                'message': '任务生成成功',
                'data': tasks,
                'raw_text': content
            })

        # 通用要求（type=None），直接复制为任务
        print("通用要求（type=None），直接返回任务")
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


@app.route('/hiagent/review-task', methods=['POST'])
def review_task():
    """审核任务"""
    try:
        data = request.get_json()
        task = data.get('task')
        context = data.get('context')

        if not task:
            return jsonify({
                'code': 400,
                'message': '任务不能为空'
            }), 400

        if not context:
            return jsonify({
                'code': 400,
                'message': '投标文件内容不能为空'
            }), 400

        print(f"开始审核任务：{str(task)[:100]}...")

        # 调用 HiAgent API 审核任务
        result_text = task_auditor.audit_task(task, context, use_sync=True)

        if not result_text:
            return jsonify({
                'code': 500,
                'message': '任务审核失败'
            }), 500

        print(f"HiAgent 返回的审核结果：{result_text}")

        # 解析审核结果
        result = TaskAuditor.parse_audit_result(result_text)

        return jsonify({
            'code': 200,
            'message': '任务审核成功',
            'data': result,
            'raw_text': result_text
        })

    except Exception as e:
        print(f"审核任务时发生错误：{str(e)}")
        return jsonify({
            'code': 500,
            'message': f'服务器错误：{str(e)}'
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