背景
HiAgent平台提供将智能体作为后端服务API被业务请求的能力，用以满足客户希望自主构建前端交互页面，或者将智能体加入到当前已有业务服务调用链路中的场景需求。
1、此文档已开启外部访问权限，可直接发链接给客户（申请时备注公司名称）。
2、如需下载发给客户，请访问pdf版：HiAgent v2.0.1 智能体接口文档.pdf
前置依赖
1. 完成智能体调试与发布
2. 打开API访问开关；
[图片]
调用步骤（以对话类聊天为例）
- 第一步：在智能体预览页右侧，获取API调用的URL和鉴权用的{{ ApiKey }}
- 第二步：
  - 在请求header加上Apikey={{ ApiKey }}，body参数中包括AppKey，也赋值为{{ ApiKey }}；
  - 所有接口需要在Body中加上UserID，UserID为调用API的用户ID（用户标识，用于定义终端用户的身份，方便检索、统计。 由开发者定义规则，需保证用户标识在应用内唯一）；UserID不支持中文，仅支持字母和数字。
- 第三步：开始对话（通用流程）
  - 选择一个合适的应用，获取应用AppID，调用CreateConversation生成一个会话ID；
  - 调用ChatQuery接口（所有流式接口都是SSE），传入会话ID，即可开始聊天，返回流式的对话数据；
  - 停止聊天：在流式输出的过程中调用StopMessage接口，即可停止聊天；
  - 重新生成：如果需要重新生成聊天结果，调用QueryAgain，可重新生成聊天结果；
  - 结果反馈：调用Feedback接口，传入消息ID，可对回答进行反馈评价（赞或踩）；
  - 查看聊天历史：获取会话的聊天历史：GetConversationMessages；
注意：下述调用代码中用到的通用代码调用方法：
import json

import requests


class AttemptExceededException(Exception):
    def init(self, message):
        self.message = message
        super().init(self.message)

    def str(self):
        return repr(self.message)


def make_request(url: str, headers: dict, data: dict, max_retries: int = 3):
    """
    发送 HTTP POST 请求并处理重试逻辑
    参数:
        url (str): 请求的 URL
        headers (dict): 请求头
        data (dict): 请求体数据
    返回:
        dict: 成功返回 JSON 响应，失败返回 None
    """

    for i in range(max_retries):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"重试 {i + 1} 次: {e}")
    raise AttemptExceededException(f"达到最大重试次数 {max_retries}")
服务：ChatService
API 列表概览
ChatQuery: 对话类聊天
ChatQueryV2: 对话类聊天V2
QueryAgain: 重新生成回复
GetAppConfigPreview: 获取应用配置
GetConversationList: 获取对话列表
GetConversationInputs: 获取对话变量输入
CreateConversation: 创建会话
UpdateConversation: 更新会话
DeleteConversation: 删除会话
StopMessage: 停止响应
GetConversationMessages: 获取会话历史消息列表
GetMessageInfo: 获取消息详情
DeleteMessage: 删除消息
Feedback: 回答反馈评价（赞或踩）
SetMessageAnswerUsed: 多组回答时，设置某个回答为默认使用的回答
GetSuggestedQuestions: 获取提问建议
RunAppWorkflow: 测试运行工作流(异步)
QueryRunAppProcess: 查询测试运行工作流运行进展(异步)
ListOauth2Token: 查询用户oauth2登录信息的接口
QueryAgainV2: 重新生成回复V2
ClearMessage: 清除消息
SyncRunAppWorkflow: 测试运行工作流(同步)
CallTriggerWebhook: 触发事件触发器

API 接口
创建会话
- 接口说明：对话类聊天接口，需要先生成会话，会话ID为AppConversationID，后续的聊天接口ChatQuery都需要传入会话ID。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）,已废弃可不传；
  2. Inputs：变量输入，可选，根据应用编排时设置的变量确定；
  3. UserID：用户标识，用于定义终端用户的身份，方便检索、统计。 由开发者定义规则，需保证用户标识在应用内唯一。（长度：1-20）， UserID不支持中文，仅支持字母和数字。
- response body参数说明：
  1. Conversation：AppConversationID,后续的聊天接口ChatQuery都需要传入会话ID;ConversationName,会话默认名（可修改）；
  2. BaseResp：系统参数，不关注；
Post /create_conversation
请求 (app.CreateConversationRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header

应用key。http 请求头中设置 Apikey={{ ApiKey }}
Inputs

map[string, string]

false
Request body(json)
变量输入。可选，根据应用编排时设置的变量确定
UserID
string
true
Request body(json)
用户ID
响应 (app.CreateConversationResponse):
参数
类型
是否必填
说明
Conversation
app.AppConversationBrief
false
对话信息
BaseResp
base.BaseResp
false



Postman示例
py代码示例
请求示例：
curl --location '{{apiurl}}/api/proxy/api/v1/create_conversation' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "Inputs": {
        "var": "variable"
    },
    "UserID": "321"
}'

def create_conversation(user_id: str) -> str:
    """
    创建会话
    :param user_id: 用户id
    :return: 对话id
    :raises: ValueError, requests.exceptions.RequestException
    """
    url = base_url + "create_conversation"
    headers = {'Apikey': api_key, 'Content-Type': 'application/json'}
    data = {"UserID": user_id, "Inputs": {"var": "variable"}}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"网络请求失败: {e}")

    try:
        result = response.json()
    except json.JSONDecodeError as e:
        raise ValueError(f"响应 JSON 解析失败: {e}")

    if "Conversation" not in result:
        raise ValueError("API 返回的结果缺少 'Conversation' 字段")
    
    if "AppConversationID" not in result["Conversation"]:
        raise ValueError("API 返回的结果缺少 'AppConversationID' 字段")

    return result["Conversation"]["AppConversationID"]
返回示例：
{
    "Conversation": {
        "AppConversationID": "ct4m7gmoc93a9ns2sngg",
        "ConversationName": "新的会话",
        "CreateTime": "",
        "LastChatTime": "",
        "EmptyConversation": false
    },
    "BaseResp": null
}






对话类聊天（建议使用V2接口）
- 接口说明： 对话类聊天接口，需要先生成会话。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. AppConversationID：会话ID，由CreateConversation接口生成；
  3. UserID：用户标识，用于定义终端用户的身份，方便检索、统计。 由开发者定义规则，需保证用户标识在应用内唯一。（长度：1-20）；
  4. Query：用户输入/提问内容；
  5. ResponseMode：streaming 流式模式（推荐）。基于 SSE（Server-Sent Events）实现类似打字机输出方式的流式返回。 blocking 阻塞模式，等待执行完毕后返回结果；
- response body参数说明：
  1. Data：SSE格式的输出；
Post /chat_query
请求 (app.ChatQueryRequest):
参数
类型
是否必填
参数作用域
说明
AppKey

string
false
Request header

应用key。http 请求头中设置 Apikey={{ ApiKey }}
AppConversationID
string
true
Request body(json)
应用侧对话ID
Query
string
true
Request body(json)
用户询问内容
ResponseMode

string
false
Request body(json)
返回数据的格式，枚举值：streaming、blocking，默认：streaming
QueryExtends
app.QueryExtendsInfo
false
Request body(json)
询问扩展信息
PubAgentJump
bool
false
Request body(json)
是否输出agent信息,默认为true
UserID
string
true
Request body(json)
用户ID
响应 (app.MessageStreamResponse):
参数
类型
是否必填
说明
Data
string
false
EventStream(data: json)

Postman示例
py代码示例
备注
请求示例：
curl --location '{{apiurl}}/api/proxy/api/v1/chat_query' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "Query": "给我讲个故事",
    "AppConversationID": "co6deaa1hp0kieia13bg",
    "ResponseMode": "streaming",
    "UserID": "321",
    "QueryExtends": {
        "Files": [
          {
            "Name": "图片.jpeg",
            "Path": "upload/full/59/e8/0304b770fd1dfebe806bf1ade61a4bc5ded18f969a1c8f803998eeb60573",
            "Size": 47525,
            "Url": "{{apiurl}}/api/proxy/down?Action=Download&Version=2022-01-01&Path=upload%2Ffull%2F59%2Fe8%2F0304b770fd1dfebe806bf1ade61a4bc5ded18f969a1c8f803998eeb60573&IsAnonymous=true"
          }
        ]
    }
}'

def chat_query(user_id: str, app_conversation_id: str, content: str):
    """
    对话类聊天
    :param user_id: 用户id
    :param app_conversation_id: 对话id
    :param content: ⽤户询问的内容
    :return:
    """
    url = base_url + "chat_query"
    headers = {'Apikey': api_key,
               'Content-Type': 'application/json',
               'Accept': 'text/event-stream'}
    data = {"UserID": user_id,
            "AppConversationID": app_conversation_id,
            "Query": content,
            "ResponseMode": "streaming"}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
    except Exception as e:
        raise ParamsException(403, str(e))
    return response
Files信息包括obs链接，关于如何将文件上传obs参考文档：Hi Agent Up服务接口调用说明

流式请求时：
请求头注意'Accept': 'text/event-stream'
代码请求时：request设置stream=True

