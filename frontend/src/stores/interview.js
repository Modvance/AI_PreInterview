import { defineStore } from 'pinia'
import { interviewApi } from '@/services/api'

export const useInterviewStore = defineStore('interview', {
  state: () => ({
    // 会话信息
    session: null,
    sessionId: null,
    
    // 面试状态
    status: 'idle', // idle, loading, ready, in_progress, completed, error
    
    // 当前题目
    currentQuestion: null,
    currentIndex: 0,
    totalQuestions: 0,
    
    // 答题记录
    answers: [],
    
    // 最近的评估反馈
    lastEvaluation: null,
    
    // 报告
    report: null,
    
    // 错误信息
    error: null
  }),

  getters: {
    // 是否正在面试中
    isInterviewing: (state) => state.status === 'in_progress',
    
    // 进度百分比
    progress: (state) => {
      if (state.totalQuestions === 0) return 0
      return Math.round((state.currentIndex / state.totalQuestions) * 100)
    },
    
    // 是否为最后一题
    isLastQuestion: (state) => state.currentIndex >= state.totalQuestions - 1
  },

  actions: {
    // 创建面试会话
    async createSession(data = {}) {
      this.status = 'loading'
      this.error = null
      
      try {
        const response = await interviewApi.createSession(data)
        this.session = response
        this.sessionId = response.id
        this.totalQuestions = response.question_count
        this.status = 'ready'
        return response
      } catch (error) {
        this.error = error.message || '创建面试失败'
        this.status = 'error'
        throw error
      }
    },

    // 开始面试
    async startInterview() {
      if (!this.sessionId) {
        throw new Error('No session created')
      }
      
      this.status = 'loading'
      
      try {
        const response = await interviewApi.startInterview(this.sessionId)
        
        if (response.success) {
          this.currentQuestion = response.data.question
          this.currentIndex = response.data.current_index
          this.totalQuestions = response.data.total_questions
          this.status = 'in_progress'
        }
        
        return response
      } catch (error) {
        this.error = error.message || '开始面试失败'
        this.status = 'error'
        throw error
      }
    },

    // 提交答案
    async submitAnswer(selectedOption, explanation) {
      if (!this.currentQuestion) {
        throw new Error('No current question')
      }
      
      try {
        const response = await interviewApi.submitAnswer(this.sessionId, {
          question_id: this.currentQuestion.id,
          selected_option: selectedOption,
          explanation: explanation
        })
        
        // 保存评估结果
        this.lastEvaluation = response.evaluation
        
        // 记录答案
        this.answers.push({
          questionId: this.currentQuestion.id,
          selectedOption,
          explanation,
          evaluation: response.evaluation
        })
        
        // 更新题目
        if (response.has_next_question && response.next_question) {
          this.currentQuestion = response.next_question
          this.currentIndex++
        } else {
          // 面试结束
          this.status = 'completed'
          this.currentQuestion = null
        }
        
        return response
      } catch (error) {
        this.error = error.message || '提交答案失败'
        throw error
      }
    },

    // 获取报告
    async fetchReport() {
      if (!this.sessionId) {
        throw new Error('No session')
      }
      
      try {
        const report = await interviewApi.getReport(this.sessionId)
        this.report = report
        return report
      } catch (error) {
        this.error = error.message || '获取报告失败'
        throw error
      }
    },

    // 重置状态
    reset() {
      this.session = null
      this.sessionId = null
      this.status = 'idle'
      this.currentQuestion = null
      this.currentIndex = 0
      this.totalQuestions = 0
      this.answers = []
      this.lastEvaluation = null
      this.report = null
      this.error = null
    }
  }
})
