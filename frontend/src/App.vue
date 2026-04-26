<template>
  <div class="app" :class="{ 'dark-mode': isDarkMode }">
    <header class="top-bar" :class="{ 'compact': isDetailPage }">
      <div class="nav-container">
        <div class="nav-brand">
          <router-link to="/" class="brand-link">
            <h1>小说书库</h1>
          </router-link>
          <div v-if="isDetailPage" class="detail-title">
            {{ currentBookTitle || '小说详情' }}
          </div>
        </div>
        <div class="nav-links" v-if="!isDetailPage && !isProfilePage && !isBookshelfPage && !isAdminPage">
          <router-link
            to="/"
            :class="['nav-link', $route.name === 'home' ? 'active' : '']"
          >
            热门推荐
          </router-link>
          <router-link
            to="/smart"
            :class="['nav-link', $route.name === 'smart' ? 'active' : '']"
          >
            智能推荐
          </router-link>
          <router-link
            to="/search"
            :class="['nav-link', $route.name === 'search' ? 'active' : '']"
          >
            搜索
          </router-link>
          <router-link
            to="/rank"
            :class="['nav-link', $route.name === 'rank' ? 'active' : '']"
          >
            排行榜
          </router-link>
          <router-link
            to="/admin/login"
            class="nav-link admin-link"
          >
            管理员入口
          </router-link>
        </div>
        <div class="user-section">
          <button
            class="theme-toggle-btn"
            @click="toggleTheme"
            title="切换主题"
          >
            <span v-if="isDarkMode">☀</span>
            <span v-else>☾</span>
          </button>

          <button
            v-if="!user"
            class="login-btn"
            @click="showLoginModal = true"
          >
            登录
          </button>
          <div v-else class="user-menu">
            <router-link to="/bookshelf" class="bookshelf-btn">
              书架
            </router-link>
            <div class="user-avatar" @click="toggleUserMenu">
              <img :src="(user.avatar && !user.avatar.includes('via.placeholder.com')) ? user.avatar : defaultAvatar" alt="用户头像">
              <span class="username">{{ user.username }}</span>
              <span class="dropdown-icon">▼</span>
            </div>
            <div v-if="showUserMenu" class="user-dropdown">
              <router-link to="/profile">个人中心</router-link>
              <a href="#" @click.prevent="logout">退出登录</a>
            </div>
          </div>
        </div>
      </div>
    </header>

    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>

    <LoginModal
      :visible="showLoginModal"
      @close="showLoginModal = false"
      @login-success="handleLoginSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import LoginModal from './components/LoginModal.vue'
import defaultAvatar from './assets/avatars/OIP-C.webp'

const router = useRouter()
const showLoginModal = ref(false)
const showUserMenu = ref(false)
const user = ref(null)
const admin = ref(null)
const isDarkMode = ref(false)
const currentBookTitle = ref('')

const isDetailPage = computed(() => {
  return router.currentRoute.value.name === 'bookDetail'
})

const isProfilePage = computed(() => {
  return router.currentRoute.value.name === 'profile'
})

const isBookshelfPage = computed(() => {
  return router.currentRoute.value.name === 'bookshelf'
})

const isAdminPage = computed(() => {
  return router.currentRoute.value.name === 'adminLogin' || router.currentRoute.value.name === 'adminPanel'
})

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const handleLoginSuccess = (userData) => {
  userData.avatar = defaultAvatar
  user.value = userData
  localStorage.setItem('user', JSON.stringify(userData))
}

const handleAdminLoginSuccess = (adminData) => {
  admin.value = adminData
  router.push('/admin/panel')
}

const handleAdminLogout = () => {
  admin.value = null
  localStorage.removeItem('admin')
  router.push('/admin/login')
}

const logout = () => {
  user.value = null
  localStorage.removeItem('user')
  localStorage.removeItem('token')
  showUserMenu.value = false
  router.push('/')
}

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem('isDarkMode', isDarkMode.value)
}

