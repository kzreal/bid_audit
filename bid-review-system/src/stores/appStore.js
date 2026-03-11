import { defineStore } from 'pinia'
import { generateTasks, reviewTask } from '../services/hiagentService'
import { parseHiagentTasks, validateTasks } from '../utils/taskParser'
import { parseReviewResult, validateReview } from '../utils/reviewParser'
import { getHiAgentType } from '../types'

export const useAppStore = defineStore('app', {
  state: () => ({
    // 招标信息
    requirementType: '',
    requirementText: '',

    // 投标文件
    bidText: '',
    contextText: '',
    currentFile: null,

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
      const passed = state.tasks.filter(task => task.review?.status === '通过').length
      const failed = state.tasks.filter(task => task.review?.status === '不通过').length
      const pending = state.tasks.filter(task => task.review?.status === '待确认').length

      return { total, reviewed, passed, failed, pending }
    },

    // 是否可以开始分析
    canAnalyze: (state) => {
      return state.requirementText.trim() && state.contextText.trim()
    },

    // 是否可以开始审核
    canReview: (state) => {
      return state.selectedTask && !state.selectedTask.review && !state.reviewing && state.contextText.trim()
    }
  },

  actions: {
    // 设置招标信息
    setRequirement(type, text) {
      this.requirementType = type
      this.requirementText = text
    },

    // 设置投标文件
    setBidFile(text, file = null) {
      this.bidText = text
      this.contextText = text
      this.currentFile = file
    },

    // 清空招标信息
    clearRequirement() {
      this.requirementType = ''
      this.requirementText = ''
    },

    // 清空投标文件
    clearBidFile() {
      this.bidText = ''
      this.contextText = ''
      this.currentFile = null
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
      this.bidText = ''
      this.contextText = ''
      this.currentFile = null
      this.tasks = []
      this.selectedTaskId = null
      this.reviewing = false
      this.loading = false
      this.error = null
      this.apiStatus = null
    },

    // 生成任务
    // 输入：requirement（招标文件信息）
    async generateTasks(useMock = false) {
      if (!this.requirementText) {
        throw new Error('招标文件信息（requirement）不能为空')
      }

      if (!this.requirementType) {
        throw new Error('请先选择要求类型（信息核对、招标要求或通用要求）')
      }

      this.setLoading(true)
      this.clearError()

      try {
        let response

        // 获取 HiAgent API 的 type 值
        const hiagentType = getHiAgentType(this.requirementType)
        console.log('要求类型:', this.requirementType, 'HiAgent type:', hiagentType)

        if (useMock) {
          // 使用模拟数据
          const { mockTaskResponse, mockDelay } = await import('../utils/mockData')
          await mockDelay(1500)
          response = mockTaskResponse
        } else {
          // 调用 hiagent API - 传递 requirement 和 type
          response = await generateTasks({
            requirement: this.requirementText,
            type: hiagentType
          })
        }

        // 解析任务
        console.log('HiAgent API 原始响应:', response)
        const parsedTasks = parseHiagentTasks(response)
        console.log('解析后的任务:', parsedTasks)

        // 验证任务
        const validation = validateTasks(parsedTasks)
        if (!validation.valid) {
          throw new Error(`任务验证失败: ${validation.errors.join(', ')}`)
        }

        // 添加时间戳
        const tasksWithTime = parsedTasks.map(task => ({
          ...task,
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

    // 审核任务
    // 输入：task（一条任务）+ context（投标文件）
    // 需要重复调用直至处理完所有任务
    async reviewTask(taskId, useMock = false) {
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

      try {
        let response

        if (useMock) {
          // 使用模拟数据
          const { mockReviewResults, mockDelay } = await import('../utils/mockData')
          await mockDelay(2000)

          // 根据任务 ID 选择不同的模拟结果
          const mockId = taskId % 3
          response = mockReviewResults[mockId === 0 ? 'pass' : mockId === 1 ? 'fail' : 'pending']
        } else {
          // 调用 hiagent API - 传递 task 和 context
          response = await reviewTask({
            task,
            context: this.contextText
          })
        }

        // 解析审核结果
        const parsedReview = parseReviewResult(response)

        // 验证审核结果
        const validation = validateReview(parsedReview)
        if (!validation.valid) {
          console.warn('审核结果验证失败:', validation.errors)
        }

        // 更新任务
        this.updateTask(taskId, {
          review: {
            ...parsedReview,
            createdAt: new Date()
          },
          updatedAt: new Date()
        })

        return parsedReview
      } catch (error) {
        console.error('审核任务失败:', error)
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