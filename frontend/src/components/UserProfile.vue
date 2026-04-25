<template>
  <div class="user-profile">
    <header class="profile-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h1>个人中心</h1>
    </header>

    <div class="profile-container">
      <div class="profile-card">
        <div class="profile-avatar">
          <img :src="user.avatar" alt="用户头像">
          <input
            type="file"
            id="avatar-upload"
            class="avatar-upload-input"
            accept="image/*"
            @change="handleAvatarUpload"
          >
          <label for="avatar-upload" class="avatar-upload-btn">更换头像</label>
        </div>
        <h2 class="profile-username">{{ user.username }}</h2>
        <p class="profile-email">{{ user.email }}</p>
      </div>

      <div class="profile-section">
        <h3 class="section-title">个人信息</h3>
        <div class="info-form">
          <div class="form-group">
            <label for="username">用户名</label>
            <input
              type="text"
              id="username"
              v-model="editForm.username"
              :disabled="!isEditing"
            >
          </div>
          <div class="form-group">
            <label for="email">邮箱</label>
            <input
              type="email"
              id="email"
              v-model="editForm.email"
              :disabled="!isEditing"
            >
          </div>
          <div class="form-actions">
            <button
              v-if="!isEditing"
              class="edit-btn"
              @click="isEditing = true"
            >
              编辑信息
            </button>
            <div v-else class="action-buttons">
              <button class="save-btn" @click="saveChanges">保存</button>
              <button class="cancel-btn" @click="cancelEdit">取消</button>
            </div>
          </div>
        </div>
      </div>

      <div class="profile-section">
        <h3 class="section-title">账号安全</h3>
        <div class="security-item">
          <span>修改密码</span>
          <button class="link-btn" @click="showChangePassword = true">修改</button>
        </div>
      </div>

      <div class="profile-section">
        <h3 class="section-title">我的评分</h3>
        <div v-if="loadingRatings" class="loading-ratings">加载评分中...</div>
        <div v-else-if="ratings.length === 0" class="no-ratings">暂无评分记录</div>
        <div v-else class="ratings-list">
          <div v-for="rating in ratings" :key="rating.id" class="rating-item">
            <div class="rating-book-info">
              <img :src="rating.book.cover_url" :alt="rating.book.title" class="rating-book-cover">
              <div class="rating-book-details">
                <h4 class="rating-book-title" @click="goToBookDetail(rating.book.book_id)">{{ rating.book.title }}</h4>
                <p class="rating-book-author">{{ rating.book.author }}</p>
                <div class="rating-time">
                  <span>评分时间: {{ formatDate(rating.created_at) }}</span>
                  <span v-if="rating.updated_at !== rating.created_at"> (更新于: {{ formatDate(rating.updated_at) }})</span>
                </div>
              </div>
            </div>
            <div class="rating-actions">
              <div v-if="editingRating && editingRating.id === rating.id" class="rating-edit">
                <StarRating
                  v-model:rating="editRatingScore"
                />
                <div class="rating-edit-buttons">
                  <button class="save-rating-btn" @click="saveRating">保存</button>
                  <button class="cancel-rating-btn" @click="cancelEditRating">取消</button>
                </div>
                <div v-if="ratingError" class="rating-error">{{ ratingError }}</div>
              </div>
              <div v-else class="rating-display">
                <div class="rating-score">{{ rating.score }}分</div>
                <div class="rating-buttons">
                  <button class="edit-rating-btn" @click="startEditRating(rating)">编辑</button>
                  <button class="delete-rating-btn" @click="deleteRating(rating.id)">删除</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="profile-section">
        <h3 class="section-title">操作</h3>
        <button class="logout-btn" @click="logout">退出登录</button>
      </div>
    </div>

    <div class="modal" v-if="showChangePassword">
      <div class="modal-overlay" @click="showChangePassword = false"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h2>修改密码</h2>
          <button class="close-btn" @click="showChangePassword = false">×</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="changePassword">
            <div class="form-group">
              <label for="old-password">旧密码</label>
              <input
                type="password"
                id="old-password"
                v-model="passwordForm.oldPassword"
                placeholder="请输入旧密码"
                required
              >
            </div>
            <div class="form-group">
              <label for="new-password">新密码</label>
              <input
                type="password"
                id="new-password"
                v-model="passwordForm.newPassword"
                placeholder="请输入新密码"
                required
              >
            </div>
            <div class="form-group">
              <label for="confirm-password">确认密码</label>
              <input
                type="password"
                id="confirm-password"
                v-model="passwordForm.confirmPassword"
                placeholder="请确认新密码"
                required
              >
            </div>
            <div class="form-actions">
              <button type="submit" class="primary-btn">确认修改</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import StarRating from './StarRating.vue'
