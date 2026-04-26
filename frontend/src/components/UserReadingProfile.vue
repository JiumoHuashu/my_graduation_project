<template>
  <div class="user-reading-profile">
    <header class="profile-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h1>阅读基因画像</h1>
    </header>

    <div class="profile-container">
      <!-- 左侧用户信息卡片 -->
      <div class="profile-sidebar">
        <div class="profile-card">
          <div class="profile-avatar">
            <img :src="userInfo.avatar" alt="用户头像">
          </div>
          <h2 class="profile-username">{{ userInfo.username }}</h2>
          <p class="profile-email">{{ userInfo.email }}</p>
          <p class="profile-joined">加入时间: {{ formatDate(userInfo.joined_date) }}</p>
        </div>
      </div>

      <!-- 右侧数据展示区 -->
      <div class="profile-content">
        <!-- 阅读统计指标 -->
        <div class="reading-stats">
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

        <!-- 图表区域 -->
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

        <!-- 字数偏好 -->
        <div class="word-count-section">
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElStatistic } from 'element-plus'
import defaultAvatar from '../assets/avatars/OIP-C.webp'

const router = useRouter()

const userInfo = ref({
  username: '',
  email: '',
  avatar: defaultAvatar,
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

    const localUser = JSON.parse(savedUser)
    const res = await axios.get('http://127.0.0.1:8000/api/user/profile/stats/', {
      params: { user_id: localUser.id }
    })

    if (res.data.code === 200) {
      const userData = res.data.data.user_info
      // 确保用户数据包含头像字段，优先使用 localStorage 中的头像，然后是后端返回的头像，最后是默认头像
      userInfo.value = {
        ...userData,
        avatar: localUser.avatar || userData.avatar || defaultAvatar
      }
      readingStats.value = res.data.data.reading_stats
      readingGene.value = res.data.data.reading_gene
      
      // 初始化图表
      initCharts()
    } else {
      // 如果后端返回错误，使用 localStorage 中的用户信息
      userInfo.value = {
        ...localUser,
        avatar: localUser.avatar || defaultAvatar
      }
      alert(res.data.msg)
    }
  } catch (error) {
    console.error('获取用户个人资料失败:', error)
    // 如果发生错误，使用 localStorage 中的用户信息
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      const localUser = JSON.parse(savedUser)
      userInfo.value = {
        ...localUser,
        avatar: localUser.avatar || defaultAvatar
      }
    }
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
        ],
        splitArea: {
          areaStyle: {
            color: ['rgba(250, 250, 250, 0.3)', 'rgba(240, 240, 240, 0.3)']
          }
        },
        axisLine: {
          lineStyle: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        }
      },
      series: [{
        name: '阅读基因',
        type: 'radar',
        data: [{
          value: Object.values(readingGene.value),
          name: '阅读基因',
          lineStyle: {
            width: 2,
            color: '#4a6fa5'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(74, 111, 165, 0.6)' },
              { offset: 1, color: 'rgba(74, 111, 165, 0.1)' }
            ])
          },
          itemStyle: {
            color: '#4a6fa5'
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
        itemStyle: {
          borderRadius: 4,
          borderColor: '#fff',
          borderWidth: 1
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        color: [
          '#4a6fa5',
          '#6c8ebf',
          '#91a7cd',
          '#b6c6e0',
          '#d1dae8',
          '#e7ecf3'
        ]
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
  background: #f9f9f9;
  min-height: 100vh;
  padding-bottom: 64px;
}

.profile-header {
  background: #ffffff;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
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
  transition: all 0.2s ease;
}

.back-btn:hover {
  opacity: 0.85;
  transform: translateY(-1px);
}

.back-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

.profile-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: -0.26px;
  color: #000000;
}

.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: grid;
  grid-template-columns: 25% 75%;
  gap: 32px;
}

@media (max-width: 768px) {
  .profile-container {
    grid-template-columns: 1fr;
  }
}

.profile-sidebar {
  display: flex;
  flex-direction: column;
}

.profile-card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 32px;
  text-align: center;
  margin-bottom: 24px;
}

.profile-avatar {
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.profile-avatar img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid rgba(74, 111, 165, 0.2);
  transition: all 0.2s ease;
}

.profile-avatar img:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(74, 111, 165, 0.3);
}

.profile-username {
  font-size: 24px;
  color: #000000;
  margin: 0 0 12px 0;
  font-weight: 600;
  letter-spacing: -0.26px;
}

.profile-email {
  font-size: 16px;
  color: #666666;
  margin: 0 0 12px 0;
  font-weight: 400;
  letter-spacing: -0.14px;
}

.profile-joined {
  font-size: 14px;
  color: #999999;
  margin: 0;
  font-weight: 400;
  letter-spacing: -0.1px;
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.reading-stats {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 32px;
}

.section-title {
  font-size: 20px;
  color: #000000;
  margin: 0 0 24px 0;
  font-weight: 600;
  letter-spacing: -0.14px;
  padding-left: 16px;
  border-left: 3px solid #4a6fa5;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 32px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.charts-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

@media (max-width: 768px) {
  .charts-container {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 32px;
  transition: all 0.2s ease;
}

.chart-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.chart {
  width: 100%;
  height: 400px;
}

.word-count-section {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  padding: 32px;
}

.word-count-ranges {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.word-count-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.word-count-label {
  width: 140px;
  font-size: 14px;
  color: #666666;
  font-weight: 400;
  letter-spacing: -0.1px;
}

.word-count-bar {
  flex: 1;
  height: 16px;
  background: #f0f0f0;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.word-count-fill {
  height: 100%;
  background: linear-gradient(90deg, #4a6fa5, #6c8ebf);
  border-radius: 8px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.word-count-fill::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.word-count-value {
  width: 50px;
  text-align: right;
  font-size: 14px;
  color: #000000;
  font-weight: 600;
  letter-spacing: -0.1px;
}

/* 暗色模式 */
.dark-mode .user-reading-profile {
  background: #000000 !important;
  color: #ffffff !important;
}

.dark-mode .profile-header {
  background: #0a0a0a;
  box-shadow: 0 1px 3px rgba(255, 255, 255, 0.1);
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
.dark-mode .reading-stats,
.dark-mode .chart-card,
.dark-mode .word-count-section {
  background: #0a0a0a;
  box-shadow: 0 2px 8px rgba(255, 255, 255, 0.05);
}

.dark-mode .stat-item {
  background: #1a1a1a;
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
  border-left-color: #6c8ebf;
}

.dark-mode .word-count-label {
  color: #b0b0b0;
}

.dark-mode .word-count-bar {
  background: #2a2a2a;
}

.dark-mode .word-count-fill {
  background: linear-gradient(90deg, #6c8ebf, #91a7cd);
}

.dark-mode .word-count-value {
  color: #ffffff;
}
</style>