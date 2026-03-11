"""
HiAgent API 使用示例
"""

from hiagent_client import TaskCreator, TaskAuditor
from config import config


def main():
    # 从配置文件读取配置
    api_url = config.API_URL
    api_key = config.API_KEY
    user_id = config.USER_ID

    # 需求文本 - 描述需要创建什么类型的任务
    requirement = """
    请根据招标文件，创建以下审核任务：
    1. 审核投标单位的资质文件是否满足招标要求
    2. 审核技术方案的可行性和创新性
    3. 审核商务条款的合规性和经济性
    4. 审核报价是否合理，是否在预算范围内
    """

    # 上下文文本 - 招标文件的实际内容
    context = """
    [招标文件内容]
    招标项目：智慧城市建设项目
    预算金额：5000万元
    要求：投标单位必须具有一级资质，注册资金不低于1亿元
    技术要求：必须包含大数据分析平台、AI应用、系统集成等内容
    评标标准：技术占60%，商务占30%，报价占10%
    """

    try:
        # 步骤1：创建任务
        print("="*60)
        print("步骤1：创建审核任务")
        print("="*60)

        task_creator = TaskCreator(api_url, api_key, user_id)

        # 使用同步调用（推荐）
        tasks_text = task_creator.create_tasks(requirement, use_sync=True)

        if not tasks_text:
            print("任务创建失败")
            return

        print(f"HiAgent 返回的任务文本：\n{tasks_text}\n")

        # 解析任务
        tasks = TaskCreator.parse_tasks(tasks_text)
        print("解析后的任务列表：")
        for task in tasks:
            print(f"  任务 {task['id']}: {task['content']}")
            if task['subtasks']:
                for subtask in task['subtasks']:
                    print(f"    子任务 {subtask['id']}: {subtask['content']}")

        # 步骤2：逐个审核任务
        print("\n" + "="*60)
        print("步骤2：审核任务")
        print("="*60)

        task_auditor = TaskAuditor(api_url, api_key, user_id)
        audit_results = []

        for task in tasks:
            print(f"\n正在审核任务 {task['id']}:")
            print(f"任务内容: {task['content']}")
            print("-" * 40)

            # 调用审核接口
            result_text = task_auditor.audit_task(task['content'], context, use_sync=True)

            if result_text:
                # 解析审核结果
                result = TaskAuditor.parse_audit_result(result_text)
                audit_results.append({
                    'task_id': task['id'],
                    'task_content': task['content'],
                    'result': result
                })

                print("审核结果：")
                print(f"  结论: {result['conclusion']}")
                print(f"  原因: {result['reason']}")
                print(f"  来源: {result['source']}")
            else:
                print(f"任务 {task['id']} 审核失败")

        # 步骤3：汇总结果
        print("\n" + "="*60)
        print("步骤3：审核结果汇总")
        print("="*60)

        for item in audit_results:
            print(f"\n任务 {item['task_id']}: {item['task_content']}")
            print(f"结论: {item['result']['conclusion']}")
            print(f"原因: {item['result']['reason']}")
            print(f"来源: {item['result']['source']}")

    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()