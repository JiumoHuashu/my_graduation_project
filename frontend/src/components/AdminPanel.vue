<template>
  <div class="admin-panel">
    <header class="admin-header">
      <h1>管理员控制台</h1>
      <div class="admin-info">
        <span>欢迎，{{ admin.username }}</span>
        <button class="logout-btn" @click="logout">退出登录</button>
      </div>
    </header>

    <div class="admin-container">
      <div class="admin-sidebar">
        <h2>功能菜单</h2>
        <ul>
          <li :class="{ active: activeMenu === 'books' }" @click="activeMenu = 'books'">书籍管理</li>
          <li :class="{ active: activeMenu === 'users' }" @click="activeMenu = 'users'">用户管理</li>
          <li :class="{ active: activeMenu === 'dashboard' }" @click="activeMenu = 'dashboard'">数据可视化</li>
        </ul>
      </div>

      <div class="admin-content">
        <!-- 书籍管理部分 -->
        <div v-if="activeMenu === 'books'">
          <div class="content-header">
            <h2>书籍管理</h2>
            <button class="add-btn" @click="showAddModal = true">添加书籍</button>
          </div>

          <div class="search-bar">
            <input 
              type="text" 
              v-model="searchKeyword" 
              placeholder="搜索书籍标题或作者"
              @input="handleSearch"
            >
          </div>

          <div class="books-table">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>书名</th>
                  <th>作者</th>
                  <th>分类</th>
                  <th>字数</th>
                  <th>阅读量</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="book in filteredBooks" :key="book.book_id">
                  <td>{{ book.book_id }}</td>
                  <td>{{ book.title }}</td>
                  <td>{{ book.author }}</td>
                  <td>{{ book.main_category }} / {{ book.sub_category }}</td>
                  <td>{{ (book.word_count / 10000).toFixed(1) }}万</td>
                  <td>{{ (book.read_count / 10000).toFixed(1) }}万</td>
                  <td>
                    <button class="edit-btn" @click="editBook(book)">编辑</button>
                    <button class="delete-btn" @click="deleteBook(book.book_id)">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="books.length === 0" class="empty-state">
            <div class="empty-icon">📚</div>
            <h3>暂无书籍数据</h3>
            <p>点击"添加书籍"按钮添加新书籍</p>
          </div>
        </div>

        <!-- 用户管理部分 -->
        <div v-if="activeMenu === 'users'">
          <div class="content-header">
            <h2>用户管理</h2>
          </div>

          <div class="search-bar">
            <input 
              type="text" 
              v-model="userSearchKeyword" 
              placeholder="搜索用户名或邮箱"
              @input="handleUserSearch"
            >
          </div>

          <div class="books-table">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>用户名</th>
                  <th>邮箱</th>
                  <th>书架书籍数</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in filteredUsers" :key="user.id">
                  <td>{{ user.id }}</td>
                  <td>{{ user.username }}</td>
                  <td>{{ user.email }}</td>
                  <td>{{ user.bookshelf.length }}</td>
                  <td>
                    <button class="edit-btn" @click="editUser(user)">编辑</button>
                    <button class="delete-btn" @click="deleteUser(user.id)">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="users.length === 0" class="empty-state">
            <div class="empty-icon">👤</div>
            <h3>暂无用户数据</h3>
            <p>用户将在注册后显示在此处</p>
          </div>
        </div>

        <!-- 数据可视化部分 -->
        <div v-if="activeMenu === 'dashboard'">
          <div class="content-header">
            <h2>数据可视化</h2>
          </div>

          <!-- 统计卡片 -->
          <div class="stats-cards">
            <div class="stat-card">
              <div class="stat-icon">📚</div>
              <div class="stat-info">
                <div class="stat-value">{{ books.length }}</div>
                <div class="stat-label">总书籍数</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">👤</div>
              <div class="stat-info">
                <div class="stat-value">{{ users.length }}</div>
                <div class="stat-label">总用户数</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">📈</div>
              <div class="stat-info">
                <div class="stat-value">{{ totalReadCount }}万</div>
                <div class="stat-label">总阅读量</div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">🏆</div>
              <div class="stat-info">
                <div class="stat-value">{{ topBookTitle || '暂无' }}</div>
                <div class="stat-label">热门书籍</div>
              </div>
            </div>
          </div>

          <div class="dashboard-content">
            <div class="chart-container">
              <h3>书籍分类分布</h3>
              <div ref="categoryChart" class="chart"></div>
            </div>

            <div class="chart-container">
              <h3>书籍阅读量统计</h3>
              <div ref="readCountChart" class="chart"></div>
            </div>

            <div class="chart-container">
              <h3>书籍字数分布</h3>
              <div ref="wordCountChart" class="chart"></div>
            </div>

            <div class="chart-container">
              <h3>书籍1-10分评分分布</h3>
              <div ref="ratingChart" class="chart"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑书籍弹窗 -->
    <div class="modal" v-if="showAddModal || showEditModal">
      <div class="modal-overlay" @click="closeModal"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ showEditModal ? '编辑书籍' : '添加书籍' }}</h2>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveBook">
            <div class="form-grid">
              <div class="form-group">
                <label for="book_id">书籍ID</label>
                <input 
                  type="text" 
                  id="book_id" 
                  v-model="bookForm.book_id" 
                  placeholder="请输入书籍ID"
                  :disabled="showEditModal"
                  required
                >
              </div>
              <div class="form-group">
                <label for="title">书名</label>
                <input 
                  type="text" 
                  id="title" 
                  v-model="bookForm.title" 
                  placeholder="请输入书名"
                  required
                >
              </div>
              <div class="form-group">
                <label for="author">作者</label>
                <input 
                  type="text" 
                  id="author" 
                  v-model="bookForm.author" 
                  placeholder="请输入作者"
                  required
                >
              </div>
              <div class="form-group">
                <label for="cover_url">封面链接</label>
                <input 
                  type="text" 
                  id="cover_url" 
                  v-model="bookForm.cover_url" 
                  placeholder="请输入封面链接"
                >
              </div>
              <div class="form-group">
                <label for="main_category">主分类</label>
                <input 
                  type="text" 
                  id="main_category" 
                  v-model="bookForm.main_category" 
                  placeholder="请输入主分类"
                  required
                >
              </div>
              <div class="form-group">
                <label for="sub_category">子分类</label>
                <input 
                  type="text" 
                  id="sub_category" 
                  v-model="bookForm.sub_category" 
                  placeholder="请输入子分类"
                  required
                >
              </div>
              <div class="form-group">
                <label for="word_count">字数</label>
                <input 
                  type="number" 
                  id="word_count" 
                  v-model.number="bookForm.word_count" 
                  placeholder="请输入字数"
                  min="0"
                >
              </div>
              <div class="form-group">
                <label for="read_count">阅读量</label>
                <input 
                  type="number" 
                  id="read_count" 
                  v-model.number="bookForm.read_count" 
                  placeholder="请输入阅读量"
                  min="0"
                >
              </div>
              <div class="form-group">
                <label for="monthly_read">月阅读数</label>
                <input 
                  type="number" 
                  id="monthly_read" 
                  v-model.number="bookForm.monthly_read" 
                  placeholder="请输入月阅读数"
                  min="0"
                >
              </div>
              <div class="form-group">
                <label for="total_read">总阅读数</label>
                <input 
                  type="number" 
                  id="total_read" 
                  v-model.number="bookForm.total_read" 
                  placeholder="请输入总阅读数"
                  min="0"
                >
              </div>
              <div class="form-group">
                <label for="monthly_flowers">月鲜花数</label>
                <input 
                  type="number" 
                  id="monthly_flowers" 
                  v-model.number="bookForm.monthly_flowers" 
                  placeholder="请输入月鲜花数"
                  min="0"
                >
              </div>
              <div class="form-group">
                <label for="total_flowers">总鲜花数</label>
                <input 
                  type="number" 
                  id="total_flowers" 
                  v-model.number="bookForm.total_flowers" 
                  placeholder="请输入总鲜花数"
                  min="0"
                >
              </div>
              <div class="form-group full-width">
                <label for="tags">标签</label>
                <input 
                  type="text" 
                  id="tags" 
                  v-model="bookForm.tags" 
                  placeholder="请输入标签，用|分隔"
                >
              </div>
              <div class="form-group full-width">
                <label for="introduction">简介</label>
                <textarea 
                  id="introduction" 
                  v-model="bookForm.introduction" 
                  placeholder="请输入简介"
                  rows="4"
                ></textarea>
              </div>
              <div class="form-group">
                <label for="onboarding_time">入站时间</label>
                <input 
                  type="text" 
                  id="onboarding_time" 
                  v-model="bookForm.onboarding_time" 
                  placeholder="请输入入站时间"
                >
              </div>
              <div class="form-group">
                <label for="update_time">更新时间</label>
                <input 
                  type="text" 
                  id="update_time" 
                  v-model="bookForm.update_time" 
                  placeholder="请输入更新时间"
                >
              </div>
            </div>
            <div class="form-actions">
              <button type="submit" class="save-btn" :disabled="loading">
                {{ loading ? '保存中...' : '保存' }}
              </button>
              <button type="button" class="cancel-btn" @click="closeModal">取消</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 编辑用户弹窗 -->
    <div class="modal" v-if="showUserEditModal">
      <div class="modal-overlay" @click="closeUserModal"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h2>编辑用户</h2>
          <button class="close-btn" @click="closeUserModal">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveUser">
            <div class="form-grid">
              <div class="form-group">
                <label for="user_id">用户ID</label>
                <input 
                  type="text" 
                  id="user_id" 
                  v-model="userForm.id" 
                  placeholder="用户ID"
                  disabled
                >
              </div>
              <div class="form-group">
                <label for="username">用户名</label>
                <input 
                  type="text" 
                  id="username" 
                  v-model="userForm.username" 
                  placeholder="请输入用户名"
                  required
                >
              </div>
              <div class="form-group">
                <label for="email">邮箱</label>
                <input 
                  type="email" 
                  id="email" 
                  v-model="userForm.email" 
                  placeholder="请输入邮箱"
                  required
                >
              </div>
              <div class="form-group full-width">
                <label for="bookshelf">书架书籍ID</label>
                <input 
                  type="text" 
                  id="bookshelf" 
                  v-model="bookshelfString" 
                  placeholder="请输入书籍ID，用逗号分隔"
                >
                <small>例如: 123,456,789</small>
              </div>
            </div>
            <div class="form-actions">
              <button type="submit" class="save-btn" :disabled="loading">
                {{ loading ? '保存中...' : '保存' }}
              </button>
              <button type="button" class="cancel-btn" @click="closeUserModal">取消</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import * as echarts from 'echarts'

