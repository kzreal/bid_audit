import http from '../utils/http'
import { retryRequest } from '../utils/http'

/**
 * hiagent API 服务
 * 用于生成审核任务和执行审核
 */

/**
 * 生成审核任务
 * 输入：requirement（招标文件信息）
 * 输出：一系列任务
 * @param {Object} params - 请求参数
 * @param {string} params.requirement - 招标信息文本
 * @returns {Promise<Object>} API 响应，包含 data 任务列表
 */
export const generateTasks = async (params) => {
  const { requirement } = params

  if (!requirement) {
    throw new Error('招标文件信息不能为空')
  }

  // 构建请求数据
  const requestData = {
    requirement,
    timestamp: new Date().toISOString()
  }

  // 使用重试机制调用 API
  const response = await retryRequest(() =>
    http.post('/hiagent/generate-tasks', requestData)
  )

  // 后端返回格式: {code: 200, data: [...], raw_text: "..."}
  // 直接返回响应，让 store 处理
  return response
}

/**
 * 审核任务
 * 输入：task（一条任务）+ context（投标文件）
 * @param {Object} params - 请求参数
 * @param {Object} params.task - 任务对象
 * @param {string} params.context - 投标文件文本
 * @returns {Promise<Object>} API 响应，包含 data 审核结果
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
  const response = await retryRequest(() =>
    http.post('/hiagent/review-task', requestData)
  )

  // 后端返回格式: {code: 200, data: {suggestion, evidence}, raw_text: "..."}
  // 需要转换为前端期望的格式
  const data = response.data || {}
  return {
    data: {
      status: determineStatus(data.suggestion),
      suggestion: data.suggestion || '',
      reason: data.suggestion || '',
      evidence: data.evidence || '',
      bidSource: data.evidence || '待补充',
      requirementSource: '招标要求'
    }
  }
}

/**
 * 多切片审核任务
 * 输入：task（一条任务）+ slices（切片内容数组）
 * 输出：汇总的审核结果（包含每个切片的结果和最终结论）
 * @param {Object} params - 请求参数
 * @param {Object} params.task - 任务对象
 * @param {Array<string>} params.slices - 切片内容数组
 * @returns {Promise<Object>} API 响应，包含 data 审核结果
 */
export const reviewTaskSlices = async (params) => {
  const { task, slices } = params

  if (!task) {
    throw new Error('任务不能为空')
  }

  if (!Array.isArray(slices) || slices.length === 0) {
    throw new Error('切片不能为空')
  }

  if (slices.length > 100) {
    throw new Error('切片数量不能超过 100 个')
  }

  // 构建请求数据
  const requestData = {
    task,
    slices,
    timestamp: new Date().toISOString()
  }

  // 使用重试机制调用 API
  const response = await retryRequest(() =>
    http.post('/hiagent/review-task-slices', requestData)
  )

  // 后端返回格式: {code: 200, data: {task, reviews: [{suggestion, evidence}]}}
  // 不做任何汇总处理，直接返回原始数据
  // 汇总和状态判断会在后续由 summary agent 完成
  const data = response.data || {}
  const reviews = data.reviews || []

  return {
    data: {
      status: '待确认',
      reason: '',
      evidence: '',
      bidSource: '待补充',
      requirementSource: '招标要求',
      slices_reviews: reviews
    }
  }
}

/**
 * 根据文本判断审核状态
 * @param {string} text - 审核结论/建议文本
 * @returns {string} 状态值：通过/不通过/待确认
 */
function determineStatus(text) {
  if (!text) return '待确认'

  if (text.includes('通过') || text.includes('符合') || text.includes('合格') || text.includes('满足')) {
    return '通过'
  }

  if (text.includes('不通过') || text.includes('不符合') || text.includes('不合格') || text.includes('未通过')) {
    return '不通过'
  }

  return '待确认'
}

/**
 * 获取 API 状态
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
  REVIEW_TASK_SLICES: '/hiagent/review-task-slices',
  GENERATE_CONCLUSION: '/hiagent/generate-conclusion',
  STATUS: '/hiagent/status'
}

/**
 * 生成最终审核结论
 * 输入：task（任务描述）+ reviews（所有切片的审核结果）
 * 输出：最终的审核结论（conclusion, reason, evidence）
 * @param {Object} params - 请求参数
 * @param {string|Object} params.task - 任务描述
 * @param {Array} params.reviews - 所有切片的审核结果
 * @returns {Promise<Object>} API 响应，包含 data 审核结果
 */
export const generateConclusion = async (params) => {
  const { task, reviews } = params

  if (!task) {
    throw new Error('任务不能为空')
  }

  if (!Array.isArray(reviews)) {
    throw new Error('审核结果必须是数组格式')
  }

  // 构建请求数据
  const requestData = {
    task,
    reviews,
    timestamp: new Date().toISOString()
  }

  // 使用重试机制调用 API
  const response = await retryRequest(() =>
    http.post('/hiagent/generate-conclusion', requestData)
  )

  // 后端返回格式: {code: 200, data: {conclusion, reason, evidence}, message: "...", raw_text: "..."}
  const data = response.data || {}
  return {
    data: {
      conclusion: data.conclusion || '待确认',
      reason: data.reason || '暂无原因说明',
      evidence: data.evidence || '待补充',
      requirementSource: '招标要求',
      bidSource: '投标文件',
      createdAt: new Date()
    }
  }
}

// 导出默认实例
export default {
  generateTasks,
  reviewTask,
  reviewTaskSlices,
  generateConclusion,
  getApiStatus
}
