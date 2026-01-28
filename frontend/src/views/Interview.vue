<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
        <h1 class="text-xl font-bold text-gray-800">AI 快速面试</h1>
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-500">
            题目 {{ interviewStore.currentIndex + 1 }} / {{ interviewStore.totalQuestions }}
          </span>
          <div class="w-32 progress-bar">
            <div class="progress-bar-fill" :style="{ width: interviewStore.progress + '%' }"></div>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-8">
      <!-- Welcome Screen -->
      <div v-if="showWelcome" class="fade-in">
        <div class="question-card text-center">
          <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-gray-800 mb-4">欢迎参加面试</h2>
          <div class="text-gray-600 whitespace-pre-line mb-8 max-w-md mx-auto">
            {{ welcomeMessage }}
          </div>
          <button
            @click="handleStartInterview"
            :disabled="starting"
            class="inline-flex items-center px-8 py-3 bg-primary-500 hover:bg-primary-600 disabled:bg-gray-400 text-white font-semibold rounded-xl shadow-lg transition-all"
          >
            <span v-if="starting">准备中...</span>
            <span v-else>开始答题</span>
            <svg v-if="!starting" class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Question Screen -->
      <div v-else-if="interviewStore.currentQuestion && !showFeedback" class="fade-in">
        <div class="question-card">
          <!-- Question Header -->
          <div class="flex items-center gap-3 mb-6">
            <span class="px-3 py-1 bg-primary-100 text-primary-700 text-sm font-medium rounded-full">
              {{ getTypeLabel(interviewStore.currentQuestion.type) }}
            </span>
            <span class="px-3 py-1 bg-gray-100 text-gray-600 text-sm font-medium rounded-full">
              {{ getDifficultyLabel(interviewStore.currentQuestion.difficulty) }}
            </span>
          </div>

          <!-- Question Title -->
          <h2 class="text-xl font-bold text-gray-800 mb-4">
            {{ interviewStore.currentQuestion.title }}
          </h2>

          <!-- Question Content -->
          <div class="text-gray-700 whitespace-pre-line mb-6 leading-relaxed">
            {{ interviewStore.currentQuestion.content }}
          </div>

          <!-- Options -->
          <div class="mb-6">
            <p class="text-sm font-medium text-gray-500 mb-3">请选择答案：</p>
            <div class="space-y-3">
              <button
                v-for="option in interviewStore.currentQuestion.options"
                :key="option.key"
                @click="selectedOption = option.key"
                :class="[
                  'option-btn',
                  selectedOption === option.key ? 'selected' : ''
                ]"
              >
                <span class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 text-gray-700 font-semibold mr-3">
                  {{ option.key }}
                </span>
                <span>{{ option.content }}</span>
              </button>
            </div>
          </div>

          <!-- Explanation Input -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              请说明您的解题思路：
            </label>
            <textarea
              v-model="explanation"
              rows="4"
              placeholder="请简要描述您的解题思路和分析过程..."
              class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all resize-none"
            ></textarea>
          </div>

          <!-- Submit Button -->
          <button
            @click="handleSubmit"
            :disabled="!canSubmit || submitting"
            class="w-full py-4 bg-primary-500 hover:bg-primary-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white font-semibold rounded-xl shadow-lg transition-all flex items-center justify-center"
          >
            <span v-if="submitting" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              提交中...
            </span>
            <span v-else>提交答案</span>
          </button>
        </div>
      </div>

      <!-- Feedback Screen -->
      <div v-else-if="showFeedback && interviewStore.lastEvaluation" class="fade-in">
        <div class="question-card">
          <!-- Result Icon -->
          <div class="text-center mb-6">
            <div :class="[
              'w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4',
              interviewStore.lastEvaluation.is_correct ? 'bg-green-100' : 'bg-orange-100'
            ]">
              <svg v-if="interviewStore.lastEvaluation.is_correct" class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else class="w-10 h-10 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 class="text-2xl font-bold" :class="interviewStore.lastEvaluation.is_correct ? 'text-green-600' : 'text-orange-600'">
              {{ interviewStore.lastEvaluation.is_correct ? '回答正确！' : '再想想看' }}
            </h3>
            <p class="text-gray-500 mt-2">得分：{{ interviewStore.lastEvaluation.score }} 分</p>
          </div>

          <!-- Feedback -->
          <div class="bg-gray-50 rounded-xl p-6 mb-6">
            <h4 class="font-semibold text-gray-800 mb-2">面试官反馈</h4>
            <p class="text-gray-700 leading-relaxed">{{ interviewStore.lastEvaluation.feedback }}</p>
          </div>

          <!-- Key Points -->
          <div v-if="interviewStore.lastEvaluation.key_points_hit?.length" class="mb-4">
            <h4 class="font-medium text-gray-700 mb-2">您提到的要点：</h4>
            <div class="flex flex-wrap gap-2">
              <span v-for="point in interviewStore.lastEvaluation.key_points_hit" :key="point"
                    class="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">
                {{ point }}
              </span>
            </div>
          </div>

          <div v-if="interviewStore.lastEvaluation.key_points_missed?.length" class="mb-6">
            <h4 class="font-medium text-gray-700 mb-2">可以补充的要点：</h4>
            <div class="flex flex-wrap gap-2">
              <span v-for="point in interviewStore.lastEvaluation.key_points_missed" :key="point"
                    class="px-3 py-1 bg-yellow-100 text-yellow-700 text-sm rounded-full">
                {{ point }}
              </span>
            </div>
          </div>

          <!-- Next Button -->
          <button
            @click="handleNext"
            class="w-full py-4 bg-primary-500 hover:bg-primary-600 text-white font-semibold rounded-xl shadow-lg transition-all"
          >
            {{ interviewStore.status === 'completed' ? '查看报告' : '下一题' }}
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-else-if="interviewStore.status === 'loading'" class="text-center py-20">
        <div class="inline-block w-12 h-12 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin"></div>
        <p class="mt-4 text-gray-500">加载中...</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useInterviewStore } from '@/stores/interview'