watch(isDarkMode, (newValue) => {
  if (newValue) {
    document.documentElement.classList.add('dark-mode')
    document.body.classList.add('dark-mode')
  } else {
    document.documentElement.classList.remove('dark-mode')
    document.body.classList.remove('dark-mode')
  }
}, { immediate: true })

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

  const savedAdmin = localStorage.getItem('admin')
  if (savedAdmin) {
    admin.value = JSON.parse(savedAdmin)
  }

  const savedTheme = localStorage.getItem('isDarkMode')
  if (savedTheme !== null) {
    isDarkMode.value = JSON.parse(savedTheme)
  } else {
    isDarkMode.value = false
  }
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background-color: #ffffff;
  color: #000000;
  transition: background-color 0.3s ease, color 0.3s ease;
  letter-spacing: -0.14px;
  font-weight: 330;
  line-height: 1.40;
}

.dark-mode {
  background-color: #000000 !important;
  color: #ffffff !important;
}

.dark-mode body {
  background-color: #000000 !important;
  color: #ffffff !important;
}
</style>

<style scoped>
.app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  min-height: 100vh;
  transition: background-color 0.3s ease, color 0.3s ease;
  background: #ffffff;
  color: #000000;
  letter-spacing: -0.01em;
}

/* 导航栏视觉重塑 */
.top-bar {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.03);
  position: sticky;
  top: 0;
  z-index: 100;
  transition: all 0.3s ease;
}

/* 紧凑模式 */
.top-bar.compact {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05);
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
  transition: all 0.3s ease;
}

.top-bar.compact .nav-container {
  height: 56px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.nav-brand h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.01em;
  white-space: nowrap;
}

.brand-link {
  text-decoration: none;
  color: #000000;
  transition: all 0.3s ease;
  display: inline-block;
  padding: 8px 16px;
  border-radius: 50px;
}

.brand-link:hover {
  background: rgba(0, 0, 0, 0.04);
  transform: translateY(-1px);
}

/* 详情页标题 */
.detail-title {
  font-size: 16px;
  font-weight: 500;
  letter-spacing: -0.01em;
  color: #666666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 300px;
}

.nav-links {
  display: flex;
  gap: 12px;
  flex: 2;
  justify-content: center;
}

/* 导航链接优化 */
.nav-link {
  text-decoration: none;
  color: #333333;
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.01em;
  transition: all 0.3s ease;
  padding: 10px 18px;
  border-radius: 50px;
  display: inline-block;
  position: relative;
}

.nav-link:hover {
  background: rgba(0, 0, 0, 0.04);
  transform: translateY(-1px);
}

.nav-link.active, .nav-link.router-link-active {
  font-weight: 600;
  background: rgba(0, 0, 0, 0.08);
}

.admin-link {
  color: #333333;
  font-weight: 400;
}

.admin-link:hover {
  background: rgba(0, 0, 0, 0.04);
  transform: translateY(-1px);
}

/* 用户工具组优化 */
.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  justify-content: flex-end;
}

/* 主题切换按钮 */
.theme-toggle-btn {
  background: rgba(0, 0, 0, 0.08);
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  color: #333333;
}

.theme-toggle-btn:hover {
  background: rgba(0, 0, 0, 0.12);
  transform: scale(1.05);
}

.theme-toggle-btn:focus {
  outline: dashed 2px #333333;
  outline-offset: 2px;
}

.login-btn {
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 10px 24px;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: -0.01em;
  cursor: pointer;
  transition: all 0.3s ease;
}

