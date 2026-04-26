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
        <div ref="categoryChart" class="chart"></div>
      </div>

      <div class="chart-container">
        <h3>书籍阅读量统计</h3>
        <div ref="readCountChart" class="chart"></div>
      </div>

      <div class="chart-container">
        <h3>书籍字数分布</h3>
        <div ref="wordCountChart" class="chart"></div>
      </div>

      <div class="chart-container">
        <h3>书籍1-10分评分分布</h3>
        <div ref="ratingChart" class="chart"></div>
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

const fetchBooks = async () => {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/admin/books/')
    if (res.data.code === 200) {
      books.value = res.data.data
      initCharts()
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
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
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
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 10,
      data: categories
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
            fontWeight: 'bold'
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

  const topBooks = [...books.value]
    .sort((a, b) => b.read_count - a.read_count)
    .slice(0, 10)

  const titles = topBooks.map(book => book.title)
  const readCounts = topBooks.map(book => book.read_count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      boundaryGap: [0, 0.01]
    },
    yAxis: {
      type: 'category',
      data: titles,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    series: [
      {
        name: '阅读量',
        type: 'bar',
        data: readCounts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
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
      data: ranges
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '书籍数量',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#fccb05' },
            { offset: 0.5, color: '#f5804e' },
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

  const ratingRanges = [
    { name: '1', min: 1, max: 2, count: 0 },
    { name: '2', min: 2, max: 3, count: 0 },
    { name: '3', min: 3, max: 4, count: 0 },
    { name: '4', min: 4, max: 5, count: 0 },
    { name: '5', min: 5, max: 6, count: 0 },
    { name: '6', min: 6, max: 7, count: 0 },
    { name: '7', min: 7, max: 8, count: 0 },
    { name: '8', min: 8, max: 9, count: 0 },
    { name: '9', min: 9, max: 10, count: 0 },
    { name: '10', min: 10, max: 11, count: 0 }
  ]

  books.value.forEach(book => {
    const rating = book.rating || 0
    for (const range of ratingRanges) {
      if (rating >= range.min && rating < range.max) {
        range.count++
        break
      }
    }
  })

  const ranges = ratingRanges.map(range => range.name)
  const counts = ratingRanges.map(range => range.count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
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
      data: ranges
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '书籍数量',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#40c9c6' },
            { offset: 0.5, color: '#5168e2' },
            { offset: 1, color: '#5168e2' }
          ])
        }
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

watch(books, () => {
  initCharts()
}, { deep: true })

onMounted(() => {
  fetchBooks()
  fetchUsers()
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
</style>
