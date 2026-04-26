<template>
  <div class="data-control-center">
    <div class="content-header">
      <h2>数据控制中心</h2>
    </div>

    <div class="data-center-content">
      <!-- 爬虫控制区 -->
      <div class="control-panel">
        <h3>爬虫控制</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="startPage">起始页码</label>
            <input
              type="number"
              id="startPage"
              v-model.number="crawlerConfig.startPage"
              placeholder="起始页码"
              min="1"
            >
          </div>
          <div class="form-group">
            <label for="endPage">结束页码</label>
            <input
              type="number"
              id="endPage"
              v-model.number="crawlerConfig.endPage"
              placeholder="结束页码"
              min="1"
            >
          </div>
          <div class="form-group">
            <label for="delay">采集延迟(ms)</label>
            <input
              type="number"
              id="delay"
              v-model.number="crawlerConfig.delay"
              placeholder="采集延迟"
              min="0"
            >
          </div>
        </div>
        <div class="control-actions">
          <button class="crawler-btn" @click="startCrawler" :disabled="crawlerLoading">
            {{ crawlerLoading ? '采集中...' : '一键启动采集' }}
          </button>
          <button class="stop-btn" @click="stopCrawler" :disabled="!crawlerLoading">
            停止
          </button>
        </div>
        <div class="crawler-stats">
          <div class="stat-item">
            <span class="stat-label">当前采集ID:</span>
            <span class="stat-value">{{ crawlerStats.currentBookId || '未开始' }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">已保存文件:</span>
            <span class="stat-value">{{ crawlerStats.savedFiles }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">异常报错:</span>
            <span class="stat-value error">{{ crawlerStats.errors }}</span>
          </div>
        </div>
      </div>

      <!-- 存储管理区 -->
      <div class="control-panel">
        <h3>存储管理</h3>
        <div class="form-group">
          <label for="jsonPath">JSON 文件路径</label>
          <input
            type="text"
            id="jsonPath"
            v-model="storageConfig.jsonPath"
            placeholder="JSON 文件路径"
          >
        </div>
        <div class="control-actions">
          <button class="storage-btn" @click="syncToDatabase('incremental')" :disabled="storageLoading">
            {{ storageLoading ? '同步中...' : '增量更新' }}
          </button>
          <button class="storage-btn danger" @click="syncToDatabase('full')" :disabled="storageLoading">
            {{ storageLoading ? '同步中...' : '清空并重新导入' }}
          </button>
        </div>
        <div v-if="storageProgress > 0" class="progress-container">
          <div class="progress-label">
            <span>同步进度:</span>
            <span>{{ storageProgress }}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: storageProgress + '%' }"></div>
          </div>
        </div>
      </div>

      <!-- 实时任务日志 -->
      <div class="console-area">
        <div class="console-header">
          <h3>实时任务日志</h3>
          <button class="clear-btn" @click="clearConsole">清空日志</button>
        </div>
        <div class="console-content" ref="consoleRef">
          <div v-if="consoleLogs.length === 0" class="console-empty">
            等待任务启动...
          </div>
          <div v-for="(log, index) in consoleLogs" :key="index" class="console-log">
            <span class="log-time">{{ log.time }}</span>
            <span class="log-content" :class="log.type">{{ log.content }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const crawlerConfig = reactive({
  startPage: 81,
  endPage: 101,
  delay: 1200
})

const crawlerLoading = ref(false)
const crawlerStats = reactive({
  currentBookId: '',
  savedFiles: 0,
  errors: 0
})

const storageConfig = reactive({
  jsonPath: 'book'
})

const storageLoading = ref(false)
const storageProgress = ref(0)

const consoleLogs = ref([])
const consoleRef = ref(null)

// Task tracking variables
let crawlerTaskId = null
let storageTaskId = null
let crawlerInterval = null
let storageInterval = null
let crawlerStopped = false

// API base URL
const API_BASE_URL = 'http://127.0.0.1:8000/api'

const formatTime = (date) => {
  const h = date.getHours().toString().padStart(2, '0')
  const m = date.getMinutes().toString().padStart(2, '0')
  const s = date.getSeconds().toString().padStart(2, '0')
  return `${h}:${m}:${s}`
}

const addConsoleLog = (content, type = 'normal') => {
  // 清理乱码和控制字符
  const cleanedContent = content.replace(/[\x00-\x1F\x7F]/g, '').trim()
  
  const time = formatTime(new Date())
  consoleLogs.value.push({ time, content: cleanedContent, type })
  
  // 解析成功日志，更新统计
  if (cleanedContent.includes('>> [完成]')) {
    const titleMatch = cleanedContent.match(/《([^》]+)》/)
    if (titleMatch) {
      const bookTitle = titleMatch[1]
      crawlerStats.savedFiles++
      addConsoleLog(`解析到书籍: ${bookTitle}`, 'success')
    }
  }
  
  // 强制滚动到底部
  nextTick(() => {
    if (consoleRef.value) {
      consoleRef.value.scrollTop = consoleRef.value.scrollHeight
    }
  })
}

const clearConsole = () => {
  consoleLogs.value = []
}

const stopCrawler = async () => {
  if (crawlerTaskId) {
    try {
      // Send request to stop the crawler task
      await axios.post(`${API_BASE_URL}/admin/crawler/stop/`, {
        task_id: crawlerTaskId
      }, {
        headers: {
          Authorization: 'Bearer ' + localStorage.getItem('admin_token')
        }
      })
    } catch (error) {
      addConsoleLog(`停止爬虫任务失败: ${error.message}`, 'error')
    }
  }
  
  crawlerStopped = true
  crawlerLoading.value = false
  
  if (crawlerInterval) {
    clearInterval(crawlerInterval)
    crawlerInterval = null
  }
  
  crawlerTaskId = null
  addConsoleLog('用户停止了爬虫任务', 'warning')
}

const pollCrawlerLogs = async () => {
  if (!crawlerTaskId) return
  
  try {
    const response = await axios.get(`${API_BASE_URL}/admin/crawler/logs/`, {
      params: { task_id: crawlerTaskId },
      headers: {
        Authorization: 'Bearer ' + localStorage.getItem('admin_token')
      }
    })
    
    if (response.data.code === 200) {
      const logs = response.data.data.logs
      const status = response.data.data.status
      
      // Process new logs
      if (logs && logs.length > 0) {
        // Only add new logs that haven't been added yet
        const existingLogContents = consoleLogs.value.map(log => log.content)
        logs.forEach(logContent => {
          if (!existingLogContents.includes(logContent)) {
            addConsoleLog(logContent, getLogType(logContent))
            
            // Update crawler stats based on log content
            if (logContent.includes('[完成]')) {
              crawlerStats.savedFiles++
            } else if (logContent.includes('[报错]')) {
              crawlerStats.errors++
            } else if (logContent.includes('处理 ID:')) {
              const match = logContent.match(/处理 ID: (\d+)/)
              if (match) {
                crawlerStats.currentBookId = match[1]
              }
            }
          }
        })
      }
      
      // Check if task is completed
      if (status === 'completed') {
        crawlerLoading.value = false
        crawlerTaskId = null
        if (crawlerInterval) {
          clearInterval(crawlerInterval)
          crawlerInterval = null
        }
        addConsoleLog('爬虫任务完成！', 'success')
      }
    }
  } catch (error) {
    addConsoleLog(`获取爬虫日志失败: ${error.message}`, 'error')
  }
}

const getLogType = (content) => {
  if (content.includes('[完成]')) return 'success'
  if (content.includes('[报错]')) return 'error'
  if (content.includes('停止')) return 'warning'
  if (content.includes('开始') || content.includes('=')) return 'info'
  return 'normal'
}

const startCrawler = async () => {
  crawlerLoading.value = true
  crawlerStopped = false
  crawlerStats.currentBookId = ''
  crawlerStats.savedFiles = 0
  crawlerStats.errors = 0

  addConsoleLog('='.repeat(50), 'info')
  addConsoleLog('开始启动飞卢爬虫...', 'success')
  addConsoleLog(`配置: 页码范围 ${crawlerConfig.startPage}-${crawlerConfig.endPage}, 延迟 ${crawlerConfig.delay}ms`, 'info')
  addConsoleLog('='.repeat(50), 'info')

  try {
    // Send request to start crawler
    const response = await axios.post(`${API_BASE_URL}/admin/crawler/start/`, {
      start_page: crawlerConfig.startPage,
      end_page: crawlerConfig.endPage,
      delay: crawlerConfig.delay
    }, {
      headers: {
        Authorization: 'Bearer ' + localStorage.getItem('admin_token')
      }
    })
    
    if (response.data.code === 200) {
      crawlerTaskId = response.data.data.task_id
      addConsoleLog(`爬虫任务已启动，任务ID: ${crawlerTaskId}`, 'info')
      
      // Start polling for logs
      crawlerInterval = setInterval(pollCrawlerLogs, 2000)
    } else {
      addConsoleLog(`启动爬虫失败: ${response.data.msg}`, 'error')
      crawlerLoading.value = false
    }
  } catch (error) {
    addConsoleLog(`启动爬虫任务异常: ${error.message}`, 'error')
    crawlerLoading.value = false
  }
}

const pollStorageLogs = async () => {
  if (!storageTaskId) return
  
  try {
    const response = await axios.get(`${API_BASE_URL}/admin/crawler/logs/`, {
      params: { task_id: storageTaskId },
      headers: {
        Authorization: 'Bearer ' + localStorage.getItem('admin_token')
      }
    })
    
    if (response.data.code === 200) {
      const logs = response.data.data.logs
      const status = response.data.data.status
      
      // Process new logs
      if (logs && logs.length > 0) {
        // Only add new logs that haven't been added yet
        const existingLogContents = consoleLogs.value.map(log => log.content)
        logs.forEach(logContent => {
          if (!existingLogContents.includes(logContent)) {
            addConsoleLog(logContent, getLogType(logContent))
            
            // Update storage progress based on log content
            const progressMatch = logContent.match(/成功导入: (\d+) 条/) || logContent.match(/完成 (\d+)/)
            if (progressMatch) {
              // Estimate progress based on log content
              const count = parseInt(progressMatch[1])
              storageProgress.value = Math.min(Math.floor((count / 100) * 100), 100)
            }
          }
        })
      }
      
      // Check if task is completed
      if (status === 'completed') {
        storageLoading.value = false
        storageTaskId = null
        storageProgress.value = 100
        if (storageInterval) {
          clearInterval(storageInterval)
          storageInterval = null
        }
        addConsoleLog('数据库同步完成！', 'success')
      }
    }
  } catch (error) {
    addConsoleLog(`获取存储日志失败: ${error.message}`, 'error')
  }
}

const syncToDatabase = async (mode) => {
  storageLoading.value = true
  storageProgress.value = 0

  addConsoleLog('='.repeat(50), 'info')
  addConsoleLog(`开始${mode === 'full' ? '清空并重新' : ''}同步到数据库...`, 'success')
  addConsoleLog(`JSON 路径: ${storageConfig.jsonPath}`, 'info')
  addConsoleLog('='.repeat(50), 'info')

  try {
    // Send request to start import
    const response = await axios.post(`${API_BASE_URL}/admin/crawler/import/`, {
      mode: mode,
      json_path: storageConfig.jsonPath
    }, {
      headers: {
        Authorization: 'Bearer ' + localStorage.getItem('admin_token')
      }
    })
    
    if (response.data.code === 200) {
      storageTaskId = response.data.data.task_id
      addConsoleLog(`导入任务已启动，任务ID: ${storageTaskId}`, 'info')
      
      // Start polling for logs
      storageInterval = setInterval(pollStorageLogs, 2000)
    } else {
      addConsoleLog(`启动导入失败: ${response.data.msg}`, 'error')
      storageLoading.value = false
    }
  } catch (error) {
    addConsoleLog(`启动导入任务异常: ${error.message}`, 'error')
    storageLoading.value = false
  }
}

const checkTaskStatus = async () => {
  try {
    // Send request to check if there are any running tasks
    const response = await axios.get(`${API_BASE_URL}/admin/check_status/`, {
      headers: {
        Authorization: 'Bearer ' + localStorage.getItem('admin_token')
      }
    })
    
    if (response.data.code === 200) {
      const data = response.data.data
      if (data.running_tasks) {
        data.running_tasks.forEach(task => {
          if (task.type === 'crawler') {
            crawlerTaskId = task.task_id
            crawlerLoading.value = true
            addConsoleLog(`发现正在运行的爬虫任务: ${task.task_id}`, 'info')
            crawlerInterval = setInterval(pollCrawlerLogs, 2000)
          } else if (task.type === 'import') {
            storageTaskId = task.task_id
            storageLoading.value = true
            addConsoleLog(`发现正在运行的导入任务: ${task.task_id}`, 'info')
            storageInterval = setInterval(pollStorageLogs, 2000)
          }
        })
      }
    }
  } catch (error) {
    addConsoleLog(`检查任务状态失败: ${error.message}`, 'error')
  }
}

// Lifecycle hooks
onMounted(() => {
  // Check for running tasks on mount
  checkTaskStatus()
})

onUnmounted(() => {
  // Clean up intervals
  if (crawlerInterval) {
    clearInterval(crawlerInterval)
  }
  if (storageInterval) {
    clearInterval(storageInterval)
  }
})
</script>

<style scoped>
.data-control-center {
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

.data-center-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.control-panel {
  background: #ffffff;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
}

.control-panel h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
  color: #000000;
  letter-spacing: -0.01em;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
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
  background: #f8f9fa;
  transition: all 0.3s ease;
  outline: none;
}

.form-group input:focus {
  border-color: #000000;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05);
}

.control-actions {
  display: flex;
  gap: 12px;
  margin: 20px 0;
}

.crawler-btn {
  background: #28a745;
  color: #ffffff;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: -0.01em;
}

.crawler-btn:hover:not(:disabled) {
  background: #218838;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
}

.crawler-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.stop-btn {
  background: #dc3545;
  color: #ffffff;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: -0.01em;
}

.stop-btn:hover:not(:disabled) {
  background: #c82333;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.stop-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.storage-btn {
  background: #007bff;
  color: #ffffff;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: -0.01em;
}

.storage-btn:hover:not(:disabled) {
  background: #0069d9;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.storage-btn.danger {
  background: #dc3545;
}

.storage-btn.danger:hover:not(:disabled) {
  background: #c82333;
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
}

.storage-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.crawler-stats {
  display: flex;
  gap: 24px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-item .stat-label {
  font-size: 14px;
  color: #666666;
  font-weight: 500;
}

.stat-item .stat-value {
  font-size: 14px;
  color: #000000;
  font-weight: 600;
}

.stat-item .stat-value.error {
  color: #dc3545;
}

.progress-container {
  margin-top: 20px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #666666;
  font-weight: 500;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #007bff;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.console-area {
  background: #000000;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  height: 400px;
  display: flex;
  flex-direction: column;
}

.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #1a1a1a;
  border-bottom: 1px solid #333333;
}

.console-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #00ff00;
  letter-spacing: -0.01em;
  font-family: Consolas, Monaco, 'Courier New', monospace;
}

.clear-btn {
  background: #1a1a1a;
  color: #00ff00;
  border: 1px solid #00ff00;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: Consolas, Monaco, 'Courier New', monospace;
}

.clear-btn:hover {
  background: #00ff00;
  color: #000000;
}

.console-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  background: #000000;
}

