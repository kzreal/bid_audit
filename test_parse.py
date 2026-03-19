"""测试 TaskCreator.parse_tasks 方法"""
from hiagent_client import TaskCreator
import json

# 测试用例 - 使用真实的 API 返回格式
test_input = '{"content":"{\n  \"tasks\": [\n    { \"id\": 1, \"task\": \"请核实投标文件中投标单位是否具备一级安防工程资质证书。\" },\n    { \"id\": 2, \"task\": \"请核实投标文件中项目编号是否为 ad1231313。\" }\n  ]\n}"}'

print("测试输入:")
print(test_input)
print("\n开始解析...")

parsed = TaskCreator.parse_tasks(test_input)
print(f"\n解析结果: {parsed}")
print(f"任务数量: {len(parsed)}")
