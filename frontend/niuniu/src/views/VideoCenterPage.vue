<template>
  <div class="page-root">
    <!-- 顶部导航 -->
    <header class="app-header">
      <div class="header-inner">
        <div class="logo" @click="goHome">
          <span class="logo-icon">📺</span>
          <span class="logo-text">量化牛牛视频</span>
        </div>
        <div class="header-right">
          <button v-if="isAdmin" class="opt-btn" @click="toggleUploadPanel" :class="{ active: isUploadPanelOpen }">
            {{ isUploadPanelOpen ? '收起上传' : '上传视频' }}
          </button>
          
          <div class="user-menu-wrapper" @mouseenter="onMenuEnter" @mouseleave="onMenuLeave">
            <div class="user-trigger" @click="toggleUserMenu" tabindex="0" @keydown.enter="toggleUserMenu">
              <span class="avatar-placeholder">{{ userText.charAt(0).toUpperCase() }}</span>
              <span class="user-name">{{ userText }}</span>
            </div>
            <transition name="fade">
              <div class="user-dropdown" v-show="showUserMenu && logged">
                <div class="dropdown-item" @click="goToUserProfile">个人主页</div>
                <div class="dropdown-item logout" @click="handleLogout">退出登录</div>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </header>

    <div class="main-container">
      <!-- 顶部可折叠上传区 (管理员) -->
      <transition name="slide-down">
        <div v-if="isAdmin && isUploadPanelOpen" class="admin-upload-section">
          <div class="upload-panel card">
            <div class="panel-header">
              <h3>上传新内容</h3>
            </div>
            <div class="upload-form">
              <div class="form-group">
                <input v-model="uploadTitle" type="text" class="input-clean" placeholder="请输入视频标题 (必填)" />
              </div>
              <div class="form-group">
                <textarea v-model="uploadDescription" class="input-clean area" placeholder="视频简介 (可选)"></textarea>
              </div>
              <div class="form-row">
                <div class="file-input-wrapper">
                  <span class="label">视频文件 (MP4/WebM)</span>
                  <input type="file" accept="video/mp4,video/webm" @change="onVideoFileChange" />
                </div>
                <div class="file-input-wrapper">
                  <span class="label">封面图片 (可选)</span>
                  <input type="file" accept="image/png,image/jpeg,image/webp" @change="onCoverFileChange" />
                </div>
              </div>
              <div class="form-actions">
                <button class="btn btn-primary" :disabled="uploading" @click="handleUpload">
                  {{ uploading ? '上传中...' : '确认发布' }}
                </button>
                <span v-if="uploadError" class="status-text error">{{ uploadError }}</span>
                <span v-if="uploadSuccess" class="status-text success">上传成功!</span>
              </div>
            </div>
          </div>
        </div>
      </transition>
      
      <!-- 主要内容区：播放器 + 列表 -->
      <div class="cinema-layout">
        <!-- 左侧/主体：播放器 -->
        <main class="player-stage">
          <div class="player-wrapper card">
            <div class="video-container">
              <video 
                v-if="activeVideo" 
                :src="activeVideo.url" 
                controls 
                autoplay
                playsinline
                class="main-video"
                :poster="activeVideo.cover_url"
              ></video>
              <div v-else class="empty-player">
                <div class="empty-content">
                  <div class="icon">🎬</div>
                  <p>请在右侧选择视频播放</p>
                </div>
              </div>
            </div>
            
            <div class="video-details" v-if="activeVideo">
              <h1 class="current-title">{{ activeVideo.title }}</h1>
              <div class="current-meta">
                <span class="time">{{ formatDate(activeVideo.updated_at) }}</span>
              </div>
              <div class="current-desc" v-if="activeVideo.description">
                {{ activeVideo.description }}
              </div>
            </div>
             <div class="video-details placeholder" v-else>
               <h1 class="current-title">欢迎来到视频中心</h1>
               <div class="current-desc">这里汇聚了最前沿的量化投资课程与实战解析。</div>
            </div>
          </div>
        </main>

        <!-- 右侧/侧栏：播放列表 -->
        <aside class="playlist-sidebar">
          <div class="sidebar-header">
            <h2>播放列表 ({{ videos.length }})</h2>
          </div>
          
          <div class="playlist-scroll">
            <div v-if="loading" class="sys-msg">加载中...</div>
            <div v-else-if="error" class="sys-msg error">{{ error }}</div>
            <div v-else-if="videos.length === 0" class="sys-msg">暂无视频</div>
            
            <div 
              v-for="item in videos" 
              :key="item.id" 
              class="video-item"
              :class="{ active: activeVideo && activeVideo.id === item.id }"
              @click="selectVideo(item)"
              tabindex="0"
              @keydown.enter="selectVideo(item)"
            >
              <div class="thumb-box">
                <img v-if="item.cover_url" :src="item.cover_url" loading="lazy" />
                <div v-else class="no-thumb">VIDEO</div>
              </div>
              <div class="info-box">
                <div class="item-title" :title="item.title">{{ item.title }}</div>
                <div class="item-meta">{{ formatDate(item.updated_at).split(' ')[0] }}</div>
              </div>
              <button 
                v-if="isAdmin" 
                class="item-delete-btn" 
                @click.stop="confirmDelete(item)" 
                title="删除视频"
              >×</button>
            </div>
          </div>
        </aside>
      </div>
    </div>

    <footer class="app-footer">
      <div class="footer-content">
        <p>量化牛牛视频中心 © 2025</p>
        <p class="risk-tip">风险提示：投资有风险，入市需谨慎</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { getVideos, uploadVideo, deleteVideo } from '@/services/videoService'

