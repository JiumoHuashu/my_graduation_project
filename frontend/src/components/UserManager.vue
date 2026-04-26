<template>
  <div class="user-manager">
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
            <td>{{ user.bookshelf ? user.bookshelf.length : 0 }}</td>
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
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'

const users = ref([])
const loading = ref(false)
const showUserEditModal = ref(false)
const userSearchKeyword = ref('')

const userForm = reactive({
  id: '',
  username: '',
  email: '',
  bookshelf: []
})

const bookshelfString = ref('')

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
  Object.keys(userForm).forEach(key => {
    if (user.hasOwnProperty(key)) {
      userForm[key] = user[key]
    }
  })
  bookshelfString.value = (userForm.bookshelf || []).join(',')
  showUserEditModal.value = true
}

const saveUser = async () => {
  loading.value = true
  try {
    userForm.bookshelf = bookshelfString.value.split(',').map(item => item.trim()).filter(item => item)
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

defineExpose({
  fetchUsers
})

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.user-manager {
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
  max-width: 600px;
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

.form-group input {
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 400;
  letter-spacing: -0.01em;
  transition: all 0.3s ease;
  outline: none;
}

.form-group input:focus {
  border-color: #000000;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
}

.form-group small {
  font-size: 12px;
  color: #999999;
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

.dark-mode .form-group input {
  background: #2d2d2d;
  border: 1px solid #3d3d3d;
  color: #ffffff;
}

.dark-mode .form-group input:focus {
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
