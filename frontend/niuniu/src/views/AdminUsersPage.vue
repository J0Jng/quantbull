<template>
  <div class="admin-users-page">
    <!-- 头部 -->
    <div class="header">
      <div class="logo" @click="goHome">用户管理</div>
      <div class="header-opt">
        <a href="#" @click.prevent="goProfile">个人主页</a>
        <div class="user-menu-container">
          <div class="user-btn">管理员</div>
        </div>
      </div>
    </div>

    <!-- 主体内容 -->
    <div class="content-container">
      <div class="content-card">
        <div class="card-header">
          <h1 class="page-title">管理员用户管理</h1>
          <div class="header-actions">
            <div class="search-box">
              <input
                v-model.trim="searchKeyword"
                type="text"
                placeholder="搜索用户名"
                class="search-input"
              />
              <button class="action-btn secondary" @click="clearSearch" :disabled="!searchKeyword">
                清除
              </button>
            </div>
            <button class="action-btn secondary" @click="fetchUsers" :disabled="loading">
              {{ loading ? '刷新中...' : '刷新列表' }}
            </button>
          </div>
        </div>

        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载用户中...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <p>{{ error }}</p>
          <button class="action-btn secondary" @click="fetchUsers">重试</button>
        </div>

        <div v-else class="table-wrapper">
          <table class="user-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>角色</th>
                <th>AI Token 余额</th>
                <th>注册时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.role }}</td>
                <td>
                  <input
                    class="token-input"
                    type="number"
                    min="0"
                    v-model.number="editTokens[user.id]"
                  />
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>
                  <button
                    class="action-btn secondary"
                    @click="viewUser(user.id)"
                    :disabled="savingIds.has(user.id)"
                  >
                    详情
                  </button>
                  <button
                    class="action-btn primary"
                    @click="saveTokens(user.id)"
                    :disabled="savingIds.has(user.id)"
                  >
                    {{ savingIds.has(user.id) ? '保存中...' : '保存' }}
                  </button>
                  <button
                    class="action-btn danger"
                    @click="removeUser(user.id)"
                    :disabled="savingIds.has(user.id)"
                  >
                    删除
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <div v-if="users.length === 0" class="empty-state">
            暂无用户数据
          </div>
          <div v-else-if="filteredUsers.length === 0" class="empty-state">
            未找到匹配用户名
          </div>
        </div>

        <div class="pagination">
          <button class="page-btn" @click="prevPage" :disabled="offset === 0">上一页</button>
          <span class="page-info">当前偏移：{{ offset }}</span>
          <button class="page-btn" @click="nextPage" :disabled="users.length < limit">下一页</button>
        </div>
      </div>
    </div>

    <FooterComponent />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import FooterComponent from '@/components/FooterComponent.vue'
import { listUsers, updateUserAiTokens, getUser, updateUser, deleteUser } from '@/services/adminService'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { initAuth, isAdmin } = useAuth()

const users = ref([])
const loading = ref(false)
const error = ref('')
const limit = ref(100)
const offset = ref(0)
const editTokens = ref({})
const savingIds = ref(new Set())
const searchKeyword = ref('')

const filteredUsers = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  if (!keyword) return users.value
  return users.value.filter((user) => String(user.username || '').toLowerCase().includes(keyword))
})

onMounted(async () => {
  await initAuth()
  if (!isAdmin.value) {
    alert('无权限访问该页面')
    router.push('/profile')
    return
  }
  fetchUsers()
})

function goHome() {
  router.push('/')
}

function goProfile() {
  router.push('/profile')
}

