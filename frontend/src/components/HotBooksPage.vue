<template>
  <div class="hot-books-page">
    <header class="page-header">
      <h1>首页</h1>
      <p>根据阅读量排序的热门小说</p>
      <p>书籍数量: {{ books.length }}</p>
      <button class="refresh-btn" @click="getHotBooks">刷新数据</button>
    </header>

    <div class="hot-books-section">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="books.length > 0" class="books-grid">
        <div
          v-for="(book, index) in books"
          :key="book.book_id"
          class="book-card"
        >
          <div class="book-rank">{{ index + 1 }}</div>
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
.hot-books-page {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: #ffffff;
  min-height: 100vh;
  padding-bottom: 48px;
}

.page-header {
  background: #000000;
  text-align: center;
  padding: 30px 24px;
  color: #ffffff;
}

.page-header h1 {
  margin: 0 0 12px 0;
  font-size: 36px;
  font-weight: 400;
  letter-spacing: -0.96px;
  line-height: 1.10;
}

.page-header p {
  margin: 0;
  font-size: 20px;
  font-weight: 330;
  letter-spacing: -0.14px;
  opacity: 0.8;
  margin-bottom: 16px;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.16);
  color: #ffffff;
  border: 1px dashed 2px rgba(255, 255, 255, 0.3);
  padding: 12px 24px;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.14px;
  cursor: pointer;
  transition: background 0.2s;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.24);
}

.refresh-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}

.hot-books-section {
  max-width: 1200px;
  margin: 48px auto;
  padding: 0 24px;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 24px;
  margin-top: 24px;
  max-width: 100%;
  overflow-x: hidden;
}

.book-card {
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 340px;
}

.book-info {
  position: relative;
  z-index: 10;
  background: transparent;
  padding: 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 150px;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
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
  display: block;
}

.book-full-intro {
  display: none;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.98);
  padding: 14px;
  font-size: 13px;
  color: #000000;
  line-height: 1.4;
  overflow-y: auto;
  z-index: 20;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.book-full-intro h4.book-title {
  margin-bottom: 12px;
  font-size: 16px;
  color: #000000;
  display: block;
  overflow: visible;
  -webkit-line-clamp: unset;
  line-clamp: unset;
  height: auto;
  cursor: pointer;
  transition: opacity 0.2s;
  z-index: 30;
  position: relative;
  font-weight: 450;
  letter-spacing: -0.14px;
}

.book-full-intro h4.book-title:hover {
  opacity: 0.7;
}

.book-full-intro-text {
  margin-top: 12px;
  line-height: 1.4;
  font-size: 13px;
  color: #666666;
  font-weight: 320;
}

.book-title {
  font-size: 16px;
  color: #000000;
  margin: 0 0 6px 0;
  line-height: 1.4;
  display: -webkit-box;
  display: box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
  cursor: pointer;
  transition: opacity 0.2s;
  font-weight: 450;
  letter-spacing: -0.14px;
}

.book-title:hover {
  opacity: 0.7;
}

.book-rank {
  position: absolute;
  top: 0;
  left: 0;
  background: #000000;
  color: #ffffff;
  padding: 6px 12px;
  font-size: 14px;
  font-weight: 540;
  letter-spacing: -0.14px;
  border-bottom-right-radius: 8px;
  z-index: 10;
}

.book-cover {
  cursor: pointer;
  position: relative;
  width: 100%;
  padding-top: 141.57%;
  overflow: hidden;
  background: #f0f0f0;
}

.book-cover img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
}

.book-cover:hover img {
  transform: scale(1.03);
}

.book-author {
  font-size: 14px;
  color: #666666;
  margin: 0 0 10px 0;
  font-weight: 320;
}

.book-meta {
  font-size: 12px;
  font-weight: 450;
  margin-bottom: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex-shrink: 0;
}

.read-count {
  color: #000000;
}

.total-flowers {
  color: #666666;
}

.monthly-flowers {
  color: #666666;
}

.book-intro {
  font-size: 13px;
  color: #333333;
  line-height: 1.3;
  display: -webkit-box;
  display: box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
  flex: 1;
  font-weight: 320;
}

.loading {
  text-align: center;
  padding: 48px 0;
  color: #666666;
  font-size: 16px;
  font-weight: 320;
}

.error {
  text-align: center;
  padding: 20px;
  color: #000000;
  background: #f5f5f5;
  border-radius: 8px;
  margin-top: 24px;
  font-weight: 400;
}

.empty {
  text-align: center;
  padding: 48px 0;
  color: #999999;
  font-size: 18px;
  font-weight: 320;
}

@media (max-width: 1200px) {
  .books-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 992px) {
  .books-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 56px 20px;
  }

  .page-header h1 {
    font-size: 36px;
  }

  .books-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .books-grid {
    grid-template-columns: 1fr;
  }
}

.dark-mode .hot-books-page {
  background: #000000 !important;
  color: #ffffff !important;
}

.dark-mode .page-header {
  background: #e0e0e0;
  color: #000000;
  padding: 30px 24px;
}

.dark-mode .book-card {
  background: #1a1a1a;
  box-shadow: none;
}

.dark-mode .book-full-intro {
  background: rgba(26, 26, 26, 0.98);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  color: #ffffff;
}

.dark-mode .book-full-intro h4.book-title {
  color: #ffffff;
}

.dark-mode .book-full-intro h4.book-title:hover {
  opacity: 0.7;
}

.dark-mode .book-full-intro-text {
  color: #b0b0b0;
}

.dark-mode .book-title {
  color: #ffffff;
}

.dark-mode .book-title:hover {
  opacity: 0.7;
}

.dark-mode .book-author {
  color: #b0b0b0;
}

.dark-mode .book-cover {
  background: #2a2a2a;
}

.dark-mode .loading {
  color: #b0b0b0;
}

.dark-mode .error {
  color: #ffffff;
  background: #1a1a1a;
}

.dark-mode .empty {
  color: #b0b0b0;
}

.dark-mode .book-intro {
  color: #e0e0e0;
}

.dark-mode .refresh-btn {
  background: rgba(0, 0, 0, 0.16);
  color: #000000;
  border: 1px dashed rgba(0, 0, 0, 0.3);
}

.dark-mode .refresh-btn:hover {
  background: rgba(0, 0, 0, 0.24);
}

.dark-mode .refresh-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
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
</style>
