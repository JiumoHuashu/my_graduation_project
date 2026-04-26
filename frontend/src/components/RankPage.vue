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
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: #f5f7f9;
  min-height: 100vh;
  letter-spacing: -0.01em;
}

.rank-header {
  background: #fff;
  text-align: center;
  padding: 24px;
  box-shadow: 0 4px 30px rgba(0,0,0,0.03);
}

.rank-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #000000;
  letter-spacing: -0.01em;
}

.rank-header p {
  margin: 0;
  font-size: 14px;
  color: #666666;
  letter-spacing: -0.01em;
}

.container {
  display: flex;
  max-width: 1100px;
  margin: 24px auto;
  gap: 24px;
  padding: 0 24px;
}

/* 侧边栏升级 */
.sidebar {
  width: 200px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  height: fit-content;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 30px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.nav-item {
  padding: 16px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
  position: relative;
}

.nav-item:hover {
  background: rgba(0, 0, 0, 0.04);
  transform: translateX(4px);
}

.nav-item.active {
  background: #000000;
  color: #ffffff;
  border-left-color: #000000;
  font-weight: 600;
}

.main-list {
  flex: 1;
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 30px rgba(0,0,0,0.05);
}

/* 榜单列表优化 */
.book-item {
  display: flex;
  padding: 24px 0;
  border-bottom: 1px solid #f0f0f0;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
}

.book-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.08);
}

/* 强化名次展示 */
.rank-badge {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #999999;
  color: #ffffff;
  text-align: center;
  line-height: 36px;
  margin-right: 20px;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s ease;
}

.rank-badge:hover {
  transform: scale(1.1);
}

/* 前三名使用金/银/铜渐变背景 */
.top-1 {
  background: linear-gradient(135deg, #FFD700, #FFA500);
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.4);
}

.top-2 {
  background: linear-gradient(135deg, #C0C0C0, #E8E8E8);
  box-shadow: 0 4px 12px rgba(192, 192, 192, 0.4);
}

.top-3 {
  background: linear-gradient(135deg, #CD7F32, #F4A460);
  box-shadow: 0 4px 12px rgba(205, 127, 50, 0.4);
}

/* 封面比例保护 */
.book-cover {
  width: 100px;
  aspect-ratio: 3/4;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.book-item:hover .book-cover img {
  transform: scale(1.05);
}

.book-info {
  flex: 1;
  margin-left: 24px;
}

.book-title {
  margin: 0 0 12px 0;
  font-size: 20px;
  font-weight: 600;
  color: #000000;
  letter-spacing: -0.01em;
}

.book-meta {
  margin-bottom: 12px;
  font-size: 13px;
  color: #666666;
  display: flex;
  align-items: center;
  gap: 12px;
}

.tag {
  background: #f5f5f5;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  color: #666666;
  transition: all 0.3s ease;
}

/* 简介文本优化 */
.book-intro {
  font-size: 14px;
  color: #999999;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 16px;
  letter-spacing: -0.01em;
}

/* 统计与交互 */
.book-stats {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 13px;
  color: #666666;
}

.hot-value {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  color: #000000;
}

.word-count {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666666;
}

.loading {
  text-align: center;
  padding: 60px 0;
  color: #666666;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    margin-bottom: 24px;
  }
  
  .nav-item {
    display: inline-block;
    border-left: none;
    border-bottom: 4px solid transparent;
    padding: 12px 16px;
  }
  
  .nav-item.active {
    border-left: none;
    border-bottom-color: #000000;
  }
  
  .book-item {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .rank-badge {
    position: absolute;
    top: 12px;
    left: 12px;
  }
  
  .book-info {
    margin-left: 0;
    margin-top: 16px;
  }
  
  .book-stats {
    justify-content: center;
  }
}

/* 深色模式样式 */
.dark-mode .rank-page {
  background: #0a0a0a !important;
  color: #ffffff !important;
}

.dark-mode .rank-header {
  background: rgba(26, 26, 26, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 30px rgba(0,0,0,0.3);
}

.dark-mode .rank-header h1 {
  color: #ffffff;
}

.dark-mode .rank-header p {
  color: #b0b0b0;
}

.dark-mode .sidebar {
  background: rgba(26, 26, 26, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 30px rgba(0,0,0,0.3);
}

.dark-mode .nav-item {
  color: #ffffff;
}

.dark-mode .nav-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.dark-mode .nav-item.active {
  background: #ffffff;
  color: #000000;
  border-left-color: #ffffff;
}

.dark-mode .main-list {
  background: rgba(26, 26, 26, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 30px rgba(0,0,0,0.3);
}

.dark-mode .book-item {
  border-bottom: 1px solid #333333;
}

.dark-mode .book-item:hover {
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

.dark-mode .book-title {
  color: #ffffff;
}

.dark-mode .book-meta {
  color: #b0b0b0;
}

.dark-mode .tag {
  background: #333333;
  color: #b0b0b0;
}

.dark-mode .book-intro {
  color: #999999;
}

.dark-mode .hot-value {
  color: #ffffff;
}

.dark-mode .word-count {
  color: #b0b0b0;
}

.dark-mode .loading {
  color: #999999;
}

/* 深色模式下前三名的金属质感 */
.dark-mode .top-1 {
  background: linear-gradient(135deg, #B8860B, #FFD700);
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
}

.dark-mode .top-2 {
  background: linear-gradient(135deg, #708090, #C0C0C0);
  box-shadow: 0 4px 12px rgba(192, 192, 192, 0.3);
}

.dark-mode .top-3 {
  background: linear-gradient(135deg, #8B4513, #CD7F32);
  box-shadow: 0 4px 12px rgba(205, 127, 50, 0.3);
}
</style>