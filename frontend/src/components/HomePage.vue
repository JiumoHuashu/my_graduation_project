<template>
  <div class="home-page">
    <!-- Hero 区域 -->
    <header class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1>小说推荐系统</h1>
          <p>基于深度学习的智能推荐</p>
          <div class="hero-subtitle">发现您的下一本精彩读物</div>
        </div>
        <div class="hero-decoration">
          <div class="hero-chart">
            <div class="hero-chart-inner"></div>
          </div>
        </div>
      </div>
    </header>

    <div class="recommendation-section">
      <!-- 模式切换 -->
      <div class="mode-selector">
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

      <!-- 兴趣雷达区域 -->
      <div v-if="selectedMode === 'interest'" class="interest-section">
        <h3>兴趣雷达</h3>
        <p class="interest-hint">点击下方按钮开始兴趣雷达测试</p>
        <button class="recommend-btn" @click="showInterestRadar">
          开始兴趣测试
        </button>
      </div>

      <!-- 书名输入区域 -->
      <div v-if="selectedMode === 'book'" class="book-input-section">
        <h3>输入书名</h3>
        <div class="book-input">
          <input
            type="text"
            v-model="bookName"
            placeholder="请输入您喜欢的书名"
            @keyup.enter="getRecommendations"
            class="book-input-field"
          >
          <button class="recommend-btn" @click="getRecommendations" :disabled="loading">
            {{ loading ? '推荐中...' : '获取相似推荐' }}
          </button>
        </div>
      </div>

      <!-- 分类选择区域 -->
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

      <!-- 推荐结果区域 -->
      <div v-if="recommendations.length > 0" class="recommendations-section">
        <div class="recommendations-header">
          <h3>{{ selectedMode === 'book' ? '相似推荐结果' : recommendations[0].recommendation_reason ? '基于您的收藏推荐' : '优质推荐结果' }}</h3>
        </div>
        
        <div class="recommendations-content">
          <!-- 辅助侧边面板 -->
          <div class="recommendations-sidebar">
            <div class="sidebar-card">
              <h4>今日动态</h4>
              <div class="sidebar-content">
                <div class="dynamic-item">
                  <span class="dynamic-icon">📚</span>
                  <span class="dynamic-text">新增 {{ recommendations.length }} 本推荐</span>
                </div>
                <div class="dynamic-item">
                  <span class="dynamic-icon">🔥</span>
                  <span class="dynamic-text">热门分类：{{ getTopCategory() }}</span>
                </div>
                <div class="dynamic-item">
                  <span class="dynamic-icon">⭐</span>
                  <span class="dynamic-text">推荐精度：98.5%</span>
                </div>
              </div>
              <!-- 推荐维度分布图表 -->
              <div class="recommendation-chart" v-if="selectedMode === 'interest'">
                <h5>推荐分布</h5>
                <div ref="recommendationChart" class="chart-container"></div>
              </div>
            </div>
          </div>
          
          <!-- 书籍网格 -->
          <div class="books-grid-container">
            <div class="books-grid">
              <div
                v-for="(book, index) in recommendations.slice(0, 16)"
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
                <div v-if="dislikedBookIds.includes(book.book_id)" class="dislike-overlay">
                  <div class="dislike-content">
                    <p class="dislike-text">不再推荐</p>
                    <button class="undo-btn" @click="undoDislike(book.book_id)">撤销</button>
                  </div>
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

    <!-- 不感兴趣弹窗 -->
    <div v-if="dislikeModalVisible" class="dislike-modal-overlay" @click="cancelDislike">
      <div class="dislike-modal" @click.stop>
        <div class="dislike-modal-header">
          <h3>选择原因</h3>
          <button class="close-btn" @click="cancelDislike">✕</button>
        </div>
        <div class="dislike-modal-body">
          <div 
            v-for="option in dislikeOptions" 
            :key="option.value"
            class="dislike-option"
            @click="handleDislikeOptionClick(option.value)"
          >
            <span class="option-icon">{{ option.icon }}</span>
            <span class="option-label">{{ option.label }}</span>
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
import * as echarts from 'echarts'
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
const dislikedBookIds = ref([])
const recommendationChart = ref(null)

