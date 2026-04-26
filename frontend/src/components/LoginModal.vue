<template>
  <div class="login-modal" v-if="visible">
    <div class="modal-overlay" @click="close"></div>
    <div class="modal-content">
      <div class="modal-header">
        <h2>{{ isRegister ? '注册账号' : '用户登录' }}</h2>
        <button class="close-btn" @click="close">×</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="username">用户名</label>
            <input 
              type="text" 
              id="username" 
              v-model="form.username" 
              placeholder="请输入用户名"
              required
            >
          </div>
          <div v-if="isRegister" class="form-group">
            <label for="email">邮箱</label>
            <input 
              type="email" 
              id="email" 
              v-model="form.email" 
              placeholder="请输入邮箱"
              required
            >
          </div>
          <div class="form-group">
            <label for="password">密码</label>
            <input 
              type="password" 
              id="password" 
              v-model="form.password" 
              placeholder="请输入密码"
              required
            >
          </div>
          <div v-if="isRegister" class="form-group">
            <label for="confirm-password">确认密码</label>
            <input 
              type="password" 
              id="confirm-password" 
              v-model="form.confirmPassword" 
              placeholder="请确认密码"
              required
            >
          </div>
          <div class="form-actions">
            <button type="submit" class="primary-btn" :disabled="loading">
              {{ loading ? (isRegister ? '注册中...' : '登录中...') : (isRegister ? '注册' : '登录') }}
            </button>
          </div>
          <div v-if="error" class="error-message">{{ error }}</div>
          <div class="form-footer">
            <span v-if="!isRegister">还没有账号？</span>
            <span v-else>已有账号？</span>
            <button 
              type="button" 
              class="link-btn" 
              @click="toggleMode"
              :disabled="loading"
            >
              {{ isRegister ? '去登录' : '去注册' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'
import defaultAvatar from '../assets/avatars/OIP-C.webp'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'login-success'])

const isRegister = ref(false)
const loading = ref(false)
const error = ref('')
const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const toggleMode = () => {
  isRegister.value = !isRegister.value
  error.value = ''
}

const close = () => {
  emit('close')
}

const handleSubmit = async () => {
  if (isRegister.value && form.password !== form.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    let res
    if (isRegister.value) {
      // 注册请求
      res = await axios.post('http://127.0.0.1:8000/api/user/register/', {
        username: form.username,
        email: form.email,
        password: form.password
      })
    } else {
      // 登录请求
      res = await axios.post('http://127.0.0.1:8000/api/user/login/', {
        username: form.username,
        password: form.password
      })
    }
    
    if (res.data.code === 200) {
      let user = res.data.data
      // 如果用户数据没有头像，使用默认头像
      if (!user.avatar) {
        user.avatar = defaultAvatar
      }
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('token', 'mock-token')
      emit('login-success', user)
      close()
    } else {
      error.value = res.data.msg
    }
  } catch (err) {
    console.error('请求失败:', err)
    error.value = '网络请求失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-modal {
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
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  transition: all 0.3s ease;
}

.modal-content {
  background: #ffffff;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 1;
  animation: fadeInUp 0.3s ease-out;
  transition: all 0.3s ease;
}

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

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #000000;
  letter-spacing: -0.01em;
}

.close-btn {
  background: #f5f5f5;
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
  background: #e0e0e0;
  color: #000000;
  transform: scale(1.05);
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #000000;
  font-weight: 500;
  letter-spacing: -0.01em;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  background: #f5f5f5;
  transition: all 0.3s ease;
  outline: none;
  letter-spacing: -0.01em;
}

.form-group input:focus {
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #000000;
}

.form-actions {
  margin-top: 24px;
}

.primary-btn {
  width: 100%;
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 14px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: -0.01em;
}

.primary-btn:hover:not(:disabled) {
  background: rgba(0, 0, 0, 0.85);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.primary-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

.primary-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.form-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #666666;
  letter-spacing: -0.01em;
}

.link-btn {
  background: none;
  border: none;
  color: #000000;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  margin-left: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
  letter-spacing: -0.01em;
}

.link-btn:hover:not(:disabled) {
  text-decoration: underline;
  opacity: 0.8;
}

.error-message {
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(245, 108, 108, 0.1);
  border-radius: 8px;
  color: #f56c6c;
  font-size: 14px;
  letter-spacing: -0.01em;
  transition: all 0.3s ease;
}

/* 深色模式 */
.dark-mode .modal-content {
  background: #1a1a1a;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
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
  color: #ffffff;
}

.dark-mode .form-group input {
  background: #2d2d2d;
  color: #ffffff;
}

.dark-mode .form-group input:focus {
  background: #3d3d3d;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
  border: 1px solid #ffffff;
}

.dark-mode .primary-btn {
  background: #ffffff;
  color: #000000;
}

.dark-mode .primary-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.15);
}

.dark-mode .form-footer {
  color: #888888;
}

.dark-mode .link-btn {
  color: #ffffff;
}

.dark-mode .link-btn:hover:not(:disabled) {
  opacity: 0.8;
}

.dark-mode .error-message {
  background: rgba(245, 108, 108, 0.2);
  color: #ff6b6b;
}
</style>