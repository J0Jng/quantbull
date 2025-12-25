import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useReportStore = defineStore('report', () => {
  // 收藏的研报ID列表
  const favorites = ref([])

  // 检查某个研报是否已收藏
  const isFavorite = (reportId) => {
    return favorites.value.includes(reportId)
  }

  // 添加收藏
  const addFavorite = (reportId) => {
    if (!favorites.value.includes(reportId)) {
      favorites.value.push(reportId)
      // 这里可以添加本地存储逻辑
      saveToLocalStorage()
    }
  }

  // 移除收藏
  const removeFavorite = (reportId) => {
    const index = favorites.value.indexOf(reportId)
    if (index > -1) {
      favorites.value.splice(index, 1)
      // 这里可以添加本地存储逻辑
      saveToLocalStorage()
    }
  }

  // 获取所有收藏的研报ID
  const getFavorites = computed(() => favorites.value)

  // 保存到本地存储（可选）
  const saveToLocalStorage = () => {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('reportFavorites', JSON.stringify(favorites.value))
    }
  }

  // 从本地存储加载（可选）
  const loadFromLocalStorage = () => {
    if (typeof localStorage !== 'undefined') {
      const saved = localStorage.getItem('reportFavorites')
      if (saved) {
        favorites.value = JSON.parse(saved)
      }
    }
  }

  // 初始化时从本地存储加载
  loadFromLocalStorage()

  return {
    favorites,
    isFavorite,
    addFavorite,
    removeFavorite,
    getFavorites
  }
})