const router = useRouter()

const admin = ref({ username: 'admin' })
const books = ref([])
const users = ref([])
const loading = ref(false)
const showAddModal = ref(false)
const showEditModal = ref(false)
const showUserEditModal = ref(false)
const searchKeyword = ref('')
const userSearchKeyword = ref('')
const activeMenu = ref('books')

// 图表相关
const categoryChart = ref(null)
const readCountChart = ref(null)
const wordCountChart = ref(null)
const ratingChart = ref(null)
let categoryChartInstance = null
let readCountChartInstance = null
let wordCountChartInstance = null
let ratingChartInstance = null

const bookForm = reactive({
  book_id: '',
  title: '',
  author: '',
  cover_url: '',
  main_category: '',
  sub_category: '',
  word_count: 0,
  read_count: 0,
  monthly_read: 0,
  total_read: 0,
  monthly_flowers: 0,
  total_flowers: 0,
  tags: '',
  introduction: '',
  onboarding_time: '',
  update_time: ''
})

const userForm = reactive({
  id: '',
  username: '',
  email: '',
  bookshelf: []
})

const bookshelfString = ref('')

const filteredBooks = computed(() => {
  if (!searchKeyword.value) {
    return books.value
  }
  const keyword = searchKeyword.value.toLowerCase()
  return books.value.filter(book => 
    book.title.toLowerCase().includes(keyword) || 
    book.author.toLowerCase().includes(keyword)
  )
})

