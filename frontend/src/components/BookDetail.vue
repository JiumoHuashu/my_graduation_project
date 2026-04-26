<template>
  <div class="book-detail">
    <!-- 悬浮返回按钮 -->
    <button class="back-btn" @click="goBack" aria-label="返回">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M19 12H5M12 19l-7-7 7-7"/>
      </svg>
    </button>

    <div v-if="loading" class="loading">数据加载中...</div>

    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else-if="book" class="detail-container">
      <!-- 非对称双栏布局 -->
      <div class="book-info-layout">
        <!-- 左侧：封面和操作按钮 -->
        <div class="book-cover-section">
          <div class="book-cover-large">
            <img :src="book.cover_url" @error="handleImgError" alt="封面">
          </div>
          <div class="book-actions">
            <button :class="['add-to-bookshelf-btn', { 'in-bookshelf': isInBookshelf }]" @click="addToBookshelf">
              {{ isInBookshelf ? '已在书架' : '加入书架' }}
            </button>
            <button class="read-btn" @click="visitOriginalPage">
              立即阅读
            </button>
          </div>
        </div>

        <!-- 右侧：书籍详细信息 -->
        <div class="book-info-main">
          <h1 class="book-title">{{ book.title }}</h1>
          <div class="book-meta">
            <span class="author">{{ book.author || '未知作者' }}</span>
            <span class="category">{{ book.category }} / {{ book.sub_category }}</span>
          </div>

          <div class="book-tags">
            <span v-for="tag in (book.tags ? book.tags.split('|') : [])" :key="tag" class="tag">{{ tag }}</span>
          </div>

          <!-- 极简网格指标卡片 -->
          <div class="book-stats">
            <div class="stat-card">
              <span class="stat-value">{{ formatNumber(book.total_read) }}</span>
              <span class="stat-label">总阅读量</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ formatNumber(book.monthly_read) }}</span>
              <span class="stat-label">月阅读量</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ formatNumber(book.total_flowers) }}</span>
              <span class="stat-label">总鲜花</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ formatNumber(book.monthly_flowers) }}</span>
              <span class="stat-label">月鲜花</span>
            </div>
          </div>

          <div class="book-info-secondary">
            <div class="info-item">
              <span class="info-label">字数</span>
              <span class="info-value">{{ (book.word_count / 10000).toFixed(1) }}万字</span>
            </div>
            <div class="info-item">
              <span class="info-label">入站时间</span>
              <span class="info-value">{{ book.onboarding_time }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">更新时间</span>
              <span class="info-value">{{ book.update_time }}</span>
            </div>
          </div>

          <!-- 评分区域 -->
          <div class="book-rating">
            <h3>书籍评分</h3>
            <div class="rating-container">
              <div class="average-rating">
                <div class="rating-value">{{ bookRating }}分</div>
                <div class="rating-count">{{ ratingCount }}人评分</div>
              </div>
              <div class="user-rating">
                <StarRating
                  v-model:rating="userRating"
                  @ratingChange="handleRatingChange"
                />
                <button
                  class="submit-rating-btn"
                  @click="submitRating"
                  :disabled="isRating"
                >
                  {{ isRating ? '提交中...' : '提交评分' }}
                </button>
                <div v-if="ratingError" class="rating-error">{{ ratingError }}</div>
              </div>
            </div>
          </div>

          <!-- 收藏和不感兴趣按钮 -->
          <div class="book-interactions">
            <button class="action-btn like-btn" :class="{ 'liked': isLiked }" @click="handleUserAction('like')">
              <span class="action-icon">❤️</span>
              <span class="action-text">{{ isLiked ? '已收藏' : '收藏' }}</span>
            </button>
            <button class="action-btn dislike-btn" @click="handleUserAction('dislike')">
              <span class="action-icon">✕</span>
              <span class="action-text">不感兴趣</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 内容简介 -->
      <div class="book-introduction">
        <h3>内容简介</h3>
        <p>{{ book.introduction || '暂无简介' }}</p>
      </div>

      <!-- 数据统计和图表 -->
      <div class="data-visualization">
        <h3>阅读倾向与数据统计</h3>
        <div class="chart-container">
          <div class="chart-item">
            <div class="chart-title">阅读量对比</div>
            <div class="chart-bar">
              <div class="bar-label">总阅读</div>
              <div class="bar-container">
                <div class="bar" :style="{ width: getBarWidth(book.total_read) + '%', transition: 'width 1s ease-in-out' }"></div>
              </div>
              <div class="bar-value">{{ formatNumber(book.total_read) }}</div>
            </div>
            <div class="chart-bar">
              <div class="bar-label">月阅读</div>
              <div class="bar-container">
                <div class="bar secondary" :style="{ width: getBarWidth(book.monthly_read) + '%', transition: 'width 1s ease-in-out' }"></div>
              </div>
              <div class="bar-value">{{ formatNumber(book.monthly_read) }}</div>
            </div>
            <div class="chart-bar">
              <div class="bar-label">月占比</div>
              <div class="bar-container">
                <div class="bar tertiary" :style="{ width: getMonthlyRatio(book.monthly_read, book.total_read) + '%', transition: 'width 1s ease-in-out' }"></div>
              </div>
              <div class="bar-value">{{ getPercentage(book.monthly_read, book.total_read) }}%</div>
            </div>
          </div>

          <div class="chart-item">
            <div class="chart-title">鲜花数对比</div>
            <div class="chart-bar">
              <div class="bar-label">总鲜花</div>
              <div class="bar-container">
                <div class="bar" :style="{ width: getBarWidth(book.total_flowers) + '%', transition: 'width 1s ease-in-out' }"></div>
              </div>
              <div class="bar-value">{{ formatNumber(book.total_flowers) }}</div>
            </div>
            <div class="chart-bar">
              <div class="bar-label">月鲜花</div>
              <div class="bar-container">
                <div class="bar secondary" :style="{ width: getBarWidth(book.monthly_flowers) + '%', transition: 'width 1s ease-in-out' }"></div>
              </div>
              <div class="bar-value">{{ formatNumber(book.monthly_flowers) }}</div>
            </div>
            <div class="chart-bar">
              <div class="bar-label">月占比</div>
              <div class="bar-container">
                <div class="bar tertiary" :style="{ width: getMonthlyRatio(book.monthly_flowers, book.total_flowers) + '%', transition: 'width 1s ease-in-out' }"></div>
              </div>
              <div class="bar-value">{{ getPercentage(book.monthly_flowers, book.total_flowers) }}%</div>
            </div>
          </div>

          <div class="chart-item full-width">
            <div class="chart-title">综合数据对比</div>
            <div class="chart-bar">
              <div class="bar-label">阅读量</div>
              <div class="bar-container">
                <div class="bar" :style="{ width: getRelativeWidth(book.total_read) + '%', transition: 'width 1s ease-in-out' }"></div>
              </div>
              <div class="bar-value">{{ formatNumber(book.total_read) }}</div>
            </div>
            <div class="chart-bar">
              <div class="bar-label">鲜花数</div>
              <div class="bar-container">
                <div class="bar secondary" :style="{ width: getRelativeWidth(book.total_flowers) + '%', transition: 'width 1s ease-in-out' }"></div>
              </div>
              <div class="bar-value">{{ formatNumber(book.total_flowers) }}</div>
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
import StarRating from './StarRating.vue'

const router = useRouter()

const props = defineProps({
  bookId: {
    type: String,
    required: true
  }
})

const book = ref(null)
const loading = ref(false)
const error = ref('')
const maxValue = ref(10000000)
const isInBookshelf = ref(false)
const isLiked = ref(false)
const bookRating = ref(0)
const userRating = ref(0)
const ratingCount = ref(0)
const isRating = ref(false)
const ratingError = ref('')

const fetchBookDetail = async () => {
  loading.value = true
  error.value = ''

  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/book/${props.bookId}/`)
    if (res.data.code === 200) {
      book.value = res.data.data
      maxValue.value = Math.max(
        book.value.total_read,
        book.value.monthly_read,
        book.value.total_flowers,
        book.value.monthly_flowers,
        1000000
      )
      await checkIfInBookshelf()
      await checkIfLiked()
      await fetchBookRating()
      await fetchUserRating()
    } else {
      error.value = res.data.msg
    }
  } catch (err) {
    console.error('获取书籍详情失败:', err)
    error.value = '获取书籍详情失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}

const handleImgError = (e) => {
  e.target.src = 'https://via.placeholder.com/300x400?text=No+Cover'
}

const formatNumber = (num) => {
  if (num >= 100000000) {
    return (num / 100000000).toFixed(1) + '亿'
  } else if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num
}

const getBarWidth = (value) => {
  return Math.min((value / maxValue.value) * 100, 100)
}

const getMonthlyRatio = (monthlyValue, totalValue) => {
  if (totalValue === 0) return 0
  return Math.min((monthlyValue / totalValue) * 100, 100)
}

const getPercentage = (value, total) => {
  if (total === 0) return 0
  return ((value / total) * 100).toFixed(1)
}

const getRelativeWidth = (value) => {
  const max = Math.max(book.value?.total_read || 0, book.value?.total_flowers || 0, 1000000)
  return Math.min((value / max) * 100, 100)
}

const goBack = () => {
  router.back()
}

const checkIfInBookshelf = async () => {
  if (!book.value) {
    isInBookshelf.value = false
    return
  }

  try {
    const savedUser = localStorage.getItem('user')
    if (!savedUser) {
      isInBookshelf.value = false
      return
    }

    const user = JSON.parse(savedUser)
    const res = await axios.get('http://127.0.0.1:8000/api/user/bookshelf/', {
      params: { user_id: user.id }
    })

    if (res.data.code === 200) {
      const bookIds = res.data.data
      isInBookshelf.value = bookIds.includes(book.value.book_id)
    } else {
      isInBookshelf.value = false
    }
  } catch (error) {
    console.error('检查书架失败:', error)
    isInBookshelf.value = false
  }
}

const checkIfLiked = async () => {
  if (!book.value) {
    isLiked.value = false
    return
  }

  try {
    const savedUser = localStorage.getItem('user')
    if (!savedUser) {
      isLiked.value = false
      return
    }

    const user = JSON.parse(savedUser)
    // 这里可以添加一个API来检查用户是否收藏了该书籍
    // 暂时默认未收藏
    isLiked.value = false
  } catch (error) {
    console.error('检查收藏状态失败:', error)
    isLiked.value = false
  }
}

const addToBookshelf = async () => {
  if (!book.value) return

  try {
    const savedUser = localStorage.getItem('user')
    if (!savedUser) {
      alert('请先登录')
      return
    }

    const user = JSON.parse(savedUser)

    if (isInBookshelf.value) {
      const res = await axios.post('http://127.0.0.1:8000/api/user/bookshelf/remove/', {
        user_id: user.id,
        book_id: book.value.book_id
      })

      if (res.data.code === 200) {
        isInBookshelf.value = false
      } else {
        alert(res.data.msg)
      }
    } else {
      const res = await axios.post('http://127.0.0.1:8000/api/user/bookshelf/', {
        user_id: user.id,
        book_id: book.value.book_id
      })

      if (res.data.code === 200) {
        isInBookshelf.value = true
      } else {
        alert(res.data.msg)
      }
    }
  } catch (error) {
    console.error('操作书架失败:', error)
    alert('操作书架失败，请检查网络连接')
  }
}

const visitOriginalPage = () => {
  if (book.value && book.value.book_id) {
    const originalUrl = `https://b.faloo.com/${book.value.book_id}.html?1`
    window.open(originalUrl, '_blank')
  }
}