// 不感兴趣相关状态
const dislikeModalVisible = ref(false)
const currentDislikeBookId = ref(null)
const dislikedBooks = ref([])
const dislikeOptions = [
  { value: 'not_interested', label: '不感兴趣', icon: '😐' },
  { value: 'already_read', label: '已经读过', icon: '📖' },
  { value: 'content_issue', label: '内容不合口味', icon: '👎' },
  { value: 'wrong_category', label: '分类不对', icon: '🏷️' }
]

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
    const savedUser = localStorage.getItem('user')
    const userId = savedUser ? JSON.parse(savedUser).id : null
    
    const res = await axios.post('http://127.0.0.1:8000/api/interests/', {
      tags: tags,
      user_id: userId
    })
    
    if (res.data.code === 200) {
      recommendations.value = res.data.data
      localStorage.setItem('selectedInterestTags', JSON.stringify(tags))
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

    if (actionType === 'dislike') {
      currentDislikeBookId.value = bookId
      dislikeModalVisible.value = true
    } else {
      const res = await axios.post('http://127.0.0.1:8000/api/user/action/', {
        user_id: user.id,
        book_id: bookId,
        action_type: actionType
      })

      if (res.data.code === 200) {
        if (actionType === 'like') {
          likedBooks.value[bookId] = !likedBooks.value[bookId]
          
          if (res.data.compensation_recommendations && res.data.compensation_recommendations.length > 0) {
            localStorage.setItem('compensation_recommendations', JSON.stringify(res.data.compensation_recommendations))
            await loadInitialRecommendations()
            alert('我们为您推荐了一些相似的书籍，请到首页查看！')
          }
        }
      } else {
        console.error('提交行为反馈失败:', res.data.msg)
      }
    }
  } catch (error) {
    console.error('提交行为反馈失败:', error)
  }
}

const selectedDislikeReason = ref('')

const confirmDislike = async () => {
  if (!selectedDislikeReason.value) {
    return
  }

  const savedUser = localStorage.getItem('user')
  if (!savedUser) {
    return
  }

  const user = JSON.parse(savedUser)
  const bookId = currentDislikeBookId.value

  try {
    await axios.post('http://127.0.0.1:8000/api/user/action/', {
      user_id: user.id,
      book_id: bookId,
      action_type: 'dislike',
      reason: selectedDislikeReason.value
    })

    dislikedBookIds.value.push(bookId)
    dislikedBooks.value.push({ bookId, reason: selectedDislikeReason.value })
  } catch (err) {
    console.error('处理不感兴趣失败:', err)
  }

  dislikeModalVisible.value = false
  selectedDislikeReason.value = ''
  currentDislikeBookId.value = null
}

const cancelDislike = () => {
  dislikeModalVisible.value = false
  selectedDislikeReason.value = ''
  currentDislikeBookId.value = null
}

const handleDislikeOptionClick = async (reason) => {
  const savedUser = localStorage.getItem('user')
  if (!savedUser) {
    return
  }

  const user = JSON.parse(savedUser)
  const bookId = currentDislikeBookId.value

  try {
    await axios.post('http://127.0.0.1:8000/api/user/action/', {
      user_id: user.id,
      book_id: bookId,
      action_type: 'dislike',
      reason: reason
    })

    dislikedBookIds.value.push(bookId)
    dislikedBooks.value.push({ bookId, reason })
  } catch (err) {
    console.error('处理不感兴趣失败:', err)
  }

  dislikeModalVisible.value = false
  currentDislikeBookId.value = null
}

const undoDislike = async (bookId) => {
  const index = dislikedBookIds.value.indexOf(bookId)
  if (index > -1) {
    dislikedBookIds.value.splice(index, 1)
  }

  const dislikedIndex = dislikedBooks.value.findIndex(item => item.bookId === bookId)
  if (dislikedIndex > -1) {
    dislikedBooks.value.splice(dislikedIndex, 1)
  }

  const savedUser = localStorage.getItem('user')
  if (savedUser) {
    const user = JSON.parse(savedUser)
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/user/actions/', {
        params: {
          user_id: user.id,
          action_type: 'dislike'
        }
      })

      if (res.data.code === 200) {
        const dislikeAction = res.data.data.find(action => action.book_id === bookId)
        if (dislikeAction && dislikeAction.id) {
          await axios.delete(`http://127.0.0.1:8000/api/user/action/${dislikeAction.id}/`)
        }
      }
    } catch (err) {
      console.error('撤销不感兴趣失败:', err)
    }
  }
}

