<template>
  <div class="simple-line-chart">
    <div class="chart-title">净值曲线</div>
    <div v-if="data && data.length > 0" class="chart-wrapper" ref="wrapperRef">
      <svg :viewBox="`0 0 ${width} ${height}`" preserveAspectRatio="none">
        <!-- Grid lines (horizontal) -->
        <g class="grid">
          <line 
            v-for="i in 5" 
            :key="i"
            :x1="0" 
            :y1="(height / 4) * (i - 1)" 
            :x2="width" 
            :y2="(height / 4) * (i - 1)" 
            stroke="#eee" 
            stroke-width="1"
          />
        </g>
        
        <!-- The Line -->
        <polyline
          :points="points"
          fill="none"
          stroke="#ff7f00"
          stroke-width="2"
          vector-effect="non-scaling-stroke"
        />
      </svg>
      
      <!-- Y Axis Labels -->
      <div class="y-axis-labels">
        <div class="y-label max">{{ maxNav.toFixed(3) }}</div>
        <div class="y-label min">{{ minNav.toFixed(3) }}</div>
      </div>

      <!-- X Axis Labels (First and Last date) -->
      <div class="x-axis-labels">
        <div class="x-label start">{{ data[0].date }}</div>
        <div class="x-label end">{{ data[data.length - 1].date }}</div>
      </div>
    </div>
    <div v-else class="no-data">
      暂无数据
    </div>
  </div>
</template>

<script setup>
import { computed, toRefs } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  },
  width: {
    type: Number,
    default: 800
  },
  height: {
    type: Number,
    default: 200
  }
})

const { data, width, height } = toRefs(props)

// 计算最大最小值
const maxNav = computed(() => {
  if (!data.value.length) return 0
  return Math.max(...data.value.map(item => item.nav))
})

const minNav = computed(() => {
  if (!data.value.length) return 0
  return Math.min(...data.value.map(item => item.nav))
})

// 生成 SVG points 字符串
const points = computed(() => {
  if (!data.value.length) return ''
  
  const count = data.value.length
  const yRange = maxNav.value - minNav.value || 1 // Avoid division by zero
  const paddingY = height.value * 0.1 // 10% padding vertically
  const effectiveHeight = height.value - 2 * paddingY
  
  return data.value.map((item, index) => {
    // X coordinate: distributed evenly
    const x = (index / (count - 1)) * width.value
    
    // Y coordinate: normalized to height (inverted because SVG Y grows downwards)
    // val - min  / range
    const normalizedY = (item.nav - minNav.value) / yRange
    const y = height.value - (paddingY + normalizedY * effectiveHeight)
    
    return `${x},${y}`
  }).join(' ')
})
</script>

<style scoped>
.simple-line-chart {
  width: 100%;
  border: 1px solid #eee;
  padding: 15px;
  background: white;
  border-radius: 8px;
  box-sizing: border-box;
}

.chart-title {
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.chart-wrapper {
  position: relative;
  width: 100%;
  height: 200px; /* Should match height prop default relative logic usually, but fixed is easier for CSS */
}

svg {
  width: 100%;
  height: 100%;
  overflow: visible;
}

.y-axis-labels {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  pointer-events: none;
}

.y-label {
  position: absolute;
  font-size: 10px;
  color: #666;
  background: rgba(255,255,255,0.7);
  padding: 0 2px;
}

.y-label.max {
  top: 0;
  left: 5px;
}

.y-label.min {
  bottom: 0;
  left: 5px;
}

.x-axis-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 5px;
  font-size: 10px;
  color: #666;
}

.no-data {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}
</style>
