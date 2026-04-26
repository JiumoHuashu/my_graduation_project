<template>
  <div class="search-page">
    <header class="page-header">
      <h1>小说书库</h1>
      <p>探索精彩的小说世界</p>
    </header>

    <div class="sticky-search-container">
      <div class="search-bar">
        <input
          type="text"
          v-model="searchKeyword"
          placeholder="搜索小说书名"
          @keyup.enter="handleSearch"
        >
        <button class="search-btn" @click="handleSearch">搜索</button>
      </div>

      <div class="category-section">
        <div class="category-scrollbar">
          <div
            v-for="cat in categoryList"
            :key="cat"
            :class="['category-chip', { 'active': selectedCategory === cat }]"
            @click="handleCategorySelect(cat)"
          >
            {{ cat }}
          </div>
        </div>
      </div>
    </div>

    <div v-if="showSearchResults" class="books-section">
      <h2>搜索结果 - "{{ searchKeyword }}"</h2>
      <div v-if="loading" class="loading">搜索中...</div>
      <div v-else-if="searchResults.length === 0" class="empty-results">
        <div class="empty-icon">🔍</div>
        <h3>未找到相关书籍</h3>
        <p>尝试使用其他关键词或浏览分类</p>
      </div>
      <div v-else class="books-grid">
        <div
          v-for="(book, index) in searchResults"
          :key="book.book_id"
          class="book-card"
          @click="goToDetail(book.book_id)"
        >
          <div class="book-cover">
            <img :src="book.cover_url" @error="handleImgError" alt="封面">
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

    <div v-else-if="selectedCategory" class="books-section">
      <h2>{{ selectedCategory }} - 热门书籍</h2>
      <div v-if="loading" class="loading">数据加载中...</div>
      <div v-else class="books-grid">
        <div
          v-for="(book, index) in books"
          :key="book.book_id"
          class="book-card"
          @click="goToDetail(book.book_id)"
        >
          <div class="book-cover">
            <img :src="book.cover_url" @error="handleImgError" alt="封面">
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
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const categoryList = ['同人小说', '玄幻奇幻', '武侠仙侠', '都市言情', '军事历史', '科幻网游', '推理灵异', '青春校园', '轻小说', '女生小说']
const selectedCategory = ref('')
const searchKeyword = ref('')
const searchResults = ref([])
const books = ref([])
const loading = ref(false)
const showSearchResults = ref(false)

const handleCategorySelect = (cat) => {
  selectedCategory.value = cat
  showSearchResults.value = false
  fetchBooks(cat)
}

const fetchBooks = async (cat) => {
  loading.value = true
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/rank/?category=${cat}`)
    books.value = res.data.data
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleImgError = (e) => {
  e.target.src = 'https://via.placeholder.com/120x160?text=No+Cover'
}

const goToDetail = (bookId) => {
  router.push(`/${bookId}`)
}

const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    return
  }

  loading.value = true
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/search/`, {
      params: { keyword: searchKeyword.value.trim() }
    })

    if (res.data.code === 200) {
      searchResults.value = res.data.data
      showSearchResults.value = true
      selectedCategory.value = ''
    }
  } catch (error) {
    console.error('搜索失败:', error)
  } finally {
    loading.value = false
  }
}

const getCategoryIcon = (cat) => {
  const iconMap = {
    '同人小说': '✦',
    '玄幻奇幻': '◈',
    '武侠仙侠': '◇',
    '都市言情': '♥',
    '军事历史': '◆',
    '科幻网游': '▶',
    '推理灵异': '◉',
    '青春校园': '○',
    '轻小说': '□',
    '女生小说': '■'
  }
  return iconMap[cat] || '▪'
}