import defaultAvatar from '../assets/avatars/OIP-C.webp'

const router = useRouter()

const user = ref({
  id: 1,
  username: 'user',
  email: 'user@example.com',
  avatar: defaultAvatar
})

const isEditing = ref(false)
const showChangePassword = ref(false)

const editForm = reactive({
  username: '',
  email: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const ratings = ref([])
const loadingRatings = ref(false)
const editingRating = ref(null)
const editRatingScore = ref(0)
const ratingError = ref('')

const goBack = () => {
  router.back()
}

const saveChanges = async () => {
  try {
    const savedUser = localStorage.getItem('user')
    if (!savedUser) {
      alert('用户未登录')
      return
    }

    const userData = JSON.parse(savedUser)
    const res = await axios.put(`http://127.0.0.1:8000/api/user/profile/${userData.id}/`, {
      username: editForm.username,
      email: editForm.email
    })

    if (res.data.code === 200) {
      user.value.username = editForm.username
      user.value.email = editForm.email
      localStorage.setItem('user', JSON.stringify(user.value))
      isEditing.value = false
      alert('保存成功')
    } else {
      alert('保存失败: ' + res.data.msg)
    }
  } catch (error) {
    console.error('更新个人信息失败:', error)
    alert('保存失败，请检查网络连接')
  }
}

const cancelEdit = () => {
  editForm.username = user.value.username
  editForm.email = user.value.email
  isEditing.value = false
}

const handleAvatarUpload = async (e) => {
  const file = e.target.files[0]
  if (file) {
    // 1. 立即显示预览（增强用户体验）
    const reader = new FileReader()
    reader.onload = async (event) => {
      try {
        const savedUser = localStorage.getItem('user')
        if (!savedUser) {
          alert('用户未登录')
          return
        }

        const userData = JSON.parse(savedUser)
        const avatarUrl = event.target.result

        console.log('用户ID:', userData.id)
        console.log('文件:', file)
        console.log('请求URL:', `http://127.0.0.1:8000/api/user/avatar/${userData.id}/`)

        // 2. 发送实际文件到后端
        const formData = new FormData()
        formData.append('avatar', file)

        // 关键：改用 post，且不要设置任何 header
        const res = await axios.post(`http://127.0.0.1:8000/api/user/avatar/${userData.id}/`, formData)

        console.log('服务器返回数据:', res.data)

        if (res.data.code === 200) {
          // 核心修改：这里必须指向后端返回的具体 URL 字段
          const newAvatarUrl = res.data.data.avatar
          
          // 如果返回的是相对路径，确保加上后端的基础地址
          // 如果后端已经返回了 http://127.0.0.1:8000/media/... 则不需要
          user.value.avatar = newAvatarUrl.startsWith('http')
            ? newAvatarUrl
            : `http://127.0.0.1:8000${newAvatarUrl}`
            
          localStorage.setItem('user', JSON.stringify(user.value))
          alert('头像更新成功！')
        } else {
          alert('头像更新失败: ' + res.data.msg)
        }
      } catch (error) {
        console.error('更新头像失败:', error)
        console.error('错误详情:', error.response)
        alert('头像更新失败，请检查网络连接')
      }
    }
    reader.readAsDataURL(file)
  }
}

const changePassword = async () => {
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    alert('两次输入的密码不一致')
    return
  }

  try {
    const savedUser = localStorage.getItem('user')
    if (!savedUser) {
      alert('用户未登录')
      return
    }

    const userData = JSON.parse(savedUser)
    const res = await axios.put(`http://127.0.0.1:8000/api/user/password/${userData.id}/`, {
      old_password: passwordForm.oldPassword,
      new_password: passwordForm.newPassword
    })

    if (res.data.code === 200) {
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
      showChangePassword.value = false
      alert('密码修改成功')
    } else {
      alert('密码修改失败: ' + res.data.msg)
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    alert('密码修改失败，请检查网络连接')
  }
}

const logout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  router.push('/')
}

const fetchUserRatings = async () => {
  try {
    const savedUser = localStorage.getItem('user')
    if (!savedUser) return

    loadingRatings.value = true
    const userData = JSON.parse(savedUser)
    const res = await axios.get('http://127.0.0.1:8000/api/user/rating/', {
      params: { user_id: userData.id }
    })

    if (res.data.code === 200) {
      ratings.value = res.data.data
    }
  } catch (error) {
    console.error('获取用户评分失败:', error)
  } finally {
    loadingRatings.value = false
  }
}

const startEditRating = (rating) => {
  editingRating.value = rating
  editRatingScore.value = rating.score
}

const saveRating = async () => {
  if (!editingRating.value) return

  try {
    const savedUser = localStorage.getItem('user')
    if (!savedUser) {
      return
    }

    const userData = JSON.parse(savedUser)
    const res = await axios.put(`http://127.0.0.1:8000/api/user/rating/${editingRating.value.id}/`, {
      score: editRatingScore.value
    })

    if (res.data.code === 200) {
      const index = ratings.value.findIndex(r => r.id === editingRating.value.id)
      if (index !== -1) {
        ratings.value[index].score = editRatingScore.value
        ratings.value[index].updated_at = new Date().toISOString()
      }
      editingRating.value = null
    } else {
      ratingError.value = res.data.msg
    }
  } catch (error) {
    console.error('更新评分失败:', error)
    ratingError.value = '更新评分失败，请检查网络连接'
  }
}

const cancelEditRating = () => {
  editingRating.value = null
  editRatingScore.value = 0
  ratingError.value = ''
}

const deleteRating = async (ratingId) => {
  if (!confirm('确定要删除这个评分吗？')) return

  try {
    const res = await axios.delete(`http://127.0.0.1:8000/api/user/rating/${ratingId}/`)

    if (res.data.code === 200) {
      ratings.value = ratings.value.filter(r => r.id !== ratingId)
    } else {
      alert(res.data.msg)
    }
  } catch (error) {
    console.error('删除评分失败:', error)
    alert('删除评分失败，请检查网络连接')
  }
}

const goToBookDetail = (bookId) => {
  router.push(`/book/${bookId}`)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  const savedUser = localStorage.getItem('user')
  if (savedUser) {
    const savedUserData = JSON.parse(savedUser)
    if (!savedUserData.avatar) {
      savedUserData.avatar = defaultAvatar
      localStorage.setItem('user', JSON.stringify(savedUserData))
    }
    user.value = savedUserData
  }
  editForm.username = user.value.username
  editForm.email = user.value.email

  fetchUserRatings()
})
</script>

