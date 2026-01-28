<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- Loading -->
      <div v-if="loading" class="text-center py-20">
        <div class="inline-block w-12 h-12 border-4 border-primary-200 border-t-primary-500 rounded-full animate-spin"></div>
        <p class="mt-4 text-gray-500">正在生成报告...</p>
      </div>

      <!-- Report Content -->
      <div v-else-if="report" class="fade-in">
        <!-- Header -->
        <div class="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <div class="flex items-start justify-between mb-6">
            <div>
              <h1 class="text-2xl font-bold text-gray-800 mb-2">面试报告</h1>
              <p class="text-gray-500">
                {{ report.candidate_name || '候选人' }}
                <span v-if="report.position"> · {{ report.position }}</span>
              </p>
            </div>
            <div class="text-right">
              <div class="text-4xl font-bold text-primary-600">{{ report.total_score }}</div>
              <div class="text-sm text-gray-500">综合得分</div>
            </div>
          </div>

          <!-- Stats -->
          <div class="grid grid-cols-3 gap-4">
            <div class="bg-gray-50 rounded-xl p-4 text-center">
              <div class="text-2xl font-bold text-gray-800">{{ report.total_questions }}</div>
              <div class="text-sm text-gray-500">总题数</div>
            </div>
            <div class="bg-green-50 rounded-xl p-4 text-center">
              <div class="text-2xl font-bold text-green-600">{{ report.correct_count }}</div>
              <div class="text-sm text-gray-500">正确数</div>
            </div>
            <div class="bg-blue-50 rounded-xl p-4 text-center">
              <div class="text-2xl font-bold text-blue-600">{{ formatDuration(report.interview_duration) }}</div>
              <div class="text-sm text-gray-500">用时</div>
            </div>
          </div>
        </div>

        <!-- Ability Scores -->
        <div class="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <h2 class="text-xl font-bold text-gray-800 mb-6">能力评估</h2>
          <div class="space-y-4">
            <div>
              <div class="flex justify-between mb-2">
                <span class="text-gray-700">逻辑思维能力</span>
                <span class="font-semibold text-gray-800">{{ report.logic_ability }}分</span>
              </div>
              <div class="progress-bar">
                <div class="progress-bar-fill bg-blue-500" :style="{ width: report.logic_ability + '%' }"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between mb-2">
                <span class="text-gray-700">表达能力</span>
                <span class="font-semibold text-gray-800">{{ report.expression_ability }}分</span>
              </div>
              <div class="progress-bar">
                <div class="progress-bar-fill bg-green-500" :style="{ width: report.expression_ability + '%' }"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between mb-2">
                <span class="text-gray-700">问题解决能力</span>
                <span class="font-semibold text-gray-800">{{ report.problem_solving }}分</span>
              </div>
              <div class="progress-bar">
                <div class="progress-bar-fill bg-purple-500" :style="{ width: report.problem_solving + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Strengths & Weaknesses -->
        <div class="grid md:grid-cols-2 gap-6 mb-6">
          <div class="bg-white rounded-2xl shadow-lg p-6">
            <h3 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
              <svg class="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              优势
            </h3>
            <ul class="space-y-2">
              <li v-for="(strength, index) in report.strengths" :key="index" 
                  class="flex items-start text-gray-700">
                <span class="w-2 h-2 bg-green-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                {{ strength }}
              </li>
            </ul>
          </div>
          <div class="bg-white rounded-2xl shadow-lg p-6">
            <h3 class="text-lg font-bold text-gray-800 mb-4 flex items-center">
              <svg class="w-5 h-5 text-yellow-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              待改进
            </h3>
            <ul class="space-y-2">
              <li v-for="(weakness, index) in report.weaknesses" :key="index"
                  class="flex items-start text-gray-700">
                <span class="w-2 h-2 bg-yellow-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                {{ weakness }}
              </li>
            </ul>
          </div>
        </div>

        <!-- Question Details -->
        <div class="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <h2 class="text-xl font-bold text-gray-800 mb-6">答题详情</h2>
          <div class="space-y-4">
            <div v-for="(qr, index) in report.question_reports" :key="index"
                 class="border border-gray-200 rounded-xl p-4">
              <div class="flex items-start justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span :class="[
                    'w-6 h-6 rounded-full flex items-center justify-center text-white text-sm',
                    qr.is_correct ? 'bg-green-500' : 'bg-red-500'
                  ]">
                    {{ index + 1 }}
                  </span>
                  <span class="font-medium text-gray-800">{{ qr.question_title }}</span>
                </div>
                <span class="text-sm font-medium" :class="qr.is_correct ? 'text-green-600' : 'text-red-600'">
                  {{ qr.score }}分
                </span>
              </div>
              <div class="text-sm text-gray-600 ml-8">
                <p>难度：{{ getDifficultyLabel(qr.difficulty) }} | 类型：{{ getTypeLabel(qr.question_type) }}</p>
                <p class="mt-1">{{ qr.evaluation_summary }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Overall Comment -->
        <div class="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">总体评价</h2>
          <p class="text-gray-700 leading-relaxed mb-4">{{ report.overall_comment }}</p>
          <div class="bg-primary-50 rounded-xl p-4">
            <h4 class="font-semibold text-primary-800 mb-2">建议</h4>
            <p class="text-primary-700">{{ report.recommendation }}</p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-4 justify-center">
          <button
            @click="goHome"
            class="px-8 py-3 bg-white text-gray-700 font-semibold rounded-xl shadow-md hover:shadow-lg transition-all"
          >
            返回首页
          </button>
          <button
            @click="startNew"
            class="px-8 py-3 bg-primary-500 text-white font-semibold rounded-xl shadow-lg hover:bg-primary-600 transition-all"
          >
            重新面试
          </button>
        </div>
      </div>

      <!-- Error -->
      <div v-else class="text-center py-20">
        <p class="text-gray-500 mb-4">报告加载失败</p>
        <button @click="goHome" class="text-primary-600 hover:text-primary-700">
          返回首页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useInterviewStore } from '@/stores/interview'

const props = defineProps({
  sessionId: String
})

const router = useRouter()
const interviewStore = useInterviewStore()

const loading = ref(true)
const report = ref(null)

const formatDuration = (seconds) => {
  if (!seconds) return '0分钟'
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  if (minutes === 0) return `${secs}秒`
  if (secs === 0) return `${minutes}分钟`
  return `${minutes}分${secs}秒`
}

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

const goHome = () => {
  interviewStore.reset()
  router.push('/')
}

const startNew = () => {
  interviewStore.reset()
  router.push('/interview')
}

onMounted(async () => {
  try {
    // 如果store中已有报告，直接使用
    if (interviewStore.report) {
      report.value = interviewStore.report
    } else {
      // 从服务器获取
      await interviewStore.fetchReport()
      report.value = interviewStore.report
    }
  } catch (error) {
    console.error('Failed to load report:', error)
  } finally {
    loading.value = false
  }
})
</script>