// Sticky search bar logic
const handleScroll = () => {
  const stickyContainer = document.querySelector('.sticky-search-container')
  if (stickyContainer) {
    if (window.scrollY > 100) {
      stickyContainer.classList.add('scrolled')
    } else {
      stickyContainer.classList.remove('scrolled')
    }
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.search-page {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: #ffffff;
  min-height: 100vh;
  padding-bottom: 48px;
}

.page-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  text-align: center;
  padding: 60px 24px;
  color: #333333;
}

.page-header h1 {
  margin: 0 0 12px 0;
  font-size: 48px;
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
}

/* Sticky search container */
.sticky-search-container {
  position: sticky;
  top: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 20px 24px;
  z-index: 100;
  transition: all 0.3s ease;
}

.sticky-search-container.scrolled {
  padding: 12px 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.search-bar {
  display: flex;
  max-width: 600px;
  margin: 0 auto 20px;
  gap: 12px;
}

.search-bar input {
  flex: 1;
  padding: 16px 24px;
  border: 1px solid #e0e0e0;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 330;
  letter-spacing: -0.14px;
  outline: none;
  background: #ffffff;
  color: #333333;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.search-bar input::placeholder {
  color: #999999;
}

.search-bar input:focus {
  border-color: #333333;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.search-btn {
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 16px 32px;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: -0.14px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.search-btn:focus {
  outline: dashed 2px #333333;
  outline-offset: 2px;
}

/* Category section */
.category-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0;
}

.category-scrollbar {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 8px;
  scrollbar-width: thin;
  scrollbar-color: #e0e0e0 #f5f5f5;
}

.category-scrollbar::-webkit-scrollbar {
  height: 6px;
}

.category-scrollbar::-webkit-scrollbar-track {
  background: #f5f5f5;
  border-radius: 3px;
}

.category-scrollbar::-webkit-scrollbar-thumb {
  background: #e0e0e0;
  border-radius: 3px;
}

.category-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #d0d0d0;
}

.category-chip {
  padding: 10px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 400;
  color: #333333;
  background: #f5f5f5;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  border: 1px solid #e0e0e0;
}

.category-chip:hover {
  background: #e8e8e8;
  transform: translateY(-2px);
}

.category-chip.active {
  background: #000000;
  color: #ffffff;
  border-color: #000000;
}

/* Empty results */
.empty-results {
  text-align: center;
  padding: 80px 0;
  color: #666666;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-results h3 {
  font-size: 20px;
  font-weight: 500;
  margin: 0 0 8px 0;
  color: #333333;
}

.empty-results p {
  font-size: 16px;
  font-weight: 320;
  margin: 0;
  opacity: 0.8;
}

/* Books section */
.books-section {
  max-width: 1200px;
  margin: 48px auto;
  padding: 0 24px;
}

.books-section h2 {
  font-size: 24px;
  color: #000000;
  margin: 0 0 32px 0;
  font-weight: 540;
  letter-spacing: -0.26px;
}

.loading {
  text-align: center;
  padding: 48px 0;
  color: #666666;
  font-size: 16px;
  font-weight: 320;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 32px;
}

.book-card {
  cursor: pointer;
  transition: all 0.3s ease;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
}

.book-card:nth-child(1) { animation-delay: 0.05s; }
.book-card:nth-child(2) { animation-delay: 0.1s; }
.book-card:nth-child(3) { animation-delay: 0.15s; }
.book-card:nth-child(4) { animation-delay: 0.2s; }
.book-card:nth-child(5) { animation-delay: 0.25s; }
.book-card:nth-child(6) { animation-delay: 0.3s; }
.book-card:nth-child(7) { animation-delay: 0.35s; }
.book-card:nth-child(8) { animation-delay: 0.4s; }
.book-card:nth-child(9) { animation-delay: 0.45s; }
.book-card:nth-child(10) { animation-delay: 0.5s; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.book-cover {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  overflow: hidden;
  background: #f0f0f0;
  border-radius: 8px;
  margin-bottom: 16px;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
}

.book-card:hover {
  transform: translateY(-8px);
}

.book-card:hover .book-cover img {
  transform: scale(1.03);
}

.book-card:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

.book-info {
  padding: 0;
}

.book-title {
  font-size: 14px;
  color: #333333;
  margin: 0 0 6px 0;
  line-height: 1.4;
  display: -webkit-box;
  display: box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
  font-weight: 450;
  letter-spacing: -0.14px;
}

.book-author {
  font-size: 13px;
  color: #666666;
  margin: 0 0 10px 0;
  font-weight: 320;
}

.book-stats {
  font-size: 12px;
  font-weight: 540;
  letter-spacing: -0.1px;
  color: #333333;
}

/* Responsive design */
@media (max-width: 768px) {
  .page-header {
    padding: 40px 20px;
  }

  .page-header h1 {
    font-size: 36px;
  }

  .sticky-search-container {
    padding: 16px 16px;
  }

  .sticky-search-container.scrolled {
    padding: 12px 16px;
  }

  .search-bar {
    max-width: 100%;
  }

  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 24px;
  }

  .books-section {
    padding: 0 16px;
  }
}

/* Dark mode */
.dark-mode .search-page {
  background: #121212 !important;
  color: #ffffff !important;
}

.dark-mode .page-header {
  background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
  color: #ffffff;
}

.dark-mode .sticky-search-container {
  background: rgba(18, 18, 18, 0.95);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.dark-mode .sticky-search-container.scrolled {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}

.dark-mode .search-bar input {
  background: #2d2d2d;
  border: 1px solid #444444;
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.dark-mode .search-bar input::placeholder {
  color: #888888;
}

.dark-mode .search-bar input:focus {
  border-color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.dark-mode .search-btn {
  background: #ffffff;
  color: #000000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.dark-mode .search-btn:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.dark-mode .search-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}

.dark-mode .category-scrollbar {
  scrollbar-color: #444444 #2d2d2d;
}

.dark-mode .category-scrollbar::-webkit-scrollbar-track {
  background: #2d2d2d;
}

.dark-mode .category-scrollbar::-webkit-scrollbar-thumb {
  background: #444444;
}

.dark-mode .category-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #555555;
}

.dark-mode .category-chip {
  background: #2d2d2d;
  color: #ffffff;
  border: 1px solid #444444;
}

.dark-mode .category-chip:hover {
  background: #3d3d3d;
}

.dark-mode .category-chip.active {
  background: #ffffff;
  color: #000000;
  border-color: #ffffff;
}

.dark-mode .empty-results {
  color: #888888;
}

.dark-mode .empty-results h3 {
  color: #ffffff;
}

.dark-mode .books-section h2 {
  color: #ffffff;
}

.dark-mode .book-title {
  color: #ffffff;
}

.dark-mode .book-author {
  color: #888888;
}

.dark-mode .book-cover {
  background: #2d2d2d;
}

.dark-mode .book-stats {
  color: #ffffff;
}

.dark-mode .loading {
  color: #888888;
}

.dark-mode .book-card:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
}
</style>
