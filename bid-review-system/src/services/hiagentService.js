import http from '../utils/http'
import { retryRequest } from '../utils/http'

/**
 * hiagent API 服务
 * 用于生成审核任务和执行审核
 */

/**
 * 解析生成任务的文本输出
 * @param {string} text - API 返回的文本
 * @returns {Array} 任务列表
 */
function parseTaskText(text) {
  if (!text || typeof text !== 'string') {
    return []
  }

  // 按行分割并过滤空行
  const lines = text.split('\n').filter(line => line.trim())

  const tasks = []
  for (const line of lines) {
    // 匹配格式: "数字.  任务描述" 或 "数字.任务描述"
    const match = line.match(/^(\d+)\.\s*(.+)$/)

    if (match) {
      const id = parseInt(match[1], 10)
      const description = match[2].trim()

      // 生成标题（取描述的前20个字符）
      const title = description.length > 20
        ? description.substring(0, 20) + '...'
        : description

      tasks.push({
        id,
        title,
        description,
        requirementSource: '招标要求',
        bidSource: '投标文件',
        status: 'pending'
      })
    }
  }

  return tasks
}

/**
 * 解析后端返回的任务数组
 * @param {Array} tasks - 后端返回的任务数组
 * @returns {Array} 标准化的任务列表
 */
function parseBackendTasks(tasks) {
  if (!Array.isArray(tasks)) {
    return []
  }

  return tasks.map((task, index) => {
    // 处理后端返回的任务格式
    const taskData = {
      id: task.id || index + 1,
      title: '',  // 稍后从 content 生成
      description: task.content || '暂无描述',
      requirementSource: '招标要求',
      bidSource: '投标文件',
      status: 'pending'
    }

    // 从内容生成标题
    if (task.content) {
      taskData.title = task.content.length > 20
        ? task.content.substring(0, 20) + '...'
        : task.content
    }

    return taskData
  })
}

/**
 * 生成审核任务
 * 输入：requirement（招标文件信息）+ type（类型）
 * 输出：一系列任务
 * @param {Object} params - 请求参数
 * @param {string} params.requirement - 招标信息文本
 * @param {number|null} params.type - 类型：0=核实信息，1=招标要求，null=通用要求
 * @returns {Promise<Array>} 任务列表
 */
export const generateTasks = async (params) => {
  const { requirement, type } = params

  if (!requirement) {
    throw new Error('招标文件信息不能为空')
  }

  // 如果是通用要求（type=null），直接返回任务，不调用 API
  if (type === null) {
    console.log('通用要求，直接返回任务，不调用 HiAgent API')
    return [{
      id: 1,
      title: requirement.length > 20 ? requirement.substring(0, 20) + '...' : requirement,
      description: requirement,
      requirementSource: '通用要求',
      bidSource: '投标文件',
      status: 'pending'
    }]
  }

  // 构建请求数据
  const requestData = {
    requirement,
    type,
    timestamp: new Date().toISOString()
  }

  console.log('调用 HiAgent API，请求数据:', requestData)

  // 使用重试机制调用 API
  return retryRequest(() =>
    http.post('/hiagent/generate-tasks', requestData)
  ).then(response => {
    // 如果响应是文本格式，解析为任务列表
    if (typeof response === 'string') {
      const tasks = parseTaskText(response)
      return tasks
    }

    // 如果响应是数组格式
    if (Array.isArray(response)) {
      return parseBackendTasks(response)
    }

    // 如果是对象格式，检查是否有 data 字段（后端返回格式）
    if (response.data && Array.isArray(response.data)) {
      return parseBackendTasks(response.data)
    }

    // 如果是对象格式，检查是否有 tasks 字段
    if (response.tasks && Array.isArray(response.tasks)) {
      return parseBackendTasks(response.tasks)
    }

    // 默认返回空数组
    return []
  }).catch(error => {
    console.error('生成任务 API 调用失败:', error)
    // 如果 API 调用失败，返回一个模拟的任务列表
    return [
      {
        id: 1,
        title: '技术方案评估',
        description: '评估投标文件中的技术方案是否完整、可行，是否满足需求文档中的所有技术要求。',
        requirementSource: '招标要求',
        bidSource: '投标文件',
        status: 'pending'
      }
    ]
  })
}

/**
 * 解析审核任务的文本输出
 * @param {string} text - API 返回的文本
 * @returns {Object} 审核结果
 */