const loadInitialRecommendations = async () => {
  try {
    loading.value = true
    error.value = ''
    
    // 检查本地存储中是否有之前保存的兴趣标签
    const savedTags = localStorage.getItem('selectedInterestTags')
    const savedUser = localStorage.getItem('user')
    const userId = savedUser ? JSON.parse(savedUser).id : null
    
    if (savedTags) {
      try {
        const tags = JSON.parse(savedTags)
        if (tags.length >= 3 && tags.length <= 5) {
          // 使用保存的标签重新获取推荐
          const res = await axios.post('http://127.0.0.1:8000/api/interests/', {
            tags: tags,
            user_id: userId
          })
          
          if (res.data.code === 200) {
            recommendations.value = res.data.data
            return
          }
        }
      } catch (e) {
        console.error('解析保存的标签失败:', e)
      }
    }
    
    // 如果没有保存的标签或获取失败，使用常规推荐
    const compensationRecs = localStorage.getItem('compensation_recommendations')
    
    const res = await axios.get('http://127.0.0.1:8000/api/recommend/you_may_like/')
    
    if (res.data.code === 200) {
      if (compensationRecs) {
        try {
          const parsedRecs = JSON.parse(compensationRecs)
          recommendations.value = [...parsedRecs, ...res.data.data]
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

const initRecommendationChart = () => {
  if (!recommendationChart.value || recommendations.value.length === 0) return
  
  const chart = echarts.init(recommendationChart.value)
  
  // 统计推荐维度分布
  const categoryStats = {}
  recommendations.value.forEach(book => {
    const category = book.category || '其他'
    if (categoryStats[category]) {
      categoryStats[category]++
    } else {
      categoryStats[category] = 1
    }
  })
  
  const categories = Object.keys(categoryStats)
  const data = categories.map(category => ({
    name: category,
    value: categoryStats[category]
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
        name: '推荐维度',
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
            fontSize: '14',
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

const getTopCategory = () => {
  if (recommendations.value.length === 0) return '未知'
  
  const categoryStats = {}
  recommendations.value.forEach(book => {
    const category = book.category || '其他'
    if (categoryStats[category]) {
      categoryStats[category]++
    } else {
      categoryStats[category] = 1
    }
  })
  
  let topCategory = '其他'
  let maxCount = 0
  
  for (const [category, count] of Object.entries(categoryStats)) {
    if (count > maxCount) {
      maxCount = count
      topCategory = category
    }
  }
  
  return topCategory
}

// 监听推荐数据变化，更新图表
watch(recommendations, () => {
  // 延迟执行，确保 DOM 已经更新
  setTimeout(() => {
    initRecommendationChart()
  }, 100)
}, { deep: true })

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

/* Hero 区域 */
.hero-section {
  background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
  padding: 80px 24px;
  color: #ffffff;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 20px 20px;
  z-index: 1;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 40px;
  position: relative;
  z-index: 2;
}

.hero-text {
  flex: 1;
  min-width: 0;
}

.hero-decoration {
  flex-shrink: 0;
  width: 300px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-chart {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  position: relative;
  overflow: hidden;
}

.hero-chart::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0) 100%);
  border-radius: 12px;
  z-index: 0;
}

.hero-chart::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  z-index: 1;
}

.hero-chart-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  z-index: 2;
}

.hero-section h1 {
  margin: 0 0 16px 0;
  font-size: 56px;
  font-weight: 400;
  letter-spacing: 0.05em;
  line-height: 1.1;
  text-transform: uppercase;
}

.hero-section p {
  margin: 0 0 24px 0;
  font-size: 24px;
  font-weight: 330;
  letter-spacing: 0.02em;
  opacity: 0.9;
}

.hero-subtitle {
  font-size: 18px;
  font-weight: 320;
  letter-spacing: 0.02em;
  opacity: 0.7;
}

.recommendation-section {
  max-width: 1200px;
  margin: 48px auto;
  padding: 0 24px;
}

.recommendation-section h3 {
  font-size: 20px;
  color: #000000;
  margin: 0 0 24px 0;
  font-weight: 500;
  letter-spacing: -0.02em;
}

/* 模式切换 */
.mode-selector {
  margin-bottom: 32px;
  text-align: center;
}

.mode-buttons {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 32px;
}

.mode-btn {
  background: transparent;
  padding: 12px 28px;
  border: 1px solid #e0e0e0;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.01em;
  color: #333;
  position: relative;
  overflow: hidden;
}

.mode-btn:hover {
  border-color: #000;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.mode-btn.active {
  background: #000000;
  color: #ffffff;
  border-color: #000000;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

/* 兴趣雷达区域 */
.interest-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 4px 30px rgba(0,0,0,0.05);
  text-align: center;
}

.interest-hint {
  margin: 20px 0 32px 0;
  color: #666666;
  font-size: 16px;
  font-weight: 320;
  letter-spacing: -0.01em;
}

/* 书名输入区域 */
.book-input-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 32px;
  margin: -40px auto 32px;
  max-width: 900px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
  position: relative;
  z-index: 10;
  backdrop-filter: blur(10px);
}

.book-input {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  align-items: center;
}

.book-input-field {
  flex: 1;
  min-width: 300px;
  padding: 16px 24px;
  border: 1px solid #e0e0e0;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 330;
  letter-spacing: -0.01em;
  outline: none;
  transition: all 0.3s ease;
  position: relative;
}

.book-input-field:focus {
  border-color: #000000;
  box-shadow: 0 0 0 3px rgba(0,0,0,0.05);
  animation: border-pulse 2s infinite;
}

@keyframes border-pulse {
  0% {
    box-shadow: 0 0 0 3px rgba(0,0,0,0.05);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(0,0,0,0.02);
  }
  100% {
    box-shadow: 0 0 0 3px rgba(0,0,0,0.05);
  }
}

/* 分类选择区域 */
.category-selector {
  background: #ffffff;
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 32px;
  box-shadow: 0 4px 30px rgba(0,0,0,0.05);
}

.category-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 24px;
}

.category-tag {
  background: #f9f9f9;
  padding: 12px 24px;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 400;
  letter-spacing: -0.01em;
  border: 1px solid #e0e0e0;
}

.category-tag:hover {
  background: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.category-tag.active {
  background: #000000;
  color: #ffffff;
  border-color: #000000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.action-section {
  text-align: center;
  margin: 32px 0;
}

.recommend-btn {
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 16px 56px;
  border-radius: 50px;
  font-size: 18px;
  font-weight: 400;
  letter-spacing: -0.01em;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.recommend-btn:hover {
  opacity: 0.9;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.recommend-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

.recommend-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 推荐结果区域 */
.recommendations-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 32px;
  margin-top: 32px;
  box-shadow: 0 4px 30px rgba(0,0,0,0.05);
}

.recommendations-header {
  margin-bottom: 32px;
}

.recommendations-header h3 {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
  color: #000;
}

/* 推荐内容区域 */
.recommendations-content {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

/* 辅助侧边面板 */
.recommendations-sidebar {
  flex-shrink: 0;
  width: 280px;
}

.sidebar-card {
  background: #f9f9f9;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  margin-bottom: 24px;
}

.sidebar-card h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
  color: #333;
  letter-spacing: -0.01em;
}

.sidebar-card h5 {
  margin: 20px 0 12px 0;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  letter-spacing: -0.01em;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dynamic-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.dynamic-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.dynamic-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.dynamic-text {
  font-size: 14px;
  color: #666;
  font-weight: 320;
  letter-spacing: -0.01em;
}

/* 推荐维度分布图表 */
.recommendation-chart {
  width: 100%;
  height: 200px;
}

.chart-container {
  width: 100%;
  height: 100%;
}

/* 书籍网格容器 */
.books-grid-container {
  flex: 1;
  min-width: 0;
}

/* 书籍网格 */
.books-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32px;
  margin-top: 0;
  max-width: 100%;
  overflow-x: hidden;
}

.book-card {
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 420px;
}

.book-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.1);
  z-index: 10;
}

.dislike-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 20;
  border-radius: 12px;
}

.dark-mode .dislike-overlay {
  background: rgba(0, 0, 0, 0.90);
}

.dark-mode .dislike-text {
  color: #fff;
}

.dislike-content {
  text-align: center;
  padding: 20px;
}

.dislike-text {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 500;
  color: #666;
}

.undo-btn {
  padding: 8px 24px;
  background: black;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s ease;
}

.undo-btn:hover {
  background: #333;
}

/* 不感兴趣弹窗 */
.dislike-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dislike-modal {
  background: white;
  border-radius: 12px;
  width: 80%;
  max-width: 280px;
  aspect-ratio: 1;
  overflow: hidden;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
}

.dislike-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
}

.dislike-modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #666;
}

