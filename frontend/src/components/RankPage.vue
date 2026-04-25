<template>
  <div class="rank-page">
    <header class="rank-header">
      <h1>小说排行榜</h1>
      <p>热门小说实时排名</p>
    </header>

    <div class="container">
      <aside class="sidebar">
        <div 
          v-for="cat in categoryList" 
          :key="cat"
          :class="['nav-item', activeCat === cat ? 'active' : '']"
          @click="handleCategoryChange(cat)"
        >
          {{ cat }}
        </div>
      </aside>

      <main class="main-list">
        <div v-if="loading" class="loading">数据加载中...</div>
        
        <div v-for="(item, index) in books" :key="item.book_id" class="book-item" @click="goToDetail(item.book_id)">
          <div class="rank-badge" :class="'top-' + (index + 1)">{{ index + 1 }}</div>
          
          <div class="book-cover">
            <img :src="item.cover_url" @error="handleImgError" alt="封面">
          </div>

          <div class="book-info">
            <h3 class="book-title">{{ item.title }}</h3>
            <div class="book-meta">
              <span>👤 {{ item.author || '未知作者' }}</span>
              <span class="tag">{{ item.category }}</span>
              <span class="tag sub">{{ item.sub_category }}</span>
            </div>
            <p class="book-intro">{{ item.introduction }}</p>
            <div class="book-stats">
              <span class="hot-value">🔥 热度：{{ (item.read_count / 10000).toFixed(1) }}万</span>
              <span class="word-count">📝 字数：{{ (item.word_count / 10000).toFixed(0) }}万字</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const books = ref([])
const loading = ref(false)
const activeCat = ref('全部')
const categoryList = ['全部', '同人小说', '玄幻奇幻', '武侠仙侠', '都市言情', '军事历史', '科幻网游', '推理灵异', '青春校园', '轻小说', '女生小说']

const fetchBooks = async (cat) => {
  loading.value = true
  const url = cat === '全部' 
    ? 'http://127.0.0.1:8000/api/rank/' 
    : `http://127.0.0.1:8000/api/rank/?category=${cat}`
  
  try {
    const res = await axios.get(url)
    books.value = res.data.data
  } catch (error) {
    console.error('获取数据失败:', error)
    alert('后端接口未启动或跨域配置错误')
  } finally {
    loading.value = false
  }
}

const handleCategoryChange = (cat) => {
  activeCat.value = cat
  fetchBooks(cat)
}

const handleImgError = (e) => {
  e.target.src = 'https://via.placeholder.com/120x160?text=No+Cover'
}

const goToDetail = (bookId) => {
  router.push(`/${bookId}`)
}

onMounted(() => fetchBooks('全部'))
</script>

<style scoped>
.rank-page {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  background: #f5f7f9;
  min-height: 100vh;
}

.rank-header {
  background: #fff;
  text-align: center;
  padding: 20px;
  border-bottom: 1px solid #ddd;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.rank-header h1 {
  margin: 0 0 5px 0;
  font-size: 24px;
  color: #333;
}

.rank-header p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.container {
  display: flex;
  max-width: 1100px;
  margin: 20px auto;
  gap: 20px;
  padding: 0 20px;
}

.sidebar {
  width: 180px;
  background: #fff;
  height: fit-content;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.nav-item {
  padding: 15px 20px;
  cursor: pointer;
  transition: 0.2s;
  border-left: 4px solid transparent;
}

.nav-item:hover {
  background: #f0f7ff;
  color: #409eff;
}

.nav-item.active {
  background: #ecf5ff;
  color: #409eff;
  border-left-color: #409eff;
  font-weight: bold;
}

.main-list {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.book-item {
  display: flex;
  padding: 20px 0;
  border-bottom: 1px solid #eee;
  position: relative;
  cursor: pointer;
  transition: 0.2s;
}

.book-item:hover {
  background: #f9f9f9;
}

.rank-badge {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #999;
  color: #fff;
  text-align: center;
  line-height: 30px;
  margin-right: 15px;
  font-weight: bold;
}

.top-1 {
  background: #ff4500;
}

.top-2 {
  background: #ff8c00;
}

.top-3 {
  background: #ffd700;
}

.book-cover img {
  width: 100px;
  height: 130px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  object-fit: cover;
}

.book-info {
  flex: 1;
  margin-left: 20px;
}

.book-title {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #333;
}

.book-meta {
  margin-bottom: 10px;
  font-size: 13px;
  color: #666;
}

.tag {
  background: #f0f2f5;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 8px;
}

.book-intro {
  font-size: 13px;
  color: #999;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 12px;
}

.book-stats {
  font-size: 14px;
  font-weight: bold;
  color: #ff4500;
}

.word-count {
  color: #666;
  margin-left: 15px;
  font-weight: normal;
}

.loading {
  text-align: center;
  padding: 50px 0;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    margin-bottom: 20px;
  }
  
  .nav-item {
    display: inline-block;
    border-left: none;
    border-bottom: 4px solid transparent;
    padding: 10px 15px;
  }
  
  .nav-item.active {
    border-left: none;
    border-bottom-color: #409eff;
  }
  
  .book-item {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .rank-badge {
    position: absolute;
    top: 10px;
    left: 10px;
  }
  
  .book-info {
    margin-left: 0;
    margin-top: 10px;
  }
}

/* 深色模式样式 */
.dark-mode .rank-page {
  background: #121212 !important;
  color: #e0e0e0 !important;
}

.dark-mode .rank-header {
  background: #1e1e1e;
  border-bottom: 1px solid #3a3a3a;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.dark-mode .rank-header h1 {
  color: #e0e0e0;
}

.dark-mode .rank-header p {
  color: #999;
}

.dark-mode .sidebar {
  background: #1e1e1e;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.dark-mode .nav-item {
  color: #e0e0e0;
}

.dark-mode .nav-item:hover {
  background: rgba(102, 177, 255, 0.1);
  color: #66b1ff;
}

.dark-mode .nav-item.active {
  background: rgba(102, 177, 255, 0.15);
  color: #66b1ff;
  border-left-color: #66b1ff;
}

.dark-mode .main-list {
  background: #1e1e1e;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.dark-mode .book-item {
  border-bottom: 1px solid #3a3a3a;
}

.dark-mode .book-item:hover {
  background: rgba(255,255,255,0.05);
}

.dark-mode .book-title {
  color: #e0e0e0;
}

.dark-mode .book-meta {
  color: #999;
}

.dark-mode .tag {
  background: #3a3a3a;
  color: #b0b0b0;
}

.dark-mode .book-intro {
  color: #999;
}

.dark-mode .book-stats {
  color: #ff6b6b;
}

.dark-mode .word-count {
  color: #999;
}

.dark-mode .loading {
  color: #999;
}
</style>