function parseReviewText(text) {
  if (!text || typeof text !== 'string') {
    return {
      status: '待确认',
      reason: '无法解析审核结果',
      requirementSource: '',
      bidSource: ''
    }
  }

  // 初始化默认值
  let status = '待确认'
  let reason = ''
  let requirementSource = ''
  let bidSource = ''

  // 提取结论
  const conclusionMatch = text.match(/结论[：:]\s*(.+)/)
  if (conclusionMatch) {
    const conclusion = conclusionMatch[1].trim()
    // 映射结论到标准状态
    if (conclusion.includes('通过') || conclusion.includes('符合')) {
      status = '通过'
    } else if (conclusion.includes('不通过') || conclusion.includes('不符合') || conclusion.includes('未通过')) {
      status = '不通过'
    } else {
      status = '待确认'
    }
  }

  // 提取原因
  const reasonMatch = text.match(/原因[：:]\s*(.+?)(?=\n来源|$)/s)
  if (reasonMatch) {
    reason = reasonMatch[1].trim()
  }

  // 提取来源
  const sourceMatch = text.match(/来源[：:]\s*(.+)/)
  if (sourceMatch) {
    const source = sourceMatch[1].trim()
    // 根据来源内容判断是招标要求还是投标文件来源
    if (/^\d+([,\s\d-]*\d*)*$/.test(source)) {
      // 纯数字行号，是投标文件来源
      bidSource = source
      requirementSource = '招标要求'
    } else {
      // 包含文字描述
      bidSource = source
      requirementSource = '招标要求'
    }
  }

  return {
    status,
    reason,
    requirementSource,
    bidSource
  }
}

/**
 * 审核任务
 * 输入：task（一条任务）+ context（投标文件）
 * 需要重复调用直至处理完所有任务
 * @param {Object} params - 请求参数
 * @param {Object} params.task - 任务对象
 * @param {string} params.context - 投标文件文本
 * @returns {Promise<Object>} 审核结果
 */
export const reviewTask = async (params) => {
  const { task, context } = params

  if (!task) {
    throw new Error('任务不能为空')
  }

  if (!context) {
    throw new Error('投标文件（context）不能为空')
  }

  // 构建请求数据
  const requestData = {
    task,
    context,
    timestamp: new Date().toISOString()
  }

  // 使用重试机制调用 API
  return retryRequest(() =>
    http.post('/hiagent/review-task', requestData)
  ).then(response => {
    // 后端返回格式: {code: 200, data: {results: [...]}, status: "...", message: "...", raw_text: "..."}
    // 需要标准化为前端期望的格式

    // 如果响应是文本格式，解析为结构化结果
    if (typeof response === 'string') {
      return parseReviewText(response)
    }

    // 如果响应是对象，处理后端返回的标准格式
    if (typeof response === 'object' && response !== null) {
      // 优先使用 data.results 数组中的数据
      let resultsArray = null
      if (response.data && response.data.results && Array.isArray(response.data.results)) {
        resultsArray = response.data.results
      }

      if (resultsArray && resultsArray.length >= 3) {
        return {
          status: resultsArray[0].conclusion || response.status || '待确认',
          reason: resultsArray[1].reason || '暂无原因说明',
          bidSource: resultsArray[2].evidence || '待补充',
          requirementSource: '招标要求',
          createdAt: new Date()
        }
      }
    }

    // 其他情况，直接返回响应
    return response
  }).catch(error => {
    console.error('审核任务 API 调用失败:', error)
    // 如果 API 调用失败，返回一个模拟的审核结果
    return {
      status: '待确认',
      reason: 'API 连接失败，返回模拟审核结果。请检查网络连接和 API 配置。',
      requirementSource: '招标要求',
      bidSource: '投标文件'
    }
  })
}

/**
 * 获取 API 状态（可选）
 * @returns {Promise<Object>} API 状态信息
 */
export const getApiStatus = async () => {
  return retryRequest(() =>
    http.get('/hiagent/status')
  ).catch(() => ({
    status: 'unknown',
    message: '无法连接到服务器'
  }))
}

// 导出 API 端点常量
export const API_ENDPOINTS = {
  GENERATE_TASKS: '/hiagent/generate-tasks',
  REVIEW_TASK: '/hiagent/review-task',
  STATUS: '/hiagent/status'
}

// 导出默认实例
export default {
  generateTasks,
  reviewTask,
  getApiStatus
}