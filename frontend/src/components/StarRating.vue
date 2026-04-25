<template>
  <div class="star-rating">
    <div
      class="stars-container"
      @mouseleave="handleMouseLeave"
    >
      <div
        v-for="index in starCount"
        :key="index"
        class="star-box"
        @mousemove="handleMouseMove($event, index)"
        @click="handleStarClick($event, index)"
      >
        <span class="star-icon empty">★</span>
        <span
          class="star-icon filled"
          :style="{ width: getFillWidth(index) + '%' }"
        >★</span>
      </div>
    </div>
    <div class="rating-label">{{ displayRating }} 分</div>
  </div>
</template>

<script>
export default {
  name: 'HalfStarRating',
  props: {
    rating: { type: Number, default: 0 },
    maxRating: { type: Number, default: 10 },
    starCount: { type: Number, default: 5 },
    readOnly: { type: Boolean, default: false }
  },
  data() {
    return {
      currentRating: this.rating,
      hoverRating: 0
    }
  },
  computed: {
    displayRating() {
      return this.hoverRating > 0 ? this.hoverRating : this.currentRating
    }
  },
  watch: {
    rating(val) {
      this.currentRating = val
    }
  },
  methods: {
    getFillWidth(index) {
      const ratingPerStar = this.maxRating / this.starCount
      const activeRating = this.displayRating

      const currentStarThreshold = (index - 1) * ratingPerStar
      const diff = activeRating - currentStarThreshold

      if (diff >= ratingPerStar) return 100
      if (diff >= ratingPerStar / 2) return 50
      return 0
    },

    calculateRating(event, index) {
      const rect = event.currentTarget.getBoundingClientRect()
      const x = event.clientX - rect.left
      const halfWidth = rect.width / 2

      const ratingPerStar = this.maxRating / this.starCount

      const starValue = x < halfWidth ? ratingPerStar / 2 : ratingPerStar
      return (index - 1) * ratingPerStar + starValue
    },

    handleMouseMove(event, index) {
      if (this.readOnly) return
      this.hoverRating = this.calculateRating(event, index)
    },

    handleStarClick(event, index) {
      if (this.readOnly) return
      this.currentRating = this.calculateRating(event, index)
      this.$emit('update:rating', this.currentRating)
    },

    handleMouseLeave() {
      if (this.readOnly) return
      this.hoverRating = 0
    }
  }
}
</script>

<style scoped>
.star-rating {
  display: flex;
  align-items: center;
  gap: 12px;
  user-select: none;
}

.stars-container {
  display: flex;
}

.star-box {
  position: relative;
  width: 30px;
  height: 30px;
  font-size: 30px;
  line-height: 1;
  cursor: pointer;
}

.star-icon {
  position: absolute;
  top: 0;
  left: 0;
  overflow: hidden;
  white-space: nowrap;
  transition: none;
}

.star-icon.empty {
  color: #ccc;
}

.star-icon.filled {
  color: #ffca28;
  z-index: 1;
}

.rating-label {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  min-width: 50px;
}

.dark-mode .rating-label {
  color: #e0e0e0;
}
</style>