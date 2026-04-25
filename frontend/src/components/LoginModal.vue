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
}

.modal-content {
  background: #fff;
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
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: 0.2s;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.form-actions {
  margin-top: 20px;
}

.primary-btn {
  width: 100%;
  background: #409eff;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: 0.2s;
}

.primary-btn:hover {
  background: #66b1ff;
}

.form-footer {
  margin-top: 15px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.link-btn {
  background: none;
  border: none;
  color: #409eff;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  margin-left: 5px;
}

.link-btn:hover {
  text-decoration: underline;
}

.error-message {
  margin-top: 15px;
  padding: 10px;
  background: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
  color: #f56c6c;
  font-size: 14px;
}
</style>