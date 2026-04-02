import pytest
import json
from unittest.mock import MagicMock, patch
from backend_server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_generate_tasks_parsing(client):
    """测试 /hiagent/generate-tasks 端点解析 HiAgent 新 JSON 结构的能力"""
    # backend_server.py 调用 TaskCreator.parse_tasks(json.dumps(result))
    # TaskCreator.parse_tasks 内部调用 json.loads(tasks_text)
    # 然后获取 result.get('output', [])
    mock_hiagent_response = {
        "status": "success",
        "output": [
            {"id": "1", "task": "任务1"},
            {"id": "2", "task": "任务2"}
        ],
        "costMs": 100
    }

    with patch('hiagent_client.TaskCreator.sync_run_workflow', return_value=mock_hiagent_response):
        response = client.post('/hiagent/generate-tasks', json={'requirement': '测试需求'})
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert len(data['data']) == 2
        assert data['data'][0]['content'] == "任务1"
        assert data['data'][1]['content'] == "任务2"

def test_review_task_parsing(client):
    """测试 /hiagent/review-task 端点解析 HiAgent 新 JSON 结构的能力"""
    # 注意：backend_server.py 中调用了 task_auditor.review_task
    # 该方法内部调用了 sync_run_review_workflow 并返回 json.dumps(result)
    mock_workflow_result = {
        "status": "success",
        "output": [
            {
                "suggestion": "审核建议文本",
                "evidence": "1, 2, 3"
            }
        ]
    }

    # 我们直接 mock task_auditor.audit_task 的返回值，因为它在 backend_server.py 中被直接调用
    with patch('hiagent_client.TaskAuditor.audit_task', return_value=json.dumps(mock_workflow_result, ensure_ascii=False)):
        response = client.post('/hiagent/review-task', json={
            'task': {'title': '测试任务'},
            'context': '测试上下文'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert data['data']['suggestion'] == "审核建议文本"
        assert data['data']['evidence'] == "1, 2, 3"

def test_generate_conclusion_parsing(client):
    """测试 /hiagent/generate-conclusion 端点解析 HiAgent 新 JSON 结构的能力"""
    # SummaryAgent.generate_conclusion 返回原始字符串
    mock_summary_output = json.dumps({
        "results": [
            {
                "conclusion": "通过",
                "reasons": [
                    {
                        "reason": "原因1",
                        "evidence": "10-20"
                    }
                ]
            }
        ]
    }, ensure_ascii=False)

    with patch('hiagent_client.SummaryAgent.generate_conclusion', return_value=mock_summary_output):
        response = client.post('/hiagent/generate-conclusion', json={
            'task': {'title': '测试任务'},
            'reviews': [{'suggestion': '建议1', 'evidence': '10-20'}]
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['code'] == 200
        assert data['data']['conclusion'] == "通过"
        assert data['data']['reason'] == "原因1"
        assert data['data']['evidence'] == "10-20"
        assert data['status'] == "通过"
