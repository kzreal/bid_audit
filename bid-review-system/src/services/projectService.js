// 项目数据服务
const STORAGE_KEY = 'bid_review_projects'

/**
 * 生成唯一ID
 */
function generateId() {
  return `proj_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

/**
 * 获取所有项目
 */
export function getAllProjects() {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (!stored) return []
  return JSON.parse(stored)
}

/**
 * 获取单个项目
 */
export function getProjectById(id) {
  const projects = getAllProjects()
  return projects.find(p => p.id === id) || null
}

/**
 * 保存项目（新增或更新）
 */
export function saveProject(project) {
  const projects = getAllProjects()
  const now = new Date().toISOString()

  if (project.id) {
    // 更新现有项目
    const index = projects.findIndex(p => p.id === project.id)
    if (index !== -1) {
      projects[index] = {
        ...projects[index],
        ...project,
        lastOpenedAt: now
      }
    }
  } else {
    // 新增项目
    project.id = generateId()
    project.createdAt = now
    project.lastOpenedAt = now
    projects.push(project)
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify(projects))
  return project
}

/**
 * 删除项目
 */
export function deleteProject(id) {
  const projects = getAllProjects()
  const filtered = projects.filter(p => p.id !== id)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))
  return filtered
}

/**
 * 更新项目最后打开时间
 */
export function updateLastOpened(id) {
  const projects = getAllProjects()
  const project = projects.find(p => p.id === id)
  if (project) {
    project.lastOpenedAt = new Date().toISOString()
    localStorage.setItem(STORAGE_KEY, JSON.stringify(projects))
  }
}

/**
 * 搜索项目
 */
export function searchProjects(query = '') {
  const projects = getAllProjects()

  if (!query) return projects

  const lowerQuery = query.toLowerCase()
  return projects.filter(p =>
    p.name.toLowerCase().includes(lowerQuery) ||
    p.fileName.toLowerCase().includes(lowerQuery)
  )
}
