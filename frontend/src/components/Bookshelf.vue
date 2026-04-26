<template>
  <div class="bookshelf">
    <header class="bookshelf-header">
      <button class="back-btn" @click="goBack">← 返回首页</button>
      <h1>我的书架</h1>
      <div class="header-actions">
        <div class="search-box">
          <input type="text" v-model="searchQuery" placeholder="搜索书籍..." class="search-input">
        </div>
        <div class="sort-options">
          <button 
            v-for="option in sortOptions" 
            :key="option.value"
            :class="['sort-btn', { active: sortBy === option.value }]"
            @click="sortBooks(option.value)"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
    </header>

    <div class="bookshelf-container">
      <div v-if="bookshelf.length === 0" class="empty-bookshelf">
        <div class="empty-icon">📚</div>
        <h2>书架是空的</h2>
        <p>去浏览书籍并添加到书架吧</p>
        <button class="browse-btn" @click="goToHome">去浏览</button>
      </div>
      
      <div v-else class="bookshelf-content">
        <!-- 侧边栏统计 -->
        <div class="sidebar-stats">
          <div class="stats-overview">
            <div class="stat-card">
              <div class="stat-value">{{ bookshelf.length }}</div>
              <div class="stat-label">总藏书</div>
            </div>
            <div class="stat-card">
              <div class="stat-value">{{ Object.keys(categoryStats).length }}</div>
              <div class="stat-label">分类数</div>
            </div>
          </div>
          
          <div class="chart-section">
            <h3>收藏分类统计</h3>
            <div ref="categoryChart" class="chart-container"></div>
          </div>
          
          <div class="category-list">
            <div 
              v-for="(count, category) in categoryStats" 
              :key="category"
              class="category-item"
            >
              <span class="category-color" :style="{ backgroundColor: getCategoryColor(category) }"></span>
              <span class="category-name">{{ category }}</span>
              <span class="category-count">{{ count }}本</span>
            </div>
          </div>
        </div>
        
        <!-- 主区书架 -->
        <div class="main-bookshelf">
          <div class="books-grid">
            <div 
              v-for="book in filteredBooks" 
              :key="book.book_id"
              class="book-card"
            >
              <div class="book-cover" @click="goToDetail(book.book_id)" style="cursor: pointer;">
                <img :src="book.cover_url" @error="handleImgError" alt="封面">
                <div class="card-actions">
                  <button class="action-btn remove-btn" @click.stop="removeFromBookshelf(book.book_id)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </button>
                  <button class="action-btn detail-btn" @click.stop="openBookDrawer(book)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <circle cx="12" cy="12" r="10"></circle>
                      <line x1="12" y1="8" x2="12" y2="12"></line>
                      <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                  </button>
                </div>
              </div>
              <div class="book-info">
                <h4 class="book-title">{{ book.title }}</h4>
                <p class="book-author">{{ book.author || '未知作者' }}</p>
                <div class="book-stats">
                  <span class="hot-value">{{ (book.read_count / 10000).toFixed(1) }}万</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 书籍详情抽屉 -->
    <div class="book-drawer" v-if="drawerVisible">
      <div class="drawer-content">
        <div class="drawer-header">
          <h3>{{ selectedBook.title }}</h3>
          <button class="close-btn" @click="closeBookDrawer">×</button>
        </div>
        <div class="drawer-body">
          <div class="book-detail-container">
            <div class="book-detail-cover">
              <img :src="selectedBook.cover_url" @error="handleImgError" alt="封面">
            </div>
            <div class="book-detail-info">
              <p class="book-detail-author">作者：{{ selectedBook.author || '未知作者' }}</p>
              <p class="book-detail-category">分类：{{ selectedBook.category || '未分类' }}</p>
              <p class="book-detail-rating">评分：{{ selectedBook.rating || '暂无评分' }}</p>
              <p class="book-detail-read-count">阅读：{{ (selectedBook.read_count / 10000).toFixed(1) }}万</p>
            </div>
          </div>
          <div class="book-summary">
            <h4>内容简介</h4>
            <p>{{ selectedBook.introduction || '暂无简介' }}</p>
          </div>
          <div class="drawer-footer">
            <button class="read-btn" @click="goToDetail(selectedBook.book_id)">阅读全文</button>
          </div>
        </div>
      </div>
    </div>
    <!-- 遮罩层 -->
    <div class="drawer-overlay" v-if="drawerVisible" @click="closeBookDrawer"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'