function formatDate(value) {
  if (!value) return '--'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

async function fetchUsers() {
  loading.value = true
  error.value = ''
  try {
    const result = await listUsers({ limit: limit.value, offset: offset.value })
    if (result.success) {
      const data = result.data?.data || result.data || []
      users.value = Array.isArray(data) ? data : []
      const newEditTokens = {}
      users.value.forEach((user) => {
        newEditTokens[user.id] = user.ai_tokens
      })
      editTokens.value = newEditTokens
    } else {
      error.value = result.message || '加载失败'
    }
  } catch (err) {
    error.value = err.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function saveTokens(userId) {
  if (!isAdmin.value) {
    alert('无权限操作')
    return
  }
  const aiTokens = editTokens.value[userId]
  if (aiTokens === null || aiTokens === undefined || Number.isNaN(aiTokens)) {
    alert('请输入有效的 AI Token 余额')
    return
  }
  if (aiTokens < 0) {
    alert('AI Token 余额不能为负数')
    return
  }

  savingIds.value.add(userId)
  try {
    const result = await updateUserAiTokens(userId, aiTokens)
    if (result.success) {
      await fetchUsers()
    } else {
      alert(result.message || '保存失败')
    }
  } catch (err) {
    alert(err.message || '保存失败')
  } finally {
    savingIds.value.delete(userId)
  }
}

async function viewUser(userId) {
  if (!isAdmin.value) {
    alert('无权限操作')
    return
  }
  savingIds.value.add(userId)
  try {
    const result = await getUser(userId)
    if (result.success) {
      const data = result.data?.data || result.data || null
      if (data) {
        alert(`ID: ${data.id}\n用户名: ${data.username}\n角色: ${data.role}\nAI Token: ${data.ai_tokens}\n注册时间: ${formatDate(data.created_at)}`)
      }
    } else {
      alert(result.message || '获取失败')
    }
  } catch (err) {
    alert(err.message || '获取失败')
  } finally {
    savingIds.value.delete(userId)
  }
}

async function removeUser(userId) {
  if (!isAdmin.value) {
    alert('无权限操作')
    return
  }
  if (!confirm('确定要删除该用户吗？此操作不可恢复。')) {
    return
  }
  savingIds.value.add(userId)
  try {
    const result = await deleteUser(userId)
    if (result.success) {
      await fetchUsers()
    } else {
      alert(result.message || '删除失败')
    }
  } catch (err) {
    alert(err.message || '删除失败')
  } finally {
    savingIds.value.delete(userId)
  }
}

function prevPage() {
  if (offset.value === 0) return
  offset.value = Math.max(0, offset.value - limit.value)
  fetchUsers()
}

function nextPage() {
  if (users.value.length < limit.value) return
  offset.value += limit.value
  fetchUsers()
}

function clearSearch() {
  searchKeyword.value = ''
}
</script>

<style scoped>
.admin-users-page {
  min-height: 100vh;
  background-color: #fff8f0;
}

.header {
  background-color: #ff7f24;
  padding: 12px 20px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 99;
}

.logo {
  font-size: 22px;
  font-weight: bold;
  color: #ffffff;
  cursor: pointer;
}

.header-opt {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-opt a {
  color: white;
  text-decoration: none;
  font-size: 14px;
}

.user-btn {
  background-color: white;
  color: #ff7f24;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: default;
}

.content-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 30px 20px;
}

.content-card {
  background: white;
  border-radius: 10px;
  padding: 30px;
  border: 2px solid #ffb380;
  box-shadow: 0 4px 12px rgba(255, 127, 36, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  color: #ff7f24;
  font-weight: bold;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn.primary {
  background: #ff7f24;
  color: white;
}

.action-btn.secondary {
  background: white;
  color: #ff7f24;
  border: 2px solid #ff7f24;
}

.action-btn.danger {
  background: #ffebe6;
  color: #d64545;
  border: 2px solid #ffb3a7;
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 40px 0;
  color: #666;
}

.loading-spinner {
  width: 36px;
  height: 36px;
  border: 4px solid #ffe6cc;
  border-top: 4px solid #ff7f24;
  border-radius: 50%;
  margin: 0 auto 10px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.table-wrapper {
  overflow-x: auto;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-input {
  width: 200px;
  padding: 8px 10px;
  border: 1px solid #ffb380;
  border-radius: 6px;
  font-size: 14px;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.user-table th,
.user-table td {
  padding: 12px 10px;
  border-bottom: 1px solid #ffe0c2;
  text-align: left;
  white-space: nowrap;
}

.user-table th {
  color: #ff7f24;
  font-weight: bold;
  background: #fff3e6;
}

.token-input {
  width: 100px;
  padding: 6px 8px;
  border: 1px solid #ffb380;
  border-radius: 4px;
}

.empty-state {
  padding: 20px 0;
  text-align: center;
  color: #999;
}

.pagination {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: flex-end;
}

.user-table td .action-btn + .action-btn {
  margin-left: 6px;
}

.page-btn {
  padding: 6px 12px;
  border: 1px solid #ffb380;
  border-radius: 4px;
  background: white;
  color: #ff7f24;
  font-weight: bold;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.page-info {
  color: #666;
}

@media (max-width: 768px) {
  .content-card {
    padding: 20px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .search-input {
    width: 100%;
  }
}
</style>
