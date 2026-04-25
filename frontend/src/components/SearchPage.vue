<template>
  <div class="search-page">
    <header class="page-header">
      <h1>小说书库</h1>
      <p>探索精彩的小说世界</p>
      <div class="search-bar">
        <input
          type="text"
          v-model="searchKeyword"
          placeholder="搜索小说书名"
          @keyup.enter="handleSearch"
        >
        <button class="search-btn" @click="handleSearch">搜索</button>
      </div>
    </header>

    <div class="category-section">
      <h2>分类浏览</h2>
      <div class="category-grid">
        <div
          v-for="cat in categoryList"
          :key="cat"
          class="category-card"
          @click="handleCategorySelect(cat)"
        >
          <div class="category-icon">{{ getCategoryIcon(cat) }}</div>
          <h3 class="category-name">{{ cat }}</h3>
        </div>
      </div>
    </div>

    <div v-if="showSearchResults" class="books-section">
      <h2>搜索结果 - "{{ searchKeyword }}"</h2>
      <div v-if="loading" class="loading">搜索中...</div>
      <div v-else-if="searchResults.length === 0" class="empty-results">
        <p>未找到相关书籍</p>
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
import { ref, onMounted } from 'vue'
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
</script>

<style scoped>
.search-page {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: #ffffff;
  min-height: 100vh;
  padding-bottom: 48px;
}

.page-header {
  background: #000000;
  text-align: center;
  padding: 80px 24px;
  color: #ffffff;
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
  margin-bottom: 24px;
}

.search-bar {
  display: flex;
  max-width: 500px;
  margin: 0 auto;
  gap: 12px;
}

.search-bar input {
  flex: 1;
  padding: 14px 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 50px;
  font-size: 16px;
  font-weight: 330;
  letter-spacing: -0.14px;
  outline: none;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  transition: border-color 0.2s;
}

.search-bar input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.search-bar input:focus {
  border-color: rgba(255, 255, 255, 0.5);
}

.search-btn {
  background: #ffffff;
  color: #000000;
  border: none;
  padding: 14px 32px;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.search-btn:hover {
  opacity: 0.85;
}

.search-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}

.empty-results {
  text-align: center;
  padding: 48px 0;
  color: #666666;
  font-size: 16px;
  font-weight: 320;
}

.category-section {
  max-width: 1200px;
  margin: 48px auto;
  padding: 0 24px;
}

.category-section h2 {
  font-size: 32px;
  color: #000000;
  margin: 0 0 32px 0;
  text-align: center;
  font-weight: 540;
  letter-spacing: -0.26px;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.category-card {
  background: #fafafa;
  border-radius: 8px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.category-icon {
  font-size: 40px;
  margin-bottom: 16px;
  color: #000000;
}

.category-name {
  font-size: 18px;
  color: #000000;
  margin: 0;
  font-weight: 450;
  letter-spacing: -0.14px;
}

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
  gap: 24px;
}

.book-card {
  background: #fafafa;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.book-cover {
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

.book-info {
  padding: 16px;
}

.book-title {
  font-size: 14px;
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
  color: #000000;
}

@media (max-width: 768px) {
  .page-header {
    padding: 56px 20px;
  }

  .page-header h1 {
    font-size: 36px;
  }

  .category-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }

  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }
}

.dark-mode .search-page {
  background: #000000 !important;
  color: #ffffff !important;
}

.dark-mode .page-header {
  background: #ffffff;
  color: #000000;
}

.dark-mode .search-bar input {
  background: rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.15);
  color: #000000;
}

.dark-mode .search-bar input::placeholder {
  color: rgba(0, 0, 0, 0.4);
}

.dark-mode .search-bar input:focus {
  border-color: rgba(0, 0, 0, 0.3);
}

.dark-mode .search-btn {
  background: #000000;
  color: #ffffff;
}

.dark-mode .search-btn:hover {
  opacity: 0.85;
}

.dark-mode .search-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

.dark-mode .category-section h2 {
  color: #ffffff;
}

.dark-mode .category-card {
  background: #0a0a0a;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-mode .category-icon {
  color: #ffffff;
}

.dark-mode .category-name {
  color: #ffffff;
}

.dark-mode .books-section h2 {
  color: #ffffff;
}

.dark-mode .book-card {
  background: #0a0a0a;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-mode .book-title {
  color: #ffffff;
}

.dark-mode .book-author {
  color: #b0b0b0;
}

.dark-mode .book-cover {
  background: #1a1a1a;
}

.dark-mode .loading {
  color: #b0b0b0;
}

.dark-mode .empty-results {
  color: #b0b0b0;
}
</style>
