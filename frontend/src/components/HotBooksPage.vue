<template>
  <div class="hot-books-page">
    <header class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1>热门榜单</h1>
          <p>根据阅读量排序的热门小说</p>
          <p>书籍数量: {{ books.length }}</p>
        </div>
        <button class="refresh-btn" @click="getHotBooks">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21.5 2v6h-6M2.5 22v-6h6M2 12A10 10 0 1 0 22 12"/>
          </svg>
          刷新数据
        </button>
      </div>
    </header>

    <div class="hot-books-section">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="books.length > 0" class="books-grid">
        <div
          v-for="(book, index) in books"
          :key="book.book_id"
          class="book-card"
          :class="{ 'top-rank': index < 3, 'top-1': index === 0, 'top-2': index === 1, 'top-3': index === 2 }"
        >
          <div class="book-rank" :class="{ 'top-rank': index < 3, 'top-1': index === 0, 'top-2': index === 1, 'top-3': index === 2 }">
            {{ index + 1 }}
          </div>
          <div class="book-cover" @click="goToDetail(book.book_id)">
            <img :src="book.cover_url || 'https://via.placeholder.com/498x705?text=No+Cover'" @error="handleImgError" alt="封面">
          </div>
          <div class="book-info">
            <h4 class="book-title" @click="goToDetail(book.book_id)">{{ book.title }}</h4>
            <p class="book-author">{{ book.author || '未知作者' }}</p>
            <div class="book-meta">
              <span class="read-count">月阅读: {{ formatNumber(book.monthly_read) }}</span>
              <span class="total-flowers">总鲜花: {{ formatNumber(book.total_flowers) }}</span>
              <span class="monthly-flowers">月鲜花: {{ formatNumber(book.monthly_flowers) }}</span>
            </div>
            <div class="book-intro">
              {{ book.introduction || '暂无简介' }}
            </div>
            <div class="book-full-intro">
              <h4 class="book-title" @click="goToDetail(book.book_id)">{{ book.title }}</h4>
              <div class="book-full-intro-text">
                {{ book.introduction || '暂无简介' }}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="empty">暂无热门书籍</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const books = ref([])
const loading = ref(true)
const error = ref('')