const filteredUsers = computed(() => {
  if (!userSearchKeyword.value) {
    return users.value
  }
  const keyword = userSearchKeyword.value.toLowerCase()
  return users.value.filter(user => 
    user.username.toLowerCase().includes(keyword) || 
    user.email.toLowerCase().includes(keyword)
  )
})

// 统计数据计算属性
const totalReadCount = computed(() => {
  const total = books.value.reduce((sum, book) => sum + (book.read_count || 0), 0)
  return (total / 10000).toFixed(1)
})

const topBookTitle = computed(() => {
  if (books.value.length === 0) return ''
  const topBook = [...books.value].sort((a, b) => (b.read_count || 0) - (a.read_count || 0))[0]
  return topBook.title.length > 10 ? topBook.title.substring(0, 10) + '...' : topBook.title
})

const fetchBooks = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/admin/books/')
    if (res.data.code === 200) {
      books.value = res.data.data
    }
  } catch (error) {
    console.error('获取书籍列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // 搜索逻辑由computed属性处理
}

const handleUserSearch = () => {
  // 搜索逻辑由computed属性处理
}

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/admin/users/')
    if (res.data.code === 200) {
      users.value = res.data.data
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

const editUser = (user) => {
  // 填充表单
  Object.keys(userForm).forEach(key => {
    if (user.hasOwnProperty(key)) {
      userForm[key] = user[key]
    }
  })
  // 更新书架字符串
  bookshelfString.value = userForm.bookshelf.join(',')
  showUserEditModal.value = true
}

const saveUser = async () => {
  loading.value = true
  try {
    // 将书架字符串转换为数组
    userForm.bookshelf = bookshelfString.value.split(',').map(item => item.trim()).filter(item => item)
    // 更新用户
    const res = await axios.put(`http://127.0.0.1:8000/api/admin/users/${userForm.id}/`, userForm)
    if (res.data.code === 200) {
      alert('更新成功')
      closeUserModal()
      fetchUsers()
    }
  } catch (error) {
    console.error('保存用户失败:', error)
    alert('保存失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

const deleteUser = async (userId) => {
  if (confirm('确定要删除这个用户吗？')) {
    loading.value = true
    try {
      const res = await axios.delete(`http://127.0.0.1:8000/api/admin/users/${userId}/`)
      if (res.data.code === 200) {
        alert('删除成功')
        fetchUsers()
      }
    } catch (error) {
      console.error('删除用户失败:', error)
      alert('删除失败，请检查网络连接')
    } finally {
      loading.value = false
    }
  }
}

const closeUserModal = () => {
  showUserEditModal.value = false
}

const addBook = () => {
  // 重置表单
  Object.keys(bookForm).forEach(key => {
    bookForm[key] = ''
  })
  bookForm.word_count = 0
  bookForm.read_count = 0
  bookForm.monthly_read = 0
  bookForm.total_read = 0
  bookForm.monthly_flowers = 0
  bookForm.total_flowers = 0
  showAddModal.value = true
  showEditModal.value = false
}

const editBook = (book) => {
  // 填充表单
  Object.keys(bookForm).forEach(key => {
    if (book.hasOwnProperty(key)) {
      bookForm[key] = book[key]
    }
  })
  showEditModal.value = true
  showAddModal.value = false
}

const saveBook = async () => {
  loading.value = true
  try {
    if (showEditModal.value) {
      // 更新书籍
      const res = await axios.put(`http://127.0.0.1:8000/api/admin/books/${bookForm.book_id}/`, bookForm)
      if (res.data.code === 200) {
        alert('更新成功')
        closeModal()
        fetchBooks()
      }
    } else {
      // 添加书籍
      const res = await axios.post('http://127.0.0.1:8000/api/admin/books/', bookForm)
      if (res.data.code === 200) {
        alert('添加成功')
        closeModal()
        fetchBooks()
      }
    }
  } catch (error) {
    console.error('保存书籍失败:', error)
    alert('保存失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

const deleteBook = async (bookId) => {
  if (confirm('确定要删除这本书吗？')) {
    loading.value = true
    try {
      const res = await axios.delete(`http://127.0.0.1:8000/api/admin/books/${bookId}/`)
      if (res.data.code === 200) {
        alert('删除成功')
        fetchBooks()
      }
    } catch (error) {
      console.error('删除书籍失败:', error)
      alert('删除失败，请检查网络连接')
    } finally {
      loading.value = false
    }
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
}

const logout = () => {
  localStorage.removeItem('admin')
  router.push('/admin/login')
}

// 初始化书籍分类分布图表
const initCategoryChart = () => {
  if (!categoryChart.value) return
  
  // 销毁旧图表实例
  if (categoryChartInstance) {
    categoryChartInstance.dispose()
  }
  
  // 创建新图表实例
  categoryChartInstance = echarts.init(categoryChart.value)
  
  // 处理数据
  const categoryData = {}  
  books.value.forEach(book => {
    const category = book.main_category
    if (categoryData[category]) {
      categoryData[category]++
    } else {
      categoryData[category] = 1
    }
  })
  
  const categories = Object.keys(categoryData)
  const counts = Object.values(categoryData)
  
  // 图表配置
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 10,
      data: categories
    },
    series: [
      {
        name: '书籍分类',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 18,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: categories.map((category, index) => ({
          value: counts[index],
          name: category
        }))
      }
    ]
  }
  
  categoryChartInstance.setOption(option)
}

// 初始化书籍阅读量统计图表
const initReadCountChart = () => {
  if (!readCountChart.value) return
  
  // 销毁旧图表实例
  if (readCountChartInstance) {
    readCountChartInstance.dispose()
  }
  
  // 创建新图表实例
  readCountChartInstance = echarts.init(readCountChart.value)
  
  // 处理数据
  const topBooks = [...books.value]
    .sort((a, b) => b.read_count - a.read_count)
    .slice(0, 10)
  
  const titles = topBooks.map(book => book.title)
  const readCounts = topBooks.map(book => book.read_count)
  
  // 图表配置
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      boundaryGap: [0, 0.01]
    },
    yAxis: {
      type: 'category',
      data: titles,
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    series: [
      {
        name: '阅读量',
        type: 'bar',
        data: readCounts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        }
      }
    ]
  }
  
  readCountChartInstance.setOption(option)
}

// 初始化书籍字数分布图表
const initWordCountChart = () => {
  if (!wordCountChart.value) return
  
  // 销毁旧图表实例
  if (wordCountChartInstance) {
    wordCountChartInstance.dispose()
  }
  
  // 创建新图表实例
  wordCountChartInstance = echarts.init(wordCountChart.value)
  
  // 处理数据
  const wordRanges = [
    { name: '0-50万', min: 0, max: 500000, count: 0 },
    { name: '50-100万', min: 500000, max: 1000000, count: 0 },
    { name: '100-200万', min: 1000000, max: 2000000, count: 0 },
    { name: '200-500万', min: 2000000, max: 5000000, count: 0 },
    { name: '500万以上', min: 5000000, max: Infinity, count: 0 }
  ]
  
  books.value.forEach(book => {
    const wordCount = book.word_count || 0
    for (const range of wordRanges) {
      if (wordCount >= range.min && wordCount < range.max) {
        range.count++
        break
      }
    }
  })
  
  const ranges = wordRanges.map(range => range.name)
  const counts = wordRanges.map(range => range.count)
  
  // 图表配置
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ranges
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '书籍数量',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#fccb05' },
            { offset: 0.5, color: '#f5804e' },
            { offset: 1, color: '#f5804e' }
          ])
        }
      }
    ]
  }
  
  wordCountChartInstance.setOption(option)
}

