import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 面试相关API
export const interviewApi = {
  // 创建面试会话
  createSession(data) {
    return api.post('/interview/sessions', data)
  },

  // 获取会话信息
  getSession(sessionId) {
    return api.get(`/interview/sessions/${sessionId}`)
  },

  // 开始面试
  startInterview(sessionId) {
    return api.post(`/interview/sessions/${sessionId}/start`)
  },

  // 获取当前题目
  getCurrentQuestion(sessionId) {
    return api.get(`/interview/sessions/${sessionId}/current-question`)
  },

  // 提交答案
  submitAnswer(sessionId, data) {
    return api.post(`/interview/sessions/${sessionId}/submit-answer`, data)
  },

  // 获取面试官反馈
  getFeedback(sessionId, questionId) {
    return api.get(`/interview/sessions/${sessionId}/feedback/${questionId}`)
  },

  // 获取面试报告
  getReport(sessionId) {
    return api.get(`/interview/sessions/${sessionId}/report`)
  },

  // 取消面试
  cancelInterview(sessionId) {
    return api.post(`/interview/sessions/${sessionId}/cancel`)
  }
}

// 题库相关API
export const questionApi = {
  // 获取所有题目
  getAllQuestions() {
    return api.get('/questions/')
  },

  // 获取题目类型
  getQuestionTypes() {
    return api.get('/questions/types')
  },

  // 获取难度等级
  getDifficultyLevels() {
    return api.get('/questions/difficulties')
  }
}

export default api
