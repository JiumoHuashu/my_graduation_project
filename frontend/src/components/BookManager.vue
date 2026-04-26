<template>
  <div class="book-manager">
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
            <td>{{ formatNumber(book.word_count) }}万</td>
            <td>{{ formatNumber(book.read_count) }}万</td>
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'

const books = ref([])
const loading = ref(false)
const showAddModal = ref(false)
const showEditModal = ref(false)
const searchKeyword = ref('')

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

const formatNumber = (num) => {
  if (!num) return '0'
  return (num / 10000).toFixed(1)
}

const handleSearch = () => {
  // 搜索逻辑由computed属性处理
}

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

const addBook = () => {
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
      const res = await axios.put(`http://127.0.0.1:8000/api/admin/books/${bookForm.book_id}/`, bookForm)
      if (res.data.code === 200) {
        alert('更新成功')
        closeModal()
        fetchBooks()
      }
    } else {
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

defineExpose({
  fetchBooks
})

onMounted(() => {
  fetchBooks()
})
</script>

<style scoped>
.book-manager {
  height: 100%;
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

/* 深色模式 */
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
</style>