// 初始化书籍评分分布图表
const initRatingChart = () => {
  if (!ratingChart.value) return
  
  // 销毁旧图表实例
  if (ratingChartInstance) {
    ratingChartInstance.dispose()
  }
  
  // 创建新图表实例
  ratingChartInstance = echarts.init(ratingChart.value)
  
  // 处理数据
  const ratingRanges = [
    { name: '1', min: 1, max: 2, count: 0 },
    { name: '2', min: 2, max: 3, count: 0 },
    { name: '3', min: 3, max: 4, count: 0 },
    { name: '4', min: 4, max: 5, count: 0 },
    { name: '5', min: 5, max: 6, count: 0 },
    { name: '6', min: 6, max: 7, count: 0 },
    { name: '7', min: 7, max: 8, count: 0 },
    { name: '8', min: 8, max: 9, count: 0 },
    { name: '9', min: 9, max: 10, count: 0 },
    { name: '10', min: 10, max: 11, count: 0 }
  ]
  
  books.value.forEach(book => {
    const rating = book.rating || 0
    for (const range of ratingRanges) {
      if (rating >= range.min && rating < range.max) {
        range.count++
        break
      }
    }
  })
  
  const ranges = ratingRanges.map(range => range.name)
  const counts = ratingRanges.map(range => range.count)
  
  // 图表配置
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ranges
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '书籍数量',
        type: 'bar',
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#40c9c6' },
            { offset: 0.5, color: '#5168e2' },
            { offset: 1, color: '#5168e2' }
          ])
        }
      }
    ]
  }
  
  ratingChartInstance.setOption(option)
}

