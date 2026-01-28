<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
    <div class="max-w-xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">面试准备</h1>
        <p class="text-gray-600">请填写基本信息，然后开始面试</p>
      </div>

      <!-- Form Card -->
      <div class="bg-white rounded-2xl shadow-lg p-8">
        <form @submit.prevent="handleStart">
          <!-- 姓名 -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              您的姓名 <span class="text-gray-400">(可选)</span>
            </label>
            <input
              v-model="form.candidateName"
              type="text"
              placeholder="请输入您的姓名"
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            />
          </div>

          <!-- 应聘职位 -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              应聘职位 <span class="text-gray-400">(可选)</span>
            </label>
            <input
              v-model="form.position"
              type="text"
              placeholder="例如：前端工程师、后端开发等"
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            />
          </div>

          <!-- 提示信息 -->
          <div class="bg-blue-50 rounded-xl p-4 mb-6">
            <div class="flex">
              <svg class="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="text-sm text-blue-700">
                <p class="font-medium mb-1">面试说明</p>
                <ul class="list-disc list-inside space-y-1 text-blue-600">
                  <li>面试一旦开始，请勿退出界面</li>
                  <li>每道题请选择答案并说明解题思路</li>
                  <li>AI面试官会根据您的回答给予反馈</li>
                  <li>面试结束后会生成详细报告</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-4 bg-primary-500 hover:bg-primary-600 disabled:bg-gray-400 text-white font-semibold rounded-xl shadow-lg transition-all duration-200 flex items-center justify-center"
          >
            <span v-if="loading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              正在准备...
            </span>
            <span v-else>开始面试</span>
          </button>
        </form>
      </div>

      <!-- Back Link -->
      <div class="text-center mt-6">
        <router-link to="/" class="text-gray-500 hover:text-gray-700 transition-colors">
          ← 返回首页
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore } from '@/stores/interview'

const router = useRouter()
const interviewStore = useInterviewStore()

const loading = ref(false)

const form = reactive({
  candidateName: '',
  position: ''
})

const handleStart = async () => {
  loading.value = true
  
  try {
    // 重置状态
    interviewStore.reset()
    
    // 创建会话（题目数量由系统自动决定）
    await interviewStore.createSession({
      candidate_name: form.candidateName || null,
      position: form.position || null
    })
    
    // 跳转到面试页面
    router.push(`/interview/${interviewStore.sessionId}`)
  } catch (error) {
    console.error('Failed to create session:', error)
    alert('创建面试失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>
