/**
 * 任务拆解工具
 * 用于解析 hiagent API 返回的任务数据
 */

/**
 * 解析 hiagent 返回的任务文本，转换为任务列表
 * @param {string|Object} data - API 返回的数据
 * @returns {Array} 任务列表
 */
export const parseHiagentTasks = (data) => {
  console.log('开始解析任务数据，类型:', typeof data, '数据:', data)

  // 如果已经是数组，直接返回
  if (Array.isArray(data)) {
    console.log('检测到数组格式，任务数量:', data.length)
    return data.map((task, index) => normalizeTask(task, index + 1))
  }

  // 如果是字符串，尝试解析
  if (typeof data === 'string') {
    try {
      // 尝试解析 JSON
      const parsed = JSON.parse(data)
      if (Array.isArray(parsed)) {
        return parsed.map((task, index) => normalizeTask(task, index + 1))
      }
    } catch (e) {
      // JSON 解析失败，按文本处理
      return parseTaskText(data)
    }
  }

  // 如果是对象，转换为单个任务
  if (typeof data === 'object') {
    return [normalizeTask(data, 1)]
  }

  // 默认返回空数组
  return []
}

/**
 * 解析文本格式的任务
 * @param {string} text - 任务文本
 * @returns {Array} 任务列表
 */
function parseTaskText(text) {
  const tasks = []
  const lines = text.split('\n').filter(line => line.trim())

  // 尝试按标题格式解析（如：1. 任务标题）
  for (const line of lines) {
    const match = line.match(/^(\d+)[.、]\s*(.+)$/)
    if (match) {
      const [, id, title] = match
      const nextIndex = lines.indexOf(line) + 1

      // 查找描述（直到下一个任务或文本结束）
      const description = []
      for (let i = nextIndex; i < lines.length; i++) {
        const nextLine = lines[i]
        const nextMatch = nextLine.match(/^\d+[.、]\s*.+$/)
        if (nextMatch) break

        description.push(nextLine.trim())
      }

      tasks.push({
        id: parseInt(id),
        title: title.trim(),
        description: description.join('\n').trim() || '暂无描述',
        requirementSource: '待补充',
        bidSource: '待补充'
      })
    }
  }

  // 如果没有按格式解析，则按段落分割
  if (tasks.length === 0) {
    let currentTask = null
    for (const line of lines) {
      // 检测是否是任务标题
      if (line.includes('任务') || line.includes('审核') || line.length < 50) {
        if (currentTask) {
          tasks.push(currentTask)
        }
        currentTask = {
          id: tasks.length + 1,
          title: line.trim(),
          description: '',
          requirementSource: '待补充',
          bidSource: '待补充'
        }
      } else if (currentTask) {
        currentTask.description += (currentTask.description ? '\n' : '') + line.trim()
      }
    }

    // 添加最后一个任务
    if (currentTask) {
      tasks.push(currentTask)
    }
  }

  // 确保每个任务都有有效的 ID
  return tasks.map((task, index) => ({
    ...task,
    id: task.id || index + 1
  }))
}

/**
 * 标准化任务对象
 * @param {Object} task - 原始任务对象
 * @param {number} index - 任务索引
 * @returns {Object} 标准化后的任务
 */
function normalizeTask(task, index) {
  return {
    id: task.id || index,
    title: task.title || task.name || `任务 ${index}`,
    description: task.description || task.content || task.detail || '暂无描述',
    requirementSource: task.requirementSource || task.requirement || '待补充',
    bidSource: task.bidSource || task.bid || '待补充',
    createdAt: new Date(),
    updatedAt: new Date()
  }
}

/**
 * 验证任务数据
 * @param {Array} tasks - 任务列表
 * @returns {Object} 验证结果
 */
export const validateTasks = (tasks) => {
  const errors = []
  const warnings = []

  if (!Array.isArray(tasks)) {
    errors.push('任务数据必须是数组')
    return { valid: false, errors, warnings }
  }

  tasks.forEach((task, index) => {
    if (!task.id) {
      warnings.push(`任务 ${index + 1} 缺少 ID，将自动生成`)
    }

    if (!task.title || task.title.trim() === '') {
      errors.push(`任务 ${index + 1} 缺少标题`)
    }

    if (!task.description || task.description.trim() === '') {
      warnings.push(`任务 ${index + 1} 缺少描述`)
    }
  })

  return {
    valid: errors.length === 0,
    errors,
    warnings
  }
}

export default {
  parseHiagentTasks,
  validateTasks
}