.console-empty {
  color: #666666;
  font-style: italic;
  font-family: Consolas, Monaco, 'Courier New', monospace;
}

.console-log {
  margin-bottom: 6px;
  display: flex;
  gap: 12px;
}

.log-time {
  color: #00ff00;
  font-weight: 500;
  min-width: 80px;
  font-family: Consolas, Monaco, 'Courier New', monospace;
}

.log-content {
  color: #00ff00;
  flex: 1;
  word-break: break-all;
  font-family: Consolas, Monaco, 'Courier New', monospace;
}

.log-content.success {
  color: #00ff00;
}

.log-content.error {
  color: #ff0000;
}

.log-content.warning {
  color: #ffff00;
}

.log-content.info {
  color: #00ffff;
}

/* 深色模式 */
.dark-mode .content-header h2 {
  color: #ffffff;
}

.dark-mode .control-panel {
  background: #2d2d2d;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}

.dark-mode .control-panel h3 {
  color: #ffffff;
}

.dark-mode .form-group input {
  background: #3d3d3d;
  border: 1px solid #4d4d4d;
  color: #ffffff;
}

.dark-mode .form-group input:focus {
  border-color: #ffffff;
  background: #4d4d4d;
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.dark-mode .crawler-btn {
  background: #28a745;
}

.dark-mode .crawler-btn:hover:not(:disabled) {
  background: #218838;
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4);
}

.dark-mode .stop-btn {
  background: #dc3545;
}

.dark-mode .stop-btn:hover:not(:disabled) {
  background: #c82333;
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.4);
}

.dark-mode .storage-btn {
  background: #007bff;
}

.dark-mode .storage-btn:hover:not(:disabled) {
  background: #0069d9;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.4);
}

.dark-mode .storage-btn.danger {
  background: #dc3545;
}

.dark-mode .storage-btn.danger:hover:not(:disabled) {
  background: #c82333;
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.4);
}

.dark-mode .crawler-stats {
  border-top-color: #3d3d3d;
}

.dark-mode .stat-item .stat-label {
  color: #888888;
}

.dark-mode .stat-item .stat-value {
  color: #ffffff;
}

.dark-mode .stat-item .stat-value.error {
  color: #ff6b6b;
}

.dark-mode .progress-bar {
  background: #3d3d3d;
}

.dark-mode .progress-fill {
  background: #007bff;
}

.dark-mode .console-area {
  background: #1e1e1e;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
}

.dark-mode .console-header {
  background: #2d2d2d;
  border-bottom-color: #3d3d3d;
}

.dark-mode .clear-btn {
  background: #3d3d3d;
  color: #ffffff;
}

.dark-mode .clear-btn:hover {
  background: #4d4d4d;
}

.dark-mode .console-content {
  background: #1e1e1e;
}

.dark-mode .console-empty {
  color: #666666;
}
</style>
