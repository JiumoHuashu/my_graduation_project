<template>
  <div class="user-reading-profile">
    <header class="profile-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h1>阅读基因画像</h1>
    </header>

    <div class="profile-container">
      <div class="profile-card">
        <div class="profile-avatar">
          <img :src="userInfo.avatar" alt="用户头像">
        </div>
        <h2 class="profile-username">{{ userInfo.username }}</h2>
        <p class="profile-email">{{ userInfo.email }}</p>
        <p class="profile-joined">加入时间: {{ formatDate(userInfo.joined_date) }}</p>
      </div>

      <div class="reading-stats-card">
        <h3 class="section-title">阅读统计</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <el-statistic :value="readingStats.total_books" label="总阅读书籍" />
          </div>
          <div class="stat-item">
            <el-statistic :value="readingStats.avg_reading_frequency" :precision="2" label="平均阅读频率(本/天)" />
          </div>
        </div>
      </div>

      <div class="charts-container">
        <div class="chart-card">
          <h3 class="section-title">阅读基因</h3>
          <div ref="radarChartRef" class="chart"></div>
        </div>

        <div class="chart-card">
          <h3 class="section-title">阅读题材分布</h3>
          <div ref="pieChartRef" class="chart"></div>
        </div>
      </div>

      <div class="word-count-card">
        <h3 class="section-title">字数偏好</h3>
        <div class="word-count-ranges">
          <div class="word-count-item">
            <span class="word-count-label">短篇 (< 50万)</span>
            <div class="word-count-bar">
              <div class="word-count-fill" :style="{ width: `${(readingStats.word_count_ranges.short / totalBooks) * 100}%` }"></div>
            </div>
            <span class="word-count-value">{{ readingStats.word_count_ranges.short }}</span>
          </div>
          <div class="word-count-item">
            <span class="word-count-label">中篇 (50-150万)</span>
            <div class="word-count-bar">
              <div class="word-count-fill" :style="{ width: `${(readingStats.word_count_ranges.medium / totalBooks) * 100}%` }"></div>
            </div>
            <span class="word-count-value">{{ readingStats.word_count_ranges.medium }}</span>
          </div>
          <div class="word-count-item">
            <span class="word-count-label">长篇 (> 150万)</span>
            <div class="word-count-bar">
              <div class="word-count-fill" :style="{ width: `${(readingStats.word_count_ranges.long / totalBooks) * 100}%` }"></div>
            </div>
            <span class="word-count-value">{{ readingStats.word_count_ranges.long }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElStatistic } from 'element-plus'

const router = useRouter()

const userInfo = ref({
  username: '',
  email: '',
  avatar: '',
  joined_date: ''
})

const readingStats = ref({
  total_books: 0,
  category_percentage: {},
  word_count_ranges: {
    short: 0,
    medium: 0,
    long: 0
  },
  avg_reading_frequency: 0
})

const readingGene = ref({
  '玄幻度': 0,
  '情感度': 0,
  '逻辑性': 0,
  '热血度': 0,
  '科技感': 0,
  '历史感': 0
})

const radarChartRef = ref(null)
const pieChartRef = ref(null)
const radarChart = ref(null)
const pieChart = ref(null)

const totalBooks = computed(() => {
  return readingStats.value.total_books || 1
})