const props = defineProps({
  sessionId: String
})

const router = useRouter()
const route = useRoute()
const interviewStore = useInterviewStore()

const showWelcome = ref(true)
const showFeedback = ref(false)
const starting = ref(false)
const submitting = ref(false)
const selectedOption = ref(null)
const explanation = ref('')

const welcomeMessage = computed(() => {
  return interviewStore.session?.welcome_message || '欢迎参加AI快速面试！'
})

const canSubmit = computed(() => {
  return selectedOption.value && explanation.value.trim().length >= 10
})

const getTypeLabel = (type) => {
  const labels = {
    logic: '逻辑推理',
    math: '数学计算',
    algorithm: '算法思维',
    scenario: '场景分析'
  }
  return labels[type] || type
}

const getDifficultyLabel = (difficulty) => {
  const labels = {
    easy: '简单',
    medium: '中等',
    hard: '困难'
  }
  return labels[difficulty] || difficulty
}

const handleStartInterview = async () => {
  starting.value = true
  try {
    await interviewStore.startInterview()
    showWelcome.value = false
  } catch (error) {
    console.error('Failed to start interview:', error)
    alert('开始面试失败，请重试')
  } finally {
    starting.value = false
  }
}

const handleSubmit = async () => {
  if (!canSubmit.value) return
  
  submitting.value = true
  try {
    await interviewStore.submitAnswer(selectedOption.value, explanation.value)
    showFeedback.value = true
  } catch (error) {
    console.error('Failed to submit answer:', error)
    alert('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

const handleNext = () => {
  if (interviewStore.status === 'completed') {
    // 跳转到报告页
    router.push(`/report/${interviewStore.sessionId}`)
  } else {
    // 显示下一题
    showFeedback.value = false
    selectedOption.value = null
    explanation.value = ''
  }
}

onMounted(async () => {
  // 检查是否有会话
  if (!interviewStore.session && props.sessionId) {
    // 尝试恢复会话（这里简化处理，实际应该从服务器获取）
    router.push('/interview')
  }
})
</script>