const { logged, userText, isAdmin, openLoginModal, logout } = useAuth()
const router = useRouter()

const showUserMenu = ref(false)
const isUploadPanelOpen = ref(false)

const videos = ref([])
const loading = ref(false)
const error = ref('')
const activeVideo = ref(null)

const uploadTitle = ref('')
const uploadDescription = ref('')
const uploadFile = ref(null)
const uploadCover = ref(null)
const uploading = ref(false)
const uploadError = ref('')
const uploadSuccess = ref(false)

function goHome() {
  router.push('/')
}

function goToUserProfile() {
  showUserMenu.value = false
  router.push('/profile')
}

function toggleUserMenu() {
  if (!logged.value) {
    openLoginModal()
    showUserMenu.value = false
  } else {
    showUserMenu.value = !showUserMenu.value
  }
}

function toggleUploadPanel() {
  isUploadPanelOpen.value = !isUploadPanelOpen.value
}

function onMenuEnter() {
  if (!logged.value) return
  showUserMenu.value = true
}

function onMenuLeave() {
  setTimeout(() => {
    showUserMenu.value = false
  }, 300)
}

function handleLogout() {
  logout()
  showUserMenu.value = false
}

function formatDate(value) {
  if (!value) return ''
  const normalized = String(value).replace('T', ' ').replace('Z', '').trim()
  return normalized.slice(0, 16)
}

async function loadVideos() {
  loading.value = true
  error.value = ''
  try {
    const response = await getVideos()
    const payload = response?.data || response
    /* 假设返回格式 { items: [] } 或直接 [] */
    videos.value = payload?.items || (Array.isArray(payload) ? payload : []) || []
    
    // 如果有视频且未选，可选不自动播放，或者自动选中第一个
    // 这里保持“不选中”的空态，等待用户点击
  } catch (err) {
    error.value = err?.message || '加载失败'
  } finally {
    loading.value = false
  }
}

function selectVideo(item) {
  if (!logged.value) {
    openLoginModal()
    return
  }
  activeVideo.value = item
  // 滚动到顶部 (移动端优化)
  if (window.innerWidth < 900) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function onVideoFileChange(event) {
  uploadFile.value = event.target.files?.[0] || null
}

function onCoverFileChange(event) {
  uploadCover.value = event.target.files?.[0] || null
}

async function handleUpload() {
  if (!uploadTitle.value.trim()) {
    uploadError.value = '请输入标题'
    return
  }
  if (!uploadFile.value) {
    uploadError.value = '请选择视频文件'
    return
  }
  uploadError.value = ''
  uploadSuccess.value = false
  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('title', uploadTitle.value.trim())
    if (uploadDescription.value.trim()) {
      formData.append('description', uploadDescription.value.trim())
    }
    formData.append('file', uploadFile.value)
    if (uploadCover.value) {
      formData.append('cover', uploadCover.value)
    }

    await uploadVideo(formData)
    uploadSuccess.value = true
    uploadTitle.value = ''
    uploadDescription.value = ''
    uploadFile.value = null
    uploadCover.value = null
    // 不要自动关闭，让用户看到成功提示
    await loadVideos()
  } catch (err) {
    uploadError.value = err?.message || '上传失败'
  } finally {
    uploading.value = false
  }
}

async function confirmDelete(item) {
  if (!confirm(`确认删除「${item.title}」？`)) return
  try {
    await deleteVideo(item.id)
    if (activeVideo.value && activeVideo.value.id === item.id) {
      activeVideo.value = null
    }
    await loadVideos()
  } catch (err) {
    alert(err?.message || '删除失败')
  }
}

onMounted(() => {
  loadVideos()
})
</script>