const router = useRouter()

const bookshelf = ref([])
const loading = ref(false)
const categoryChart = ref(null)
const categoryStats = ref({})
const searchQuery = ref('')
const sortBy = ref('recent')
const drawerVisible = ref(false)
const selectedBook = ref({})

const sortOptions = [
  { value: 'recent', label: '最近添加' },
  { value: 'rating', label: '评分最高' }
]

const openBookDrawer = async (book) => {
  // 确保selectedBook对象包含所有必要字段
  selectedBook.value = {
    ...book,
    introduction: book.introduction || '暂无简介',
    rating: 0
  }
  
  // 获取书籍评分
  await fetchBookRating(book.book_id)
  
  drawerVisible.value = true
  // 阻止背景滚动
  document.body.style.overflow = 'hidden'
}

const fetchBookRating = async (bookId) => {
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/book/rating/${bookId}/`)
    if (res.data.code === 200) {
      selectedBook.value.rating = res.data.data.average_score
    }
  } catch (error) {
    console.error('获取书籍评分失败:', error)
  }
}

const closeBookDrawer = () => {
  drawerVisible.value = false
  // 恢复背景滚动
  document.body.style.overflow = ''
}

const filteredBooks = computed(() => {
  let result = [...bookshelf.value]
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(book => 
      book.title.toLowerCase().includes(query) || 
      (book.author && book.author.toLowerCase().includes(query))
    )
  }
  
  // 排序
  switch (sortBy.value) {
    case 'recent':
      // 假设 bookshelf 中的书籍有添加时间字段，这里暂时按 book_id 排序
      result.sort((a, b) => b.book_id - a.book_id)
      break
    case 'rating':
      // 按评分排序
      result.sort((a, b) => (b.rating || 0) - (a.rating || 0))
      break
  }
  
  return result
})

const sortBooks = (value) => {
  sortBy.value = value
}

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
  
  // 检查是否为暗色模式
  const isDarkMode = document.body.classList.contains('dark-mode')
  
  // 配色方案
  const colors = isDarkMode 
    ? ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#c0c4cc']
    : ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#c0c4cc']
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      show: false
    },
    series: [
      {
        name: '分类',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: isDarkMode ? '#2c2c2c' : '#fff',
          borderWidth: 2,
          opacity: 0.8
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          itemStyle: {
            opacity: 1
          },
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold',
            color: isDarkMode ? '#e0e0e0' : '#333'
          }
        },
        labelLine: {
          show: false
        },
        data: data,
        color: colors
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
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
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
  transition: all 0.3s ease;
}

.back-btn:hover {
  opacity: 0.85;
  transform: translateY(-2px);
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
  flex: 1;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.search-box {
  position: relative;
}

.search-input {
  padding: 10px 15px;
  border: none;
  border-radius: 50px;
  background: #f4f4f4;
  font-size: 14px;
  width: 200px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  width: 250px;
  box-shadow: 0 0 0 2px rgba(0,0,0,0.1);
}

.sort-options {
  display: flex;
  gap: 10px;
}

.sort-btn {
  background: transparent;
  border: 1px solid #e0e0e0;
  padding: 8px 16px;
  border-radius: 50px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.sort-btn:hover {
  background: #f4f4f4;
}

.sort-btn.active {
  background: #000000;
  color: #ffffff;
  border-color: #000000;
}

.bookshelf-container {
  max-width: 1400px;
  margin: 30px auto;
  padding: 0 24px;
}

.empty-bookshelf {
  text-align: center;
  padding: 80px 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 24px;
}

.empty-bookshelf h2 {
  margin: 0 0 12px 0;
  font-size: 24px;
  color: #333;
}

.empty-bookshelf p {
  margin: 0 0 32px 0;
  font-size: 16px;
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
  transition: all 0.3s ease;
}

.browse-btn:hover {
  opacity: 0.85;
  transform: translateY(-2px);
}

.browse-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

.bookshelf-content {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

/* 侧边栏统计 */
.sidebar-stats {
  width: 25%;
  min-width: 300px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.03);
  padding: 24px;
  position: sticky;
  top: 24px;
  align-self: flex-start;
}

.stats-overview {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  flex: 1;
  background: #f9f9f9;
  border-radius: 8px;
  padding: 16px;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #409eff;
  border-radius: 4px 0 0 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #000;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.chart-section {
  margin-bottom: 24px;
}

.chart-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.chart-container {
  width: 100%;
  height: 200px;
  margin-bottom: 16px;
}

.category-list {
  margin-top: 16px;
}

.category-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  padding: 8px 0;
}

.category-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 12px;
  flex-shrink: 0;
}

.category-name {
  flex: 1;
  color: #333;
}

.category-count {
  font-weight: bold;
  color: #333;
  flex-shrink: 0;
}

/* 主区书架 */
.main-bookshelf {
  flex: 1;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 24px;
}

.book-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
  position: relative;
}

.book-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.1);
}

.book-cover {
  position: relative;
  aspect-ratio: 3/4;
  background: #f4f4f4;
  overflow: hidden;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.book-card:hover .book-cover img {
  transform: scale(1.05);
}

.card-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.book-card:hover .card-actions {
  opacity: 1;
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.action-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.remove-btn {
  color: #f56c6c;
}

.remove-btn:hover {
  background: #f56c6c;
  color: white;
}

.detail-btn {
  color: #409eff;
}

.detail-btn:hover {
  background: #409eff;
  color: white;
}

.book-info {
  padding: 16px;
  display: flex;
  flex-direction: column;
  min-height: 100px;
}

.book-title {
  font-size: 14px;
  color: #000000;
  margin: 0 0 6px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 39px;
  font-weight: 500;
  letter-spacing: -0.14px;
}

.book-author {
  font-size: 12px;
  color: #666666;
  margin: 0 0 10px 0;
  font-weight: 320;
  letter-spacing: -0.1px;
}

.book-stats {
  font-size: 12px;
  font-weight: 600;
  color: #000000;
  margin-top: auto;
  letter-spacing: -0.1px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .bookshelf-content {
    flex-direction: column;
  }
  
  .sidebar-stats {
    width: 100%;
    min-width: unset;
    position: static;
  }
  
  .stats-overview {
    justify-content: center;
  }
  
  .chart-container {
    max-width: 400px;
    margin: 0 auto 16px;
  }
}

@media (max-width: 768px) {
  .bookshelf-container {
    padding: 0 16px;
  }
  
  .bookshelf-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .search-input {
    width: 150px;
  }
  
  .search-input:focus {
    width: 180px;
  }
  
  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 16px;
  }
  
  .stat-card {
    padding: 12px;
  }
  
  .stat-value {
    font-size: 20px;
  }
}

/* 深色模式样式 */
.dark-mode .bookshelf {
  background: #121212 !important;
  color: #e0e0e0 !important;
}

.dark-mode .bookshelf-header {
  background: #1e1e1e;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.dark-mode .bookshelf-header h1 {
  color: #e0e0e0;
}

.dark-mode .search-input {
  background: #2c2c2c;
  color: #e0e0e0;
}

.dark-mode .search-input:focus {
  box-shadow: 0 0 0 2px rgba(255,255,255,0.1);
}

.dark-mode .sort-btn {
  border-color: #3a3a3a;
  color: #e0e0e0;
}

.dark-mode .sort-btn:hover {
  background: #2c2c2c;
}

.dark-mode .sort-btn.active {
  background: #ffffff;
  color: #000000;
  border-color: #ffffff;
}

.dark-mode .empty-bookshelf {
  background: #1e1e1e;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.dark-mode .empty-bookshelf h2 {
  color: #e0e0e0;
}

.dark-mode .empty-bookshelf p {
  color: #b0b0b0;
}

.dark-mode .sidebar-stats {
  background: #1e1e1e;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.dark-mode .stat-card {
  background: #2c2c2c;
}

.dark-mode .stat-value {
  color: #e0e0e0;
}

.dark-mode .stat-label {
  color: #b0b0b0;
}

.dark-mode .chart-section h3 {
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

.dark-mode .book-cover {
  background: #2c2c2c;
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

.dark-mode .action-btn {
  background: rgba(44, 44, 44, 0.9);
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
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

/* 书籍详情抽屉样式 */
.book-drawer {
  position: fixed;
  top: 0;
  right: 0;
  width: 450px;
  height: 100vh;
  background: #ffffff;
  box-shadow: -4px 0 20px rgba(0,0,0,0.1);
  z-index: 1000;
  transform: translateX(100%);
  transition: transform 0.3s ease;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.book-drawer.show {
  transform: translateX(0);
}

.drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 999;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.drawer-overlay.show {
  opacity: 1;
}

.drawer-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.drawer-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.drawer-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  transition: color 0.3s ease;
}

.close-btn:hover {
  color: #333;
}

.drawer-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.book-detail-container {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.book-detail-cover {
  width: 120px;
  flex-shrink: 0;
}

.book-detail-cover img {
  width: 100%;
  aspect-ratio: 3/4;
  object-fit: contain;
  background: #f4f4f4;
  border-radius: 8px;
}

.book-detail-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.book-detail-author,
.book-detail-category,
.book-detail-rating,
.book-detail-read-count {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.book-summary {
  margin-bottom: 24px;
}

.book-summary h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.book-summary p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #666;
}

.drawer-footer {
  padding: 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
}

.drawer-footer .read-btn {
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 10px 24px;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 400;
  letter-spacing: -0.14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.drawer-footer .read-btn:hover {
  opacity: 0.85;
  transform: translateY(-2px);
}

/* 动画效果 */
.book-drawer {
  animation: slideIn 0.3s ease forwards;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.drawer-overlay {
  animation: fadeIn 0.3s ease forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .book-drawer {
    width: 100%;
  }
  
  .book-detail-container {
    flex-direction: column;
  }
  
  .book-detail-cover {
    width: 100%;
    max-width: 150px;
    margin: 0 auto;
  }
  
  .book-detail-info {
    text-align: center;
  }
}

/* 深色模式样式 */
.dark-mode .book-drawer {
  background: #1e1e1e;
  box-shadow: -4px 0 20px rgba(0,0,0,0.3);
}

.dark-mode .drawer-header {
  border-bottom: 1px solid #3a3a3a;
}

.dark-mode .drawer-header h3 {
  color: #e0e0e0;
}

.dark-mode .close-btn {
  color: #b0b0b0;
}

.dark-mode .close-btn:hover {
  color: #e0e0e0;
}

.dark-mode .drawer-body {
  background: #1e1e1e;
}

.dark-mode .book-detail-cover img {
  background: #2c2c2c;
}

.dark-mode .book-detail-author,
.dark-mode .book-detail-category,
.dark-mode .book-detail-rating,
.dark-mode .book-detail-read-count {
  color: #b0b0b0;
}

.dark-mode .book-summary h4 {
  color: #e0e0e0;
}

.dark-mode .book-summary p {
  color: #b0b0b0;
}

.dark-mode .drawer-footer {
  border-top: 1px solid #3a3a3a;
  background: #1e1e1e;
}

.dark-mode .drawer-footer .read-btn {
  background: #ffffff;
  color: #000000;
}
</style>