const getHotBooks = async () => {
  loading.value = true
  error.value = ''

  try {
    const savedUser = localStorage.getItem('user')

    if (savedUser) {
      const user = JSON.parse(savedUser)

      const bookshelfResponse = await fetch(`/api/user/bookshelf/?user_id=${user.id}`)
      const bookshelfRes = await bookshelfResponse.json()

      if (bookshelfRes.code === 200) {
        const bookshelfData = bookshelfRes.data

        if (bookshelfData && bookshelfData.length > 0) {
          const recommendResponse = await fetch(`/api/recommend/bookshelf/?user_id=${user.id}`)
          const recommendRes = await recommendResponse.json()

          if (recommendRes.code === 200) {
            books.value = recommendRes.data
          } else {
            error.value = recommendRes.msg
          }
        } else {
          const hotResponse = await fetch('/api/hot/')
          const hotRes = await hotResponse.json()

          if (hotRes.code === 200) {
            books.value = hotRes.data
          } else {
            error.value = hotRes.msg
          }
        }
      } else {
        const hotResponse = await fetch('/api/hot/')
        const hotRes = await hotResponse.json()

        if (hotRes.code === 200) {
          books.value = hotRes.data
        } else {
          error.value = hotRes.msg
        }
      }
    } else {
      const hotResponse = await fetch('/api/hot/')
      const hotRes = await hotResponse.json()

      if (hotRes.code === 200) {
        books.value = hotRes.data
      } else {
        error.value = hotRes.msg
      }
    }
  } catch (err) {
    error.value = '获取热门书籍失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

const goToDetail = (bookId) => {
  router.push(`/${bookId}`)
}

const handleImgError = (e) => {
  e.target.src = 'https://via.placeholder.com/498x705?text=No+Cover'
}

const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num
}

getHotBooks()

onMounted(() => {
  getHotBooks()
})
</script>

<style scoped>
:global(body) {
  overflow-x: hidden;
  margin: 0;
  padding: 0;
}

.hot-books-page {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: #ffffff;
  min-height: 100vh;
  padding-bottom: 48px;
  overflow-x: hidden;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* 头部区域 */
.page-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 40px 24px;
  color: #333333;
  position: relative;
  overflow: hidden;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 32px;
  position: relative;
  z-index: 2;
}

.header-text {
  flex: 1;
  min-width: 0;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 500;
  letter-spacing: -0.02em;
  line-height: 1.1;
}

.page-header p {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 320;
  letter-spacing: -0.01em;
  opacity: 0.8;
}

/* 刷新按钮 */
.refresh-btn {
  background: transparent;
  color: #333333;
  border: 1px solid #e0e0e0;
  padding: 10px 20px;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 400;
  letter-spacing: -0.01em;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.refresh-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  border-color: #000000;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.refresh-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

/* 热门书籍区域 */
.hot-books-section {
  max-width: 1200px;
  margin: 48px auto;
  padding: 0 24px;
  overflow-x: hidden;
}

/* 书籍网格 */
.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 30px;
  margin-top: 24px;
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* 书籍卡片 */
.book-card {
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 400px;
  width: 100%;
  box-sizing: border-box;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.book-card:hover .book-intro {
  display: none;
}

.book-card:hover .book-author {
  display: none;
}

.book-card:hover .book-meta {
  display: none;
}

.book-card:hover .book-full-intro {
  display: flex;
}

/* 书籍信息 */
.book-info {
  position: relative;
  z-index: 10;
  background: transparent;
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 180px;
}

/* 书籍标题 */
.book-title {
  font-size: 16px;
  color: #333333;
  margin: 0 0 8px 0;
  line-height: 1.4;
  display: -webkit-box;
  display: box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
  cursor: pointer;
  transition: opacity 0.3s ease;
  font-weight: 500;
  letter-spacing: -0.01em;
}

.book-title:hover {
  opacity: 0.8;
}

/* 榜单名次 */
.book-rank {
  position: absolute;
  top: 12px;
  left: 12px;
  background: rgba(0, 0, 0, 0.8);
  color: #ffffff;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: -0.01em;
  border-radius: 20px;
  z-index: 10;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

/* 前三名样式 */
.book-rank.top-1 {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #333333;
  font-size: 18px;
  padding: 10px 16px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
}

.book-rank.top-2 {
  background: linear-gradient(135deg, #c0c0c0 0%, #e0e0e0 100%);
  color: #333333;
  font-size: 16px;
  padding: 9px 14px;
  font-weight: 600;
  box-shadow: 0 4px 10px rgba(192, 192, 192, 0.3);
}

.book-rank.top-3 {
  background: linear-gradient(135deg, #cd7f32 0%, #e6b368 100%);
  color: #333333;
  font-size: 16px;
  padding: 9px 14px;
  font-weight: 600;
  box-shadow: 0 4px 10px rgba(205, 127, 50, 0.3);
}

/* 书籍封面 */
.book-cover {
  cursor: pointer;
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  overflow: hidden;
  background: #f4f4f4;
}

.book-cover img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.5s ease;
}

.book-cover:hover img {
  transform: scale(1.05);
}

/* 书籍作者 */
.book-author {
  font-size: 14px;
  color: #666666;
  margin: 0 0 12px 0;
  font-weight: 320;
  letter-spacing: -0.01em;
}

/* 书籍元数据 */
.book-meta {
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
  letter-spacing: -0.01em;
}

.read-count {
  color: #333333;
}

.total-flowers {
  color: #666666;
}

.monthly-flowers {
  color: #666666;
}

/* 书籍简介 */
.book-intro {
  font-size: 13px;
  color: #333333;
  line-height: 1.4;
  display: -webkit-box;
  display: box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
  flex: 1;
  font-weight: 320;
  letter-spacing: -0.01em;
}

/* 书籍悬停详情 */
.book-full-intro {
  display: none;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  padding: 20px;
  font-size: 14px;
  color: #333333;
  line-height: 1.5;
  overflow-y: auto;
  z-index: 20;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  flex-direction: column;
}

.book-full-intro h4.book-title {
  margin-bottom: 16px;
  font-size: 18px;
  color: #333333;
  display: block;
  overflow: visible;
  -webkit-line-clamp: unset;
  line-clamp: unset;
  height: auto;
  cursor: pointer;
  transition: opacity 0.3s ease;
  z-index: 30;
  position: relative;
  font-weight: 500;
  letter-spacing: -0.01em;
}

.book-full-intro h4.book-title:hover {
  opacity: 0.8;
}

.book-full-intro-text {
  margin-top: 16px;
  line-height: 1.6;
  font-size: 14px;
  color: #666666;
  font-weight: 320;
  flex: 1;
}

/* 加载状态 */
.loading {
  text-align: center;
  padding: 64px 0;
  color: #666666;
  font-size: 16px;
  font-weight: 320;
  letter-spacing: -0.01em;
}

/* 错误状态 */
.error {
  text-align: center;
  padding: 24px;
  color: #333333;
  background: #f9f9f9;
  border-radius: 12px;
  margin-top: 24px;
  font-weight: 400;
  letter-spacing: -0.01em;
}

/* 空状态 */
.empty {
  text-align: center;
  padding: 64px 0;
  color: #999999;
  font-size: 18px;
  font-weight: 320;
  letter-spacing: -0.01em;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 24px;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
    gap: 24px;
  }
  
  .book-card {
    min-height: 380px;
  }
}

@media (max-width: 992px) {
  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 20px;
  }
  
  .book-card {
    min-height: 360px;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 32px 20px;
  }
  
  .page-header h1 {
    font-size: 28px;
  }
  
  .books-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  
  .book-card {
    min-height: 340px;
  }
  
  .hot-books-section {
    padding: 0 16px;
  }
}

@media (max-width: 480px) {
  .books-grid {
    grid-template-columns: 1fr;
  }
  
  .book-card {
    min-height: 400px;
  }
}

/* 暗色模式 */
.dark-mode .hot-books-page {
  background: #121212 !important;
  color: #ffffff !important;
}

.dark-mode .page-header {
  background: linear-gradient(135deg, #1a1a1a 0%, #2c2c2c 100%);
  color: #ffffff;
}

.dark-mode .header-text p {
  opacity: 0.7;
}

.dark-mode .refresh-btn {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.dark-mode .refresh-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: #ffffff;
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.1);
}

.dark-mode .refresh-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}

.dark-mode .book-card {
  background: #1a1a1a;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.dark-mode .book-card:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
}

.dark-mode .book-full-intro {
  background: rgba(26, 26, 26, 0.95);
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
  color: #ffffff;
}

.dark-mode .book-full-intro h4.book-title {
  color: #ffffff;
}

.dark-mode .book-full-intro-text {
  color: #b0b0b0;
}

.dark-mode .book-title {
  color: #ffffff;
}

.dark-mode .book-author {
  color: #b0b0b0;
}

.dark-mode .book-cover {
  background: #2c2c2c;
}

.dark-mode .book-intro {
  color: #e0e0e0;
}

.dark-mode .read-count {
  color: #e0e0e0;
}

.dark-mode .total-flowers {
  color: #b0b0b0;
}

.dark-mode .monthly-flowers {
  color: #b0b0b0;
}

.dark-mode .loading {
  color: #b0b0b0;
}

.dark-mode .error {
  color: #ffffff;
  background: #2c2c2c;
}

.dark-mode .empty {
  color: #b0b0b0;
}

/* 暗色模式下的前三名样式 */
.dark-mode .book-rank.top-1 {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #333333;
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.4);
}

.dark-mode .book-rank.top-2 {
  background: linear-gradient(135deg, #c0c0c0 0%, #e0e0e0 100%);
  color: #333333;
  box-shadow: 0 4px 10px rgba(192, 192, 192, 0.4);
}

.dark-mode .book-rank.top-3 {
  background: linear-gradient(135deg, #cd7f32 0%, #e6b368 100%);
  color: #333333;
  box-shadow: 0 4px 10px rgba(205, 127, 50, 0.4);
}
</style>