返回示例：
流式
{
event:text
data:data: {"event": "message_start", "task_id": "6b2f4720-a14e-413d-9783-024442a58e7d"}

event:text
data:data: {"event": "message", "task_id": "6b2f4720-a14e-413d-9783-024442a58e7d", "id": "01JDHDFNH1XMJG89SEP2F49HDV", "answer": "你", "created_at": 1732530134, "conversation_id": "01JDHDFNGYRB130PZSEDE8R70B"}
}
if __name__ == '__main__':
    try:
        uid = "321"
        conversation_id = create_conversation(uid)
        print(f"conversation_id: {conversation_id}")

        question = "给我讲个故事"
        resp = chat_query(uid, conversation_id, question)
        start_time = time.time()
        task_id = None

        for line in resp.iter_lines(chunk_size=4):
            if line:  # 过滤掉空行
                line = line.decode("utf-8")
                if line.startswith("data:"):
                    data = line.strip("data:").strip()
                    if data:
                        try:
                            data = json.loads(data)
                            if "event" in data and data["event"] == "message":
                                print(data["answer"], end="")
                            if "task_id" in data:
                                task_id = data["task_id"]
                        except json.JSONDecodeError as e:
                            print(f"JSON 解析失败: {e}")
                        except KeyError as e:
                            print(f"返回数据缺少必要字段: {e}")

        print("\n")
        print(f"整体耗时：{time.time() - start_time}")

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
    except ValueError as e:
        print(f"API 返回结果异常: {e}")
    except Exception as e:
        print(f"未知错误: {e}")

Data是标准的sse流式返回，用户需要自行解析data字段。字段含义如下：
- event：事件类型,枚举值
  - message_start：消息开始
  - message：消息
  - message_end：消息结束
  - message_output_start：开始输出
  - message_output_end：输出结束
  - message_cost：消息消耗
  - suggestion：问题建议
  - suggestion_cost：问题建议消耗
  - agent_thought：思考
  - agent_thought_end：思考结束
  - message_replace：消息替换
  - message_failed：消息失败
  - knowledge_retrieve：知识库检索
  - knowledge_retrieve_end：知识库检索结束
  - agent_jump：agent跳转事件
  - agent_take_over：agent接管最终回答的事件
  - intention：意图
  - qa_retrieve：问答库检索
  - qa_retrieve_end：问答库检索结束
  - knowledge_graph_retrieve：图谱库检索
  - knowledge_graph_retrieve_end：图谱库检索结束
  - terminology_retrieve：术语库检索
  - terminology_retrieve_end：术语库检索结束
  - tool_message：消息节点
  - think_message_output_start：思考开始
  - think_message：思考内容
  - think_message_output_end：思考结束
- task_id：任务ID，等效于当前对话的全局消息ID
- id：消息ID，包括当前对话的全局消息ID和嵌套的子消息ID：全局消息ID作为其他接口的MessageID入参；对话时如果调用工具等，会生成子消息ID。流式场景下，最外层的message_start、message_end里的ID为全局消息ID；非流式场景只会返回全局消息ID。
- answer：模型回复内容；
- created_at：消息创建时间；
- conversation_id：模型会话ID，作用与app_conversation_id一致。区别为：app_conversation_id作为用户感知的一个会话的标识，具有业务属性；conversation_id只作为底层模型交互的会话的标识，屏蔽用户感知
返回示例：
非流式
{
event:text
data:data: {"event": "message_end", "task_id": "6b2f4720-a14e-413d-9783-024442a58e7d", "id": "01JDHDFNH1XMJG89SEP2F49HDV", "answer": "你好，回答完毕", "created_at": 1732530134, "conversation_id": "01JDHDFNGYRB130PZSEDE8R70B"}
}

if __name__ == '__main__':
    try:
        uid = "321"
        conversation_id = create_conversation(uid)
        print(f"conversation_id: {conversation_id}")

        question = "给我讲个故事"
        resp = chat_query(uid, conversation_id, question)
        start_time = time.time()
        task_id = None

        for line in resp.iter_lines(chunk_size=4):
            if line:  # 过滤掉空行
                line = line.decode("utf-8")
                if line.startswith("data:"):
                    data = line.strip("data:").strip()
                    if data:
                        try:
                            data = json.loads(data)
                            if "event" in data and data["event"] == "message_end":
                                print(data["answer"], end="")
                            if "task_id" in data:
                                task_id = data["task_id"]
                        except json.JSONDecodeError as e:
                            print(f"JSON 解析失败: {e}")
                        except KeyError as e:
                            print(f"返回数据缺少必要字段: {e}")

        print("\n")
        print(f"整体耗时：{time.time() - start_time}")

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
    except ValueError as e:
        print(f"API 返回结果异常: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
chat_query接口非流式返回也是SSE结构的数据（历史遗留问题），该接口不再推荐，建议使用chat_query_v2

对话类聊天V2（推荐使用）
- 接口说明： 对话类聊天接口，和ChatQuery区别是，ChatQueryV2返回结构更加规范
  1. 流式返回：标准的SSE返回（区别于chat_query,每个消息体里没有嵌套data字段）；
  2. 非流式返回：返回完整的消息内容（json格式返回，区别于chat_query,返回不是SSE格式的）；
  3. 其他与ChatQuery完全一致
!!! 注意：该接口的非流式调用谨慎使用，接口仅用在聚焦问题和回答的场景，token消耗未记录到智能体日志中，关注智能体日志统计的用户，谨慎使用，该场景请使用 chat_query 进行替代。
Post /chat_query_v2
请求 (app.ChatQueryRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header

应用key。http 请求头中设置 Apikey={{ ApiKey }}
AppConversationID
string
true
Request body(json)
应用侧对话ID
Query
string
true
Request body(json)
用户询问内容
ResponseMode

string
false
Request body(json)
返回数据的格式，枚举值：streaming、blocking，默认：streaming
PubAgentJump
bool
false
Request body(json)
是否输出agent信息,默认为true
QueryExtends
app.QueryExtendsInfo
false
Request body(json)
询问扩展信息
UserID
string
true
Request body(json)
用户ID
响应 (app.MessageStreamResponse):
参数
类型
是否必填
说明
Data
string
false
EventStream(data: json)

Postman示例
py代码示例
备注
请求示例：
curl --location '{{apiurl}}/api/proxy/api/v1/chat_query_v2' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "Query": "给我讲个故事",
    "AppConversationID": "co6deaa1hp0kieia13bg",
    "ResponseMode": "streaming",
    "UserID": "321",
    "QueryExtends": {
        "Files": [
          {
            "Name": "图片.jpeg",
            "Path": "upload/full/59/e8/0304b770fd1dfebe806bf1ade61a4bc5ded18f969a1c8f803998eeb60573",
            "Size": 47525,
            "Url": "{{apiurl}}/api/proxy/down?Action=Download&Version=2022-01-01&Path=upload%2Ffull%2F59%2Fe8%2F0304b770fd1dfebe806bf1ade61a4bc5ded18f969a1c8f803998eeb60573&IsAnonymous=true"
          }
        ]
    }
}'

// 阻塞式输出调用方法
def chat_query_v2(user_id: str, app_conversation_id: str, content: str):
    """
    对话类聊天V2
    :param user_id: 用户id
    :param app_conversation_id: 对话id
    :param content: ⽤户询问的内容
    :return:
    """
    url = base_url + "chat_query_v2"
    headers = {'Apikey': api_key,
               'Content-Type': 'application/json'}
    data = {"UserID": user_id,
            "AppConversationID": app_conversation_id,
            "Query": content,
            "ResponseMode": "blocking"}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"网络请求失败: {e}")

    return response
    

// 流式输出调用方法
def chat_query_v2_sse(user_id: str, app_conversation_id: str, content: str):
    """
    对话类聊天V2
    :param user_id: 用户id
    :param app_conversation_id: 对话id
    :param content: ⽤户询问的内容
    :return:
    """
    url = base_url + "chat_query_v2"
    headers = {'Apikey': api_key,
               'Content-Type': 'application/json', 'Accept': 'text/event-stream'}
    data = {"UserID": user_id,
            "AppConversationID": app_conversation_id,
            "Query": content}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"网络请求失败: {e}")

    return response
Files信息包括obs链接，关于如何将文件上传obs参考文档：Hi Agent Up服务接口调用说明

流式请求时：
请求头注意'Accept': 'text/event-stream'
代码请求时：request设置stream=True
返回示例：
流式
{
event:text
data: {"event": "message_start", "task_id": "6b2f4720-a14e-413d-9783-024442a58e7d"}

event:text
data: {"event": "message", "task_id": "6b2f4720-a14e-413d-9783-024442a58e7d", "id": "01JDHDFNH1XMJG89SEP2F49HDV", "answer": "你", "created_at": 1732530134, "conversation_id": "01JDHDFNGYRB130PZSEDE8R70B"}
}
if __name__ == '__main__':
    try:
        uid = "321"
        conversation_id = create_conversation(uid)
        print(f"conversation_id: {conversation_id}")

        question = "给我讲个故事"
        resp = chat_query_v2_sse(uid, conversation_id, question)
        start_time = time.time()
        task_id = None

        for line in resp.iter_lines(chunk_size=4):
            if line:  # 过滤掉空行
                line = line.decode("utf-8")
                if line.startswith("data:"):
                    data = line.strip("data:").strip()
                    if data:
                        try:
                            data = json.loads(data)
                            if "event" in data and data["event"] == "message":
                                print(data["answer"], end="")
                            if "task_id" in data:
                                task_id = data["task_id"]
                        except json.JSONDecodeError as e:
                            print(f"JSON 解析失败: {e}")
                        except KeyError as e:
                            print(f"返回数据缺少必要字段: {e}")

        print("\n")
        print(f"整体耗时：{time.time() - start_time}")

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
    except ValueError as e:
        print(f"API 返回结果异常: {e}")
    except Exception as e:
        print(f"未知错误: {e}")