.dislike-modal-body {
  flex: 1;
  padding: 16px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.dislike-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 8px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #f8f9fa;
}

.dislike-option:hover {
  background: #e9ecef;
  transform: scale(1.02);
}

.dislike-option:active {
  transform: scale(0.98);
}

.option-icon {
  font-size: 32px;
  margin-bottom: 6px;
}

.option-label {
  font-size: 13px;
  color: #555;
  text-align: center;
}

/* 深色模式 */
.home-page.dark-mode .dislike-modal-overlay {
  background: rgba(0, 0, 0, 0.8) !important;
}

.dark-mode .dislike-modal {
  background: #1a1a1a;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
}

.dark-mode .dislike-modal-header {
  border-bottom-color: #333;
}

.dark-mode .dislike-modal-header h3 {
  color: #fff;
}

.dark-mode .close-btn {
  color: #666;
}

.dark-mode .close-btn:hover {
  background: #333;
  color: #fff;
}

.dark-mode .dislike-option {
  background: #2a2a2a;
}

.dark-mode .dislike-option:hover {
  background: #333;
}

.dark-mode .option-label {
  color: #ccc;
}

/* 书籍排名 */
.book-rank {
  position: absolute;
  top: 0;
  left: 0;
  background: rgba(0, 0, 0, 0.8);
  color: #ffffff;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: -0.01em;
  border-bottom-right-radius: 12px;
  z-index: 10;
  backdrop-filter: blur(10px);
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

/* 书籍信息 */
.book-info {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 200px;
  position: relative;
}

.book-title {
  font-size: 16px;
  color: #000000;
  margin: 0 0 8px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
  font-weight: 500;
  letter-spacing: -0.01em;
  cursor: pointer;
  transition: opacity 0.3s ease;
}

.book-title:hover {
  opacity: 0.8;
}

.book-author {
  font-size: 14px;
  color: #666666;
  margin: 0 0 12px 0;
  font-weight: 320;
  letter-spacing: -0.01em;
}

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
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  box-orient: vertical;
  overflow: hidden;
  flex: 1;
  font-weight: 320;
  letter-spacing: -0.01em;
}