<style scoped>
:root {
  --primary: #ff7f24;
  --primary-hover: #e06917;
  --bg-page: #f4f5f7;
  --bg-card: #ffffff;
  --text-main: #18191c;
  --text-sub: #9499a0;
  --border: #e3e5e7;
  --divider: #f1f2f3;
  --shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.page-root {
  min-height: 100vh;
  background-color: var(--bg-page, #f4f5f7);
  color: var(--text-main, #333);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  display: flex;
  flex-direction: column;
}

/* Header */
.app-header {
  background: #fff;
  height: 60px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  height: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 700;
  color: #333;
  cursor: pointer;
}
.logo-icon { font-size: 24px; }

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.opt-btn {
  background: none;
  border: 1px solid var(--primary, #ff7f24);
  color: var(--primary, #ff7f24);
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}
.opt-btn:hover, .opt-btn.active {
  background: var(--primary, #ff7f24);
  color: white;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}
.user-trigger:hover { background-color: #f1f2f3; }
.avatar-placeholder {
  width: 32px;
  height: 32px;
  background: #ff7f24;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}
.user-name { font-size: 14px; font-weight: 500; }

.user-menu-wrapper { position: relative; }
.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: white;
  min-width: 140px;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  padding: 8px 0;
  border: 1px solid #eee;
}
.dropdown-item {
  padding: 10px 16px;
  font-size: 14px;
  cursor: pointer;
  color: #333;
}
.dropdown-item:hover { background-color: #f6f7f8; }
.dropdown-item.logout { color: #ff4d4f; border-top: 1px solid #eee; margin-top: 4px; }

/* Main layout */
.main-container {
  flex: 1;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Upload Panel */
.admin-upload-section { margin-bottom: 10px; }
.upload-panel { padding: 20px; border-radius: 12px; background: white; border: 1px solid var(--border, #e3e5e7); }
.panel-header h3 { font-size: 16px; margin-bottom: 16px; color: #333; }
.upload-form { display: grid; gap: 16px; }
.input-clean {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border 0.2s;
}
.input-clean:focus { border-color: var(--primary, #ff7f24); outline: none; }
.form-row { display: flex; gap: 20px; flex-wrap: wrap; }
.file-input-wrapper { display: flex; flex-direction: column; gap: 4px; font-size: 13px; color: #666; }
.form-actions { display: flex; align-items: center; gap: 16px; margin-top: 10px; }
.btn { border: none; padding: 8px 20px; border-radius: 6px; font-size: 14px; cursor: pointer; transition: opacity 0.2s; }
.btn-primary { background: var(--primary, #ff7f24); color: white; }
.btn-primary:active { opacity: 0.8; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.status-text { font-size: 13px; }
.status-text.error { color: #ff4d4f; }
.status-text.success { color: #52c41a; }

/* Cinema Layout - GRID */
.cinema-layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 24px;
  align-items: start;
}

/* Player Stage */
.player-stage { min-width: 0; } /* Fix grid overflow */
.card { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.video-container {
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #000;
  border-radius: 8px 8px 0 0;
  overflow: hidden;
  position: relative;
}
.main-video { width: 100%; height: 100%; object-fit: contain; }

.empty-player {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  color: #fff; background: #1f2329;
}
.empty-content { text-align: center; opacity: 0.6; }
.empty-content .icon { font-size: 48px; margin-bottom: 12px; }

.video-details { padding: 20px; }
.current-title { font-size: 20px; font-weight: 600; line-height: 1.4; margin-bottom: 12px; }
.current-meta { color: #9499a0; font-size: 13px; margin-bottom: 16px; display: flex; gap: 16px; }
.current-desc { font-size: 14px; line-height: 1.6; color: #61666d; white-space: pre-wrap; }
.video-details.placeholder { border-radius: 0 0 8px 8px; }

/* Playlist Sidebar */
.playlist-sidebar {
  background: white;
  border-radius: 8px;
  height: calc(100vh - 140px);
  position: sticky;
  top: 80px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.sidebar-header { padding: 16px; border-bottom: 1px solid #f1f2f3; font-size: 15px; font-weight: 600; }
.playlist-scroll { flex: 1; overflow-y: auto; padding: 8px; }

.video-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}
.video-item:hover { background: #f1f2f3; }
.video-item.active { background: #fff3e8; }
.video-item.active .item-title { color: var(--primary, #ff7f24); }

.thumb-box {
  width: 120px;
  height: 68px;
  flex-shrink: 0;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}
.thumb-box img { width: 100%; height: 100%; object-fit: cover; }
.no-thumb {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; color: #999;
}

.info-box { flex: 1; min-width: 0; display: flex; flex-direction: column; justify-content: space-between; }
.item-title {
  font-size: 14px;
  font-weight: 500;
  line-height: 1.3;
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.item-meta { font-size: 12px; color: #9499a0; }

.item-delete-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(0,0,0,0.3);
  color: white;
  border: none;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s;
}
.item-delete-btn:hover { background: #ff4d4f; }
.video-item:hover .item-delete-btn { opacity: 1; }

.sys-msg { padding: 40px; text-align: center; color: #999; font-size: 13px; }
.sys-msg.error { color: #ff4d4f; }

/* Footer */
.app-footer { margin-top: auto; padding: 30px 20px; text-align: center; color: #999; font-size: 12px; border-top: 1px solid #eaeaea; background: #fff; }
.risk-tip { margin-top: 8px; color: #ccc; }

/* Animations */
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.3s ease-out; max-height: 500px; opacity: 1; overflow: hidden; }
.slide-down-enter-from, .slide-down-leave-to { max-height: 0; opacity: 0; margin-bottom: 0; padding-top: 0; padding-bottom: 0; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* Responsive */
@media (max-width: 900px) {
  .cinema-layout { grid-template-columns: 1fr; }
  .playlist-sidebar { height: auto; position: static; max-height: 500px; }
}
</style>
