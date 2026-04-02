import { defineStore } from 'pinia'
import { generateTasks, reviewTask, reviewTaskSlices, generateConclusion } from '../services/hiagentService'
import { getAllProjects, saveProject, deleteProject } from '../services/projectService'

export const useAppStore = defineStore('app', {
  state: () => ({
    // 招标信息
    requirementText: '',

    // 投标文件切片
    bidSlices: [],  // 切片内容数组 [{index, title, level, content, startLine, endLine}]
    sliceMetadata: [],  // 切片元数据 [{index, title, level, startLine, endLine}]
    contextText: '',  // 单个文本输入（保留兼容性）

    // 任务列表
    tasks: [],
    selectedTaskId: null,

    // 审核状态
    reviewing: false,

    // API状态
    apiStatus: null,

    // UI状态
    loading: false,
    error: null,

    // 模版功能
    templateDrawerOpen: false,           // 模版库抽屉开关
    currentEditingTemplate: null,        // 当前编辑的模版
    appliedTemplateHistory: [],           // 应用历史（用于撤销）

    // 新布局状态
    currentTab: 'upload',               // 当前Tab
    wordDocument: null,                  // Word文档文件对象
    wordDocumentWithBookmarks: null,     // 带书签的Word文档文件对象
    highlightLine: null,                 // 高亮行号
    previewMode: 'original',             // 预览模式 (original/slice)
    projectName: '',                     // 项目名称
    sliceLevel: 0,                       // 切片层级
    selectedSliceIndex: null,           // 当前选中的切片索引

    // 项目管理
    currentProjectId: null,              // 当前项目ID
    projects: []                         // 项目列表
  }),

  getters: {
    // 获取选中的任务
    selectedTask: (state) => {
      return state.tasks.find(task => task.id === state.selectedTaskId)
    },

    // 获取任务统计
    taskStats: (state) => {
      const total = state.tasks.length
      const reviewed = state.tasks.filter(task => task.review).length
      const passed = state.tasks.filter(task => task.review?.conclusion === '通过').length
      const failed = state.tasks.filter(task => task.review?.conclusion === '不通过').length
      const pending = state.tasks.filter(task => task.review?.conclusion === '待确认').length

      return { total, reviewed, passed, failed, pending }
    },

    // 是否可以开始分析
    canAnalyze: (state) => {
      return state.requirementText.trim()
    },

    // 是否可以开始审核
    canReview: (state) => {
      return state.selectedTask && !state.selectedTask.review && !state.reviewing
    },

    // 是否使用多切片审核
    useSliceReview: (state) => {
      return state.bidSlices.length > 0
    },

    // 是否可以撤销模版应用
    canUndoTemplateApplication: (state) => {
      return state.appliedTemplateHistory.length > 0
    },

    // 当前Tab对应的组件
    currentTabComponent: (state) => {
      const tabMap = {
        'upload': 'UploadTab',
        'create-task': 'CreateTaskTab',
        'task-list': 'TaskListTab',
        'review-result': 'ReviewResultTab'
      }
      return tabMap[state.currentTab] || 'UploadTab'
    },

    // 是否为Word预览模式
    isWordPreviewMode: (state) => {
      return state.wordDocument !== null
    }
  },

  actions: {
    // 设置招标信息
    setRequirement(text) {
      this.requirementText = text
    },

    // 设置投标文件切片
    setBidSlices(slices) {
      this.bidSlices = slices
    },

    // 设置切片元数据
    setSliceMetadata(metadata) {
      this.sliceMetadata = metadata
    },

    // 清空招标信息
    clearRequirement() {
      this.requirementText = ''
    },

    // 清空投标文件
    clearBidFile() {
      this.bidSlices = []
      this.contextText = ''
    },

    // 设置任务列表
    setTasks(tasks) {
      this.tasks = tasks
    },

    // 选择任务
    selectTask(taskId) {
      this.selectedTaskId = taskId
    },

    // 更新任务
    updateTask(taskId, updates) {
      const index = this.tasks.findIndex(task => task.id === taskId)
      if (index !== -1) {
        this.tasks[index] = { ...this.tasks[index], ...updates }
      }
    },

    // 添加任务
    addTask(task) {
      this.tasks.push(task)
    },

    // 开始审核
    startReviewing() {
      this.reviewing = true
    },

    // 结束审核
    endReviewing() {
      this.reviewing = false
    },

    // 设置加载状态
    setLoading(loading) {
      this.loading = loading
    },

    // 设置错误
    setError(error) {
      this.error = error
    },

    // 清空错误
    clearError() {
      this.error = null
    },

    // 重置所有状态
    reset() {
      this.requirementText = ''
      this.bidSlices = []
      this.contextText = ''
      this.tasks = []
      this.selectedTaskId = null
      this.reviewing = false
      this.loading = false
      this.error = null
      this.apiStatus = null
    },

    // 生成任务
    async generateTasks() {
      if (!this.requirementText) {
        throw new Error('招标文件信息（requirement）不能为空')
      }

      this.setLoading(true)
      this.clearError()

      try {
        // 调用 hiagent API - 只传递 requirement
        const response = await generateTasks({
          requirement: this.requirementText
        })

        // 处理后端返回的任务数据，确保有 title 和 description 字段
        const tasksWithTime = response.data.map((task, index) => ({
          id: Date.now() + Math.random() + index, // 始终生成唯一 id，避免后端返回重复 id 的问题
          title: task.task || task.content || `任务 ${index + 1}`,
          description: '',  // 留空，避免重复显示
          subtasks: task.subtasks || [],
          createdAt: new Date(),
          updatedAt: new Date()
        }))

        // 追加模式：将新任务追加到现有任务列表
        this.tasks = [...this.tasks, ...tasksWithTime]
        return [...this.tasks, ...tasksWithTime]
      } catch (error) {
        console.error('生成任务失败:', error)
        this.setError(error.message || '生成任务失败，请重试')
        throw error
      } finally {
        this.setLoading(false)
      }
    },

    // 审核任务（单个文本输入）
    async reviewTask(taskId) {
      if (!taskId) {
        throw new Error('任务ID不能为空')
      }

      // 获取任务对象
      const task = this.tasks.find(t => t.id === taskId)
      if (!task) {
        throw new Error('任务不存在')
      }

      this.setLoading(true)
      this.clearError()
      this.startReviewing()

      try {
        // 如果有切片，使用切片审核；否则检查 contextText
        if (this.bidSlices.length > 0) {
          await this.reviewTaskWithSlices(taskId)
        } else {
          if (!this.contextText) {
            throw new Error('投标文件不能为空')
          }
          // 调用 hiagent API - 传递 task 和 context
          const response = await reviewTask({
            task,
            context: this.contextText
          })
        }

        // 更新任务
        this.updateTask(taskId, {
          review: {
            ...response.data,
            createdAt: new Date()
          },
          updatedAt: new Date()
        })

        return response.data
      } catch (error) {
        console.error('审核任务失败:', error)
        this.setError(error.message || '审核任务失败，请重试')
        throw error
      } finally {
        this.setLoading(false)
        this.endReviewing()
      }
    },

    // 多切片审核任务
    async reviewTaskWithSlices(taskId) {
      if (!taskId) {
        throw new Error('任务ID不能为空')
      }

      if (this.bidSlices.length === 0) {
        throw new Error('投标文件切片不能为空')
      }

      // 获取任务对象
      const task = this.tasks.find(t => t.id === taskId)
      if (!task) {
        throw new Error('任务不存在')
      }

      this.setLoading(true)
      this.clearError()
      this.startReviewing()

      try {
        // 调用多切片审核 API - 提取纯内容数组
        const slicesContent = this.bidSlices.map(slice =>
          typeof slice === 'string' ? slice : (slice.content || '')
        )
        const response = await reviewTaskSlices({
          task,
          slices: slicesContent
        })

        const reviews = response.data?.slices_reviews || []

        // 为每个切片审核结果注入行号信息，创建新数组确保引用正确
        const reviewsWithLineNumbers = reviews.map((review, index) => ({
          ...review,
          lineNumber: this.sliceMetadata[index]?.startLine || null,
          sliceTitle: this.sliceMetadata[index]?.title || '',
          level: this.sliceMetadata[index]?.level || 0
        }))

        // 调用 generate-conclusion 生成最终结论 - 格式化reviews为LLM需要的结构
        const conclusionReviews = reviewsWithLineNumbers.map(r => ({
          title: r.sliceTitle,
          suggestion: r.suggestion,
          evidence: r.evidence || 'null'
        }))

        // task 直接使用 title 字符串
        const taskText = typeof task === 'object' ? task.title : task

        const conclusionResponse = await generateConclusion({
          task: taskText,
          reviews: conclusionReviews
        })

        // 从 reasons 数组中收集所有 evidence 行号，拼接为 bidSource
        const reasons = conclusionResponse.data?.reason ?? []
        const allEvidence = reasons
          .map(r => r.evidence)
          .filter(e => e && e !== '')
          .join(', ')

        // 更新任务
        this.updateTask(taskId, {
          review: {
            ...response.data,
            slices_reviews: reviewsWithLineNumbers,
            conclusion: conclusionResponse.data?.conclusion || '待确认',
            reason: reasons,
            evidence: '',
            bidSource: allEvidence || '',
            requirementSource: '招标要求',
            createdAt: new Date()
          },
          updatedAt: new Date()
        })

        return response.data
      } catch (error) {
        console.error('多切片审核任务失败:', error)
        this.setError(error.message || '审核任务失败，请重试')
        throw error
      } finally {
        this.setLoading(false)
        this.endReviewing()
      }
    },

    // 获取 API 状态
    async checkApiStatus() {
      try {
        const { getApiStatus } = await import('../services/hiagentService')
        this.apiStatus = await getApiStatus()
        return this.apiStatus
      } catch (error) {
        this.apiStatus = {
          status: 'error',
          message: error.message || '无法连接到服务器'
        }
        return this.apiStatus
      }
    },

    // 获取带书签的预览文档
    async fetchPreviewWithBookmarks(file) {
      if (!file) {
        throw new Error('文件不能为空')
      }

      try {
        const formData = new FormData()
        formData.append('file', file)

        const response = await fetch('/document/preview-with-bookmarks', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          throw new Error('获取预览失败')
        }

        const result = await response.json()

        if (result.code !== 200) {
          throw new Error(result.message || '获取预览失败')
        }

        const { fileData, filename } = result.data

        // 将 base64 转换为 File 对象
        const byteCharacters = atob(fileData)
        const byteNumbers = new Array(byteCharacters.length)
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i)
        }
        const byteArray = new Uint8Array(byteNumbers)
        const blob = new Blob([byteArray], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })
        const bookmarkedFile = new File([blob], filename || 'preview.docx', {
          type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        })

        this.wordDocumentWithBookmarks = bookmarkedFile
        console.log('带书签预览文档已加载:', bookmarkedFile.name)
        return bookmarkedFile
      } catch (error) {
        console.error('获取带书签预览失败:', error)
        this.setError(error.message || '获取带书签预览失败')
        throw error
      }
    },

    // 切片文档
    async sliceDocument(file, maxLevel = 0) {
      if (!file) {
        throw new Error('文件不能为空')
      }

      this.setLoading(true)
      this.clearError()

      try {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('max_level', maxLevel)

        const response = await fetch('/document/slice', {
          method: 'POST',
          body: formData
        })

        if (!response.ok) {
          throw new Error('切片失败')
        }

        const result = await response.json()

        if (result.code !== 200) {
          throw new Error(result.message || '切片失败')
        }

        const { slices } = result.data

        // 转换切片数据为 bidSlices 格式
        this.sliceMetadata = slices.map(s => ({
          index: s.index,
          title: s.title,
          level: s.level,
          startLine: s.startLine,
          endLine: s.endLine || s.startLine
        }))

        // 转换内容为纯文本（使用 alltomarkdown 格式：<!--id--> 标记）
        this.bidSlices = slices.map(s => {
          let contentText = ''
          let inTable = false

          s.content.forEach((item, idx) => {
            const idMarker = `<!-- ${item.id || item.line} -->`

            if (item.type === 'heading') {
              contentText += `${idMarker} ${'#'.repeat(item.level)} ${item.text}\n`
              inTable = false
            } else if (item.type === 'paragraph') {
              contentText += `${idMarker} ${item.text}\n`
              inTable = false
            } else if (item.type === 'table-row') {
              // 表格：检查是否是新的表格（当前一行不是表格的最后一行）
              const nextItem = s.content[idx + 1]
              const isLastRow = !nextItem || nextItem.type !== 'table-row'

              if (!inTable) {
                // 第一个表格行，作为表头
                contentText += `${idMarker} | ${item.data.join(' | ')} |\n`
                contentText += `${' '.repeat(idMarker.length)}| ${item.data.map(() => '---').join(' | ')} |\n`
              } else {
                contentText += `${idMarker} | ${item.data.join(' | ')} |\n`
              }
              inTable = !isLastRow
            } else if (item.type === 'image') {
              contentText += `${idMarker} ${item.text}\n`
              inTable = false
            }
          })

          return {
            index: s.index,
            title: s.title,
            level: s.level,
            content: contentText.trim(),
            startLine: s.startLine,
            endLine: s.endLine || s.startLine
          }
        })

        console.log('文档切片完成:', this.sliceMetadata.length, '个切片')

        // 切片完成后，获取带书签的预览文档
        // 注意：这里使用传入的 file 参数，需要先切片获取 line_no 才能写入书签
        // 但书签需要在切片时写入，所以这里单独调用预览接口
        // 由于文件已上传，我们使用 wordDocument 字段
        if (this.wordDocument) {
          try {
            await this.fetchPreviewWithBookmarks(this.wordDocument)
          } catch (e) {
            console.warn('获取带书签预览失败，将使用原始文档:', e)
          }
        }

        return this.bidSlices
      } catch (error) {
        console.error('文档切片失败:', error)
        this.setError(error.message || '文档切片失败')
        throw error
      } finally {
        this.setLoading(false)
      }
    },

    // ========== 模版功能相关 ==========

    // 打开模版库抽屉
    openTemplateDrawer() {
      this.templateDrawerOpen = true
    },

    // 关闭模版库抽屉
    closeTemplateDrawer() {
      this.templateDrawerOpen = false
    },

    // 切换模版库抽屉
    toggleTemplateDrawer() {
      this.templateDrawerOpen = !this.templateDrawerOpen
    },

    // 设置当前编辑的模版
    setCurrentEditingTemplate(template) {
      this.currentEditingTemplate = template
    },

    // 清空当前编辑的模版
    clearCurrentEditingTemplate() {
      this.currentEditingTemplate = null
    },

    // 应用模版到任务列表
    applyTemplate(template) {
      if (!template || !template.tasks || template.tasks.length === 0) {
        return
      }

      // 保存当前任务列表到历史记录（用于撤销）
      this.appliedTemplateHistory.push([...this.tasks])

      // 将模版任务追加到现有任务列表
      const newTasks = template.tasks.map(task => ({
        id: Date.now() + Math.random(),
        title: typeof task === 'string' ? task : task.title,
        description: '',
        subtasks: [],
        createdAt: new Date(),
        updatedAt: new Date()
      }))

      this.tasks = [...this.tasks, ...newTasks]

      // 清空选中状态
      this.selectedTaskId = null
    },

    // 撤销最近一次模版应用
    undoTemplateApplication() {
      if (this.appliedTemplateHistory.length === 0) {
        return false
      }

      // 恢复上一个任务列表状态
      this.tasks = this.appliedTemplateHistory.pop()
      this.selectedTaskId = null
      return true
    },

    // 清空应用历史
    clearTemplateHistory() {
      this.appliedTemplateHistory = []
    },

    // ========== 新布局相关 ==========

    // 设置当前Tab
    setCurrentTab(tabId) {
      const validTabs = ['upload', 'create-task', 'task-list', 'review-result']
      if (validTabs.includes(tabId)) {
        this.currentTab = tabId
      }
    },

    // 设置Word文档
    setWordDocument(file) {
      this.wordDocument = file
    },

    // 设置高亮行
    setHighlightLine(lineNumber) {
      this.highlightLine = lineNumber
    },

    // 设置预览模式
    setPreviewMode(mode) {
      const validModes = ['original', 'slice']
      if (validModes.includes(mode)) {
        this.previewMode = mode
      }
    },

    // 设置项目名称
    setProjectName(name) {
      this.projectName = name
    },

    // 设置切片层级
    setSliceLevel(level) {
      this.sliceLevel = level
    },

    // 设置选中的切片索引
    setSelectedSliceIndex(index) {
      this.selectedSliceIndex = index
    },

    // ========== 项目管理相关 ==========

    // 加载所有项目
    loadProjects() {
      this.projects = getAllProjects()
    },

    // 创建项目
    createProject(projectData) {
      const saved = saveProject(projectData)
      this.loadProjects()
      return saved
    },

    // 选择项目
    selectProject(projectId) {
      this.currentProjectId = projectId
    },

    // 删除项目
    deleteProject(projectId) {
      deleteProject(projectId)
      this.loadProjects()
      if (this.currentProjectId === projectId) {
        this.currentProjectId = null
      }
    },

    // 设置当前项目ID
    setCurrentProjectId(projectId) {
      this.currentProjectId = projectId
    }
  }
})