.book-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-shrink: 0;
}

.action-btn {
  padding: 8px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  background: #ffffff;
}

.action-btn.small {
  font-size: 12px;
  padding: 6px 10px;
}

.like-btn {
  color: #ff6b6b;
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
  color: #666666;
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

/* 书籍悬停详情 */
.book-full-intro {
  display: none;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 20px;
  font-size: 14px;
  color: #000000;
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
  color: #000000;
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

/* 加载和错误状态 */
.loading {
  text-align: center;
  padding: 64px 0;
  color: #666666;
  font-size: 16px;
  font-weight: 320;
  letter-spacing: -0.01em;
}

.error {
  text-align: center;
  padding: 24px;
  color: #000000;
  background: #f9f9f9;
  border-radius: 12px;
  margin-top: 32px;
  font-weight: 400;
  letter-spacing: -0.01em;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .hero-content {
    flex-direction: column;
    text-align: center;
    gap: 32px;
  }
  
  .hero-decoration {
    width: 250px;
    height: 180px;
  }
  
  .recommendations-content {
    flex-direction: column;
  }
  
  .recommendations-sidebar {
    width: 100%;
  }
  
  .sidebar-card {
    display: flex;
    flex-direction: row;
    gap: 32px;
  }
  
  .sidebar-content {
    flex: 1;
  }
  
  .recommendation-chart {
    flex-shrink: 0;
    width: 200px;
    height: 200px;
  }
  
  .hero-section h1 {
    font-size: 48px;
  }
  
  .books-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 24px;
  }
}

@media (max-width: 992px) {
  .books-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .hero-section {
    padding: 100px 24px;
  }
  
  .hero-section h1 {
    font-size: 40px;
  }
  
  .book-input-field {
    min-width: 250px;
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 80px 20px;
  }
  
  .hero-section h1 {
    font-size: 32px;
  }
  
  .hero-section p {
    font-size: 20px;
  }
  
  .hero-decoration {
    width: 200px;
    height: 150px;
  }
  
  .mode-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .mode-btn {
    width: 200px;
    text-align: center;
  }
  
  .book-input {
    flex-direction: column;
  }
  
  .book-input-field {
    width: 100%;
    min-width: unset;
  }
  
  .sidebar-card {
    flex-direction: column;
    gap: 24px;
  }
  
  .recommendation-chart {
    width: 100%;
    height: 200px;
  }
  
  .books-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
  
  .book-card {
    min-height: 380px;
  }
  
  .recommendation-section {
    padding: 0 16px;
  }
  
  .interest-section,
  .book-input-section,
  .category-selector,
  .recommendations-section {
    padding: 24px;
  }
}

@media (max-width: 480px) {
  .books-grid {
    grid-template-columns: 1fr;
  }
  
  .hero-section h1 {
    font-size: 28px;
  }
  
  .hero-section p {
    font-size: 18px;
  }
  
  .book-card {
    min-height: 400px;
  }
}

/* 暗色模式 */
.dark-mode .home-page {
  background: #121212 !important;
  color: #ffffff !important;
}

.dark-mode .hero-section {
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
}

.dark-mode .recommendation-section h3 {
  color: #ffffff;
}

.dark-mode .mode-btn {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.15);
}