const fetchBookRating = async () => {
  if (!book.value) return

  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/book/rating/${book.value.book_id}/`)
    if (res.data.code === 200) {
      bookRating.value = res.data.data.average_score
      ratingCount.value = res.data.data.count
    }
  } catch (error) {
    console.error('获取书籍评分失败:', error)
  }
}

const fetchUserRating = async () => {
  if (!book.value) return

  try {
    const savedUser = localStorage.getItem('user')
    if (!savedUser) return

    const user = JSON.parse(savedUser)
    const res = await axios.get('http://127.0.0.1:8000/api/user/rating/', {
      params: { user_id: user.id }
    })

    if (res.data.code === 200) {
      const ratings = res.data.data
      const userRatingData = ratings.find(rating => rating.book.book_id === book.value.book_id)
      if (userRatingData) {
        userRating.value = userRatingData.score
      }
    }
  } catch (error) {
    console.error('获取用户评分失败:', error)
  }
}

const handleRatingChange = (rating) => {
  userRating.value = rating
}

const submitRating = async () => {
  if (!book.value) return

  try {
    const savedUser = localStorage.getItem('user')
    if (!savedUser) {
      alert('请先登录')
      return
    }

    isRating.value = true
    ratingError.value = ''

    const user = JSON.parse(savedUser)
    const res = await axios.post('http://127.0.0.1:8000/api/user/rating/', {
      user_id: user.id,
      book_id: book.value.book_id,
      score: userRating.value
    })

    if (res.data.code === 200) {
      await fetchBookRating()
    } else {
      ratingError.value = res.data.msg
    }
  } catch (error) {
    console.error('提交评分失败:', error)
    ratingError.value = '提交评分失败，请检查网络连接'
  } finally {
    isRating.value = false
  }
}

const handleUserAction = async (actionType) => {
  if (!book.value) return

  try {
    const savedUser = localStorage.getItem('user')
    if (!savedUser) {
      alert('请先登录')
      return
    }

    const user = JSON.parse(savedUser)
    const res = await axios.post('http://127.0.0.1:8000/api/user/action/', {
      user_id: user.id,
      book_id: book.value.book_id,
      action_type: actionType
    })

    if (res.data.code === 200) {
      // 对于收藏行为，更新isLiked状态
      if (actionType === 'like') {
        isLiked.value = !isLiked.value
        
        // 处理补偿推荐
        if (res.data.compensation_recommendations && res.data.compensation_recommendations.length > 0) {
          // 将补偿推荐的书籍添加到本地存储，供首页使用
          localStorage.setItem('compensation_recommendations', JSON.stringify(res.data.compensation_recommendations))
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

onMounted(() => {
  fetchBookDetail()
})

watch(() => props.bookId, (newId) => {
  if (newId) {
    fetchBookDetail()
  }
})
</script>

<style scoped>
:global(body) {
  overflow-x: hidden;
  margin: 0;
  padding: 0;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
}

.book-detail {
  background: #ffffff;
  min-height: 100vh;
  padding-bottom: 48px;
  position: relative;
}

/* 悬浮返回按钮 */
.back-btn {
  position: fixed;
  top: 24px;
  left: 24px;
  background: rgba(255, 255, 255, 0.9);
  color: #333333;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 12px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-btn:hover {
  background: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
}

.back-btn:focus {
  outline: dashed 2px #333333;
  outline-offset: 2px;
}

.loading, .error {
  text-align: center;
  padding: 100px 0;
  color: #666666;
  font-size: 16px;
  font-weight: 320;
}

.error {
  color: #333333;
}

.detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 24px;
}

/* 非对称双栏布局 */
.book-info-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 48px;
  margin-bottom: 48px;
  align-items: start;
}

/* 左侧：封面和操作按钮 */
.book-cover-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: sticky;
  top: 100px;
}

/* 封面美化 */
.book-cover-large {
  position: relative;
  width: 100%;
  aspect-ratio: 3/4;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1), 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.book-cover-large:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15), 0 4px 12px rgba(0, 0, 0, 0.1);
}

.book-cover-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* 操作按钮 */
.book-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.add-to-bookshelf-btn, .read-btn {
  padding: 16px 24px;
  border: none;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: -0.01em;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.add-to-bookshelf-btn {
  background: #000000;
  color: #ffffff;
  font-weight: 600;
}

.add-to-bookshelf-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.add-to-bookshelf-btn.in-bookshelf {
  background: rgba(0, 0, 0, 0.3);
}

.read-btn {
  background: transparent;
  color: #333333;
  border: 1px solid #e0e0e0;
  font-weight: 500;
}

.read-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

/* 右侧：书籍详细信息 */
.book-info-main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.book-title {
  font-size: 32px;
  color: #333333;
  margin: 0;
  font-weight: 500;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.book-meta {
  display: flex;
  gap: 24px;
  font-size: 16px;
  font-weight: 320;
  letter-spacing: -0.01em;
  color: #666666;
}

/* 标签优化 */
.book-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: #f9f9f9;
  padding: 6px 14px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 400;
  letter-spacing: -0.01em;
  color: #333333;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
}

.tag:hover {
  background: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 极简网格指标卡片 */
.book-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 8px;
}

.stat-card {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #333333;
  margin-bottom: 8px;
}

.stat-label {
  display: block;
  font-size: 13px;
  color: #666666;
  font-weight: 320;
  letter-spacing: -0.01em;
}

.book-info-secondary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  margin-bottom: 8px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-label {
  font-size: 13px;
  color: #666666;
  font-weight: 320;
  letter-spacing: -0.01em;
}

.info-value {
  font-size: 16px;
  color: #333333;
  font-weight: 400;
  letter-spacing: -0.01em;
}

/* 评分区域 */
.book-rating {
  background: rgba(249, 249, 249, 0.8);
  backdrop-filter: blur(12px);
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.book-rating:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
}

.book-rating h3 {
  font-size: 18px;
  color: #333333;
  margin: 0 0 20px 0;
  font-weight: 500;
  letter-spacing: -0.01em;
}

.rating-container {
  display: flex;
  gap: 48px;
  align-items: flex-start;
}

.average-rating {
  flex: 1;
  text-align: center;
}

.average-rating .rating-value {
  font-size: 48px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #333333;
  margin-bottom: 8px;
}

.average-rating .rating-count {
  font-size: 14px;
  color: #666666;
  font-weight: 320;
}

.user-rating {
  flex: 2;
}

.submit-rating-btn {
  margin-top: 16px;
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 12px 24px;
  border-radius: 50px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: -0.01em;
  transition: all 0.3s ease;
}

.submit-rating-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.submit-rating-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.rating-error {
  margin-top: 12px;
  font-size: 13px;
  color: #333333;
  font-weight: 400;
}

/* 收藏和不感兴趣按钮 */
.book-interactions {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.action-btn {
  flex: 1;
  padding: 14px 24px;
  border: 1px solid #e0e0e0;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.01em;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #ffffff;
  color: #333333;
}

.like-btn {
  border-color: #ff6b6b;
  color: #ff6b6b;
}

.like-btn:hover {
  background: rgba(255, 107, 107, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.2);
}

.like-btn.liked {
  background: #ff6b6b;
  color: #ffffff;
  border-color: #ff6b6b;
  animation: pulse 0.5s ease;
}

.dislike-btn {
  border-color: #666666;
  color: #666666;
}

.dislike-btn:hover {
  background: rgba(102, 102, 102, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 102, 102, 0.2);
}

.action-icon {
  font-size: 16px;
}

.action-text {
  font-size: 14px;
  font-weight: 500;
}

/* 内容简介 */
.book-introduction {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  padding: 32px;
  margin-bottom: 32px;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.book-introduction:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
}

.book-introduction h3 {
  font-size: 20px;
  color: #333333;
  margin: 0 0 16px 0;
  font-weight: 500;
  letter-spacing: -0.01em;
}

.book-introduction p {
  font-size: 16px;
  line-height: 1.6;
  color: #666666;
  margin: 0;
  font-weight: 320;
  letter-spacing: -0.01em;
}

/* 数据统计和图表 */
.data-visualization {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  padding: 32px;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.data-visualization:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
}

.data-visualization h3 {
  font-size: 20px;
  color: #333333;
  margin: 0 0 24px 0;
  font-weight: 500;
  letter-spacing: -0.01em;
}

.chart-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.chart-item {
  background: #f9f9f9;
  padding: 24px;
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
  border: 1px solid rgba(0, 0, 0, 0.05);
}

.chart-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.chart-title {
  font-size: 16px;
  font-weight: 500;
  letter-spacing: -0.01em;
  color: #333333;
  margin-bottom: 20px;
  text-align: center;
}

.chart-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.bar-label {
  width: 80px;
  font-size: 13px;
  color: #666666;
  font-weight: 320;
  letter-spacing: -0.01em;
}

.bar-container {
  flex: 1;
  height: 8px;
  background: rgba(0, 0, 0, 0.08);
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  height: 100%;
  background: #404040;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.bar.secondary {
  background: #4a6fa5;
}

.bar.tertiary {
  background: #5c8599;
}

.chart-item.full-width {
  grid-column: 1 / -1;
}

.bar-value {
  width: 100px;
  font-size: 13px;
  color: #666666;
  text-align: right;
  font-weight: 400;
  letter-spacing: -0.01em;
}

/* 响应式设计 */
@media (max-width: 992px) {
  .book-info-layout {
    grid-template-columns: 1fr;
    gap: 32px;
  }
  
  .book-cover-section {
    position: static;
  }
  
  .book-cover-large {
    max-width: 250px;
    margin: 0 auto;
  }
  
  .book-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .book-info-secondary {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .rating-container {
    flex-direction: column;
    gap: 24px;
  }
  
  .chart-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .detail-container {
    padding: 32px 16px;
  }
  
  .book-title {
    font-size: 28px;
  }
  
  .book-meta {
    flex-direction: column;
    gap: 8px;
  }
  
  .book-actions {
    flex-direction: row;
  }
  
  .add-to-bookshelf-btn, .read-btn {
    flex: 1;
  }
  
  .book-interactions {
    flex-direction: column;
  }
  
  .book-introduction,
  .data-visualization {
    padding: 24px;
  }
}

/* 暗色模式 */
.dark-mode .book-detail {
  background: #121212 !important;
  color: #ffffff !important;
}

.dark-mode .back-btn {
  background: rgba(26, 26, 26, 0.9);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.dark-mode .back-btn:hover {
  background: rgba(30, 30, 30, 0.9);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
}

.dark-mode .back-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}

.dark-mode .loading {
  color: #b0b0b0;
}

.dark-mode .error {
  color: #ffffff;
}

.dark-mode .book-cover-large {
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3), 0 2px 8px rgba(0, 0, 0, 0.2);
}

.dark-mode .book-cover-large:hover {
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), 0 4px 12px rgba(0, 0, 0, 0.3);
}

.dark-mode .book-title {
  color: #ffffff;
}

.dark-mode .book-meta {
  color: #b0b0b0;
}

.dark-mode .tag {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .tag:hover {
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.dark-mode .stat-card {
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.dark-mode .stat-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}

.dark-mode .stat-value {
  color: #ffffff;
}

.dark-mode .stat-label {
  color: #b0b0b0;
}

.dark-mode .info-label {
  color: #b0b0b0;
}

.dark-mode .info-value {
  color: #ffffff;
}

.dark-mode .book-rating {
  background: rgba(26, 26, 26, 0.8);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.dark-mode .book-rating:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4);
}

.dark-mode .book-rating h3 {
  color: #ffffff;
}

.dark-mode .average-rating .rating-value {
  color: #ffffff;
}

.dark-mode .average-rating .rating-count {
  color: #b0b0b0;
}

.dark-mode .rating-error {
  color: #ffffff;
}

.dark-mode .action-btn {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .like-btn {
  border-color: #ff6b6b;
  color: #ff6b6b;
}

.dark-mode .like-btn:hover {
  background: rgba(255, 107, 107, 0.2);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
}

.dark-mode .dislike-btn {
  border-color: #b0b0b0;
  color: #b0b0b0;
}

.dark-mode .dislike-btn:hover {
  background: rgba(176, 176, 176, 0.2);
  box-shadow: 0 4px 12px rgba(176, 176, 176, 0.3);
}

.dark-mode .add-to-bookshelf-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .add-to-bookshelf-btn:hover {
  box-shadow: 0 6px 20px rgba(255, 255, 255, 0.2);
}

.dark-mode .add-to-bookshelf-btn.in-bookshelf {
  background: rgba(255, 255, 255, 0.3);
}

.dark-mode .read-btn {
  background: transparent;
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-mode .read-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.15);
}

.dark-mode .submit-rating-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .submit-rating-btn:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2);
}

.dark-mode .book-introduction {
  background: rgba(26, 26, 26, 0.8);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.dark-mode .book-introduction:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4);
}

.dark-mode .book-introduction h3 {
  color: #ffffff;
}

.dark-mode .book-introduction p {
  color: #b0b0b0;
}

.dark-mode .data-visualization {
  background: rgba(26, 26, 26, 0.8);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.dark-mode .data-visualization:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4);
}

.dark-mode .data-visualization h3 {
  color: #ffffff;
}

.dark-mode .chart-item {
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.dark-mode .chart-item:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}

.dark-mode .chart-title {
  color: #ffffff;
}

.dark-mode .bar-label {
  color: #b0b0b0;
}

.dark-mode .bar-container {
  background: rgba(255, 255, 255, 0.1);
}

.dark-mode .bar {
  background: #666666;
}

.dark-mode .bar.secondary {
  background: #6a8eba;
}

.dark-mode .bar.tertiary {
  background: #7ca2b8;
}

.dark-mode .bar-value {
  color: #b0b0b0;
}

/* 动画效果 */
@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}
</style>