<style scoped>
.user-profile {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: #ffffff;
  min-height: 100vh;
  padding-bottom: 48px;
}

.profile-header {
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

.profile-header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 540;
  letter-spacing: -0.26px;
  color: #000000;
}

.profile-container {
  max-width: 800px;
  margin: 24px auto;
  padding: 0 24px;
}

.profile-card {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 32px;
  text-align: center;
  margin-bottom: 24px;
}

.profile-avatar {
  position: relative;
  display: inline-block;
  margin-bottom: 16px;
}

.profile-avatar img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(0, 0, 0, 0.08);
  transition: opacity 0.2s;
}

.avatar-upload-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 2;
}

.avatar-upload-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #000000;
  color: #ffffff;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  cursor: pointer;
  transition: opacity 0.2s;
  z-index: 1;
  padding: 0;
  font-weight: 400;
  letter-spacing: -0.1px;
}

.avatar-upload-btn:hover {
  opacity: 0.85;
}

.profile-avatar:hover img {
  opacity: 0.8;
}

.profile-username {
  font-size: 24px;
  color: #000000;
  margin: 0 0 8px 0;
  font-weight: 540;
  letter-spacing: -0.26px;
}

.profile-email {
  font-size: 16px;
  color: #666666;
  margin: 0;
  font-weight: 330;
  letter-spacing: -0.14px;
}

.profile-section {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 1px 0 rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(0, 0, 0, 0.08);
  padding: 24px;
  margin-bottom: 24px;
}

