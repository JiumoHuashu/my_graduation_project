<template>
  <div class="admin-login">
    <div class="login-container">
      <h1>管理员登录</h1>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="form.username" 
            placeholder="请输入管理员用户名"
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
        <div class="form-actions">
          <button type="submit" class="login-btn" :disabled="loading">
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
      </form>
      <div class="login-tips">
        <p>默认管理员账户：</p>
        <ul>
          <li>admin / admin123</li>
          <li>manager / manager123</li>
          <li>root / root123</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const form = reactive({
  username: '',
  password: ''
})

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const res = await axios.post('http://127.0.0.1:8000/api/admin/login/', {
      username: form.username,
      password: form.password
    })
    
    if (res.data.code === 200) {
      // 保存管理员信息到localStorage
      localStorage.setItem('admin', JSON.stringify(res.data.data))
      // 跳转到管理员面板
      router.push('/admin/panel')
    } else {
      error.value = res.data.msg
    }
  } catch (err) {
    console.error('登录失败:', err)
    error.value = '登录失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.admin-login {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: #f4f7f9;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  letter-spacing: -0.01em;
}

.login-container {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.05);
  padding: 40px;
  width: 100%;
  max-width: 400px;
  transition: all 0.3s ease;
}

.login-container h1 {
  text-align: center;
  margin: 0 0 32px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  letter-spacing: -0.01em;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a1a;
  letter-spacing: -0.01em;
}

.form-group input {
  width: 100%;
  padding: 14px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  background: #f9f9f9;
  transition: all 0.3s ease;
  outline: none;
  letter-spacing: -0.01em;
}

.form-group input:focus {
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
  border: 1px solid #1a1a1a;
}

.form-actions {
  margin-top: 32px;
}

.login-btn {
  width: 100%;
  background: #1a1a1a;
  color: #ffffff;
  border: none;
  padding: 14px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 1px;
}

.login-btn:hover:not(:disabled) {
  background: #333333;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

.login-btn:disabled {
  background: #e0e0e0;
  color: #999999;
  cursor: not-allowed;
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

.login-tips {
  margin-top: 32px;
  padding: 16px;
  background: #ffffff;
  border: 1px dashed #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.login-tips p {
  margin: 0 0 12px 0;
  font-weight: 500;
  color: #1a1a1a;
  letter-spacing: -0.01em;
}

.login-tips ul {
  margin: 0;
  padding-left: 20px;
  color: #666666;
  letter-spacing: -0.01em;
}

.login-tips li {
  margin-bottom: 6px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 32px 24px;
  }
  
  .login-container h1 {
    font-size: 20px;
    margin-bottom: 24px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-actions {
    margin-top: 24px;
  }
  
  .login-tips {
    margin-top: 24px;
  }
}

/* 深色模式样式 */
.dark-mode .admin-login {
  background: #0a0a0a;
}

.dark-mode .login-container {
  background: #141414;
  box-shadow: 0 20px 50px rgba(0,0,0,0.3);
}

.dark-mode .login-container h1 {
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

.dark-mode .login-btn {
  background: #ffffff;
  color: #0a0a0a;
}

.dark-mode .login-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.15);
}

.dark-mode .login-btn:disabled {
  background: #3d3d3d;
  color: #666666;
}

.dark-mode .error-message {
  background: rgba(245, 108, 108, 0.2);
  color: #ff6b6b;
}

.dark-mode .login-tips {
  background: #141414;
  border: 1px dashed #3d3d3d;
}

.dark-mode .login-tips p {
  color: #ffffff;
}

.dark-mode .login-tips ul {
  color: #999999;
}
</style>