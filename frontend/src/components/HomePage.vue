<template>
  <div class="home-page">
    <header class="home-header">
      <h1>小说推荐系统</h1>
      <p>基于深度学习的智能推荐</p>
    </header>

    <div class="recommendation-section">
      <h2>智能推荐</h2>

      <div class="mode-selector">
        <h3>选择推荐模式</h3>
        <div class="mode-buttons">
          <button
            class="mode-btn"
            :class="{ active: selectedMode === 'book' }"
            @click="selectMode('book')"
          >
            基于书名推荐
          </button>
          <button
            class="mode-btn"
            :class="{ active: selectedMode === 'category' }"
            @click="selectMode('category')"
          >
            基于分类推荐
          </button>
          <button
            class="mode-btn"
            :class="{ active: selectedMode === 'interest' }"
            @click="selectMode('interest')"
          >
            兴趣雷达
          </button>
        </div>
      </div>

      <div v-if="selectedMode === 'interest'" class="interest-section">
        <h3>兴趣雷达</h3>
        <p class="interest-hint">点击下方按钮开始兴趣雷达测试</p>
        <button class="recommend-btn" @click="showInterestRadar">
          开始兴趣测试
        </button>
      </div>

      <div v-if="selectedMode === 'book'" class="book-input-section">
        <h3>输入书名</h3>
        <div class="book-input">
          <input
            type="text"
            v-model="bookName"
            placeholder="请输入您喜欢的书名"
            @keyup.enter="getRecommendations"
          >
          <button class="recommend-btn" @click="getRecommendations" :disabled="loading">
            {{ loading ? '推荐中...' : '获取相似推荐' }}
          </button>
        </div>
      </div>

      <div v-if="selectedMode === 'category'" class="category-selector">
        <h3>选择分类（可多选）</h3>
        <div class="category-tags">
          <div
            v-for="cat in mainCategories"
            :key="cat"
            class="category-tag"
            :class="{ active: selectedCategories.includes(cat) }"
            @click="toggleCategory(cat)"
          >
            {{ cat }}
          </div>
        </div>
        <div v-if="selectedCategories.length > 0" class="action-section">
          <button class="recommend-btn" @click="getRecommendations" :disabled="loading">
            {{ loading ? '推荐中...' : '获取优质推荐' }}
          </button>
        </div>
      </div>

      <div v-if="recommendations.length > 0" class="recommendations-section">
        <h3>{{ selectedMode === 'book' ? '相似推荐结果' : recommendations[0].recommendation_reason ? '基于您的收藏推荐' : '优质推荐结果' }}</h3>
        <div class="books-grid">
          <div
            v-for="(book, index) in recommendations.slice(0, 10)"
            :key="index"
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
                <span v-if="selectedMode === 'book'" class="similarity-value">相似度: {{ book.similarity.toFixed(4) }}</span>
                <span v-else class="rating-value">评分: {{ book.read_count.toFixed(4) }}</span>
                <span v-if="selectedMode === 'category'" class="sub-category">类别: {{ book.sub_category }}</span>
              </div>
              <div class="book-intro">
                {{ book.intro }}
              </div>
              <div class="book-actions">
                <button class="action-btn small like-btn" :class="{ 'liked': likedBooks[book.book_id] }" @click="handleUserAction(book.book_id, 'like')">
                  <span class="action-icon">❤️</span>
                </button>
                <button class="action-btn small dislike-btn" @click="handleUserAction(book.book_id, 'dislike')">
                  <span class="action-icon">✕</span>
                </button>
              </div>
              <div class="book-full-intro">
                <h4 class="book-title" @click="goToDetail(book.book_id)">{{ book.title }}</h4>
                <div class="book-full-intro-text">
                  {{ book.intro }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading">加载推荐中...</div>
      <div v-if="error" class="error">{{ error }}</div>
    </div>

    <!-- 兴趣雷达模态框 -->
    <InterestRadar 
      :visible="interestRadarVisible" 
      @confirm="handleInterestConfirm"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import InterestRadar from './InterestRadar.vue'

const router = useRouter()

const mainCategories = ['同人小说', '玄幻奇幻', '武侠仙侠', '都市言情', '军事历史', '科幻网游', '推理灵异', '青春校园', '轻小说', '女生小说']

const selectedMode = ref('interest')
const bookName = ref('')
const selectedCategories = ref([])
const recommendations = ref([])
const loading = ref(false)
const error = ref('')
const interestRadarVisible = ref(false)
const likedBooks = ref({})

const selectMode = (mode) => {
  selectedMode.value = mode
  selectedCategories.value = []
  bookName.value = ''
  recommendations.value = []
  error.value = ''
  interestRadarVisible.value = false
  
  // 当选择兴趣雷达模式时，重新加载推荐列表，包括补偿推荐
  if (mode === 'interest') {
    loadInitialRecommendations()
  }
}

const showInterestRadar = () => {
  interestRadarVisible.value = true
}

const handleInterestConfirm = async (tags) => {
  interestRadarVisible.value = false
  loading.value = true
  error.value = ''
  
  try {
    const res = await axios.post('http://127.0.0.1:8000/api/interests/', {
      tags: tags
    })
    
    if (res.data.code === 200) {
      recommendations.value = res.data.data
    } else {
      error.value = res.data.msg
    }
  } catch (err) {
    console.error('获取兴趣推荐失败:', err)
    error.value = '获取推荐失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

const toggleCategory = (cat) => {
  const index = selectedCategories.value.indexOf(cat)
  if (index > -1) {
    selectedCategories.value.splice(index, 1)
  } else {
    selectedCategories.value.push(cat)
  }
  recommendations.value = []
  error.value = ''
}

const getRecommendations = async () => {
  if (selectedMode.value === 'book') {
    if (!bookName.value.trim()) {
      error.value = '请输入书名'
      return
    }
  } else if (selectedMode.value === 'category') {
    if (selectedCategories.value.length === 0) {
      error.value = '请至少选择一个分类'
      return
    }
  }

  loading.value = true
  error.value = ''

  try {
    let res
    if (selectedMode.value === 'book') {
      res = await axios.get(`http://127.0.0.1:8000/api/recommend/book/`, {
        params: { book_name: bookName.value.trim() }
      })
    } else if (selectedMode.value === 'category') {
      res = await axios.get(`http://127.0.0.1:8000/api/recommend/category/`, {
        params: { categories: selectedCategories.value.join(',') }
      })
    }

    if (res.data.code === 200) {
      recommendations.value = res.data.data
    } else {
      error.value = res.data.msg
    }
  } catch (err) {
    console.error('获取推荐失败:', err)
    error.value = '获取推荐失败，请检查网络连接'
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

const handleUserAction = async (bookId, actionType) => {
  try {
    const savedUser = localStorage.getItem('user')
    if (!savedUser) {
      alert('请先登录')
      return
    }

    const user = JSON.parse(savedUser)
    const res = await axios.post('http://127.0.0.1:8000/api/user/action/', {
      user_id: user.id,
      book_id: bookId,
      action_type: actionType
    })

    if (res.data.code === 200) {
      // 对于收藏行为，更新likedBooks状态
      if (actionType === 'like') {
        likedBooks.value[bookId] = !likedBooks.value[bookId]
        
        // 处理补偿推荐
        if (res.data.compensation_recommendations && res.data.compensation_recommendations.length > 0) {
          // 将补偿推荐的书籍添加到本地存储，供首页使用
          localStorage.setItem('compensation_recommendations', JSON.stringify(res.data.compensation_recommendations))
          // 重新加载推荐列表，显示补偿推荐
          await loadInitialRecommendations()
          // 提示用户有新的推荐
          alert('我们为您推荐了一些相似的书籍，请到首页查看！')
        }
      }
    } else {
      console.error('提交行为反馈失败:', res.data.msg)
    }
  } catch (error) {
    console.error('提交行为反馈失败:', error)
  }
}

const loadInitialRecommendations = async () => {
  try {
    loading.value = true
    error.value = ''
    
    // 首先检查本地存储中是否有补偿推荐的书籍
    const compensationRecs = localStorage.getItem('compensation_recommendations')
    
    // 然后获取常规推荐
    const res = await axios.get('http://127.0.0.1:8000/api/recommend/you_may_like/')
    
    if (res.data.code === 200) {
      if (compensationRecs) {
        try {
          const parsedRecs = JSON.parse(compensationRecs)
          // 将补偿推荐的书籍添加到推荐列表的最前端
          recommendations.value = [...parsedRecs, ...res.data.data]
          // 清除本地存储中的补偿推荐，避免重复显示
          localStorage.removeItem('compensation_recommendations')
        } catch (e) {
          console.error('解析补偿推荐失败:', e)
          recommendations.value = res.data.data
        }
      } else {
        recommendations.value = res.data.data
      }
    } else {
      error.value = res.data.msg
    }
  } catch (err) {
    console.error('获取推荐失败:', err)
    error.value = '获取推荐失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadInitialRecommendations()
})
</script>

<style scoped>
.home-page {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: #ffffff;
  min-height: 100vh;
  padding-bottom: 48px;
}

.home-header {
  background: #000000;
  text-align: center;
  padding: 80px 24px;
  color: #ffffff;
}

.home-header h1 {
  margin: 0 0 12px 0;
  font-size: 48px;
  font-weight: 400;
  letter-spacing: -0.96px;
  line-height: 1.10;
}

.home-header p {
  margin: 0;
  font-size: 20px;
  font-weight: 330;
  letter-spacing: -0.14px;
  opacity: 0.8;
}

.recommendation-section {
  max-width: 1200px;
  margin: 48px auto;
  padding: 0 24px;
}

.recommendation-section h2 {
  font-size: 32px;
  color: #000000;
  margin: 0 0 32px 0;
  text-align: center;
  font-weight: 540;
  letter-spacing: -0.26px;
}

.recommendation-section h3 {
  font-size: 18px;
  color: #000000;
  margin: 0 0 16px 0;
  font-weight: 450;
  letter-spacing: -0.14px;
}

.mode-selector {
  background: #ffffff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.mode-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.mode-btn {
  background: rgba(0, 0, 0, 0.06);
  padding: 12px 24px;
  border: none;
  border-radius: 50px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.14px;
  color: #000000;
}

.mode-btn:hover {
  background: rgba(0, 0, 0, 0.12);
}

.mode-btn.active {
  background: #000000;
  color: #ffffff;
}

.mode-hint {
  margin-top: 12px;
  color: #666666;
  font-size: 14px;
  text-align: center;
  font-weight: 320;
  letter-spacing: -0.1px;
}

.book-input-section {
  background: #ffffff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.book-input {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.book-input input {
  flex: 1;
  min-width: 200px;
  padding: 14px 20px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 50px;
  font-size: 16px;
  font-weight: 330;
  letter-spacing: -0.14px;
  outline: none;
  transition: border-color 0.2s;
}

.book-input input:focus {
  border-color: #000000;
}

.category-selector {
  background: #ffffff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-tag {
  background: rgba(0, 0, 0, 0.06);
  padding: 10px 20px;
  border-radius: 50px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 14px;
  font-weight: 400;
  letter-spacing: -0.14px;
}

.category-tag:hover {
  background: rgba(0, 0, 0, 0.12);
}

.category-tag.active {
  background: #000000;
  color: #ffffff;
}

.action-section {
  text-align: center;
  margin: 32px 0;
}

.recommend-btn {
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 14px 48px;
  border-radius: 50px;
  font-size: 18px;
  font-weight: 400;
  letter-spacing: -0.14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.recommend-btn:hover {
  opacity: 0.85;
}

.recommend-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

.recommend-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.recommendations-section {
  background: #ffffff;
  border-radius: 8px;
  padding: 24px;
  margin-top: 32px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
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

.book-info {
  padding: 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 150px;
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
  font-weight: 450;
  letter-spacing: -0.14px;
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

.similarity-value {
  color: #000000;
}

.rating-value {
  color: #666666;
}

.sub-category {
  color: #666666;
  font-weight: 320;
}

.book-intro {
  font-size: 13px;
  color: #666666;
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

.book-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.action-btn {
  padding: 6px 12px;
  border: 1px solid #000000;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.action-btn.small {
  font-size: 12px;
  padding: 4px 8px;
}

.like-btn {
  background: #ffffff;
  color: #000000;
  border-color: #ff6b6b;
  transition: all 0.3s ease;
}

.like-btn:hover {
  background: rgba(255, 107, 107, 0.1);
  transform: scale(1.1);
}

.like-btn.liked {
  background: #ff6b6b;
  color: #ffffff;
  border-color: #ff6b6b;
  animation: pulse 0.5s ease;
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

.dislike-btn {
  background: #ffffff;
  color: #000000;
  border-color: #666666;
  transition: all 0.3s ease;
}

.dislike-btn:hover {
  background: rgba(102, 102, 102, 0.1);
  transform: scale(1.1);
}

.action-icon {
  font-size: 12px;
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

.interest-section {
  background: #ffffff;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
  text-align: center;
}

.interest-hint {
  margin: 16px 0 24px 0;
  color: #666666;
  font-size: 14px;
  font-weight: 320;
  letter-spacing: -0.1px;
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
  .home-header {
    padding: 56px 20px;
  }

  .home-header h1 {
    font-size: 36px;
  }

  .mode-buttons {
    flex-direction: column;
  }

  .mode-btn {
    width: 100%;
    text-align: center;
  }

  .book-input {
    flex-direction: column;
  }

  .book-input input {
    width: 100%;
  }

  .books-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .book-cover img {
    height: 180px;
  }
}

@media (max-width: 480px) {
  .books-grid {
    grid-template-columns: 1fr;
  }
}

.book-full-intro-text {
  margin-top: 12px;
  line-height: 1.4;
}

.book-card {
  min-height: 400px;
  height: auto;
}

.book-info {
  height: auto;
  min-height: 180px;
}

.dark-mode .home-page {
  background: #000000 !important;
  color: #ffffff !important;
}

.dark-mode .home-header {
  background: #ffffff;
  color: #000000;
}

.dark-mode .recommendation-section h2 {
  color: #ffffff;
}

.dark-mode .recommendation-section h3 {
  color: #ffffff;
}

.dark-mode .mode-selector {
  background: #0a0a0a;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-mode .mode-btn {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.dark-mode .mode-btn:hover {
  background: rgba(255, 255, 255, 0.16);
}

.dark-mode .mode-btn.active {
  background: #ffffff;
  color: #000000;
}

.dark-mode .book-input-section {
  background: #0a0a0a;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-mode .book-input input {
  background: #1a1a1a;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff;
}

.dark-mode .category-selector {
  background: #0a0a0a;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-mode .category-tag {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.dark-mode .category-tag:hover {
  background: rgba(255, 255, 255, 0.16);
}

.dark-mode .recommendations-section {
  background: #0a0a0a;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
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

.dark-mode .category-tag.active {
  background: #ffffff;
  color: #000000;
}

.dark-mode .recommend-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .recommend-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}

.dark-mode .similarity-value {
  color: #e0e0e0;
}

.dark-mode .rating-value {
  color: #b0b0b0;
}

.dark-mode .sub-category {
  color: #b0b0b0;
}

.dark-mode .book-intro {
  color: #e0e0e0;
}
</style>