.section-title {
  font-size: 18px;
  color: #000000;
  margin: 0 0 20px 0;
  font-weight: 540;
  letter-spacing: -0.14px;
  padding-left: 12px;
  border-left: 2px solid #000000;
}

.info-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  color: #666666;
  font-weight: 320;
  letter-spacing: -0.1px;
}

.form-group input {
  padding: 12px 16px;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 50px;
  font-size: 16px;
  font-weight: 330;
  letter-spacing: -0.14px;
  transition: border-color 0.2s;
  outline: none;
}

.form-group input:focus {
  border-color: #000000;
}

.form-group input:disabled {
  background: #fafafa;
  cursor: not-allowed;
  color: #666666;
}

.form-actions {
  margin-top: 8px;
}

.edit-btn, .save-btn, .cancel-btn, .logout-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.edit-btn, .save-btn {
  background: #000000;
  color: #ffffff;
}

.edit-btn:hover, .save-btn:hover {
  opacity: 0.85;
}

.edit-btn:focus, .save-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

.cancel-btn {
  background: rgba(0, 0, 0, 0.08);
  color: #000000;
  margin-left: 12px;
}

.cancel-btn:hover {
  background: rgba(0, 0, 0, 0.12);
}

.action-buttons {
  display: flex;
  gap: 0;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  font-size: 16px;
  color: #000000;
  font-weight: 330;
  letter-spacing: -0.14px;
}

.security-item:last-child {
  border-bottom: none;
}

.link-btn {
  background: none;
  border: none;
  color: #000000;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  font-weight: 400;
  letter-spacing: -0.14px;
  text-decoration: underline;
}

.link-btn:hover {
  opacity: 0.7;
}

.logout-btn {
  background: #ffffff;
  color: #000000;
  border: 1px solid #000000;
  width: 100%;
  padding: 14px;
  font-size: 16px;
}

.logout-btn:hover {
  background: rgba(0, 0, 0, 0.04);
}

.logout-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

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
}

.modal-content {
  background: #ffffff;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  position: relative;
  z-index: 1;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #000000;
  font-weight: 540;
  letter-spacing: -0.26px;
}

.close-btn {
  background: rgba(0, 0, 0, 0.08);
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #000000;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.12);
}

.modal-body {
  padding: 24px;
}

.modal-body .form-group {
  margin-bottom: 16px;
}

.modal-body .form-group:last-of-type {
  margin-bottom: 0;
}

.primary-btn {
  width: 100%;
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 14px;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.primary-btn:hover {
  opacity: 0.85;
}

.primary-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

.loading-ratings, .no-ratings {
  text-align: center;
  padding: 48px 0;
  color: #666666;
  font-size: 16px;
  font-weight: 320;
}

.ratings-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rating-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
  transition: background 0.2s;
}

.rating-item:hover {
  background: #f0f0f0;
}