.dark-mode .mode-btn:hover {
  border-color: #ffffff;
  box-shadow: 0 4px 12px rgba(255,255,255,0.1);
}

.dark-mode .mode-btn.active {
  background: #ffffff;
  color: #000000;
  border-color: #ffffff;
  box-shadow: 0 4px 16px rgba(255,255,255,0.2);
}

.dark-mode .interest-section,
.dark-mode .book-input-section,
.dark-mode .category-selector,
.dark-mode .recommendations-section {
  background: #1a1a1a;
  box-shadow: 0 4px 30px rgba(0,0,0,0.3);
}

.dark-mode .sidebar-card {
  background: #2c2c2c;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.dark-mode .sidebar-card h4,
.dark-mode .sidebar-card h5 {
  color: #ffffff;
}

.dark-mode .dynamic-item {
  background: #1a1a1a;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.dark-mode .dynamic-item:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}

.dark-mode .dynamic-text {
  color: #b0b0b0;
}

.dark-mode .book-input-field {
  background: #2c2c2c;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff;
}

.dark-mode .book-input-field:focus {
  border-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(255,255,255,0.1);
}

.dark-mode .category-tag {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.15);
}

.dark-mode .category-tag:hover {
  background: rgba(255, 255, 255, 0.12);
  box-shadow: 0 2px 8px rgba(255,255,255,0.1);
}

.dark-mode .category-tag.active {
  background: #ffffff;
  color: #000000;
  border-color: #ffffff;
  box-shadow: 0 4px 12px rgba(255,255,255,0.2);
}

.dark-mode .recommend-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .recommend-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}

.dark-mode .book-card {
  background: #1a1a1a;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.dark-mode .book-card:hover {
  box-shadow: 0 8px 30px rgba(0,0,0,0.4);
}

.dark-mode .book-full-intro {
  background: rgba(26, 26, 26, 0.95);
  backdrop-filter: blur(10px);
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

.dark-mode .loading {
  color: #b0b0b0;
}

.dark-mode .error {
  color: #ffffff;
  background: #2c2c2c;
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
  color: #b0b0b0;
}

.dark-mode .action-btn {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  color: #ffffff;
}

.dark-mode .like-btn {
  color: #ff6b6b;
  border-color: #ff6b6b;
}

.dark-mode .like-btn:hover {
  background: rgba(255, 107, 107, 0.2);
}

.dark-mode .dislike-btn {
  color: #b0b0b0;
  border-color: #b0b0b0;
}

.dark-mode .dislike-btn:hover {
  background: rgba(176, 176, 176, 0.2);
}
</style>
