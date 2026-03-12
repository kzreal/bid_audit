/**
 * 行号解析工具
 * 用于从投标来源中提取行号并显示对应内容
 */

/**
 * 解析来源字符串中的行号
 * 支持以下格式：
 * - "1" - 单行
 * - "7-9" - 行范围
 * - "1, 7-9, 162-199" - 逗号分隔的多个行号/范围
 * - "第5行" - 中文格式
 * - "行号: 5" - 行号格式
 * @param {string} source - 来源字符串
 * @returns {Array|null} 返回行号数组，无法解析返回 null
 */
export function parseLineNumbers(source) {
  if (!source || typeof source !== 'string') {
    return null
  }

  const result = []

  // 首先尝试匹配逗号分隔的格式: "1, 7-9, 162-199"
  const commaPattern = /^(\d+(?:\s*[-~至到]\s*\d+)?)(?:,\s*(\d+(?:\s*[-~至到]\s*\d+)?))*$/
  if (commaPattern.test(source.trim())) {
    // 按逗号分割
    const parts = source.split(/,|，/).map(s => s.trim()).filter(s => s)
    for (const part of parts) {
      // 检查是否是范围格式: 7-9
      const rangeMatch = part.match(/^(\d+)\s*[-~至到]\s*(\d+)$/)
      if (rangeMatch) {
        result.push(parseInt(rangeMatch[1]), parseInt(rangeMatch[2]))
      } else {
        // 单行格式: 1
        const numMatch = part.match(/^(\d+)$/)
        if (numMatch) {
          result.push(parseInt(numMatch[1]))
        }
      }
    }
    return result.length > 0 ? result : null
  }

  // 尝试匹配其他格式
  const patterns = [
    // 第5行, 第 5 行
    /第\s*(\d+)\s*行/i,
    // 行号:5, 行号: 5
    /行号\s*[：:]\s*(\d+)/i,
    // Line:5, Line: 5
    /Line\s*[：:]\s*(\d+)/i,
    // L5, L:5
    /L\s*[：:]?\s*(\d+)/i,
    // 第5-10行, 第 5 - 10 行 (范围)
    /第\s*(\d+)\s*[-~至到]\s*(\d+)\s*行/i,
    // 行号:5-10
    /行号\s*[：:]\s*(\d+)\s*[-~至到]\s*(\d+)/i
  ]

  for (const pattern of patterns) {
    const match = source.match(pattern)
    if (match) {
      // 如果是范围格式（有两个数字）
      if (match[2]) {
        return [parseInt(match[1]), parseInt(match[2])]
      }
      // 单行格式
      return [parseInt(match[1])]
    }
  }

  return null
}

/**
 * 从文本中提取指定行的内容
 * @param {string} text - 完整文本内容
 * @param {number} lineNumber - 行号（从1开始）
 * @returns {string} 该行的内容，行号超出范围返回空字符串
 */
export function getLineContent(text, lineNumber) {
  if (!text || lineNumber < 1) {
    return ''
  }

  const lines = text.split('\n')
  const index = lineNumber - 1 // 转换为0-based索引

  if (index >= 0 && index < lines.length) {
    return lines[index].trim()
  }

  return ''
}

/**
 * 从文本中提取指定行范围的内容
 * @param {string} text - 完整文本内容
 * @param {number} startLine - 起始行号（从1开始）
 * @param {number} endLine - 结束行号（从1开始）
 * @returns {string} 范围内的内容，用换行符连接
 */
export function getLineRangeContent(text, startLine, endLine) {
  if (!text || startLine < 1) {
    return ''
  }

  const lines = text.split('\n')
  const startIndex = startLine - 1
  const endIndex = Math.min(endLine - 1, lines.length - 1)

  if (startIndex >= lines.length) {
    return ''
  }

  return lines.slice(startIndex, endIndex + 1).join('\n')
}

/**
 * 根据行号数组提取内容
 * 支持多个单行和范围，如 [1, 7, 9] 或 [1, 7, 9, 162, 199]
 * @param {string} text - 完整文本内容
 * @param {Array<number>} lineNumbers - 行号数组，单行和范围的起始结束行交替
 * @returns {string} 提取的内容，用分隔符连接
 */
export function getLinesContent(text, lineNumbers) {
  if (!text || !lineNumbers || lineNumbers.length === 0) {
    return ''
  }

  const lines = text.split('\n')
  const results = []

  // 遍历行号数组，处理单行和范围
  let i = 0
  while (i < lineNumbers.length) {
    const current = lineNumbers[i]
    const next = lineNumbers[i + 1]

    if (next !== undefined && next > current) {
      // 是一个范围：current 到 next
      const startLine = current - 1
      const endLine = Math.min(next - 1, lines.length - 1)

      if (startLine < lines.length) {
        const rangeLines = lines.slice(startLine, endLine + 1).map(l => l.trim())
        results.push(`[${current}-${next}]`)
        results.push(...rangeLines)
      }
      i += 2 // 跳过下一个数字，因为它是范围的结束
    } else {
      // 单行
      const index = current - 1
      if (index >= 0 && index < lines.length) {
        results.push(`[${current}]`)
        results.push(lines[index].trim())
      }
      i += 1
    }
  }

  return results.join('\n')
}

/**
 * 解析来源并返回格式化的内容
 * @param {string} source - 来源字符串
 * @param {string} context - 完整的文本内容
 * @returns {Object} 包含 original（原始来源）和 segments（解析后的分段内容）的对象
 */
export function parseSourceWithContext(source, context) {
  const lineNumbers = parseLineNumbers(source)

  if (!lineNumbers) {
    return {
      original: source,
      segments: [],
      hasLineNumbers: false
    }
  }

  const segments = []
  const lines = context.split('\n')

  // 遍历行号数组，为每个范围创建分段
  let i = 0
  while (i < lineNumbers.length) {
    const current = lineNumbers[i]
    const next = lineNumbers[i + 1]

    if (next !== undefined && next > current) {
      // 是一个范围：current 到 next
      const startLine = current
      const endLine = next
      const startLineIndex = startLine - 1
      const endLineIndex = Math.min(endLine - 1, lines.length - 1)

      if (startLineIndex < lines.length) {
        const rangeLines = lines.slice(startLineIndex, endLineIndex + 1).map(l => l.trim())
        const content = rangeLines.join('\n')
        segments.push({
          type: 'range',
          label: `${startLine}-${endLine}`,
          lineNumbers: [startLine, endLine],
          content: content,
          lineCount: rangeLines.length
        })
      }
      i += 2 // 跳过下一个数字
    } else {
      // 单行
      const lineNum = current
      const index = lineNum - 1
      if (index >= 0 && index < lines.length) {
        segments.push({
          type: 'single',
          label: `${lineNum}`,
          lineNumbers: [lineNum],
          content: lines[index].trim(),
          lineCount: 1
        })
      }
      i += 1
    }
  }

  return {
    original: source,
    segments: segments,
    lineNumbers: lineNumbers,
    hasLineNumbers: segments.length > 0
  }
}

export default {
  parseLineNumbers,
  getLineContent,
  getLineRangeContent,
  parseSourceWithContext
}
