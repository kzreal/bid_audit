// 模版数据服务
const STORAGE_KEY = 'bid_review_templates'

/**
 * 生成唯一ID
 */
function generateId() {
  return `tpl_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * 默认模版数据
 */
const DEFAULT_TEMPLATES = [
  {
    id: 'tpl_default_1',
    name: '基础审核模版',
    description: '包含投标文件的基本审核项目',
    tags: ['基础', '常用'],
    createdAt: new Date().toISOString(),
    tasks: [
      '检查投标文件完整性，确认投标文件包含所有必需的章节和附件',
      '验证资质文件，检查企业资质、营业执照等文件是否有效',
      '核对报价信息，确认报价是否符合招标文件要求'
    ]
  },
  {
    id: 'tpl_default_2',
    name: '技术方案审核',
    description: '技术方案相关的审核项目',
    tags: ['技术', '方案'],
    createdAt: new Date().toISOString(),
    tasks: [
      '技术方案可行性，评估技术方案是否可行且符合要求',
      '技术指标符合性，核对技术参数是否达到招标要求',
      '项目实施计划，检查项目实施计划是否合理完整',
      '团队资质审核，验证项目团队人员的资质和经验'
    ]
  },
  {
    id: 'tpl_default_3',
    name: '商务条款审核',
    description: '商务合同条款相关的审核项目',
    tags: ['商务', '合同'],
    createdAt: new Date().toISOString(),
    tasks: [
      '付款条款审核，检查付款方式和比例是否符合要求',
      '交付期限核对，确认交付期限是否满足招标要求',
      '违约条款审查，审查违约责任条款的合理性',
      '质保期约定，检查质保期是否符合规定'
    ]
  }
]

/**
 * 初始化模版数据
 */
function initializeTemplates() {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (!stored) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_TEMPLATES))
    return DEFAULT_TEMPLATES
  }
  return JSON.parse(stored)
}

/**
 * 获取所有模版
 */
export function getAllTemplates() {
  return initializeTemplates()
}

/**
 * 获取单个模版
 */
export function getTemplateById(id) {
  const templates = getAllTemplates()
  return templates.find(t => t.id === id) || null
}

/**
 * 保存模版（新增或更新）
 */
export function saveTemplate(template) {
  const templates = getAllTemplates()

  if (template.id) {
    // 更新现有模版
    const index = templates.findIndex(t => t.id === template.id)
    if (index !== -1) {
      templates[index] = {
        ...templates[index],
        ...template,
        updatedAt: new Date().toISOString()
      }
    }
  } else {
    // 新增模版
    template.id = generateId()
    template.createdAt = new Date().toISOString()
    templates.push(template)
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify(templates))
  return template
}

/**
 * 删除模版
 */
export function deleteTemplate(id) {
  const templates = getAllTemplates()
  const filtered = templates.filter(t => t.id !== id)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))
  return filtered
}

/**
 * 搜索模版
 */
export function searchTemplates(query = '', tags = []) {
  const templates = getAllTemplates()

  return templates.filter(template => {
    // 关键词搜索
    const matchesQuery = !query ||
      template.name.toLowerCase().includes(query.toLowerCase()) ||
      template.description.toLowerCase().includes(query.toLowerCase())

    // 标签筛选
    const matchesTags = tags.length === 0 ||
      tags.every(tag => template.tags.includes(tag))

    return matchesQuery && matchesTags
  })
}

/**
 * 获取所有标签
 */
export function getAllTags() {
  const templates = getAllTemplates()
  const tagSet = new Set()

  templates.forEach(template => {
    template.tags.forEach(tag => tagSet.add(tag))
  })

  return Array.from(tagSet).sort()
}

/**
 * 从任务列表创建模版
 */
export function createTemplateFromTasks(templateInfo, tasks) {
  const template = {
    id: generateId(),
    name: templateInfo.name || '新建模版',
    description: templateInfo.description || '',
    tags: templateInfo.tags || [],
    createdAt: new Date().toISOString(),
    tasks: tasks.map(task => task.title || task)
  }

  return saveTemplate(template)
}

/**
 * 导出模版数据
 */
export function exportTemplates() {
  const templates = getAllTemplates()
  const dataStr = JSON.stringify(templates, null, 2)
  const dataBlob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(dataBlob)

  const link = document.createElement('a')
  link.href = url
  link.download = `bid_review_templates_${new Date().toISOString().slice(0, 10)}.json`
  link.click()

  URL.revokeObjectURL(url)
}

/**
 * 导入模版数据
 */
export function importTemplates(jsonData) {
  try {
    const templates = JSON.parse(jsonData)
    if (!Array.isArray(templates)) {
      throw new Error('数据格式错误：必须是模版数组')
    }

    // 合并到现有模版
    const existingTemplates = getAllTemplates()
    const existingIds = new Set(existingTemplates.map(t => t.id))

    let newCount = 0
    templates.forEach(template => {
      if (!existingIds.has(template.id)) {
        existingTemplates.push(template)
        newCount++
      }
    })

    localStorage.setItem(STORAGE_KEY, JSON.stringify(existingTemplates))
    return { success: true, count: newCount }
  } catch (error) {
    return { success: false, error: error.message }
  }
}

/**
 * 恢复默认模版
 */
export function restoreDefaultTemplates() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(DEFAULT_TEMPLATES))
  return DEFAULT_TEMPLATES
}