.login-btn:hover {
  background: rgba(0, 0, 0, 0.85);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.login-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

.user-menu {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 书架按钮 */
.bookshelf-btn {
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 10px 24px;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: -0.01em;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
}

.bookshelf-btn:hover {
  background: rgba(0, 0, 0, 0.85);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  text-decoration: none;
  color: #ffffff;
}

.bookshelf-btn:focus {
  outline: dashed 2px #000000;
  outline-offset: 2px;
}

/* 用户头像 */
.user-avatar {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 6px 16px;
  border-radius: 50px;
  transition: all 0.3s ease;
}

.user-avatar:hover {
  background: rgba(0, 0, 0, 0.04);
  transform: translateY(-1px);
}

.user-avatar img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.user-avatar:hover img {
  transform: scale(1.1);
}

.username {
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.01em;
  color: #333333;
  white-space: nowrap;
}

.dropdown-icon {
  font-size: 10px;
  color: #666666;
  transition: transform 0.3s ease;
}

.user-avatar:hover .dropdown-icon {
  transform: rotate(180deg);
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
  padding: 8px 0;
  min-width: 180px;
  margin-top: 8px;
  z-index: 1000;
  transition: all 0.3s ease;
}

.user-dropdown a {
  display: block;
  padding: 12px 20px;
  text-decoration: none;
  color: #333333;
  font-size: 16px;
  font-weight: 400;
  letter-spacing: -0.01em;
  transition: all 0.3s ease;
}

.user-dropdown a:hover {
  background: rgba(0, 0, 0, 0.04);
  padding-left: 24px;
}

.user-dropdown a:focus {
  outline: dashed 2px #333333;
  outline-offset: -2px;
}

/* 路由切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-container {
    padding: 0 16px;
  }

  .nav-brand h1 {
    font-size: 18px;
  }

  .detail-title {
    max-width: 200px;
    font-size: 14px;
  }

  .nav-links {
    gap: 8px;
  }

  .nav-link {
    font-size: 14px;
    padding: 8px 12px;
  }

  .user-section {
    gap: 8px;
  }

  .login-btn, .bookshelf-btn {
    font-size: 14px;
    padding: 8px 16px;
  }

  .username {
    display: none;
  }

  .user-avatar {
    gap: 8px;
    padding: 6px 12px;
  }
}

/* 暗色模式 */
.app.dark-mode {
  background-color: #0a0a0a !important;
  color: #ffffff !important;
}

.app.dark-mode .top-bar {
  background: rgba(10, 10, 10, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
}

.app.dark-mode .top-bar.compact {
  background: rgba(10, 10, 10, 0.98);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
}

.app.dark-mode .brand-link {
  color: #ffffff;
}

.app.dark-mode .brand-link:hover {
  background: rgba(255, 255, 255, 0.08);
}

.app.dark-mode .detail-title {
  color: #b0b0b0;
}

.app.dark-mode .nav-link {
  color: #ffffff;
}

.app.dark-mode .nav-link:hover {
  background: rgba(255, 255, 255, 0.08);
}

.app.dark-mode .nav-link.active,
.app.dark-mode .nav-link.router-link-active {
  font-weight: 600;
  background: rgba(255, 255, 255, 0.12);
}

.app.dark-mode .admin-link {
  color: #ffffff;
}

.app.dark-mode .admin-link:hover {
  background: rgba(255, 255, 255, 0.08);
}

.app.dark-mode .login-btn {
  background: #ffffff;
  color: #000000;
}

.app.dark-mode .login-btn:hover {
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.15);
}

.app.dark-mode .bookshelf-btn {
  background: #ffffff;
  color: #000000;
}

.app.dark-mode .bookshelf-btn:hover {
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.15);
}

.app.dark-mode .bookshelf-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}

.app.dark-mode .user-avatar {
  color: #ffffff;
}

.app.dark-mode .user-avatar:hover {
  background: rgba(255, 255, 255, 0.08);
}

.app.dark-mode .username {
  color: #ffffff;
}

.app.dark-mode .dropdown-icon {
  color: #b0b0b0;
}

.app.dark-mode .user-dropdown {
  background: #1a1a1a;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

.app.dark-mode .user-dropdown a {
  color: #ffffff;
}

.app.dark-mode .user-dropdown a:hover {
  background: rgba(255, 255, 255, 0.08);
}

.app.dark-mode .theme-toggle-btn {
  background: rgba(255, 255, 255, 0.16);
  color: #ffffff;
}

.app.dark-mode .theme-toggle-btn:hover {
  background: rgba(255, 255, 255, 0.24);
}

.app.dark-mode .theme-toggle-btn:focus {
  outline: dashed 2px #ffffff;
  outline-offset: 2px;
}
</style>
