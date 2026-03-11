/**
 * 审核结果拆解工具
 * 用于解析 hiagent API 返回的审核结果
 */

/**
 * 解析 hiagent 返回的审核结果
 * @param {string|Object} data - API 返回的数据
 * @returns {Object} 审核结果对象
 */
export const parseReviewResult = (data) => {
  // 如果已经是对象，检查是否包含审核相关字段
  if (typeof data === 'object' && data !== null) {
    // 如果已经包含标准字段，直接返回
    if (data.status || data.result || data.conclusion) {
      return normalizeReviewResult(data)
    }
  }

  // 如果是字符串，尝试解析
  if (typeof data === 'string') {
    try {
      // 尝试解析 JSON
      const parsed = JSON.parse(data)
      return normalizeReviewResult(parsed)
    } catch (e) {
      // JSON 解析失败，按文本处理
      return parseReviewText(data)
    }
  }

  // 默认返回审核结果模板
  return {
    status: '待确认',
    reason: '无法解析审核结果',
    requirementSource: '待补充',
    bidSource: '待补充',
    score: {},
    createdAt: new Date()
  }
}

/**
 * 解析文本格式的审核结果
 * @param {string} text - 审核结果文本
 * @returns {Object} 审核结果对象
 */
function parseReviewText(text) {
  const result = {
    status: '待确认',
    reason: text.trim(),
    requirementSource: '待补充',
    bidSource: '待补充',
    score: {},
    createdAt: new Date()
  }

  // 尝试从文本中提取状态
  const statusMatch = text.match(/(?:结论|结果|状态)[：:]\s*(通过|不通过|待确认|合格|不合格|建议修改)/i)
  if (statusMatch) {
    const statusMap = {
      '通过': '通过',
      '不通过': '不通过',
      '待确认': '待确认',
      '合格': '通过',
      '不合格': '不通过',
      '建议修改': '待确认'
    }
    result.status = statusMap[statusMatch[1]] || '待确认'
  }

  // 尝试提取来源信息
  const sourceMatches = text.match(/(?:需求|招标)[：:]\s*([^\n]+)/g)
  if (sourceMatches) {
    result.requirementSource = sourceMatches[0].replace(/(?:需求|招标)[：:]\s*/, '')
  }

  const bidSourceMatch = text.match(/(?:投标|方案)[：:]\s*([^\n]+)/g)
  if (bidSourceMatch) {
    result.bidSource = bidSourceMatch[0].replace(/(?:投标|方案)[：:]\s*/, '')
  }

  // 尝试提取评分信息
  const scoreMatches = text.match(/(?:技术|价格|经验|质量)[：:]\s*(\d+)%/g)
  if (scoreMatches) {
    result.score = {}
    scoreMatches.forEach(match => {
      const [key, value] = match.match(/(.+?)[:：]\s*(\d+)%/).slice(1)
      const scoreKey = getScoreKey(key)
      result.score[scoreKey] = parseInt(value)
    })
  }

  return result
}

/**
 * 标准化审核结果对象
 * @param {Object} data - 原始审核结果对象
 * @returns {Object} 标准化后的审核结果
 */
function normalizeReviewResult(data) {
  const result = {
    status: data.status || data.result || data.conclusion || '待确认',
    reason: data.reason || data.detail || data.explanation || data.content || '暂无原因说明',
    requirementSource: data.requirementSource || data.requirement || '待补充',
    bidSource: data.bidSource || data.bid || data.proposal || '待补充',
    score: data.score || data.rating || {},
    createdAt: data.createdAt || new Date()
  }

  // 标准化状态值
  const statusMap = {
    'pass': '通过',
    'fail': '不通过',
    'pending': '待确认',
    'qualified': '通过',
    'unqualified': '不通过',
    'approved': '通过',
    'rejected': '不通过'
  }
  result.status = statusMap[result.status] || result.status

  // 确保评分是数字
  if (typeof result.score === 'object') {
    for (const key in result.score) {
      if (typeof result.score[key] === 'string') {
        result.score[key] = parseInt(result.score[key]) || 0
      }
    }
  }

  return result
}

/**
 * 获取评分键名
 * @param {string} key - 原始键名
 * @returns {string} 标准化键名
 */
function getScoreKey(key) {
  const keyMap = {
    '技术': 'technical',
    '技术匹配': 'technical',
    '技术方案': 'technical',
    '价格': 'price',
    '报价': 'price',
    '费用': 'price',
    '经验': 'experience',
    '经验匹配': 'experience',
    '案例': 'experience',
    '质量': 'quality',
    '质量保障': 'quality',
    '质量方案': 'quality',
    '进度': 'schedule',
    '工期': 'schedule',
    '时间': 'schedule',
    '服务': 'service',
    '售后': 'service',
    '方案': 'solution',
    '创新': 'innovation'
  }

  // 检查是否包含关键词
  for (const [k, v] of Object.entries(keyMap)) {
    if (key.includes(k)) {
      return v
    }
  }

  // 默认返回小写
  return key.toLowerCase().replace(/\s+/g, '')
}

/**
 * 验证审核结果
 * @param {Object} review - 审核结果对象
 * @returns {Object} 验证结果
 */
export const validateReview = (review) => {
  const errors = []
  const warnings = []

  if (!review) {
    errors.push('审核结果不能为空')
    return { valid: false, errors, warnings }
  }

  if (!review.status) {
    errors.push('审核结果缺少状态')
  }

  const validStatuses = ['通过', '不通过', '待确认']
  if (!validStatuses.includes(review.status)) {
    warnings.push(`未知的审核状态: ${review.status}`)
  }

  if (!review.reason || review.reason.trim() === '') {
    errors.push('审核结果缺少原因说明')
  }

  if (!review.requirementSource || review.requirementSource.trim() === '') {
    warnings.push('缺少需求来源信息')
  }

  if (!review.bidSource || review.bidSource.trim() === '') {
    warnings.push('缺少投标来源信息')
  }

  // 验证评分
  if (review.score && typeof review.score === 'object') {
    for (const [key, value] of Object.entries(review.score)) {
      if (typeof value !== 'number' || value < 0 || value > 100) {
        warnings.push(`评分 ${key} 的值 ${value} 不在有效范围内 (0-100)`)
      }
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings
  }
}

export default {
  parseReviewResult,
  validateReview
}