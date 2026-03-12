import { extractCommentLineNumber, parseSourceWithContext } from './lineParser.js'

// 测试数据
const testContext = `
空行1
<!-- 335 --> | 企业规模生产 （施工安装）能力 | 企业总人数及技术人员数量 | 总人数：6090人； 高级职称人数：111人； 中级职称人数：512人； | 后附企业组织机构图、企业规模、服务能力简介等。 |

空行2
<!-- 336 --> | 企业规模生产 （施工安装）能力 | 服务能力 | 免费指导安装调试：设备安装调试时，我司将派经验丰富的工程技术人员现场指导安装调试，直至设备正常投入运行。设备调试运行后，由双方及有关部门共同对产品按验收标准进行总体验收。 响应速度迅速：保证在接到用户需求4小时内响应，12小时内派专职技术服务人员到现场排除设备故障。 | 后附企业组织机构图、企业规模、服务能力简介等。 |

空行3
<!-- 340 --> | 企业规模生产 （施工安装）能力 | 技术人员 | 技术人员总数：111人（高级职称）； 员工构成：高级职称人员11人，中级职称人员51人，初级职称人员49人； | 后附企业组织机构图、企业组织架构图、企业规模等。 |

空行4
<!-- 341 --> | 企业规模生产 （施工安装）能力 | 技术人员 | 技术人员总数：111人（高级职称）； 员工构成：高级职称人员11人，中级职称人员51人，初级职称人员49人； | 后附企业组织机构图、企业组织架构图、企业规模等。 |
`

describe('lineParser', () => {
  test('extractCommentLineNumber should extract line number from comment', () => {
    expect(extractCommentLineNumber('<!-- 335 --> 内容')).toBe(335)
    expect(extractCommentLineNumber('  <!-- 336 -->   ')).toBe(336)
    expect(extractCommentLineNumber('非注释内容')).toBe(null)
    expect(extractCommentLineNumber('')).toBe(null)
  })

  test('parseSourceWithContext should handle line numbers with comments correctly', () => {
    // 测试单个行号
    const result1 = parseSourceWithContext('340', testContext)
    expect(result1.original).toBe('340')
    expect(result1.segments).toHaveLength(1)
    expect(result1.segments[0].label).toBe('340')
    expect(result1.segments[0].content).toContain('技术人员总数：111人（高级职称）')

    // 测试范围行号
    const result2 = parseSourceWithContext('340-341', testContext)
    expect(result2.original).toBe('340-341')
    expect(result2.segments).toHaveLength(1)
    expect(result2.segments[0].label).toBe('340-341')
    expect(result2.segments[0].content).toContain('技术人员总数：111人（高级职称）')

    // 测试不存在的行号
    const result3 = parseSourceWithContext('999', testContext)
    expect(result3.hasLineNumbers).toBe(false)
  })

  test('parseSourceWithContext should ignore empty lines', () => {
    const result = parseSourceWithContext('340', testContext)
    // 验证获取的内容是第340行，而不是因为空行导致的第336行
    expect(result.segments[0].content).toContain('技术人员总数：111人（高级职称）')
    expect(result.segments[0].content).not.toContain('免费指导安装调试')
  })
})