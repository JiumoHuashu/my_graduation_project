<template>
  <div class="book-detail">
    <header class="detail-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h1>书籍详情</h1>
    </header>

    <div v-if="loading" class="loading">数据加载中...</div>

    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else-if="book" class="detail-container">
      <div class="book-info-card">
        <div class="book-cover-large">
          <img :src="book.cover_url" @error="handleImgError" alt="封面">
        </div>

        <div class="book-info-main">
          <h2 class="book-title">{{ book.title }}</h2>
          <div class="book-meta">
            <span class="author">{{ book.author || '未知作者' }}</span>
            <span class="category">{{ book.category }} / {{ book.sub_category }}</span>
          </div>

          <div class="book-tags">
            <span v-for="tag in (book.tags ? book.tags.split('|') : [])" :key="tag" class="tag">{{ tag }}</span>
          </div>

          <div class="book-stats">
            <div class="stat-item">
              <span class="stat-label">总阅读量</span>
              <span class="stat-value">{{ formatNumber(book.total_read) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">月阅读量</span>
              <span class="stat-value">{{ formatNumber(book.monthly_read) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总鲜花</span>
              <span class="stat-value">{{ formatNumber(book.total_flowers) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">月鲜花</span>
              <span class="stat-value">{{ formatNumber(book.monthly_flowers) }}</span>
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

          <div class="book-rating">
            <h3>书籍评分</h3>
            <div class="rating-container">
              <div class="average-rating">
                <div class="rating-label">平均评分</div>
                <div class="rating-value">{{ bookRating }}分</div>
                <div class="rating-count">({{ ratingCount }}人评分)</div>
              </div>
              <div class="user-rating">
                <div class="rating-label">我的评分</div>
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

          <div class="book-actions">
            <button :class="['add-to-bookshelf-btn', { 'in-bookshelf': isInBookshelf }]" @click="addToBookshelf">
              {{ isInBookshelf ? '已在书架' : '加入书架' }}
            </button>
            <button class="action-btn like-btn" :class="{ 'liked': isLiked }" @click="handleUserAction('like')">
              <span class="action-icon">❤️</span>
            </button>
            <div class="original-page-container">
              <button class="original-btn" @click="visitOriginalPage">
                访问原网页
              </button>
              <button class="action-btn dislike-btn small" @click="handleUserAction('dislike')">
                <span class="action-icon">✕</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="book-introduction">
        <h3>内容简介</h3>
        <p>{{ book.introduction || '暂无简介' }}</p>
      </div>

      <div class="data-visualization">
        <h3>数据统计</h3>
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
.book-detail {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: #ffffff;
  min-height: 100vh;
  padding-bottom: 48px;
}

.detail-header {
  background: #ffffff;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
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

.detail-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 540;
  letter-spacing: -0.26px;
  color: #000000;
}

.loading, .error {
  text-align: center;
  padding: 100px 0;
  color: #666666;
  font-size: 16px;
  font-weight: 320;
}

.error {
  color: #000000;
}

.detail-container {
  max-width: 1000px;
  margin: 24px auto;
  padding: 0 24px;
}

.book-info-card {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 32px;
  margin-bottom: 24px;
  display: flex;
  gap: 32px;
}

.book-cover-large img {
  width: 200px;
  height: 280px;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  object-fit: cover;
}

.book-info-main {
  flex: 1;
}

.book-title {
  font-size: 28px;
  color: #000000;
  margin: 0 0 16px 0;
  font-weight: 540;
  letter-spacing: -0.26px;
  line-height: 1.20;
}

.book-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 330;
  letter-spacing: -0.14px;
  color: #666666;
}

.book-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.tag {
  background: rgba(0, 0, 0, 0.06);
  padding: 6px 16px;
  border-radius: 50px;
  font-size: 13px;
  font-weight: 400;
  letter-spacing: -0.14px;
  color: #000000;
}

.book-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
  padding: 24px;
  background: #fafafa;
  border-radius: 8px;
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 13px;
  color: #666666;
  margin-bottom: 6px;
  font-weight: 320;
  letter-spacing: -0.1px;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 540;
  letter-spacing: -0.14px;
  color: #000000;
}

.book-info-secondary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
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
  letter-spacing: -0.1px;
}

.info-value {
  font-size: 16px;
  color: #000000;
  font-weight: 400;
  letter-spacing: -0.14px;
}

.book-rating {
  margin: 24px 0;
  padding: 24px;
  background: #fafafa;
  border-radius: 8px;
}

.book-rating h3 {
  font-size: 18px;
  color: #000000;
  margin: 0 0 16px 0;
  font-weight: 540;
  letter-spacing: -0.14px;
  padding-left: 12px;
  border-left: 2px solid #000000;
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

.average-rating .rating-label {
  font-size: 14px;
  color: #666666;
  margin-bottom: 12px;
  font-weight: 320;
  letter-spacing: -0.1px;
}

.average-rating .rating-value {
  font-size: 36px;
  font-weight: 540;
  letter-spacing: -0.26px;
  color: #000000;
  margin-bottom: 6px;
}

.average-rating .rating-count {
  font-size: 13px;
  color: #666666;
  font-weight: 320;
}

.user-rating {
  flex: 2;
}

.user-rating .rating-label {
  font-size: 14px;
  color: #666666;
  margin-bottom: 12px;
  font-weight: 320;
  letter-spacing: -0.1px;
}

.submit-rating-btn {
  margin-top: 16px;
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 10px 24px;
  border-radius: 50px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 400;
  letter-spacing: -0.14px;
  transition: opacity 0.2s;
}

.submit-rating-btn:hover:not(:disabled) {
  opacity: 0.85;
}

.submit-rating-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

.submit-rating-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.rating-error {
  margin-top: 12px;
  font-size: 13px;
  color: #000000;
  font-weight: 400;
}

.book-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  flex-wrap: wrap;
}

.add-to-bookshelf-btn, .action-btn, .original-btn {
  flex: 1;
  min-width: 120px;
  padding: 14px 24px;
  border: none;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.14px;
  cursor: pointer;
  transition: opacity 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-btn {
  border: 1px solid #000000;
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

.dislike-btn.small {
  font-size: 12px;
  padding: 6px 12px;
  min-width: auto;
  flex: none;
}

.action-icon {
  font-size: 14px;
}

.original-page-container {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.original-btn {
  flex: 1;
  min-width: 140px;
  padding: 14px 24px;
  background: #ffffff;
  color: #000000;
  border: 1px solid #000000;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.14px;
  cursor: pointer;
  transition: background 0.2s;
}

.original-btn:hover {
  background: rgba(0, 0, 0, 0.04);
}

.original-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

.add-to-bookshelf-btn {
  background: #000000;
  color: #ffffff;
}

.add-to-bookshelf-btn:hover {
  opacity: 0.85;
}

.add-to-bookshelf-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

.add-to-bookshelf-btn.in-bookshelf {
  background: rgba(0, 0, 0, 0.3);
}

.add-to-bookshelf-btn.in-bookshelf:hover {
  opacity: 0.85;
}

.original-btn {
  background: #ffffff;
  color: #000000;
  border: 1px solid #000000;
  padding: 14px 24px;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.14px;
  cursor: pointer;
  transition: background 0.2s;
}

.original-btn:hover {
  background: rgba(0, 0, 0, 0.04);
}

.original-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

.book-introduction {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 24px;
  margin-bottom: 24px;
}

.book-introduction h3 {
  font-size: 18px;
  color: #000000;
  margin: 0 0 16px 0;
  font-weight: 540;
  letter-spacing: -0.14px;
  padding-left: 12px;
  border-left: 2px solid #000000;
}

.book-introduction p {
  font-size: 16px;
  line-height: 1.60;
  color: #666666;
  margin: 0;
  font-weight: 330;
  letter-spacing: -0.1px;
}

.data-visualization {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 24px;
}

.data-visualization h3 {
  font-size: 18px;
  color: #000000;
  margin: 0 0 24px 0;
  font-weight: 540;
  letter-spacing: -0.14px;
  padding-left: 12px;
  border-left: 2px solid #000000;
}

.chart-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.chart-item {
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
}

.chart-title {
  font-size: 14px;
  font-weight: 540;
  letter-spacing: -0.14px;
  color: #000000;
  margin-bottom: 16px;
  text-align: center;
}

.chart-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.bar-label {
  width: 60px;
  font-size: 13px;
  color: #666666;
  font-weight: 320;
  letter-spacing: -0.1px;
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
  background: #000000;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.bar.secondary {
  background: #666666;
}

.bar.tertiary {
  background: #999999;
}

.chart-item.full-width {
  grid-column: 1 / -1;
}

.bar-value {
  width: 80px;
  font-size: 12px;
  color: #666666;
  text-align: right;
  font-weight: 320;
  letter-spacing: -0.1px;
}

@media (max-width: 768px) {
  .book-info-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .book-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .book-info-secondary {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .chart-container {
    grid-template-columns: 1fr;
  }
}

.dark-mode .book-detail {
  background: #000000 !important;
  color: #ffffff !important;
}

.dark-mode .detail-header {
  background: #000000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-mode .detail-header h1 {
  color: #ffffff;
}

.dark-mode .loading {
  color: #b0b0b0;
}

.dark-mode .error {
  color: #ffffff;
}

.dark-mode .book-info-card {
  background: #0a0a0a;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
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
}

.dark-mode .book-stats {
  background: #1a1a1a;
}

.dark-mode .stat-label {
  color: #b0b0b0;
}

.dark-mode .stat-value {
  color: #ffffff;
}

.dark-mode .info-label {
  color: #b0b0b0;
}

.dark-mode .info-value {
  color: #ffffff;
}

.dark-mode .book-introduction {
  background: #0a0a0a;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-mode .book-introduction h3 {
  color: #ffffff;
  border-left-color: #ffffff;
}

.dark-mode .book-introduction p {
  color: #b0b0b0;
}

.dark-mode .data-visualization {
  background: #0a0a0a;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-mode .data-visualization h3 {
  color: #ffffff;
  border-left-color: #ffffff;
}

.dark-mode .chart-item {
  background: #1a1a1a;
}

.dark-mode .chart-title {
  color: #ffffff;
}

.dark-mode .bar-label {
  color: #b0b0b0;
}

.dark-mode .bar-container {
  background: rgba(255, 255, 255, 0.08);
}

.dark-mode .bar-value {
  color: #b0b0b0;
}

.dark-mode .book-rating {
  background: #1a1a1a;
}

.dark-mode .book-rating h3 {
  color: #ffffff;
  border-left-color: #ffffff;
}

.dark-mode .average-rating .rating-label {
  color: #b0b0b0;
}

.dark-mode .average-rating .rating-value {
  color: #ffffff;
}

.dark-mode .average-rating .rating-count {
  color: #b0b0b0;
}

.dark-mode .user-rating .rating-label {
  color: #b0b0b0;
}

.dark-mode .rating-error {
  color: #ffffff;
}

.dark-mode .back-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .back-btn:hover {
  opacity: 0.85;
}

.dark-mode .back-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}

.dark-mode .add-to-bookshelf-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .add-to-bookshelf-btn:hover {
  opacity: 0.85;
}

.dark-mode .add-to-bookshelf-btn.in-bookshelf {
  background: rgba(255, 255, 255, 0.3);
}

.dark-mode .add-to-bookshelf-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}

.dark-mode .original-btn {
  background: #000000;
  color: #ffffff;
  border: 1px solid #ffffff;
}

.dark-mode .original-btn:hover {
  background: rgba(255, 255, 255, 0.08);
}

.dark-mode .original-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}
</style>
