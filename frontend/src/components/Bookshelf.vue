<template>
  <div class="bookshelf">
    <header class="bookshelf-header">
      <button class="back-btn" @click="goBack">← 返回首页</button>
      <h1>我的书架</h1>
    </header>

    <div class="bookshelf-container">
      <div v-if="bookshelf.length === 0" class="empty-bookshelf">
        <div class="empty-icon">📚</div>
        <h2>书架是空的</h2>
        <p>去浏览书籍并添加到书架吧</p>
        <button class="browse-btn" @click="goToHome">去浏览</button>
      </div>
      
      <div v-else class="bookshelf-content">
        <div class="books-grid">
          <div 
            v-for="book in bookshelf" 
            :key="book.book_id"
            class="book-card"
          >
            <div class="book-cover">
              <img :src="book.cover_url" @error="handleImgError" alt="封面">
              <button class="remove-btn" @click.stop="removeFromBookshelf(book.book_id)">
                ×
              </button>
            </div>
            <div class="book-info">
              <h4 class="book-title">{{ book.title }}</h4>
              <p class="book-author">{{ book.author || '未知作者' }}</p>
              <div class="book-stats">
                <span class="hot-value">🔥 {{ (book.read_count / 10000).toFixed(1) }}万</span>
              </div>
              <button class="read-btn" @click="goToDetail(book.book_id)">
                阅读
              </button>
            </div>
          </div>
        </div>
        
        <div class="bookshelf-stats">
          <h2>我的收藏</h2>
          <p class="books-count">共{{ bookshelf.length }}本</p>
          <div class="stats-card">
            <h3>收藏分类统计</h3>
            <div ref="categoryChart" class="chart-container"></div>
            <div class="category-list">
              <div 
                v-for="(count, category) in categoryStats" 
                :key="category"
                class="category-item"
              >
                <span class="category-color" :style="{ backgroundColor: getCategoryColor(category) }"></span>
                <span class="category-name">{{ category }}</span>
                <span class="category-count">{{ count }}本</span>
                <span class="category-percent">({{ getCategoryPercent(count) }}%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'

const router = useRouter()

const bookshelf = ref([])
const loading = ref(false)
const categoryChart = ref(null)
const categoryStats = ref({})

const goBack = () => {
  router.back()
}

const goToHome = () => {
  router.push('/')
}

const goToDetail = (bookId) => {
  router.push(`/${bookId}`)
}

const handleImgError = (e) => {
  e.target.src = 'https://via.placeholder.com/120x160?text=No+Cover'
}

const calculateCategoryStats = () => {
  const stats = {}
  bookshelf.value.forEach(book => {
    const category = book.category || '其他'
    if (stats[category]) {
      stats[category]++
    } else {
      stats[category] = 1
    }
  })
  categoryStats.value = stats
}

const getCategoryColor = (category) => {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#c0c4cc']
  const index = Object.keys(categoryStats.value).indexOf(category) % colors.length
  return colors[index]
}

const getCategoryPercent = (count) => {
  if (bookshelf.value.length === 0) return 0
  return Math.round((count / bookshelf.value.length) * 100)
}

const initCategoryChart = () => {
  if (!categoryChart.value) return
  
  const chart = echarts.init(categoryChart.value)
  
  const categories = Object.keys(categoryStats.value)
  const data = categories.map(category => ({
    name: category,
    value: categoryStats.value[category]
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: categories
    },
    series: [
      {
        name: '分类',
        type: 'pie',
        radius: ['50%', '70%'],
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
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: data
      }
    ]
  }
  
  chart.setOption(option)
  
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

const fetchBookshelf = async () => {
  loading.value = true
  try {
    // 从localStorage获取用户信息
    const savedUser = localStorage.getItem('user')
    if (!savedUser) {
      alert('请先登录')
      return
    }
    
    const user = JSON.parse(savedUser)
    const res = await axios.get('http://127.0.0.1:8000/api/user/bookshelf/', {
      params: { user_id: user.id }
    })
    
    if (res.data.code === 200) {
      const bookIds = res.data.data
      // 根据bookIds获取书籍详情
      const bookPromises = bookIds.map(bookId => 
        axios.get(`http://127.0.0.1:8000/api/book/${bookId}/`)
      )
      
      const bookResponses = await Promise.all(bookPromises)
      const books = bookResponses
        .filter(response => response.data.code === 200)
        .map(response => response.data.data)
      
      bookshelf.value = books
    }
  } catch (error) {
    console.error('获取书架失败:', error)
    alert('获取书架失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

const removeFromBookshelf = async (bookId) => {
  try {
    // 从localStorage获取用户信息
    const savedUser = localStorage.getItem('user')
    if (!savedUser) {
      alert('请先登录')
      return
    }
    
    const user = JSON.parse(savedUser)
    const res = await axios.post('http://127.0.0.1:8000/api/user/bookshelf/remove/', {
      user_id: user.id,
      book_id: bookId
    })
    
    if (res.data.code === 200) {
      // 重新获取书架数据
      await fetchBookshelf()
    } else {
      alert(res.data.msg)
    }
  } catch (error) {
    console.error('移除失败:', error)
    alert('移除失败，请检查网络连接')
  }
}

// 监听书架数据变化，重新计算分类统计并初始化图表
watch(bookshelf, () => {
  calculateCategoryStats()
  setTimeout(() => {
    initCategoryChart()
  }, 100)
}, { deep: true })

onMounted(() => {
  fetchBookshelf()
})
</script>

<style scoped>
.bookshelf {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: #ffffff;
  min-height: 100vh;
  padding-bottom: 40px;
}

.bookshelf-header {
  background: #ffffff;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
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

.bookshelf-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 540;
  letter-spacing: -0.26px;
  color: #000000;
}

.bookshelf-container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
}

.empty-bookshelf {
  text-align: center;
  padding: 60px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-bookshelf h2 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #333;
}

.empty-bookshelf p {
  margin: 0 0 30px 0;
  font-size: 14px;
  color: #666;
}

.browse-btn {
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 12px 24px;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.browse-btn:hover {
  opacity: 0.85;
}

.browse-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

.bookshelf-content {
  display: flex;
  gap: 30px;
}

.books-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 20px;
}

.bookshelf-stats {
  width: 350px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  padding: 20px;
  position: sticky;
  top: 20px;
  align-self: flex-start;
}

.bookshelf-stats h2 {
  margin: 0 0 5px 0;
  font-size: 20px;
  color: #333;
}

.books-count {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: #666;
}

.stats-card {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
}

.stats-card h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  color: #333;
  text-align: center;
}

.chart-container {
  width: 100%;
  height: 250px;
  margin-bottom: 20px;
}

.category-list {
  margin-top: 20px;
}

.category-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  font-size: 14px;
}

.category-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 10px;
}

.category-name {
  flex: 1;
  color: #333;
}

.category-count {
  margin-right: 10px;
  font-weight: bold;
  color: #333;
}

.category-percent {
  color: #999;
}

.book-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  transition: 0.3s;
}

.book-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
}