Data是标准的sse流式返回，用户需要自行解析data字段。字段含义如下：
- event：事件类型,枚举值
  - message_start：消息开始
  - message：消息
  - message_end：消息结束
  - message_output_start：开始输出
  - message_output_end：输出结束
  - message_cost：消息消耗
  - suggestion：问题建议
  - suggestion_cost：问题建议消耗
  - agent_thought：思考
  - agent_thought_end：思考结束
  - message_replace：消息替换
  - message_failed：消息失败
  - knowledge_retrieve：知识库检索
  - knowledge_retrieve_end：知识库检索结束
  - agent_jump：agent跳转事件
  - agent_take_over：agent接管最终回答的事件
  - intention：意图
  - qa_retrieve：问答库检索
  - qa_retrieve_end：问答库检索结束
  - knowledge_graph_retrieve：图谱库检索
  - knowledge_graph_retrieve_end：图谱库检索结束
  - terminology_retrieve：术语库检索
  - terminology_retrieve_end：术语库检索结束
  - tool_message：消息节点
  - think_message_output_start：思考开始
  - think_message：思考内容
  - think_message_output_end：思考结束
- task_id：任务ID，等效于当前对话的全局消息ID
- id：消息ID，包括当前对话的全局消息ID和嵌套的子消息ID：全局消息ID作为其他接口的MessageID入参；对话时如果调用工具等，会生成子消息ID。流式场景下，最外层的message_start、message_end里的ID为全局消息ID；非流式场景只会返回全局消息ID。
- answer：模型回复内容；
- created_at：消息创建时间；
- conversation_id：模型会话ID，作用与app_conversation_id一致。区别为：app_conversation_id作为用户感知的一个会话的标识，具有业务属性；conversation_id只作为底层模型交互的会话的标识，屏蔽用户感知
返回示例：
非流式
{
    "event": "message",
    "task_id": "01JFW1QJJBRNVZ0B7JH0E034ST",
    "id": "01JFW1QJJBRNVZ0B7JH0E034ST",
    "conversation_id": "01JFW1P2DC7HBVK1383KCN494W",
    "answer": "你好！你是想分享这个图片文件的相关信息呢，还是有关于这个文件有什么问题想询问，比如如何打开、保存之类的？",
    "created_at": 1735034398，
    "think_messages": ["推理过程消息内容"],
    "tool_messages": ["工具消息输出内容"]
}

if __name__ == '__main__':
    try:
        uid = "321"
        conversation_id = create_conversation(uid)
        print(f"conversation_id: {conversation_id}")

        question = "给我讲个故事"
        resp = chat_query_v2(uid, conversation_id, question)
        start_time = time.time()

        try:
            result = resp.json()
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析失败: {e}")

        print("解析返回的 JSON 数据：")
        for key, value in result.items():
            print(f"{key}: {value}")

        print("\n")
        print(f"整体耗时：{time.time() - start_time}")

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
    except ValueError as e:
        print(f"API 返回结果异常: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
推荐使用chat_query_v2
返回参数：
  think_messages： 推理思考消息列表。开启模型配置推理过程开关，则输出智能体对话中推理的过程消息，如果智能体中包含多个可推理模型对话，则返回每次推理的信息。
  tool_messages：工具消息列表。工作流中消息节点输出的消息。
重新生成回复
- 接口说明：用于对话类聊天接口，重新生成回复（所有流式接口都是SSE）。注意：最多支持10次重新生成。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. AppConversationID：会话ID，由CreateConversation接口生成；
  3. UserID：用户标识，用于定义终端用户的身份，方便检索、统计。 由开发者定义规则，需保证用户标识在应用内唯一。（长度：1-20）；
  4. MessageID：上轮对话返回的ID；
- response body参数说明：
  1. Data：SSE格式的输出；
Post /query_again
请求 (app.QueryAgainRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header

应用key。http 请求头中设置 Apikey={{ ApiKey }}
AppConversationID
string
true
Request body(json)
应用侧对话ID
MessageID

string
true
Request body(json)
消息ID
PubAgentJump
bool
false
Request body(json)
是否输出agent信息,默认为true
UserID

string
true
Request body(json)
用户ID
响应 (app.MessageStreamResponse):
参数
类型
是否必填
说明
Data
string
false
EventStream(data: json)

Postman
python代码
备注
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/query_again' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "AppConversationID": "co6deaa1hp0kieia13bg",
    "MessageID": "01HTH3FGMYMSYDH8JYY3V7AGE9",
    "UserID": "321"
}'
def query_again(user_id: str, app_conversation_id: str, message_id: str):
    url = base_url + "query_again"
    headers = {'Apikey': api_key,
               'Content-Type': 'application/json',
               'Accept': 'text/event-stream'}
    data = {
        "AppConversationID": app_conversation_id,
        "MessageID": message_id,
        "UserID": user_id
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"网络请求失败: {e}")

    return response
只有流式
返回示例
{
event:text
data:data: {"event": "message_start", "task_id": "6b2f4720-a14e-413d-9783-024442a58e7d"}

event:text
data:data: {"event": "message", "task_id": "6b2f4720-a14e-413d-9783-024442a58e7d", "id": "01JDHDFNH1XMJG89SEP2F49HDV", "answer": "你", "created_at": 1732530134, "conversation_id": "01JDHDFNGYRB130PZSEDE8R70B"}
}

if __name__ == '__main__':
    try:
        uid = "321"
        app_conversation_id = "cv5c9rl93q03lmornb2g"
        message_id = "01JNR12H305AET4ZZ7TFT08MAN"

        resp = query_again(uid, app_conversation_id, message_id)
        start_time = time.time()
        task_id = None

        for line in resp.iter_lines(chunk_size=4):
            if line:  # 过滤掉空行
                line = line.decode("utf-8")
                if line.startswith("data:"):
                    data = line.strip("data:").strip()
                    if data:
                        try:
                            data = json.loads(data)
                            if "event" in data and data["event"] == "message":
                                print(data["answer"], end="")
                            if "task_id" in data:
                                task_id = data["task_id"]
                        except json.JSONDecodeError as e:
                            print(f"JSON 解析失败: {e}")
                        except KeyError as e:
                            print(f"返回数据缺少必要字段: {e}")

        print("\n")
        print(f"整体耗时：{time.time() - start_time}")

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
    except ValueError as e:
        print(f"API 返回结果异常: {e}")
    except Exception as e:
        print(f"未知错误: {e}")

重新生成回复V2
- 接口说明： 用于对话类聊天接口，重新生成回复（所有流式接口都是SSE），和QueryAgain区别是，QueryAgainV2返回结构更加规范。注意：最多支持10次重新生成。
  1. 流式返回：标准的SSE返回（区别于query_again,每个消息体里没有嵌套data字段）；
  2. 其他与QueryAgain完全一致
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. AppConversationID：会话ID，由CreateConversation接口生成；
  3. UserID：用户标识，用于定义终端用户的身份，方便检索、统计。 由开发者定义规则，需保证用户标识在应用内唯一。（长度：1-20）；
  4. MessageID：上轮对话返回的ID；
- response body参数说明：
  1. Data：SSE格式的输出；
Post /query_again_v2
请求 (app.QueryAgainRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header

应用key。http 请求头中设置 Apikey={{ ApiKey }}
AppConversationID
string
true
Request body(json)
应用侧对话ID
MessageID
string
true
Request body(json)
消息ID
UserID
string
true
Request body(json)
用户ID
响应 (app.MessageStreamResponse):
参数
类型
是否必填
说明
Data
string
false
EventStream(data: json)

Postman
python代码
备注
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/query_again_v2' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "AppConversationID": "co6deaa1hp0kieia13bg",
    "MessageID": "01HTH3FGMYMSYDH8JYY3V7AGE9",
    "UserID": "321"
}'
def query_again2(user_id: str, app_conversation_id: str, message_id: str):
    url = base_url + "query_again"
    headers = {'Apikey': api_key,
               'Content-Type': 'application/json',
               'Accept': 'text/event-stream'}
    data = {
        "AppConversationID": app_conversation_id,
        "MessageID": message_id,
        "UserID": user_id
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"网络请求失败: {e}")

    return response
只有流式
返回示例
{
event:text
data: {"event": "message_start", "task_id": "6b2f4720-a14e-413d-9783-024442a58e7d"}

event:text
data: {"event": "message", "task_id": "6b2f4720-a14e-413d-9783-024442a58e7d", "id": "01JDHDFNH1XMJG89SEP2F49HDV", "answer": "你", "created_at": 1732530134, "conversation_id": "01JDHDFNGYRB130PZSEDE8R70B"}
}
if __name__ == '__main__':
    try:
        uid = "321"
        app_conversation_id = "cv5c9rl93q03lmornb2g"
        message_id = "01JNR12H305AET4ZZ7TFT08MAN"

        resp = query_again2(uid, app_conversation_id, message_id)
        start_time = time.time()
        task_id = None

        for line in resp.iter_lines(chunk_size=4):
            if line:  # 过滤掉空行
                line = line.decode("utf-8")
                if line.startswith("data:"):
                    data = line.strip("data:").strip()
                    if data:
                        try:
                            data = json.loads(data)
                            if "event" in data and data["event"] == "message":
                                print(data["answer"], end="")
                            if "task_id" in data:
                                task_id = data["task_id"]
                        except json.JSONDecodeError as e:
                            print(f"JSON 解析失败: {e}")
                        except KeyError as e:
                            print(f"返回数据缺少必要字段: {e}")

        print("\n")
        print(f"整体耗时：{time.time() - start_time}")

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
    except ValueError as e:
        print(f"API 返回结果异常: {e}")
    except Exception as e:
        print(f"未知错误: {e}")

获取应用配置
- 接口说明： 获取应用配置。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. UserID：用户标识，用于定义终端用户的身份；
Post /get_app_config_preview
请求 (app.GetAppConfigPreviewRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
UserID
string
true
Request body(json)
用户ID，此接口不需要强校验用户ID
响应 (app.GetAppConfigPreviewResponse):
参数
类型
是否必填
说明
VariableConfigs
list[app.VariableConfig]
false
变量配置
Name
string
false
名称
OpenMessage
string
false
开场白文本
OpenQuery
list[string]
false
开场白问题
Icon
string
false
图标
Background
string
false
图标背景色
MessageTimes
i32
false
生成更多类似
SuggestEnabled
bool
false
会话建议
Image
string
false
自定义图片
AgentMode
string
false
智能体模式：Single：单Agent模式；Multi:多Agent模式
AgentNodeSuggestEnabledMap
map[string, bool]
false
多Agent模式下是否启用问题建议，map<节点ID: 是否启用问题建议>。节点 ID为多 agent 模式下每个智能体对应的节点 ID
VoiceConfig
app.VoiceConfig

语音配置
WorkspaceID
string
false
智能体所属工作空间 ID
BaseResp
base.BaseResp
false


Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/get_app_config_preview' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "UserID": "321"
}'

普通接口调用，暂不提供
返回示例
{
    "Name": "dd",
    "OpenMessage": "",
    "OpenQuery": [],
    "Icon": "MobilePhone",
    "Background": "background_1",
    "MessageTimes": 0,
    "SuggestEnabled": false,
    "Image": "",
    "AgentMode": "Single",
    "AgentNodeSuggestEnabledMap": {},
    "VoiceConfig": {},
    "BaseResp": null
}

普通接口调用，暂不提供
获取对话列表
- 接口说明：获取对话列表，由CreateConversation接口生成的会话列表。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. UserID：用户标识，用于定义终端用户的身份；
Post /get_conversation_list
请求 (app.GetConversationListRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
UserID
string
true
Request body(json)
用户ID
响应 (app.GetConversationListResponse):
参数
类型
是否必填
说明
ConversationList
list[app.AppConversationBrief]
false
对话列表
BaseResp
base.BaseResp
false


Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/get_conversation_list' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "UserID": "321"
}'

普通接口调用，暂不提供
返回示例
{
    "ConversationList": [
        {
            "AppConversationID": "ctbat448v1t2jaap2kag",
            "ConversationName": "新的会话",
            "CreateTime": "2024-12-09 16:47:12",
            "LastChatTime": "2024-12-09 18:47:05",
            "EmptyConversation": false
        }
    ],
    "BaseResp": null
}

普通接口调用，暂不提供

获取对话变量输入
- 接口说明：获取对话变量输入，变量在平台应用编排界面设置。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}。
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. AppConversationID：会话ID，由CreateConversation接口生成；
  3. UserID：用户标识，用于定义终端用户的身份；
