/**
 * 模拟 hiagent API 响应数据
 * 用于测试和开发
 */

/**
 * 模拟任务生成响应
 */
export const mockTaskResponse = `
1. 技术方案完整性评估
   评估投标文件中的技术方案是否完整、可行，是否满足需求文档中的所有技术要求。
   需要检查架构设计、技术路线、实施方案等关键要素。

2. 价格合理性分析
   分析投标报价是否合理，与市场平均水平相比是否存在偏差。
   需要核实成本构成、报价明细、总价合理性等。

3. 经验资质匹配度
   审核投标方的过往经验和资质是否满足项目要求。
   需要检查项目经验、团队配置、相关认证等。

4. 实施方案可行性
   评估投标文件中的实施方案是否切实可行，能否保证项目按时交付。
   需要检查进度计划、资源配置、风险预案等。

5. 质量保障体系
   审核投标方是否建立健全的质量保障体系，确保项目质量。
   需要检查质量标准、检测方法、验收流程等。
`

/**
 * 模拟审核结果响应
 */
export const mockReviewResponse = {
  taskId: 1,
  status: '通过',
  reason: '投标方的技术方案完整详细，包含了需求文档中要求的所有技术要素。架构设计合理，技术路线清晰，实施计划周详，具备良好的可行性。报价处于市场合理区间，性价比高。投标方具有丰富的相关项目经验，团队能力匹配，质量保障体系完善。',
  requirementSource: '需求文档第3章：技术要求 - 明确要求技术方案完整、架构合理、实施可行',
  bidSource: '投标文件第4章：技术方案 - 详细技术架构、实施计划、技术优势分析',
  score: {
    technical: 92,
    price: 85,
    experience: 88,
    schedule: 90,
    quality: 95
  }
}

/**
 * 模拟不同的审核结果
 */
export const mockReviewResults = {
  pass: {
    taskId: 1,
    status: '通过',
    reason: '投标文件符合所有招标要求，技术方案优秀，价格合理，经验丰富。建议中标。',
    requirementSource: '需求文档第2-5章',
    bidSource: '投标文件全文',
    score: {
      technical: 95,
      price: 88,
      experience: 92,
      quality: 94,
      schedule: 90
    }
  },
  fail: {
    taskId: 2,
    status: '不通过',
    reason: '投标报价超出预算范围30%，且未提供充分的成本构成说明。技术方案中缺少关键技术的实施方案。',
    requirementSource: '需求文档第5章：预算要求',
    bidSource: '投标文件第6章：报价清单',
    score: {
      technical: 65,
      price: 45,
      experience: 80,
      quality: 70,
      schedule: 75
    }
  },
  pending: {
    taskId: 3,
    status: '待确认',
    reason: '投标方的部分技术方案需要进一步澄清，建议召开技术澄清会议进行详细讨论。',
    requirementSource: '需求文档第3章：技术要求',
    bidSource: '投标文件第4章：技术方案',
    score: {
      technical: 78,
      price: 82,
      experience: 85,
      quality: 80,
      schedule: 85
    }
  }
}

/**
 * 模拟 API 调用延迟
 */
export const mockDelay = (ms = 1000) => {
  return new Promise(resolve => setTimeout(resolve, ms))
}