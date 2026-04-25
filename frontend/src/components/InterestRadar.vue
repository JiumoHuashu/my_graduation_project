<template>
  <div class="interest-radar-modal" v-if="visible">
    <div class="modal-content">
      <h2>兴趣雷达</h2>
      <p class="subtitle">选择3-5个你感兴趣的标签，我们将为你推荐相关小说</p>
      
      <div class="tags-container">
        <div 
          v-for="tag in tags" 
          :key="tag"
          class="tag-item"
          :class="{ active: selectedTags.includes(tag) }"
          @click="toggleTag(tag)"
        >
          {{ tag }}
        </div>
      </div>
      
      <div class="selected-info">
        <span>已选择 {{ selectedTags.length }} 个标签</span>
        <span class="hint">(需要选择3-5个)</span>
      </div>
      
      <div class="button-group">
        <button 
          class="confirm-btn"
          :disabled="selectedTags.length < 3 || selectedTags.length > 5"
          @click="confirmSelection"
        >
          开始探索
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'InterestRadar',
  props: {
    visible: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      tags: [
        '玄幻', '奇幻', '武侠', '仙侠', '都市',
        '言情', '历史', '科幻', '悬疑', '推理',
        '恐怖', '军事', '游戏', '体育', '二次元'
      ],
      selectedTags: []
    }
  },
  methods: {
    toggleTag(tag) {
      const index = this.selectedTags.indexOf(tag)
      if (index > -1) {
        this.selectedTags.splice(index, 1)
      } else {
        if (this.selectedTags.length < 5) {
          this.selectedTags.push(tag)
        }
      }
    },
    confirmSelection() {
      if (this.selectedTags.length >= 3 && this.selectedTags.length <= 5) {
        this.$emit('confirm', this.selectedTags)
      }
    }
  }
}
</script>

<style scoped>
.interest-radar-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  border-radius: 16px;
  padding: 40px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

h2 {
  font-size: 28px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 16px;
  color: #333;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 32px;
  font-size: 16px;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 24px;
}

.tag-item {
  padding: 12px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
}

.tag-item:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.tag-item.active {
  background-color: #1890ff;
  color: #fff;
  border-color: #1890ff;
}

.selected-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  font-size: 14px;
  color: #666;
}

.hint {
  font-size: 12px;
  color: #999;
}

.button-group {
  display: flex;
  justify-content: center;
}

.confirm-btn {
  padding: 14px 48px;
  background-color: #1890ff;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.confirm-btn:hover:not(:disabled) {
  background-color: #40a9ff;
}

.confirm-btn:disabled {
  background-color: #e0e0e0;
  cursor: not-allowed;
  color: #999;
}

@media (max-width: 768px) {
  .modal-content {
    padding: 30px;
    width: 95%;
  }
  
  h2 {
    font-size: 24px;
  }
  
  .tag-item {
    padding: 10px 16px;
    font-size: 13px;
  }
  
  .confirm-btn {
    padding: 12px 40px;
    font-size: 15px;
  }
}
</style>