.book-cover {
  position: relative;
  height: 240px;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  font-size: 18px;
  font-weight: bold;
  color: #f56c6c;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: 0.2s;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.remove-btn:hover {
  background: #f56c6c;
  color: white;
}

.book-info {
  padding: 15px;
  display: flex;
  flex-direction: column;
  min-height: 100px;
}

.book-title {
  font-size: 14px;
  color: #000000;
  margin: 0 0 5px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 39px;
  font-weight: 400;
  letter-spacing: -0.14px;
}

.book-author {
  font-size: 12px;
  color: #666666;
  margin: 0 0 8px 0;
  font-weight: 320;
  letter-spacing: -0.1px;
}

.book-stats {
  font-size: 12px;
  font-weight: 540;
  color: #000000;
  margin-bottom: auto;
  letter-spacing: -0.1px;
}

.read-btn {
  width: 100%;
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 8px 16px;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 400;
  letter-spacing: -0.14px;
  cursor: pointer;
  transition: opacity 0.2s;
  margin-top: 10px;
}

.read-btn:hover {
  opacity: 0.85;
}

.read-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .bookshelf-content {
    flex-direction: column;
  }
  
  .bookshelf-stats {
    width: 100%;
    position: static;
  }
}

@media (max-width: 768px) {
  .bookshelf-container {
    padding: 0 15px;
  }
  
  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 15px;
  }
  
  .book-cover {
    height: 200px;
  }
  
  .chart-container {
    height: 200px;
  }
}

/* 深色模式样式 */
.dark-mode .bookshelf {
  background: #121212 !important;
  color: #e0e0e0 !important;
}

.dark-mode .bookshelf-header {
  background: #1e1e1e;
  border-bottom: 1px solid #3a3a3a;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.dark-mode .bookshelf-header h1 {
  color: #e0e0e0;
}

.dark-mode .empty-bookshelf {
  background: #1e1e1e;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.dark-mode .empty-bookshelf h2 {
  color: #e0e0e0;
}

.dark-mode .empty-bookshelf p {
  color: #b0b0b0;
}

.dark-mode .bookshelf-stats {
  background: #1e1e1e;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.dark-mode .bookshelf-stats h2 {
  color: #e0e0e0;
}

.dark-mode .books-count {
  color: #b0b0b0;
}

.dark-mode .stats-card {
  background: #2c2c2c;
}

.dark-mode .stats-card h3 {
  color: #e0e0e0;
}

.dark-mode .category-item {
  color: #e0e0e0;
}

.dark-mode .category-name {
  color: #e0e0e0;
}

.dark-mode .category-count {
  color: #e0e0e0;
}

.dark-mode .book-card {
  background: #1e1e1e;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.dark-mode .book-title {
  color: #e0e0e0;
}

.dark-mode .book-author {
  color: #b0b0b0;
}

.dark-mode .book-stats {
  color: #e0e0e0;
}

.dark-mode .remove-btn {
  background: rgba(44, 44, 44, 0.9);
  box-shadow: 0 2px 5px rgba(0,0,0,0.3);
}

.dark-mode .remove-btn:hover {
  background: #f56c6c;
  color: white;
}

.dark-mode .back-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .back-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}

.dark-mode .browse-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .browse-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}

.dark-mode .read-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .read-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}
</style>