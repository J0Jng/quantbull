<template>
  <div class="admin-users-page">
    <!-- 头部 -->
    <div class="header">
      <div class="logo" @click="goHome">用户管理</div>
      <div class="header-opt">
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

        <div class="create-user-card">
          <h2>创建普通用户</h2>
          <div class="create-user-form">
            <input v-model.trim="createForm.username" type="text" placeholder="用户名" class="form-input" />
            <input v-model.trim="createForm.password" type="password" placeholder="密码（至少6位，含字母和数字）" class="form-input" />
            <input v-model.trim="createForm.email" type="email" placeholder="邮箱（可选）" class="form-input" />
            <input v-model.trim="createForm.phone" type="text" placeholder="手机号（可选）" class="form-input" />
            <button class="action-btn primary" :disabled="creating" @click="createNormalUser">
              {{ creating ? '创建中...' : '创建普通用户' }}
            </button>
          </div>
          <p class="create-user-tip">该入口仅允许创建 role=user 的普通用户。</p>
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
                <th>用户名</th>
                <th>角色</th>
                <th>AI 额度</th>
                <th>新密码</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
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
                <td>
                  <input
                    class="password-input"
                    type="password"
                    placeholder="输入新密码"
                    v-model.trim="editPasswords[user.id]"
                    :disabled="savingIds.has(user.id)"
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
                    class="action-btn secondary"
                    @click="savePassword(user.id)"
                    :disabled="savingIds.has(user.id)"
                  >
                    修改密码
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
import { listUsers, updateUserAiTokens, getUser, updateUser, deleteUser, createUser } from '@/services/adminService'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { initAuth, logged, isAdmin } = useAuth()

const users = ref([])
const loading = ref(false)
const error = ref('')
const limit = ref(100)
const offset = ref(0)
const editTokens = ref({})
const editPasswords = ref({})
const savingIds = ref(new Set())
const searchKeyword = ref('')
const creating = ref(false)
const createForm = ref({
  username: '',
  password: '',
  email: '',
  phone: ''
})

const filteredUsers = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  if (!keyword) return users.value
  return users.value.filter((user) => String(user.username || '').toLowerCase().includes(keyword))
})

onMounted(async () => {
  await initAuth()
  if (!logged.value) {
    alert('请先登录')
    router.replace('/home')
    return
  }
  if (!isAdmin.value) {
    alert('仅管理员可访问该页面')
    router.replace('/home')
    return
  }
  fetchUsers()
})

function goHome() {
  router.push('/')
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
      const newEditPasswords = {}
      users.value.forEach((user) => {
        newEditTokens[user.id] = user.ai_tokens
        newEditPasswords[user.id] = ''
      })
      editTokens.value = newEditTokens
      editPasswords.value = newEditPasswords
    } else {
      error.value = result.message || '加载失败'
    }
  } catch (err) {
    error.value = err.message || '加载失败'
  } finally {
    loading.value = false
  }
}

async function createNormalUser() {
  const username = createForm.value.username.trim()
  const password = createForm.value.password.trim()
  const email = createForm.value.email.trim()
  const phone = createForm.value.phone.trim()

  if (!username || !password) {
    alert('请输入用户名和密码')
    return
  }

  creating.value = true
  try {
    const result = await createUser({
      username,
      password,
      email: email || null,
      phone: phone || null,
      role: 'user'
    })

    if (!result.success) {
      alert(result.message || '创建用户失败')
      return
    }

    createForm.value = { username: '', password: '', email: '', phone: '' }
    await fetchUsers()
    alert('创建普通用户成功')
  } catch (err) {
    alert(err.message || '创建用户失败')
  } finally {
    creating.value = false
  }
}

async function saveTokens(userId) {
  const aiTokens = editTokens.value[userId]
  if (aiTokens === null || aiTokens === undefined || Number.isNaN(aiTokens)) {
    alert('请输入有效的 AI 额度')
    return
  }
  if (aiTokens < 0) {
    alert('AI 额度不能为负数')
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

async function savePassword(userId) {
  const password = (editPasswords.value[userId] || '').trim()
  if (!password) {
    alert('请输入新密码')
    return
  }
  if (password.length < 6) {
    alert('密码长度至少 6 位')
    return
  }

  savingIds.value.add(userId)
  try {
    const result = await updateUser(userId, { password })
    if (result.success) {
      editPasswords.value[userId] = ''
      await fetchUsers()
    } else {
      alert(result.message || '修改密码失败')
    }
  } catch (err) {
    alert(err.message || '修改密码失败')
  } finally {
    savingIds.value.delete(userId)
  }
}

async function viewUser(userId) {
  savingIds.value.add(userId)
  try {
    const result = await getUser(userId)
    if (result.success) {
      const data = result.data?.data || result.data || null
      if (data) {
        alert(`ID: ${data.id}\n用户名: ${data.username}\n角色: ${data.role}\nAI 额度: ${data.ai_tokens}\n创建时间: ${formatDate(data.created_at)}`)
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

.create-user-card {
  margin-bottom: 20px;
  padding: 16px;
  background: #fff7ef;
  border: 1px solid #ffd9b3;
  border-radius: 8px;
}

.create-user-card h2 {
  margin: 0 0 12px;
  color: #ff7f24;
  font-size: 18px;
}

.create-user-form {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  align-items: center;
}

.form-input {
  padding: 8px 10px;
  border: 1px solid #ffb380;
  border-radius: 6px;
  font-size: 14px;
}

.create-user-tip {
  margin: 8px 0 0;
  font-size: 12px;
  color: #a8682a;
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

.password-input {
  width: 160px;
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

  .create-user-form {
    grid-template-columns: 1fr;
  }
}
</style>