Post /get_conversation_inputs
请求 (app.GetConversationInputsRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
AppConversationID
string
true
Request body(json)
应用侧会话ID

UserID
string
true
Request body(json)
用户ID
响应 (app.GetConversationInputsResponse):
参数
类型
是否必填
说明
Inputs
map[string, string]
false
变量输入
BaseResp
base.BaseResp
false


Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/get_conversation_inputs' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "AppKey": "co6dd4i1hp0kieia137g",
    "UserID": "321"
}'

普通接口调用，暂不提供

返回示例
{
    "Inputs": {
      "var": "val"
    },
    "BaseResp": null
}

普通接口调用，暂不提供


更新会话
- 接口说明：更新会话，包括会话名称、变量。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. AppConversationID：会话ID，由CreateConversation接口生成；
  3. ConversationName：会话名称；
  4. Inputs：变量输入；
  5. UserID：用户标识，用于定义终端用户的身份；
Post /update_conversation
请求 (app.UpdateConversationRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
AppConversationID
string
true
Request body(json)
应用侧会话ID
ConversationName
string
false
Request body(json)
修改会话名称
Inputs
map[string, string]
false
Request body(json)
修改变量输入
UserID
string
true
Request body(json)
用户ID
响应 (common.EmptyResponse):
参数
类型
是否必填
说明

Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/update_conversation' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "AppConversationID": "co6deaa1hp0kieia13bg",
    "ConversationName": "更新会话",
    "Inputs": {
        "var": "variable"
    },
    "UserID": "321"
}'

普通接口调用，暂不提供
返回示例
{}

普通接口调用，暂不提供

删除会话
- 接口说明：删除会话。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}。
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. AppConversationID：会话ID，由CreateConversation接口生成；
  3. UserID：用户标识，用于定义终端用户的身份；
Post /delete_conversation
请求 (app.DeleteConversationRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
AppConversationID
string
true
Request body(json)
应用侧会话ID
UserID
string
true
Request body(json)
用户ID
响应 (common.EmptyResponse):
参数
类型
是否必填
说明

Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/delete_conversation' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "AppConversationID": "co6deaa1hp0kieia13bg",
    "UserID": "321"
}
'

普通接口调用，暂不提供
返回示例
{}

普通接口调用，暂不提供
停止响应
- 接口说明：停止响应，在聊天类接口输出过程中，强制停止。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. TaskID：任务ID（其实为消息 ID），对话聊天接口接口生成；
  3. UserID：用户标识，用于定义终端用户的身份；
Post /stop_message
请求 (app.StopMessageRequest):
参数
类型
是否必填
参数作用域
说明
TaskID
string
true
Request body(json)
消息ID（请使用MessageID，1.5.0及之后版本将去掉TaskID参数）
MessageID
string
true
Request body(json)
消息ID
任务 ID 和 消息 ID 必填其一
AppKey

string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
UserID
string
true
Request body(json)
用户ID
响应 (common.EmptyResponse):
参数
类型
是否必填
说明

Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/stop_message' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "AppKey": "co6dd4i1hp0kieia137g",
    "MessageID": "be80e08f-bb46-46c5-a687-15824a7c4107",
    "UserID": "321"
}
'

普通接口调用，暂不提供
返回示例
{}

普通接口调用，暂不提供
清除会话消息
- 接口说明：在聊天类智能体中，清楚指定会话下消息。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. AppConversationID：会话ID，由CreateConversation 接口生成；
  3. UserID：用户标识，用于定义终端用户的身份；
Post /clear_message
请求 (app.ClearMessageRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
AppConversationID
string
true
Request body(json)
应用侧会话ID
UserID
string
true
Request body(json)
用户ID
响应 (common.EmptyResponse):
参数
类型
是否必填
说明

Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/clear_message' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "AppConversationID": "ct4m7gmoc93a9ns2sngg",
    "UserID": "321"
}
'

普通接口调用，暂不提供

返回示例
{}

普通接口调用，暂不提供

获取会话历史消息列表
- 接口说明：获取会话历史消息列表，对话轮数的消息。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}。
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. AppConversationID：会话ID，由CreateConversation 接口生成；
  3. Limit：限制数量；
  4. UserID：用户标识，用于定义终端用户的身份；
Post /get_conversation_messages
请求 (app.GetConversationMessagesRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
AppConversationID
string
true
Request body(json)
应用侧会话ID
Limit
i32
true
Request body(json)
限制数量返回条数。1-100
UserID
string
true
Request body(json)
用户ID
响应 (app.GetConversationMessagesResponse):
参数
类型
是否必填
说明
Messages
list[app.ChatMessageInfo]
false

对话消息列表
BaseResp
base.BaseResp
false


Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/get_conversation_messages' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "AppKey": "co6dd4i1hp0kieia137g",
    "Limit": 100,
    "AppConversationID": "co6deaa1hp0kieia13bg",
    "UserID": "321"
}'

普通接口调用，暂不提供
返回示例
{
    "Messages": [
        {
            "ConversationID": "01JENGF8YA4NWT8AHP0WD9PTT6",
            "QueryID": "ctbcla1pgge5cea2drig",
            "Query": "北京天气",
            "AnswerInfo": {
                "Answer": "您想知道最近北京的天气情况吗？我可以帮您查询最新的天气信息并提供给您。\n\n根据今天的天气预报，北京的天气状况如下：\n- 日期：2023年11月28日\n- 温度：5℃到15℃\n- 降水概率：60%\n- 风速：3-4级\n\n请注意这些信息可能随时更新，保暖的同时出门记得携带雨具。您还可以通过网站、手机应用或者智能助手来查看更详细的天气信息。需要更具体的天气信息吗？比如特定时间的天气或者是未来几天的天气预报？",
                "MessageID": "01JENGF8YABMJBFG5YV1RB1J27",
                "CreatedTime": 1733741225,
                "TaskID": "01JENGF8YABMJBFG5YV1RB1J27",
                "Like": 0,
                "TotalTokens": 125,
                "Latency": 9.897,
                "TracingJsonStr": "",
                "RetrieverResource": false
            },
            "OtherAnswers": [],
            "Inputs": {}
        }
    ],
    "BaseResp": null
}

普通接口调用，暂不提供
获取消息详情
- 接口说明：获取消息详情，包括消息的返回内容，消耗的token等。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. MessageID：消息ID，由聊天接口返回；
  3. UserID：用户标识，用于定义终端用户的身份；
Post /get_message_info
请求 (app.GetMessageInfoRequest):
参数
类型
是否必填
参数作用域
说明
MessageID
string
true
Request body(json)
消息ID
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
UserID
string
true
Request body(json)
用户ID
响应 (app.GetMessageInfoResponse):
参数
类型
是否必填
说明
MessageInfo
app.ChatMessageInfo
false
消息详情
BaseResp
base.BaseResp
false


Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/get_message_info' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "AppKey": "co6dd4i1hp0kieia137g",
    "MessageID": "01HTH35SQHX8WGS006NTWVBSN7",
    "UserID": "321"
}'

