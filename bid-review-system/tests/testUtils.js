/**
 * 测试工具函数
 */

/**
 * 模拟招标数据
 */
export const mockRequirementData = {
  type: 'bidding-requirement',
  text: `
# 项目需求文档

## 1. 项目概述
本项目是一个智能化的投标文件审核系统，需要实现对招标文件的自动解析和投标文件的智能审核。

## 2. 技术要求
### 2.1 系统架构
- 前端：Vue 3 + Vite + Tailwind CSS
- 后端：Node.js + Express
- 数据库：MySQL 8.0
- 部署：Docker + Nginx

### 2.2 功能要求
- 文档解析：支持 PDF、Word、Markdown 格式
- 智能审核：基于 LLM 的文本分析
- 任务管理：任务的生成、分配、跟踪
- 报表生成：审核报告的自动生成

## 3. 预算要求
项目总预算：500-800万元
开发周期：6个月
维护期：12个月

## 4. 投标人资格
- 具有相关项目经验3年以上
- 团队规模不少于10人
- 具有相关资质认证
`
}

/**
 * 模拟投标数据
 */
export const mockBidData = {
  text: `
# 投标文件

## 1. 公司简介
我们是一家专业的软件开发公司，成立于2010年，现有员工50人，其中技术团队35人。

## 2. 技术方案
### 2.1 系统架构
采用微服务架构，使用 Spring Cloud Alibaba 技术栈，确保系统的高可用性和可扩展性。

### 2.2 开发计划
- 需求分析：2周
- 系统设计：3周
- 开发实现：12周
- 测试部署：2周
- 上线运维：持续

## 3. 项目报价
- 人工成本：600万元
- 硬件成本：100万元
- 其他费用：50万元
- 总计：750万元

## 4. 项目经验
- 智能审核系统（2021-2023）
- OA办公系统（2020-2022）
- 电商平台（2019-2021）
`
}

/**
 * 测试任务数据
 */
export const testTasks = [
  {
    id: 1,
    title: '技术方案完整性评估',
    description: '评估投标文件中的技术方案是否完整、可行，是否满足需求文档中的所有技术要求。',
    requirementSource: '需求文档第2章：技术要求',
    bidSource: '投标文件第2章：技术方案',
    review: null
  },
  {
    id: 2,
    title: '价格合理性分析',
    description: '分析投标报价是否合理，与市场平均水平相比是否存在偏差。',
    requirementSource: '需求文档第3章：预算要求',
    bidSource: '投标文件第3章：项目报价',
    review: null
  }
]

/**
 * 测试审核结果
 */
export const testReviewResults = [
  {
    taskId: 1,
    status: '通过',
    reason: '投标方的技术方案完整详细，包含了需求文档中要求的所有技术要素。架构设计合理，技术路线清晰，实施计划周详。',
    requirementSource: '需求文档第2章：技术要求',
    bidSource: '投标文件第2章：技术方案',
    score: {
      technical: 90,
      price: 85,
      experience: 88,
      quality: 92,
      schedule: 87
    }
  },
  {
    taskId: 2,
    status: '待确认',
    reason: '投标报价略高于预算上限，但提供了详细的价格构成说明，建议进一步澄清。',
    requirementSource: '需求文档第3章：预算要求',
    bidSource: '投标文件第3章：项目报价',
    score: {
      technical: 95,
      price: 75,
      experience: 90,
      quality: 88,
      schedule: 85
    }
  }
]

/**
 * 性能测试数据
 */
export const performanceTestData = {
  largeText: 'Lorem ipsum dolor sit amet, '.repeat(1000),
  tasks: Array(50).fill(null).map((_, i) => ({
    id: i + 1,
    title: `测试任务 ${i + 1}`,
    description: '这是一个测试任务，用于测试系统的性能表现。',
    requirementSource: '测试需求',
    bidSource: '测试投标',
    review: i % 5 === 0 ? testReviewResults[0] : null
  }))
}

/**
 * 测试用例
 */
export const testCases = {
  // 文本输入测试
  textInput: {
    name: '文本输入测试',
    steps: [
      '在招标信息区域输入文本',
      '在投标文件区域输入文本',
      '验证字符计数功能',
      '验证清空功能'
    ],
    expected: [
      '文本能够正常输入',
      '字符计数正确',
      '清空功能正常'
    ]
  },

  // 任务生成测试
  taskGeneration: {
    name: '任务生成测试',
    steps: [
      '输入招标和投标文本',
      '选择要求类型',
      '点击"开始分析"',
      '等待任务生成完成'
    ],
    expected: [
      '任务列表正常显示',
      '任务数量正确',
      '任务信息完整'
    ]
  },

  // 任务审核测试
  taskReview: {
    name: '任务审核测试',
    steps: [
      '选择一个任务',
      '点击"开始审核"',
      '等待审核完成',
      '查看审核结果'
    ],
    expected: [
      '审核正常进行',
      '结果正确显示',
      '状态正确更新'
    ]
  }
}