.rating-book-info {
  flex: 1;
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.rating-book-cover {
  width: 60px;
  height: 80px;
  border-radius: 4px;
  object-fit: cover;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.rating-book-details {
  flex: 1;
}

.rating-book-title {
  font-size: 16px;
  font-weight: 450;
  color: #000000;
  margin: 0 0 6px 0;
  cursor: pointer;
  transition: opacity 0.2s;
  letter-spacing: -0.14px;
}

.rating-book-title:hover {
  opacity: 0.7;
}

.rating-book-author {
  font-size: 14px;
  color: #666666;
  margin: 0 0 8px 0;
  font-weight: 320;
}

.rating-time {
  font-size: 12px;
  color: #666666;
  font-weight: 320;
}

.rating-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.rating-display {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.rating-score {
  font-size: 20px;
  font-weight: 540;
  color: #000000;
  letter-spacing: -0.14px;
}

.rating-buttons {
  display: flex;
  gap: 8px;
}

.edit-rating-btn, .delete-rating-btn, .save-rating-btn, .cancel-rating-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 400;
  letter-spacing: -0.14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.edit-rating-btn {
  background: rgba(0, 0, 0, 0.08);
  color: #000000;
}

.edit-rating-btn:hover {
  background: rgba(0, 0, 0, 0.12);
}

.delete-rating-btn {
  background: rgba(0, 0, 0, 0.08);
  color: #000000;
}

.delete-rating-btn:hover {
  background: rgba(0, 0, 0, 0.12);
}

.rating-edit {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
  width: 100%;
}

.rating-edit-buttons {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.save-rating-btn {
  background: #000000;
  color: #ffffff;
}

.save-rating-btn:hover {
  opacity: 0.85;
}

.cancel-rating-btn {
  background: rgba(0, 0, 0, 0.08);
  color: #000000;
}

.cancel-rating-btn:hover {
  background: rgba(0, 0, 0, 0.12);
}

.rating-error {
  font-size: 13px;
  color: #000000;
  font-weight: 400;
  margin-top: 8px;
}

@media (max-width: 768px) {
  .profile-container {
    padding: 0 16px;
  }

  .profile-card {
    padding: 24px;
  }

  .profile-section {
    padding: 20px;
  }

  .rating-item {
    flex-direction: column;
  }

  .rating-actions {
    align-items: flex-start;
    width: 100%;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid rgba(0, 0, 0, 0.08);
  }

  .rating-display {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  .rating-edit {
    width: 100%;
    align-items: flex-start;
  }

  .rating-book-cover {
    width: 50px;
    height: 67px;
  }
}

.dark-mode .user-profile {
  background: #000000 !important;
  color: #ffffff !important;
}

.dark-mode .profile-header {
  background: #000000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-mode .profile-header h1 {
  color: #ffffff;
}

.dark-mode .back-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .back-btn:hover {
  opacity: 0.85;
}

.dark-mode .profile-card {
  background: #0a0a0a;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-mode .profile-username {
  color: #ffffff;
}

.dark-mode .profile-email {
  color: #b0b0b0;
}

.dark-mode .profile-section {
  background: #0a0a0a;
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.dark-mode .section-title {
  color: #ffffff;
  border-left-color: #ffffff;
}

.dark-mode .form-group label {
  color: #b0b0b0;
}

.dark-mode .form-group input {
  background: #1a1a1a;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #ffffff;
}

.dark-mode .form-group input:focus {
  border-color: #ffffff;
}

.dark-mode .form-group input:disabled {
  background: #1a1a1a;
  color: #b0b0b0;
}

.dark-mode .edit-btn, .dark-mode .save-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .cancel-btn {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.dark-mode .cancel-btn:hover {
  background: rgba(255, 255, 255, 0.16);
}

.dark-mode .security-item {
  color: #ffffff;
  border-bottom-color: rgba(255, 255, 255, 0.08);
}

.dark-mode .link-btn {
  color: #ffffff;
}

.dark-mode .logout-btn {
  background: #000000;
  color: #ffffff;
  border: 1px solid #ffffff;
}

.dark-mode .logout-btn:hover {
  background: rgba(255, 255, 255, 0.08);
}

.dark-mode .modal-content {
  background: #000000;
}

.dark-mode .modal-header {
  border-bottom-color: rgba(255, 255, 255, 0.08);
}

.dark-mode .modal-header h2 {
  color: #ffffff;
}

.dark-mode .close-btn {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.dark-mode .close-btn:hover {
  background: rgba(255, 255, 255, 0.16);
}

.dark-mode .loading-ratings, .dark-mode .no-ratings {
  color: #b0b0b0;
}

.dark-mode .rating-item {
  background: #1a1a1a;
}

.dark-mode .rating-item:hover {
  background: #2a2a2a;
}

.dark-mode .rating-book-title {
  color: #ffffff;
}

.dark-mode .rating-book-author {
  color: #b0b0b0;
}

.dark-mode .rating-time {
  color: #b0b0b0;
}

.dark-mode .rating-score {
  color: #e0e0e0;
}

.dark-mode .edit-rating-btn {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.dark-mode .edit-rating-btn:hover {
  background: rgba(255, 255, 255, 0.16);
}

.dark-mode .delete-rating-btn {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.dark-mode .delete-rating-btn:hover {
  background: rgba(255, 255, 255, 0.16);
}

.dark-mode .save-rating-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .cancel-rating-btn {
  background: rgba(255, 255, 255, 0.08);
  color: #ffffff;
}

.dark-mode .rating-error {
  color: #ffffff;
}
</style>
