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
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-container h1 {
  text-align: center;
  margin: 0 0 30px 0;
  font-size: 24px;
  color: #333;
  font-weight: bold;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px;
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
  margin-top: 30px;
}

.login-btn {
  width: 100%;
  background: #409eff;
  color: white;
  border: none;
  padding: 14px;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: 0.2s;
}

.login-btn:hover:not(:disabled) {
  background: #66b1ff;
}

.login-btn:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
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

.login-tips {
  margin-top: 30px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
}

.login-tips p {
  margin: 0 0 10px 0;
  font-weight: 500;
  color: #333;
}

.login-tips ul {
  margin: 0;
  padding-left: 20px;
  color: #666;
}

.login-tips li {
  margin-bottom: 5px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 30px 20px;
  }
  
  .login-container h1 {
    font-size: 20px;
  }
}

/* 深色模式样式 */
.dark-mode .admin-login {
  background: linear-gradient(135deg, #3a3a3a 0%, #1e1e1e 100%);
}

.dark-mode .login-container {
  background: #1e1e1e;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.dark-mode .login-container h1 {
  color: #e0e0e0;
}

.dark-mode .form-group label {
  color: #e0e0e0;
}

.dark-mode .form-group input {
  background: #3a3a3a;
  border: 1px solid #4a4a4a;
  color: #e0e0e0;
}

.dark-mode .form-group input:focus {
  border-color: #66b1ff;
  box-shadow: 0 0 0 2px rgba(102, 177, 255, 0.2);
}

.dark-mode .error-message {
  background: #3a2a2a;
  border: 1px solid #5a3a3a;
  color: #ff6b6b;
}

.dark-mode .login-tips {
  background: #2c2c2c;
}

.dark-mode .login-tips p {
  color: #e0e0e0;
}

.dark-mode .login-tips ul {
  color: #999;
}
</style>