const goBack = () => {
  router.back()
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchUserProfile = async () => {
  try {
    const savedUser = localStorage.getItem('user')
    if (!savedUser) {
      alert('请先登录')
      router.push('/')
      return
    }

    const user = JSON.parse(savedUser)
    const res = await axios.get('http://127.0.0.1:8000/api/user/profile/stats/', {
      params: { user_id: user.id }
    })

    if (res.data.code === 200) {
      userInfo.value = res.data.data.user_info
      readingStats.value = res.data.data.reading_stats
      readingGene.value = res.data.data.reading_gene
      
      // 初始化图表
      initCharts()
    } else {
      alert(res.data.msg)
    }
  } catch (error) {
    console.error('获取用户个人资料失败:', error)
    alert('获取用户个人资料失败，请检查网络连接')
  }
}

const initCharts = () => {
  // 初始化雷达图
  if (radarChartRef.value) {
    radarChart.value = echarts.init(radarChartRef.value)
    const radarOption = {
      title: {
        text: '阅读基因雷达图',
        left: 'center'
      },
      tooltip: {},
      radar: {
        indicator: [
          { name: '玄幻度', max: 100 },
          { name: '情感度', max: 100 },
          { name: '逻辑性', max: 100 },
          { name: '热血度', max: 100 },
          { name: '科技感', max: 100 },
          { name: '历史感', max: 100 }
        ]
      },
      series: [{
        name: '阅读基因',
        type: 'radar',
        data: [{
          value: Object.values(readingGene.value),
          name: '阅读基因',
          areaStyle: {
            opacity: 0.3
          }
        }]
      }]
    }
    radarChart.value.setOption(radarOption)
  }

  // 初始化饼图
  if (pieChartRef.value) {
    pieChart.value = echarts.init(pieChartRef.value)
    const pieOption = {
      title: {
        text: '阅读题材分布',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [{
        name: '阅读题材',
        type: 'pie',
        radius: '50%',
        data: Object.entries(readingStats.value.category_percentage).map(([name, value]) => ({
          name,
          value
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    }
    pieChart.value.setOption(pieOption)
  }
}

const handleResize = () => {
  if (radarChart.value) {
    radarChart.value.resize()
  }
  if (pieChart.value) {
    pieChart.value.resize()
  }
}

onMounted(() => {
  fetchUserProfile()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.user-reading-profile {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: #ffffff;
  min-height: 100vh;
  padding-bottom: 48px;
}

.profile-header {
  background: #ffffff;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 10px 20px;
  border-radius: 50px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 400;
  letter-spacing: -0.14px;
  transition: opacity 0.2s;
}

.back-btn:hover {
  opacity: 0.85;
}

.back-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

.profile-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 540;
  letter-spacing: -0.26px;
  color: #000000;
}

.profile-container {
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 24px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

.profile-card {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 32px;
  text-align: center;
}

.profile-avatar {
  position: relative;
  display: inline-block;
  margin-bottom: 16px;
}

.profile-avatar img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(0, 0, 0, 0.08);
  transition: opacity 0.2s;
}

.profile-username {
  font-size: 24px;
  color: #000000;
  margin: 0 0 8px 0;
  font-weight: 540;
  letter-spacing: -0.26px;
}

.profile-email {
  font-size: 16px;
  color: #666666;
  margin: 0 0 8px 0;
  font-weight: 330;
  letter-spacing: -0.14px;
}

.profile-joined {
  font-size: 14px;
  color: #999999;
  margin: 0;
  font-weight: 320;
  letter-spacing: -0.1px;
}

.reading-stats-card {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 24px;
}

.section-title {
  font-size: 18px;
  color: #000000;
  margin: 0 0 20px 0;
  font-weight: 540;
  letter-spacing: -0.14px;
  padding-left: 12px;
  border-left: 2px solid #000000;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.stat-item {
  text-align: center;
}

.charts-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 768px) {
  .charts-container {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 24px;
}

.chart {
  width: 100%;
  height: 400px;
}

.word-count-card {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 24px;
}

.word-count-ranges {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.word-count-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.word-count-label {
  width: 120px;
  font-size: 14px;
  color: #666666;
  font-weight: 320;
  letter-spacing: -0.1px;
}

.word-count-bar {
  flex: 1;
  height: 12px;
  background: #f0f0f0;
  border-radius: 6px;
  overflow: hidden;
}

.word-count-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #45a049);
  border-radius: 6px;
  transition: width 0.3s ease;
}

.word-count-value {
  width: 40px;
  text-align: right;
  font-size: 14px;
  color: #000000;
  font-weight: 400;
  letter-spacing: -0.1px;
}

.dark-mode .user-reading-profile {
  background: #000000 !important;
  color: #ffffff !important;
}

.dark-mode .profile-header {
  background: #000000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-mode .profile-header h1 {
  color: #ffffff;
}

.dark-mode .back-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .back-btn:hover {
  opacity: 0.85;
}

.dark-mode .profile-card,
.dark-mode .reading-stats-card,
.dark-mode .chart-card,
.dark-mode .word-count-card {
  background: #0a0a0a;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-mode .profile-username {
  color: #ffffff;
}

.dark-mode .profile-email {
  color: #b0b0b0;
}

.dark-mode .profile-joined {
  color: #888888;
}

.dark-mode .section-title {
  color: #ffffff;
  border-left-color: #ffffff;
}

.dark-mode .word-count-label {
  color: #b0b0b0;
}

.dark-mode .word-count-bar {
  background: #2a2a2a;
}

.dark-mode .word-count-value {
  color: #ffffff;
}
</style>