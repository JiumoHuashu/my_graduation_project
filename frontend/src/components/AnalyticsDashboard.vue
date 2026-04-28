<template>
  <div class="analytics-dashboard">
    <div class="content-header">
      <h2>数据可视化</h2>
    </div>

    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon">📚</div>
        <div class="stat-info">
          <div class="stat-value">{{ books.length }}</div>
          <div class="stat-label">总书籍数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👤</div>
        <div class="stat-info">
          <div class="stat-value">{{ users.length }}</div>
          <div class="stat-label">总用户数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📈</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalReadCount }}万</div>
          <div class="stat-label">总阅读量</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏆</div>
        <div class="stat-info">
          <div class="stat-value">{{ topBookTitle || '暂无' }}</div>
          <div class="stat-label">热门书籍</div>
        </div>
      </div>
    </div>

    <div class="dashboard-content">
      <div class="chart-container">
        <h3>书籍分类分布</h3>
        <div v-if="books.length === 0" class="empty-state">
          <p>暂无统计数据</p>
        </div>
        <div v-else ref="categoryChart" class="chart"></div>
      </div>

      <div class="chart-container">
        <h3>书籍阅读量分布</h3>
        <div v-if="books.length === 0" class="empty-state">
          <p>暂无统计数据</p>
        </div>
        <div v-else ref="readCountChart" class="chart"></div>
      </div>

      <div class="chart-container">
        <h3>书籍字数分布</h3>
        <div v-if="books.length === 0" class="empty-state">
          <p>暂无统计数据</p>
        </div>
        <div v-else ref="wordCountChart" class="chart"></div>
      </div>

      <div class="chart-container">
        <h3>书籍评分分布</h3>
        <div v-if="books.length === 0" class="empty-state">
          <p>暂无统计数据</p>
        </div>
        <div v-else ref="ratingChart" class="chart"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

const books = ref([])
const users = ref([])
const ratings = ref([])
const bookshelfData = ref({})

const categoryChart = ref(null)
const readCountChart = ref(null)
const wordCountChart = ref(null)
const ratingChart = ref(null)

let categoryChartInstance = null
let readCountChartInstance = null
let wordCountChartInstance = null
let ratingChartInstance = null

const totalReadCount = computed(() => {
  const total = books.value.reduce((sum, book) => sum + (book.read_count || 0), 0)
  return (total / 10000).toFixed(1)
})

const topBookTitle = computed(() => {
  if (books.value.length === 0) return ''
  const topBook = [...books.value].sort((a, b) => (b.read_count || 0) - (a.read_count || 0))[0]
  return topBook.title.length > 10 ? topBook.title.substring(0, 10) + '...' : topBook.title
})

const readCountDistribution = computed(() => {
  const ranges = [
    { name: '0-10万', min: 0, max: 100000, count: 0 },
    { name: '10-50万', min: 100000, max: 500000, count: 0 },
    { name: '50-100万', min: 500000, max: 1000000, count: 0 },
    { name: '100-500万', min: 1000000, max: 5000000, count: 0 },
    { name: '500万以上', min: 5000000, max: Infinity, count: 0 }
  ]

  books.value.forEach(book => {
    const readCount = book.read_count || 0
    for (const range of ranges) {
      if (readCount >= range.min && readCount < range.max) {
        range.count++
        break
      }
    }
  })

  return ranges
})

const ratingDistribution = computed(() => {
  const ranges = [
    { name: '1-3分（低）', min: 1, max: 4, count: 0, color: '#94a3b8' },
    { name: '4-6分（中）', min: 4, max: 7, count: 0, color: '#60a5fa' },
    { name: '7-8分（高）', min: 7, max: 9, count: 0, color: '#34d399' },
    { name: '9-10分（顶尖）', min: 9, max: 11, count: 0, color: '#f59e0b' }
  ]

  ratings.value.forEach(rating => {
    const score = rating.score
    for (const range of ranges) {
      if (score >= range.min && score < range.max) {
        range.count++
        break
      }
    }
  })

  return ranges
})

const fetchBooks = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/admin/books/')
    if (res.data.code === 200) {
      books.value = res.data.data
    }
  } catch (error) {
    console.error('获取书籍列表失败:', error)
  }
}

const fetchUsers = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/admin/users/')
    if (res.data.code === 200) {
      users.value = res.data.data
      await fetchBookshelfData()
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

const fetchRatings = async () => {
  try {
    const allRatings = []
    for (const user of users.value) {
      const res = await axios.get(`http://127.0.0.1:8000/api/user/rating/?user_id=${user.id}`)
      if (res.data.code === 200 && res.data.data) {
        allRatings.push(...res.data.data)
      }
    }
    ratings.value = allRatings
  } catch (error) {
    console.error('获取评分数据失败:', error)
  }
}

const fetchBookshelfData = async () => {
  try {
    const data = {}
    for (const user of users.value) {
      const res = await axios.get(`http://127.0.0.1:8000/api/user/bookshelf/?user_id=${user.id}`)
      if (res.data.code === 200 && res.data.data) {
        data[user.id] = res.data.data
      }
    }
    bookshelfData.value = data
  } catch (error) {
    console.error('获取书架数据失败:', error)
  }
}

const initCategoryChart = () => {
  if (!categoryChart.value) return

  if (categoryChartInstance) {
    categoryChartInstance.dispose()
  }

  categoryChartInstance = echarts.init(categoryChart.value)

  const categoryData = {}
  books.value.forEach(book => {
    const category = book.main_category
    if (categoryData[category]) {
      categoryData[category]++
    } else {
      categoryData[category] = 1
    }
  })

  const categories = Object.keys(categoryData)
  const counts = Object.values(categoryData)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)',
      textStyle: {
        color: '#8b949e'
      }
    },
    legend: {
      orient: 'vertical',
      left: 10,
      data: categories,
      textStyle: {
        color: '#8b949e'
      }
    },
    series: [
      {
        name: '书籍分类',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold',
            color: '#ffffff'
          }
        },
        labelLine: {
          show: false
        },
        data: categories.map((category, index) => ({
          value: counts[index],
          name: category
        }))
      }
    ]
  }

  categoryChartInstance.setOption(option)
}

