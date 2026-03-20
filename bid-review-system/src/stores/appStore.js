import { defineStore } from 'pinia'
import { generateTasks, reviewTask, reviewTaskSlices } from '../services/hiagentService'
import { getHiAgentType } from '../types'

export const useAppStore = defineStore('app', {
  state: () => ({
    // 招标信息
    requirementType: '',
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
    error: null
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
      return state.requirementText.trim() && (state.contextText.trim() || state.bidSlices.length > 0)
    },

    // 是否可以开始审核
    canReview: (state) => {
      return state.selectedTask && !state.selectedTask.review && !state.reviewing
    },

    // 是否使用多切片审核
    useSliceReview: (state) => {
      return state.bidSlices.length > 0
    }
  },

  actions: {
    // 设置招标信息
    setRequirement(type, text) {
      this.requirementType = type
      this.requirementText = text
    },

    // 设置投标文件切片
    setBidSlices(slices) {
      this.bidSlices = slices
    },

    // 清空招标信息
    clearRequirement() {
      this.requirementType = ''
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
      this.requirementType = ''
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

      if (!this.requirementType) {
        throw new Error('请先选择要求类型（信息核对、招标要求或通用要求）')
      }

      this.setLoading(true)
      this.clearError()

      try {
        // 获取 HiAgent API 的 type 值
        const hiagentType = getHiAgentType(this.requirementType)

        // 调用 hiagent API - 传递 requirement 和 type
        const response = await generateTasks({
          requirement: this.requirementText,
          type: hiagentType
        })

        // 处理后端返回的任务数据，确保有 title 和 description 字段
        const tasksWithTime = response.data.map(task => ({
          id: task.id || Date.now() + Math.random(),  // 确保有 id
          title: task.title || task.content || task.description || `任务 ${task.id}`,
          description: task.description || task.content || '',
          subtasks: task.subtasks || [],
          createdAt: new Date(),
          updatedAt: new Date()
        }))

        this.setTasks(tasksWithTime)
        return tasksWithTime
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

      if (!this.contextText) {
        throw new Error('投标文件（context）不能为空')
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
        // 调用 hiagent API - 传递 task 和 context
        const response = await reviewTask({
          task,
          context: this.contextText
        })

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
    }
  }
})