普通接口调用，暂不提供

返回示例
{
    "MessageInfo": {
        "ConversationID": "01JENGF8YA4NWT8AHP0WD9PTT6",
        "QueryID": "ctbcla1pgge5cea2drig",
        "Query": "北京天气",
        "AnswerInfo": {
            "Answer": "您想知道最近北京的天气情况吗？我可以帮您查询最新的天气信息并提供给您。\n\n根据今天的天气预报，北京的天气状况如下：\n- 日期：2023年11月28日\n- 温度：5℃到15℃\n- 降水概率：60%\n- 风速：3-4级\n\n请注意这些信息可能随时更新，保暖的同时出门记得携带雨具。您还可以通过网站、手机应用或者智能助手来查看更详细的天气信息。需要更具体的天气信息吗？比如特定时间的天气或者是未来几天的天气预报？",
            "MessageID": "01JENGF8YABMJBFG5YV1RB1J27",
            "CreatedTime": 1733741225,
            "TaskID": "01JENGF8YABMJBFG5YV1RB1J27",
            "Like": 0,
            "TotalTokens": 125,
            "Latency": 9.897,
            "TracingJsonStr": "",
            "RetrieverResource": false
        },
        "OtherAnswers": [],
        "Inputs": null
    },
    "BaseResp": null
}

这里作为提取『引用归属』的代码示例：（特别鸣谢@黄冬 ）
def get_message_info(self, message_id):
        """
        根据消息 ID 获取消息的详细信息，特别是文档相关信息。
        参数:
        - message_id (str): 消息的 ID。
        返回:
        dict: 包含消息详细信息的字典，如果出现错误则返回 None。
        """
        url = base_url+"/api/proxy/api/v1/get_message_info"
        headers = {"Apikey": self.api_key, "Content-Type": "application/json"}
        data = {"MessageID": message_id, "UserID": self.user_id}
        try:
            response = requests.get(url, headers=headers, json=data)
            response.raise_for_status()
           
            result = response.json()['MessageInfo']['AnswerInfo']['TracingJsonStr']
           
            result = json.loads(result)
            # 遍历解析后的结果列表
            for item in result:
                # 找到知识检索结束的事件
                if item["event"] == "knowledge_retrieve_end":
                    # 遍历该事件中文档输出列表
                    for doc in item["docs"]["outputList"]:
                        # 提取文档的名称
                        document_name = doc["metadata"]["document_name"]
                        # 提取文档的 OBS 链接地址
                        document_obs_url = doc["metadata"]["document_obs_url"]
                        # 打印文档名称
                        print(f"文档名称: {document_name}")
                        s3_url = f"https://{self.host}/api/proxy/down?Action=Download&Version=2022-01-01&Path={document_obs_url}&IsAnonymous=true"
                        # 打印文档的 OBS 链接地址
                        print(f"OBS 链接地址: {s3_url}")
                        # 打印分隔线，用于区分不同文档信息
                        print("-" * 50)
            # 返回解析后的结果
            return result
        except requests.RequestException as e:
            # 处理请求过程中出现的异常，打印错误信息
            print(f"Request error: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            # 处理 JSON 解析或键值提取过程中出现的异常，打印错误信息
            print(f"Error parsing response: {e}")
        # 如果出现异常，返回 None
        return None
删除消息
- 接口说明：删除消息，用户只能删除自己对话的消息，删除后，消息不会出现在对话上下文
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. MessageID：消息ID，由聊天接口返回；
  3. QueryID：询问ID，由get_message_info返回（重新生成时，通过query_id来归纳一个消息组）；
  4. UserID：用户标识，用于定义终端用户的身份；
Post /delete_message
请求 (app.DeleteMessageRequest):
参数
类型
是否必填
参数作用域
说明
MessageID
string
false
Request body(json)
消息ID,传消息ID不能同时传询问ID
QueryID
string
false
Request body(json)
询问ID,传询问ID不能同时传消息ID
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
UserID
string
true
Request body(json)
用户ID
响应 (common.EmptyResponse):
参数
类型
是否必填
说明

Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/delete_message' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "AppKey": "co6dd4i1hp0kieia137g",
    "MessageID": "01HTH35SQHX8WGS006NTWVBSN7",
    "QueryID": "ed6d9dje447dhtf4a74hds",
    "UserID": "321"
}'

普通接口调用，暂不提供

返回示例
{}

普通接口调用，没有提供的价值，如不会写可复制postman请求让大模型写

回答反馈评价（赞或踩）
- 接口说明：
  1. 聊天返回结果反馈评价（赞或踩）。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. MessageID：消息ID，由聊天接口返回；
  3. LikeType：反馈类型；
  4. UserID：用户标识，用于定义终端用户的身份；
Post /feedback
请求 (app.FeedbackRequest):
参数
类型
是否必填
参数作用域
说明
MessageID
string
true
Request body(json)
消息ID
LikeType
common.LikeType
true
Request body(json)
反馈类型
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
UserID
string
true
Request body(json)
用户ID
响应 (common.EmptyResponse):
参数
类型
是否必填
说明

Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/feedback' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "AppKey": "co6dd4i1hp0kieia137g",
    "MessageID": "01HTH35SQHX8WGS006NTWVBSN7",
    "LikeType": 1,
    "UserID": "321"
}'

普通接口调用，暂不提供
返回示例
{}

普通接口调用，暂不提供

多组回答时，设置某个回答为默认使用的回答
- 接口说明： 多组回答时，设置某个回答为默认使用的回答。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. MessageID：消息ID，由聊天接口返回；
  3. UserID：用户标识，用于定义终端用户的身份；
Post /set_message_answer_used
请求 (app.SetMessageAnswerUsedRequest):
参数
类型
是否必填
参数作用域
说明
MessageID
string
true
Request body(json)
消息ID
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
UserID
string
true
Request body(json)
用户ID
响应 (common.EmptyResponse):
参数
类型
是否必填
说明

Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/set_message_answer_used' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "AppKey": "co6dd4i1hp0kieia137g",
    "MessageID": "01HTH35SQHX8WGS006NTWVBSN7",
    "UserID": "321"
}'

普通接口调用，暂不提供

返回示例
{}

普通接口调用，暂不提供

获取提问建议
- 接口说明：聊天类接口专用，用于获取提问建议。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. MessageID：消息ID，由聊天接口返回；
  3. UserID：用户标识，用于定义终端用户的身份；
Post /get_suggested_questions
请求 (app.GetSuggestedQuestionsRequest):
参数
类型
是否必填
参数作用域
说明
MessageID
string
true
Request body(json)
消息ID
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
UserID
string
true
Request body(json)
用户ID
响应 (app.GetSuggestedQuestionsResponse):
参数
类型
是否必填
说明
SuggestedQuestions
list[string]
false
推荐列表
BaseResp
base.BaseResp
false


Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/get_suggested_questions' \
--header 'Apikey: co6dd4i1hp0kieia137g' \
--header 'Content-Type: application/json' \
--data '{
    "AppKey": "co6dd4i1hp0kieia137g",
    "MessageID": "01HTH35SQHX8WGS006NTWVBSN7",
    "UserID": "321"
}'

普通接口调用，暂不提供

返回示例
{
    "SuggestedQuestions": [
        "明天天气如何？",
        "未来一周天气？",
        "现在温度多少？"
    ],
    "BaseResp": null
}

普通接口调用，暂不提供
测试运行工作流(异步)
- 接口说明：应用类型为流程编排型时，测试运行工作流(异步)。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. InputData：输入json参数；
  3. UserID：用户标识，用于定义终端用户的身份；
