import { defineStore } from 'pinia'
import { generateTasks, reviewTask, reviewTaskSlices, generateConclusion } from '../services/hiagentService'

export const useAppStore = defineStore('app', {
  state: () => ({
    // 招标信息
    requirementText: '',

    // 投标文件切片
    bidSlices: [],  // 切片内容数组
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
    appliedTemplateHistory: []           // 应用历史（用于撤销）
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
        const tasksWithTime = response.data.map(task => ({
          id: task.id || Date.now() + Math.random(),
          title: task.task || task.content || `任务 ${task.id}`,
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

        // 调用 generate-conclusion 生成最终结论
        const conclusionResponse = await generateConclusion({
          task,
          reviews
        })

        // 更新任务
        this.updateTask(taskId, {
          review: {
            ...response.data,
            conclusion: conclusionResponse.data?.conclusion || '待确认',
            reason: conclusionResponse.data?.reason || '',
            evidence: conclusionResponse.data?.evidence || '待补充',
            bidSource: conclusionResponse.data?.evidence || '待补充',
            requirementSource: conclusionResponse.data?.requirementSource || '招标要求',
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
    }
  }
})