// 初始化所有图表
const initCharts = () => {
  if (activeMenu.value === 'dashboard') {
    setTimeout(() => {
      initCategoryChart()
      initReadCountChart()
      initWordCountChart()
      initRatingChart()
    }, 100)
  }
}

// 监听activeMenu变化
watch(activeMenu, (newMenu) => {
  initCharts()
  if (newMenu === 'users') {
    fetchUsers()
  }
})

// 监听books变化
watch(books, () => {
  initCharts()
}, { deep: true })

// 监听窗口大小变化
window.addEventListener('resize', () => {
  categoryChartInstance?.resize()
  readCountChartInstance?.resize()
  wordCountChartInstance?.resize()
  ratingChartInstance?.resize()
})

onMounted(() => {
  // 从localStorage获取管理员信息
  const savedAdmin = localStorage.getItem('admin')
  if (savedAdmin) {
    admin.value = JSON.parse(savedAdmin)
  }
  fetchBooks()
  
  // 初始化图表
  initCharts()
})
</script>

<style scoped>
.admin-panel {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: #f8f9fa;
  min-height: 100vh;
  letter-spacing: -0.01em;
}

.admin-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 16px 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}

.admin-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: #000000;
}

.admin-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logout-btn {
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: -0.01em;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(0, 0, 0, 0.85);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.logout-btn:focus {
  outline: 2px solid #000000;
  outline-offset: 2px;
}

.admin-container {
  display: flex;
  max-width: 1200px;
  margin: 24px auto;
  gap: 24px;
  padding: 0 24px;
}

/* 侧边栏与导航 */
.admin-sidebar {
  width: 180px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
  padding: 24px;
  height: fit-content;
  flex-shrink: 0;
  transition: all 0.3s ease;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.admin-sidebar h2 {
  margin: 0 0 24px 0;
  font-size: 14px;
  color: #666666;
  font-weight: 500;
  letter-spacing: -0.01em;
  text-transform: uppercase;
}

.admin-sidebar ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.admin-sidebar li {
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: -0.01em;
  color: #000000;
  position: relative;
  left: 0;
  border-left: 4px solid transparent;
}

.admin-sidebar li:hover {
  background: rgba(0, 0, 0, 0.04);
  left: 4px;
}

.admin-sidebar li.active {
  background: rgba(0, 0, 0, 0.08);
  color: #000000;
  font-weight: 600;
  left: 4px;
  border-left-color: #000000;
}

/* 主内容区 */
.admin-content {
  flex: 1;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
  padding: 24px;
  transition: all 0.3s ease;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.content-header h2 {
  margin: 0;
  font-size: 18px;
  color: #000000;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.add-btn {
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: -0.01em;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-btn:hover {
  background: rgba(0, 0, 0, 0.85);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.add-btn:focus {
  outline: 2px solid #000000;
  outline-offset: 2px;
}

.search-bar {
  margin-bottom: 24px;
}

.search-bar input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 400;
  letter-spacing: -0.01em;
  transition: all 0.3s ease;
  outline: none;
}

.search-bar input:focus {
  border-color: #000000;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
}

/* 表格系统重构 */
.books-table {
  overflow-x: auto;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.books-table table {
  width: 100%;
  border-collapse: collapse;
}

.books-table th,
.books-table td {
  padding: 16px 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.books-table th {
  background: #f8f9fa;
  font-weight: 500;
  color: #666666;
  font-size: 12px;
  letter-spacing: -0.01em;
  text-transform: uppercase;
}

.books-table tr:hover td {
  background: #f8f9fa;
}

/* 操作按钮 */
.edit-btn,
.delete-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 400;
  letter-spacing: -0.14px;
  cursor: pointer;
  transition: opacity 0.2s;
  margin-right: 8px;
}

.edit-btn {
  background: rgba(0, 0, 0, 0.08);
  color: #000000;
}

.edit-btn:hover {
  background: rgba(0, 0, 0, 0.12);
}

.delete-btn {
  background: rgba(0, 0, 0, 0.08);
  color: #000000;
}

.delete-btn:hover {
  background: rgba(0, 0, 0, 0.12);
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-top: 24px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #000000;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
  color: #666666;
  font-weight: 400;
  letter-spacing: -0.01em;
}

/* 弹窗与表单 */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.modal-content {
  background: #ffffff;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 1;
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
  color: #000000;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.close-btn {
  background: #f8f9fa;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666666;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #e9ecef;
  color: #000000;
}

.modal-body {
  padding: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 14px;
  color: #666666;
  font-weight: 500;
  letter-spacing: -0.01em;
}

.form-group input,
.form-group textarea {
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 400;
  letter-spacing: -0.01em;
  transition: all 0.3s ease;
  outline: none;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #000000;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.save-btn,
.cancel-btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: -0.01em;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-btn {
  background: #000000;
  color: #ffffff;
  border: none;
}

.save-btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.85);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.save-btn:focus {
  outline: 2px solid #000000;
  outline-offset: 2px;
}

.cancel-btn {
  background: #f8f9fa;
  color: #666666;
  border: 1px solid #e0e0e0;
}

.cancel-btn:hover {
  background: #e9ecef;
  color: #000000;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  font-size: 32px;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #000000;
  letter-spacing: -0.01em;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #666666;
  font-weight: 500;
  letter-spacing: -0.01em;
  text-transform: uppercase;
}

/* 数据可视化 */
.dashboard-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
  margin-top: 24px;
}

.chart-container {
  background: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.chart-container:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.chart-container h3 {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: #666666;
  font-weight: 500;
  letter-spacing: -0.01em;
  text-transform: uppercase;
}

.chart {
  height: 300px;
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-container {
    flex-direction: column;
    padding: 0 16px;
  }

  .admin-sidebar {
    width: 100%;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .dashboard-content {
    grid-template-columns: 1fr;
  }

  .chart {
    height: 250px;
  }

  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 深色模式 */
.dark-mode .admin-panel {
  background: #0a0a0a !important;
  color: #ffffff !important;
}

.dark-mode .admin-header {
  background: rgba(26, 26, 26, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.dark-mode .admin-header h1 {
  color: #ffffff;
}

.dark-mode .logout-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .logout-btn:hover {
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.15);
}

.dark-mode .admin-sidebar {
  background: #0a0a0a;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-mode .admin-sidebar h2 {
  color: #b0b0b0;
}

.dark-mode .admin-sidebar li {
  color: #ffffff;
  border-left-color: transparent;
}

.dark-mode .admin-sidebar li:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.dark-mode .admin-sidebar li.active {
  background: rgba(255, 255, 255, 0.12);
  font-weight: 540;
  color: #ffffff;
  border-left-color: #ffffff;
}

.dark-mode .admin-content {
  background: #1a1a1a;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.dark-mode .content-header h2 {
  color: #ffffff;
}

.dark-mode .add-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .add-btn:hover {
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.15);
}

.dark-mode .search-bar input {
  background: #2d2d2d;
  border: 1px solid #3d3d3d;
  color: #ffffff;
}

.dark-mode .search-bar input:focus {
  border-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.dark-mode .books-table {
  background: #1a1a1a;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.dark-mode .books-table th {
  background: #2d2d2d;
  color: #b0b0b0;
  border-bottom-color: #3d3d3d;
}

.dark-mode .books-table td {
  border-bottom-color: #3d3d3d;
  color: #ffffff;
}

.dark-mode .books-table tr:hover td {
  background: #2d2d2d;
}

.dark-mode .edit-btn {
  background: rgba(255, 255, 255, 0.16);
  color: #ffffff;
}

.dark-mode .edit-btn:hover {
  background: rgba(255, 255, 255, 0.24);
}

.dark-mode .delete-btn {
  background: rgba(255, 255, 255, 0.16);
  color: #ffffff;
}

.dark-mode .delete-btn:hover {
  background: rgba(255, 255, 255, 0.24);
}

.dark-mode .empty-state {
  background: #2d2d2d;
}

.dark-mode .empty-state h3 {
  color: #ffffff;
}

.dark-mode .empty-state p {
  color: #888888;
}

.dark-mode .modal-content {
  background: #1a1a1a;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.dark-mode .modal-header {
  border-bottom-color: #3d3d3d;
}

.dark-mode .modal-header h2 {
  color: #ffffff;
}

.dark-mode .close-btn {
  background: #2d2d2d;
  color: #888888;
}

.dark-mode .close-btn:hover {
  background: #3d3d3d;
  color: #ffffff;
}

.dark-mode .form-group label {
  color: #b0b0b0;
}

.dark-mode .form-group input,
.dark-mode .form-group textarea {
  background: #2d2d2d;
  border: 1px solid #3d3d3d;
  color: #ffffff;
}

.dark-mode .form-group input:focus,
.dark-mode .form-group textarea:focus {
  border-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.dark-mode .save-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .save-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.15);
}

.dark-mode .cancel-btn {
  background: #2d2d2d;
  color: #888888;
  border: 1px solid #3d3d3d;
}

.dark-mode .cancel-btn:hover {
  background: #3d3d3d;
  color: #ffffff;
}

.dark-mode .stat-card {
  background: #2d2d2d;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.dark-mode .stat-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.dark-mode .stat-icon {
  background: #3d3d3d;
}

.dark-mode .stat-value {
  color: #ffffff;
}

.dark-mode .stat-label {
  color: #888888;
}

.dark-mode .chart-container {
  background: #2d2d2d;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.dark-mode .chart-container:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.dark-mode .chart-container h3 {
  color: #888888;
}
</style>