Post /run_app_workflow
请求 (app.RunAppWorkflowRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header

应用key。http 请求头中设置 Apikey={{ ApiKey }}
InputData

string
true
Request body(json)

输入json参数，工作流开始节点指定参数入参， json类型字符串
NoDebug
bool
false
Request body(json)
是否非debug模式，建议传true（非debug模式下只会返回失败的节点信息，速度更快）；如果传false，会返回全量的节点信息
UserID
string
true
Request body(json)
用户ID
响应 (workflow.SubmitWorkflowDebugResponse):
参数
类型
是否必填
说明
runId
string
false
异步运行任务 ID，用于 query_run_app_process 接口进行状态轮寻

Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/run_app_workflow' \
--header 'Apikey: cnndp5ubmcq0s7g3s8og' \
--header 'Content-Type: application/json' \
--data '{
    "InputData": "{\"content\":\"我想上天\"}",
    "UserID": "321"
}'

def run_workflow(text: str, max_retries: int = 3) -> Any | None:
    """
    执行工作流并返回 runId

    参数:
        text (str): 输入文本内容
        max_retries (int): 最大重试次数，默认3次

    返回:
        str: 成功返回 runId，失败返回 None
    """
    # 验证输入数据
    if not text.strip():
        raise ValueError("输入文本不能为空")

    API_URL = base_url+"run_app_workflow"
    HEADERS = {
        "Content-Type": "application/json",
        "Apikey": API_KEY
    }
    BASE_DATA = {
        "UserID": USER_ID,
        "InputData": json.dumps({"input": text})
    }

    result = make_request(API_URL, HEADERS, BASE_DATA, max_retries)

    if result and 'runId' in result:
        return result['runId']
    return None

返回示例
{
    "runId": "c4213b25cd614424ade0009ceb445f36"
}


测试运行工作流(同步)
- 接口说明：应用类型为流程编排型时，测试运行工作流(同步)。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. InputData：输入json参数；
  3. UserID：用户标识，用于定义终端用户的身份；
Post /sync_run_app_workflow
请求 (app.SyncRunAppWorkflowRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
InputData

string

true
Request body(json)
输入json参数，工作流开始节点指定参数入参， json类型字符串
NoDebug

bool

false
Request body(json)
是否非debug模式，建议传true（非debug模式下只会返回失败的节点信息，速度更快）；如果传false，会返回全量的节点信息
UserID
string
true
Request body(json)
用户ID
响应 (workflow.RuntimeFlowRunResp):
参数
类型
是否必填
说明
runId
string
false
工作流运行任务ID
status
string
false
运行状态
nodes
map[string, workflow.Node]
false
节点信息
steps
list[string]
false
已运行的节点
code
i32
false
code
message
string
false
运行信息
costMs
i64
false
运行花费时间, ms
output
string
false
最终运行结果


Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/sync_run_app_workflow' \
--header 'Apikey: cnndp5ubmcq0s7g3s8og' \
--header 'Content-Type: application/json' \
--data '{
    "InputData": "{\"content\":\"我想上天\"}",
    "UserID": "321"
}'

def run_workflow(text: str, max_retries: int = 3) -> Any | None:
    """
    执行工作流并返回 runId

    参数:
        text (str): 输入文本内容
        max_retries (int): 最大重试次数，默认3次

    返回:
        str: 成功返回 runId，失败返回 None
    """
    # 验证输入数据
    if not text.strip():
        raise ValueError("输入文本不能为空")

    API_URL = base_url+"sync_run_app_workflow"
    HEADERS = {
        "Content-Type": "application/json",
        "Apikey": API_KEY
    }
    BASE_DATA = {
        "UserID": USER_ID,
        "InputData": json.dumps({"input": text})
    }

    result = make_request(API_URL, HEADERS, BASE_DATA, max_retries)

    if result and 'runId' in result:
        return result['runId']
    return None

返回示例
{
    "status": "success",
    "nodes": {
        "ctbe233ml3fgfs3u2skg": {
            "input": "{\"dd\":\"你好\"}",
            "output": "{\"dd\":\"你好\"}",
            "status": "success",
            "message": "",
            "costMs": 3,
            "costToken": 0,
            "nodeType": "start"
        },
        "ctbe233ml3fgfs3u2sl0": {
            "input": "{\"output\":\"你好\"}",
            "output": "{\"output\":\"你好\"}",
            "status": "success",
            "message": "",
            "costMs": 8,
            "costToken": 0,
            "nodeType": "end"
        }
    },
    "output": "this is output content",
    "steps": null,
    "costMs": 16
}



查询测试运行工作流运行进展(异步)
- 接口说明：应用类型为流程编排型时，查询测试运行工作流运行进展(异步)。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. RunID：运行ID；
Post /query_run_app_process
请求 (app.QueryRunAppProcessRequest):
参数
类型
是否必填
参数作用域
说明
RunID

string
true
Request body(json)
工作流运行任务ID
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
UserID
string
true
Request body(json)
用户ID
响应 (workflow.RuntimeFlowRunResp):
参数
类型
是否必填
说明
runId
string
false
工作流运行任务ID
status
string
false
运行状态
nodes
map[string, workflow.Node]
false
节点信息
steps
list[string]
false
已运行的节点
code
i32
false
code
message
string
false
运行信息
costMs
i64
false
运行花费时间, ms
output
string
false
最终运行结果

Postman
python代码
请求示例
curl --location '{{apiurl}}/api/proxy/api/v1/query_run_app_process' \
--header 'Apikey: cnndp5ubmcq0s7g3s8og' \
--header 'Content-Type: application/json' \
--data '{
    "RunID": "4deecd7c453a46febfe6d84b179e2ed9",
    "UserID": "321",
    "AppKey": "cnndp5ubmcq0s7g3s8og"
}'

轮询结果，特别鸣谢@黄冬 
def get_process(run_id, max_retries=10):
    query_y_run_app_process_url = base_url+"query_run_app_process"
    data = {
        "UserID": USER_ID,
        "RunID": run_id
    }
    headers = {"Content-Type": "application/json", "Apikey": API_KEY}

    retry_count = 0
    while True:
        result = make_request(query_y_run_app_process_url, headers, data, 1)
        if result:
            if result.get('status') == "success":
                print(result)
                return result
            print(result)

        # 重试逻辑
        retry_count += 1
        if retry_count >= max_retries:
            print("Max retries exceeded")
            return None

        # 指数退避等待（2, 4, 8, 16...秒）
        time.sleep(min(2 ** retry_count, 30))  # 最大间隔30秒

返回示例
{
    "status": "success",
    "nodes": {
        "ctbe233ml3fgfs3u2skg": {
            "input": "{\"dd\":\"你好\"}",
            "output": "{\"dd\":\"你好\"}",
            "status": "success",
            "message": "",
            "costMs": 3,
            "costToken": 0,
            "nodeType": "start"
        },
        "ctbe233ml3fgfs3u2sl0": {
            "input": "{\"output\":\"你好\"}",
            "output": "{\"output\":\"你好\"}",
            "status": "success",
            "message": "",
            "costMs": 8,
            "costToken": 0,
            "nodeType": "end"
        }
    },
    "output": "this is output content",
    "steps": null,
    "costMs": 16
}



查询用户oauth2登录信息的接口
- 接口说明：查询用户oauth2登录信息的接口。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
Post /list_oauth2_token
请求 (common.EmptyRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
UserID
string
true
Request body(json)
用户ID
响应 (plugin.ListOauth2TokenResp):
参数
类型
是否必填
说明
Total
i64
true
列表总数
Items
list[plugin.Oauth2TokenItem]
true
Oauth2登录信息列表
请求示例：
curl --location '{{apiurl}}/api/proxy/api/v1/list_oauth2_token' \
--header 'Apikey: cnndp5ubmcq0s7g3s8og' \
--header 'Content-Type: application/json' \
--data '{
    "UserID": "321"
}'
触发事件触发器
- 接口说明：触发发布后的智能体中事件触发器执行工作。
- 请求header说明：
  1. 请求header需要加上Authorization=Bearer {{ WebHookBearerToken }}；WebHookBearToken 为事件触发器中配置的 bearer token.
- body参数说明：无固定（json）。根据具体的事件触发器中设定的请求参数。
Post /trigger/webhook?key={{WebHookKey}}
- query 参数说明:
  - WebHookKey: 智能体中配置的事件触发器分配的唯一标识。
请求 :
参数
类型
是否必填
参数作用域
说明
Authorization
string
是
Request header
事件触发器 webhook web token, 创建智能体事件触发器时获取。
Authorization=Bearer {{ WebHookBearerToken }}
无固定
object
否
Request body(json)
**根据具体的事件触发器中设定的请求参数
响应 (plugin.EmptyResponse):
参数
类型
是否必填
说明




请求示例：
curl --location '{{apiurl}}/api/proxy/api/v1/trigger/webhook?key={{WebHookKey}}' \
--header 'Authorization: Bearer {{WebHookBearerToken}}' \
--header 'Content-Type: application/json' \
--data '{
    "a": "hnf"
}'

继续对话
- 接口说明：对话过程用，页面关了，再次打开页面，如该对话还没结束，可以继续用这个接口获取流式对话数据。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. MessageID：需要继续对话的消息ID；
  3. RespDataStandard： 是否标准输出;
  4. UserID：用户标识，用于定义终端用户的身份；
Post /chat_continue
请求 (app.ChatContinueRequest):
参数
类型
是否必填
参数作用域
说明
MessageID
string
false
Request body(json)
消息ID,传消息ID不能同时传询问ID
RespDataStandard
bool
false
Request body(json)
是否标准输出, 兼容非标准 sse 输出，建议打开
请求示例：
curl --location --request POST 'http://33.234.30.131:32300/api/proxy/api/v1/chat_continue' \
--header 'Apikey: d1dnchn77meus8cut020' \
--header 'Content-Type: application/json' \
--data-raw '{
    "MessageID": "01JYJKP7JHK25F2VT88480J8BF",
    "RespDataStandard": true,
    "UserID": "321"
}'
响应 (app.MessageStreamResponse):
参数
类型
是否必填
说明
Data
string
false
EventStream(data: json)
响应示例：
event:text
data:{"event":"message_start","task_id":"01JYJKP7JHK25F2VT88480J8BF","id":"01JYJKP7JHK25F2VT88480J8BF","conversation_id":"01JYJKP7DQE0VJAQE3XBGAAS8B","answer":"","created_at":0}

event:text
data:{"event":"message_output_start","task_id":"01JYJKP7JHK25F2VT88480J8BF","id":"01JYJKP7JHK25F2VT88480J8BF","conversation_id":"01JYJKP7DQE0VJAQE3XBGAAS8B","answer":"","created_at":0}

event:text
data:{"event":"message","task_id":"01JYJKP7JHK25F2VT88480J8BF","id":"01JYJKP7JHK25F2VT88480J8BF","conversation_id":"01JYJKP7DQE0VJAQE3XBGAAS8B","answer":"你好呀！请你详细描述一下角色的相关信息，包括角色概述、主要职责、工作目标等内容，这样我就能按照要求完成输出啦。 ","created_at":1750823804}

event:text
data:{"event":"message_output_end","task_id":"01JYJKP7JHK25F2VT88480J8BF","id":"01JYJKP7JHK25F2VT88480J8BF","conversation_id":"01JYJKP7DQE0VJAQE3XBGAAS8B","answer":"","created_at":0}

