// 任务类型
export const TaskStatus = {
  PENDING: 'pending',
  REVIEWING: 'reviewing',
  COMPLETED: 'completed'
}

export const ReviewStatus = {
  PASS: '通过',
  FAIL: '不通过',
  PENDING: '待确认'
}

// 招标要求类型
export const RequirementType = {
  INFORMATION_CHECK: 'information-check',  // 核实信息，推给 hiagent，type=0
  BIDDING_REQUIREMENT: 'bidding-requirement',  // 招标要求，推给 hiagent，type=1
  GENERAL_REQUIREMENT: 'general-requirement'  // 通用要求，不走 hiagent，直接推送任务
}

// 获取 HiAgent API 的 type 值
export const getHiAgentType = (requirementType) => {
  const typeMap = {
    [RequirementType.INFORMATION_CHECK]: 0,
    [RequirementType.BIDDING_REQUIREMENT]: 1,
    [RequirementType.GENERAL_REQUIREMENT]: null  // 通用要求不调用 hiagent
  }
  return typeMap[requirementType]
}

// API 端点
export const API_ENDPOINTS = {
  GENERATE_TASKS: '/hiagent/generate-tasks',
  REVIEW_TASK: '/hiagent/review-task'
}

// 任务数据结构
export const TaskSchema = {
  id: Number,
  title: String,
  description: String,
  requirementSource: String,
  bidSource: String,
  review: {
    status: String,
    reason: String,
    requirementSource: String,
    bidSource: String,
    score: Object
  },
  createdAt: Date,
  updatedAt: Date
}

// 审核结果数据结构
export const ReviewSchema = {
  taskId: Number,
  status: String,
  reason: String,
  requirementSource: String,
  bidSource: String,
  score: Object,
  createdAt: Date
}