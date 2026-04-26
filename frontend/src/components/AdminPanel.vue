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
          <li :class="{ active: activeMenu === 'data-center' }" @click="activeMenu = 'data-center'">数据控制中心</li>
        </ul>
      </div>

      <div class="admin-content">
        <transition name="fade" mode="out-in">
          <BookManager v-if="activeMenu === 'books'" key="books" />
          <UserManager v-else-if="activeMenu === 'users'" key="users" />
          <AnalyticsDashboard v-else-if="activeMenu === 'dashboard'" key="dashboard" />
          <DataControlCenter v-else-if="activeMenu === 'data-center'" key="data-center" />
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import BookManager from './BookManager.vue'
import UserManager from './UserManager.vue'
import AnalyticsDashboard from './AnalyticsDashboard.vue'
import DataControlCenter from './DataControlCenter.vue'

const router = useRouter()

const admin = ref({ username: 'admin' })
const activeMenu = ref('books')

const logout = () => {
  localStorage.removeItem('admin')
  router.push('/admin/login')
}

onMounted(() => {
  const savedAdmin = localStorage.getItem('admin')
  if (savedAdmin) {
    admin.value = JSON.parse(savedAdmin)
  }
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

.admin-content {
  flex: 1;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
  padding: 24px;
  transition: all 0.3s ease;
  min-height: 600px;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
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
</style>