event:text
data:{"event":"message_cost","task_id":"01JYJKP7JHK25F2VT88480J8BF","id":"01JYJKP7JHK25F2VT88480J8BF","conversation_id":"01JYJKP7DQE0VJAQE3XBGAAS8B","answer":"","created_at":0,"latency":1.79,"input_tokens":175,"output_tokens":36,"start_time_first_resp":1750823805390,"latency_first_resp":891}

event:text
data:{"event":"message_end","task_id":"01JYJKP7JHK25F2VT88480J8BF","id":"01JYJKP7JHK25F2VT88480J8BF","conversation_id":"01JYJKP7DQE0VJAQE3XBGAAS8B","answer":"","created_at":0}
获取长期记忆列表
- 接口说明：获取长期记忆列表
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. ListOpt：分页信息；
  3. Filter： 列表过滤条件;
  4. UserID：用户标识，用于定义终端用户的身份；
Post /list_long_memory
请求 (app.ListLongMemoryOpenRequest):
参数
类型
是否必填
参数作用域
说明
ListOpt
common.ListOption

false
Request body(json)
分页配置
Filter

app.ListLongMemoryFilter
false
Request body(json)
筛选条件

请求示例：
curl --location --request POST 'http://33.234.30.131:32300/api/proxy/api/v1/list_long_memory' \
--header 'Apikey: d1dr86v77meus8cuu7o0' \
--header 'Content-Type: application/json' \
--data-raw '{
    "ListOpt": {
        "Sort": [
            {
                "SortField": "created_at",
                "SortOrder": "desc"
            }
        ],
        "PageNumber": 1,
        "PageSize": 10
    },
    "Filter": {
        "StartTime": "2024-06-25T00:00:00Z",
        "EndTime": "2025-06-26T00:00:00Z",
        "Keyword": "喜欢"
    },
    "UserID": "321"
}'
响应 (app.ListLongMemoryResponse):
参数
类型
是否必填
说明
Items
list<app.LongMemoryItem>
false
记忆列表
长期记忆在 item 中获取
Total
int
false
总数
BaseResp
base.BaseResp
false
基础相应信息
更新长期记忆
- 接口说明：更新长期记忆。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. MemoryID：长期记忆ID；
  3. Memory： 长期记忆内容;
  4. UserID：用户标识，用于定义终端用户的身份；
Post /update_long_memory
请求 (app.UpdateLongMemoryOpenRequest):
参数
类型
是否必填
参数作用域
说明
MemoryID
string

true
Request body(json)
记忆ID
Memory

string
true
Request body(json)
记忆内容

请求示例：
curl --location --request POST 'http://33.234.30.131:32300/api/proxy/api/v1/update_long_memory' \
--header 'Apikey: d1dr86v77meus8cuu7o0' \
--header 'Content-Type: application/json' \
--data-raw '{
   "AppKey": "d1dr86v77meus8cuu7o0",
   "MemoryID": "d1dsihvclq3pv8acs5sg",
   "Memory": "我家在北京、我喜欢运动、我会打网球、我毕业于清华大学",
   "UserID": "321"
}'
响应 (common.EmptyResponse):
参数
类型
是否必填
说明
删除长期记忆
- 接口说明：删除长期记忆。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. MemoryIDs：长期记忆ID列表；
  3. UserID：用户标识，用于定义终端用户的身份；
Post /delete_long_memory
请求 (app.DeleteLongMemoryOpenRequest):
参数
类型
是否必填
参数作用域
说明
MemoryIDs
list<string>

true
Request body(json)
记忆ID列表
请求示例：
curl --location --request POST 'http://33.234.30.131:32300/api/proxy/api/v1/delete_long_memory' \
--header 'Apikey: d1dr86v77meus8cuu7o0' \
--header 'Content-Type: application/json' \
--data-raw '{
    "AppKey": "d1dr86v77meus8cuu7o0",
    "MemoryIDs": [
        "d1dsihvclq3pv8acs5sg",
        "d1dsi9nclq3pv8acs5r0"
    ],
    "UserID": "321"
}'
响应 (common.EmptyResponse):
参数
类型
是否必填
说明
清除长期记忆
- 接口说明：删除长期记忆。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. UserID：用户标识，用于定义终端用户的身份；
Post /clear_long_memory
请求 (app.ClearLongMemoryOpenRequest):
参数
类型
是否必填
参数作用域
说明
请求示例：
curl --location --request POST 'http://33.234.30.131:32300/api/proxy/api/v1/clear_long_memory' \
--header 'Apikey: d1dr86v77meus8cuu7o0' \
--header 'Content-Type: application/json' \
--data-raw '{
    "AppKey": "d1dr86v77meus8cuu7o0",
    "UserID": "321"
}'
响应 (common.EmptyResponse):
参数
类型
是否必填
说明
异步恢复工作流运行
- 接口说明：异步恢复工作流执行, 用于信息收集节点的回调接口。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. RunId: 工作流执行 ID, 标识工作流一次执行操作；
  2. UserType：用户类型，用户类型（只有租户管理员鉴权模式下，该字段有效，支持App和IAM，不传则默认应用自定义用户App）
  3. Input：输入信息 json encode 信息收集回调使用 {"query": "恢复内容"}
  4. Debug：是否非debug模式，建议传true（非debug模式下只会返回失败的节点信息，速度更快）；如果传false，会返回全量的节点信息
Post /async_resume_app_workflow
请求 (openapi.AsyncResumeAppWorkflowReq):
参数
类型
是否必填
参数作用域
说明
RunId
string
true
Request body(json)
工作流执行 ID, 标识工作流一次执行操作
UserType
common.UserType

false
Request body(json)
用户类型，用户类型（只有租户管理员鉴权模式下，该字段有效，支持App和IAM，不传则默认应用自定义用户App）
Input
string
true
Request body(json)
输入信息 json encode 信息收集回调使用 {"query": "恢复内容"}
Debug
bool
false
Request body(json)
是否非debug模式，建议传true（非debug模式下只会返回失败的节点信息，速度更快）；如果传false，会返回全量的节点信息
请求示例：
curl --location --request POST 'http://33.234.30.131:32300/api/proxy/api/v1/async_resume_app_workflow' \
--header 'Apikey: d1h1aef101hc35himnqg' \
--header 'Accept-Charset: application/json' \
--header 'Content-Type: application/json' \
--data-raw '{
    "RunId": "031b75bf8c804254b312e5358a5ed080",
    "UserType": "App",
    "Input": "{\"query\": \"我叫小明\"}",
    "Debug": true,
    "UserID": "321"
}'
响应 (common.EmptyResponse):
参数
类型
是否必填
说明
置顶会话
- 接口说明：置顶会话。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. AppConversationID：会话ID，由CreateConversation接口生成；
  3. UserID：用户标识，用于定义终端用户的身份；
Post /set_conversation_top
请求 (app.SetConversationTopRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
UserID
string
true
Request body(json)
用户ID
AppConversationID
string
true
Request body(json)
App 侧会话 ID
请求示例：
curl --location --request POST 'http://33.234.30.131:32300/api/proxy/api/v1/set_conversation_top' \
--header 'Apikey: d1dr86v77meus8cuu7o0' \
--header 'Content-Type: application/json' \
--data-raw '{
    "AppKey": "d1dr86v77meus8cuu7o0", 
    "UserID": "321",          
    "AppConversationID": "d1h3fn8lara1ne0b3h60" 
}'
响应 (common.EmptyResponse):
参数
类型
是否必填
说明
取消会话置顶
- 接口说明：取消置顶会话。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. AppConversationID：会话ID，由CreateConversation接口生成；
  3. UserID：用户标识，用于定义终端用户的身份；
Post /cancel_conversation_top
请求 (app.CancelConversationTopRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
UserID
string
true
Request body(json)
用户ID
AppConversationID
string
true
Request body(json)
App 侧会话 ID
请求示例：
curl --location --request POST 'http://33.234.30.131:32300/api/proxy/api/v1/cancel_conversation_top' \
--header 'Apikey: d1dr86v77meus8cuu7o0' \
--header 'Content-Type: application/json' \
--data-raw '{
    "AppKey": "d1dr86v77meus8cuu7o0", 
    "UserID": "321",          
    "AppConversationID": "d1h3fn8lara1ne0b3h60" 
}'
响应 (common.EmptyResponse):
参数
类型
是否必填
说明
查询智能体技能工具异步任务
- 接口说明：查询智能体中技能工具（工作流，插件等。目前仅支持工作流）在对话工程中发起的异步任务。
- 请求header说明：
  1. 请求header需要加上Apikey={{ ApiKey }}；
- body参数说明：
  1. AppKey：赋值为{{ ApiKey }}（值同header的Apikey）；
  2. AppConversationID：会话ID，由CreateConversation接口生成；
  3. TaskIDs：任务 ID 列表。任务 ID ：对话接口返回的 data（sse） 数据中，event=Interrupted && interrupted_type=async_task 的 task_id。
  4. UserID：用户标识，用于定义终端用户的身份；
Post /query_skill_async_task
请求 (app.QueryAppSkillAsyncTaskOpenRequest):
参数
类型
是否必填
参数作用域
说明
AppKey
string
false
Request header
应用key。http 请求头中设置 Apikey={{ ApiKey }}
UserID
string
true
Request body(json)
用户ID
AppConversationID
string
true
Request body(json)
App 侧会话 ID
TaskIDs