const initReadCountChart = () => {
  if (!readCountChart.value) return

  if (readCountChartInstance) {
    readCountChartInstance.dispose()
  }

  readCountChartInstance = echarts.init(readCountChart.value)

  const distribution = readCountDistribution.value
  const ranges = distribution.map(range => range.name)
  const counts = distribution.map(range => range.count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      textStyle: {
        color: '#8b949e'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ranges,
      axisLabel: {
        color: '#8b949e'
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#8b949e'
      }
    },
    series: [
      {
        name: '书籍数量',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#388bfd' },
            { offset: 1, color: '#79c0ff' }
          ])
        }
      }
    ]
  }

  readCountChartInstance.setOption(option)
}

const initWordCountChart = () => {
  if (!wordCountChart.value) return

  if (wordCountChartInstance) {
    wordCountChartInstance.dispose()
  }

  wordCountChartInstance = echarts.init(wordCountChart.value)

  const wordRanges = [
    { name: '0-50万', min: 0, max: 500000, count: 0 },
    { name: '50-100万', min: 500000, max: 1000000, count: 0 },
    { name: '100-200万', min: 1000000, max: 2000000, count: 0 },
    { name: '200-500万', min: 2000000, max: 5000000, count: 0 },
    { name: '500万以上', min: 5000000, max: Infinity, count: 0 }
  ]

  books.value.forEach(book => {
    const wordCount = book.word_count || 0
    for (const range of wordRanges) {
      if (wordCount >= range.min && wordCount < range.max) {
        range.count++
        break
      }
    }
  })

  const ranges = wordRanges.map(range => range.name)
  const counts = wordRanges.map(range => range.count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      textStyle: {
        color: '#8b949e'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ranges,
      axisLabel: {
        color: '#8b949e'
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#8b949e'
      }
    },
    series: [
      {
        name: '书籍数量',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#fccb05' },
            { offset: 1, color: '#f5804e' }
          ])
        }
      }
    ]
  }

  wordCountChartInstance.setOption(option)
}

const initRatingChart = () => {
  if (!ratingChart.value) return

  if (ratingChartInstance) {
    ratingChartInstance.dispose()
  }

  ratingChartInstance = echarts.init(ratingChart.value)

  const distribution = ratingDistribution.value
  const data = distribution.map(range => ({
    value: range.count,
    name: range.name,
    itemStyle: {
      color: range.color
    }
  }))

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)',
      textStyle: {
        color: '#8b949e'
      }
    },
    legend: {
      orient: 'vertical',
      left: 10,
      data: distribution.map(range => range.name),
      textStyle: {
        color: '#8b949e'
      }
    },
    series: [
      {
        name: '书籍评分',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold',
            color: '#ffffff'
          }
        },
        labelLine: {
          show: false
        },
        data: data
      }
    ]
  }

  ratingChartInstance.setOption(option)
}

const initCharts = () => {
  setTimeout(() => {
    initCategoryChart()
    initReadCountChart()
    initWordCountChart()
    initRatingChart()
  }, 100)
}

const resizeCharts = () => {
  categoryChartInstance?.resize()
  readCountChartInstance?.resize()
  wordCountChartInstance?.resize()
  ratingChartInstance?.resize()
}

watch([books, ratings], () => {
  initCharts()
}, { deep: true })

onMounted(async () => {
  await fetchBooks()
  await fetchUsers()
  await fetchRatings()
  initCharts()
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  categoryChartInstance?.dispose()
  readCountChartInstance?.dispose()
  wordCountChartInstance?.dispose()
  ratingChartInstance?.dispose()
})
</script>

<style scoped>
.analytics-dashboard {
  height: 100%;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.content-header h2 {
  margin: 0;
  font-size: 18px;
  color: #000000;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  font-size: 32px;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #000000;
  letter-spacing: -0.01em;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #666666;
  font-weight: 500;
  letter-spacing: -0.01em;
  text-transform: uppercase;
}

.dashboard-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-top: 24px;
}

.chart-container {
  background: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
  position: relative;
}

.chart-container:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.chart-container h3 {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: #666666;
  font-weight: 500;
  letter-spacing: -0.01em;
  text-transform: uppercase;
}

.chart {
  height: 300px;
  width: 100%;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #999;
  font-size: 16px;
}

/* 深色模式 */
.dark-mode .content-header h2 {
  color: #ffffff;
}

.dark-mode .stat-card {
  background: #2d2d2d;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.dark-mode .stat-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.dark-mode .stat-icon {
  background: #3d3d3d;
}

.dark-mode .stat-value {
  color: #ffffff;
}

.dark-mode .stat-label {
  color: #888888;
}

.dark-mode .chart-container {
  background: #2d2d2d;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.dark-mode .chart-container:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.dark-mode .chart-container h3 {
  color: #888888;
}

.dark-mode .empty-state {
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-content {
    grid-template-columns: 1fr;
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    padding: 16px;
  }
  
  .chart {
    height: 250px;
  }
  
  .empty-state {
    height: 250px;
  }
}
</style>