list<string>
true
Request body(json)
任务 ID 列表。任务 ID ：对话接口返回的 data（sse） 事件数据中，event=Interrupted && interrupted_type=async_task 的事件的 task_id。
当产生该事件和该类型的事件任务时，通过 task_id 查询异步任务状态。
[图片]

请求示例：
curl --location --request POST 'http://33.234.30.131:32300/api/proxy/api/v1/query_skill_async_task' \
--header 'Apikey: d1h4gvv101hc35hin160' \
--header 'Content-Type: application/json' \
--data-raw '{
    "AppKey":"d1h4gvv101hc35hin160",
    "AppConversationID": "d1h4s8glara1ne0b3hf0",
    "TaskIDs":["01JZ002Q40JHZ698JBGYEPHNEW"],
    "UserID":"321"
}'
响应 (app.QueryAppSkillAsyncTaskResponse):
参数
类型
是否必填
说明
Infos
list<app.AppSkillAsyncTaskInfo>
false
工具异步任务信息

结构体定义
app.AppConversationBrief
说明:
参数
类型
是否必填
说明
AppConversationID
string
false
应用侧会话ID
ConversationName
string
false
会话名称
app.ChatMessageInfo
说明:
参数
类型
是否必填
说明
ConversationID
string
false
会话ID
QueryID
string
false
询问ID
Query
string
false
询问内容
AnswerInfo
app.MessageAnswerInfo
false
回答信息
OtherAnswers
list[app.MessageAnswerInfo]
false
其他回答
QueryExtends
app.QueryExtendsInfo
false
询问扩展信息
app.MessageAnswerInfo
说明:
参数
类型
是否必填
说明
Answer
string
false
答复内容
MessageID
string
false
消息ID
CreatedTime
i32
false
时间戳
TaskID
string
false
任务ID
Like
common.LikeType
false
点赞
TotalTokens
i32
false
token消耗
Latency
double
false
耗时, 单位秒
TracingJsonStr
string
false
tracing, debug相关接口才返回
app.FileInfo
说明:
参数
类型
是否必填
说明
Path
string
false
路径
Name
string
false
名称
Size
i64
false
大小
Url
string
false
链接
app.QueryExtendsInfo
说明:
参数
类型
是否必填
说明
Files
list[app.FileInfo]
false
文件列表
app.VariableConfig
说明:
参数
类型
是否必填
说明
Key
string
true
变量KEY
Name
string
true
字段名称
Description
string
false
描述
Required
bool
true
是否必填
VariableType
common.VariableType
true
变量类型：文本Text 枚举Enum 段落Paragraph
EnumValues
list[string]
false
枚举值, 变量类型是Enum时必填
TextMaxLength
i32
false
文本最大长度限制, 变量类型是Text时必填
app.VoiceConfig
说明：
参数
类型
是否必填
说明
Enable
bool
false
智能体内是否启用音频播放功能
AutoPlay
bool
false
自动播放开关
Speaker
string
false
发音人.智能体文字转语音配置中对应的音色：
zh_female_shuangkuaisisi_moon_bigtts：爽快思思
zh_male_wennuanahu_moon_bigtts：温暖阿虎
zh_female_linjianvhai_moon_bigtts：邻家女孩
zh_female_kailangjiejie_moon_bigtts：开朗姐姐
zh_male_linjiananhai_moon_bigtts：邻家男孩
zh_female_xinlingjitang_moon_bigtts：心灵鸡汤
zh_male_jingqiangkanye_moon_bigtts：京腔侃爷
zh_female_wanwanxiaohe_moon_bigtts：湾湾小何
zh_female_daimengchuanmei_moon_bigtts：呆萌川妹
zh_male_guozhoudege_moon_bigtts：广州德哥
zh_male_guangxiyuanzhou_moon_bigtts：广西远舟
zh_male_yuzhouzixuan_moon_bigtts：豫州子轩
zh_male_aojiaobazong_moon_bigtts：傲娇霸总
zh_male_shenyeboke_moon_bigtts：深夜播客
ICL_zh_female_heainainai_tob：和蔼奶奶
base.BaseResp
说明:
参数
类型
是否必填
说明
StatusMessage
string
false

StatusCode
i32
false

Extra
map[string, string]
false

common.LikeType
说明: 枚举类型
参数
类型
是否必填
说明
Dislike
i32
false
枚举值:-1，点踩
Default
i32
false
枚举值:0，未操作
Like
i32
false
枚举值:1，点赞
common.ListOption
说明: ListOption
参数
类型
是否必填
说明
Sort
list[common.Sorter]
false

PageNumber
i32
false
排序字段
PageSize
i32
false
页码
common.Sorter
说明: Sorter
参数
类型
是否必填
说明
SortField
string
true
排序字段，填snake_case，例如操作时间就填created_at，更新时间填updated_at
SortOrder
string
false
排序顺序，默认desc，可填desc, asc
common.VariableType
说明: 变量类型
参数
类型
是否必填
说明
VariableTypeText
string
false
枚举值：Text，文本类型
VariableTypeParagraph
string
false
枚举值：Paragraph，段落类型
VariableTypeEnum
string
false
枚举值：Enum，枚举类型
workflow.DebugInputVariable
说明:
参数
类型
是否必填
说明
Name
string
true
变量名称
StringValue
string
false
string 类型的变量值，StringValue, IntValue, DoubleValue, BoolValue 四个字段只能选一个
IntValue
i64
false
int 类型的变量值，StringValue, IntValue, DoubleValue, BoolValue 四个字段只能选一个
DoubleValue
double
false
double 类型的变量值，StringValue, IntValue, DoubleValue, BoolValue 四个字段只能选一个
BoolValue
bool
false
bool 类型的变量值，StringValue, IntValue, DoubleValue, BoolValue 四个字段只能选一个
workflow.Node
说明:
参数
类型
是否必填
说明
input
string
false
节点输入
output
string
false
节点输出
status
string
false
节点状态
message
string
false
节点信息
costMs
i32
false
节点运行花费时间，ms
costToken
i32
false
节点运行花费 token
BizCode
common.BizCode
false
业务码
nodeType

string
false
节点类型，支持 Start, End, LLM, Code, Knowledge, Condition, Tool, Workflow 的节点类型
LoopBlock
LoopBlock
false
循环体运行结果
common.BizCode
说明：
参数
类型
是否必填
说明
Code
string
false
业务码
Message
string
false
描述
Data
map[string, string]
false
额外信息
workflow.LoopBlock
说明：
参数
类型
是否必填
说明
nodes
map[string, workflow.Node]
false
节点信息
steps
list[string]
false
已运行的节点
status
string
false
循环状态

plugin.Oauth2TokenItem
说明:
参数
类型
是否必填
说明
PluginID
string
true
插件ID
APPID
string
true
应用ID
APPUserID
string
true
应用用户ID
TokenExpiresAt
string
false
token 过期时间
IsTokenValid
bool
true
token 是否有效, 如果 插件认证配置更新, 未登录, token 过期 会标记失效
IsRefreshTokenValid
bool
true
refreshToken 是否有效, 如果 插件认证配置更新, 未登录, 无refrshToken 会标记失效
app.ListLongMemoryFilter
说明：长期记忆过滤条件
参数
类型
是否必填
说明
StartTime
string
false
检索日志开始时间，时间格式遵守timeRFC3339
EndTime
string
false
检索日志结束时间，时间格式遵守timeRFC3339
Keyword
string
false
关键词
app.LongMemoryItem
说明：长期记忆列表项
参数
类型
是否必填
说明
MemoryID
string
false
记忆ID
Memory
string
false
记忆内容
MemoryVectorRawDim
int
false
记忆向量原始维度
CreateTimestamp
int
false
记忆创建时间戳，单位秒
UpdateTimestamp
int
false
记忆更新时间戳，单位秒
common.UserType
说明: 用户类别
参数
类型
是否必填
说明
UserTypeApp
string
false
枚举值：App，应用自定义用户（目前主要是openapi访问用户，userID应用开发者自定义）
UserTypeIAM
string
false
枚举值：IAM，HiAgent平台用户（即iam用户，userID使用iam的用户ID）
UserTypeVisitor
string
false
枚举值：Visitor，web匿名访问用户（userID服务端自动生成写到浏览器cookie）
UserTypeLark
string
false
枚举值：Lark，lark用户（userID使用lark的用户openID）
UserTypeWechat
string
false
枚举值：Wechat，wechat用户（userID使用wechat的用户openID）
app.AppSkillAsyncTaskInfo
说明：智能体技能工具异步任务信息
参数
类型
是否必填
说明
TaskID
string
false
应用技能异步任务 ID
Status
common.AppSkillAsyncTaskStatus

false
应用技能异步任务状态，PROCESSING: 运行中，SUCCEED: 成功，FAILED: 失败, INVALID: 无效
OriginMessageID
string

false
源消息ID，应用技能开始异步技能时，会将消息ID作为源消息ID
Reason
string
false
报错信息
MessageID
string
false
当前消息 ID。进行中情况下不一定有值。异步任务往往会单独进行对话，会产生另外一个对话记录。
common.AppSkillAsyncTaskStatus
说明: 用户类别
参数
类型
是否必填
说明
AppSkillAsyncTaskStatusProcessing
string
false
枚举值：PROCESSING，应用技能异步任务状态: 处理中
AppSkillAsyncTaskStatusSucceed
string
false
枚举值：SUCCEED，应用技能异步任务状态: 成功
AppSkillAsyncTaskStatusFailed
string
false
枚举值：FAILED，应用技能异步任务状态: 失败
AppSkillAsyncTaskStatusInvalid
string
false
枚举值：INVALID，应用技能异步任务状态: 无效。无效的 taskID.
