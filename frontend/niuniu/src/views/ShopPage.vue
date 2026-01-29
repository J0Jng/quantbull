<template>
  <div>
    <!-- 头部 -->
    <div class="header">
      <div class="logo" @click="goHome">量化牛牛商城</div>
      <div class="header-opt">
        <!-- 管理员按钮 -->
        <a href="#" v-if="isAdmin" @click.prevent="showAddProductModal = true" class="admin-btn">
          ➕ 新增商品
        </a>
        <a href="#" @click.prevent="goToOrders">我的订单</a>
        <a href="#" @click.prevent="goToCart" class="cart-link">
          购物车
          <span class="cart-badge" v-if="cartBadgeCount > 0">{{ cartBadgeCount }}</span>
        </a>
        <div class="user-menu-container" @mouseenter="onMenuEnter" @mouseleave="onMenuLeave">
          <div class="user-btn" @click="toggleUserMenu">{{ userText }}</div>
          <div class="user-dropdown" v-show="showUserMenu && logged" @mouseenter="onDropdownEnter" @mouseleave="onDropdownLeave">
            <div class="dropdown-item" @click="goToUserProfile">个人主页</div>
            <div class="dropdown-item logout" @click="handleLogout">退出登录</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <input v-model="searchQuery" type="text" placeholder="搜索因子、策略、课程、书籍等" @keyup.enter="performSearch" />
      <button class="search-btn" @click="performSearch">搜索</button>
    </div>

    <!-- 分类导航 -->
    <div class="category-nav">
      <a href="#factor" class="category-item" :class="{ active: activeCategory==='factor' }" @click.prevent="go('factor')">因子</a>
      <a href="#strategy" class="category-item" :class="{ active: activeCategory==='strategy' }" @click.prevent="go('strategy')">策略</a>
      <a href="#fund" class="category-item fund" v-show="showFund" :class="{ active: activeCategory==='fund' }" @click.prevent="go('fund')">基金</a>
      <a href="#advisor" class="category-item" :class="{ active: activeCategory==='advisor' }" @click.prevent="go('advisor')">投顾</a>
      <a href="#course" class="category-item" :class="{ active: activeCategory==='course' }" @click.prevent="go('course')">课程</a>
      <a href="#book" class="category-item" :class="{ active: activeCategory==='book' }" @click.prevent="go('book')">书籍</a>
      <a href="#talent" class="category-item" :class="{ active: activeCategory==='talent' }" @click.prevent="go('talent')">人才</a>
      <a href="#bank" class="category-item" :class="{ active: activeCategory==='bank' }" @click.prevent="go('bank')">银行产品</a>
      <a href="#insurance" class="category-item" :class="{ active: activeCategory==='insurance' }" @click.prevent="go('insurance')">保险产品</a>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载商品中...</p>
    </div>

    <!-- 主容器 -->
    <div class="container" id="goodsContainer" :class="{ 'show-price': logged }" v-else>
      <!-- 因子分类 -->
      <h2 class="section-title" id="factor">量化因子</h2>
      <div class="goods-grid">
        <div class="goods-card" v-for="item in factorItems" :key="item.id">
          <img :src="item.img || defaultImg" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">因子</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ formatPrice(item.price) }}</div>
            <div class="goods-btn">
              <button class="buy-btn" @click="addToCart(item)">加入购物车</button>
            </div>
            <!-- 管理员操作按钮 -->
            <div class="admin-actions" v-if="isAdmin">
              <button class="edit-btn" @click="openEditModal(item)">编辑</button>
              <button class="delete-btn" @click="confirmDelete(item)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 策略分类 -->
      <h2 class="section-title" id="strategy">量化策略</h2>
      <div class="goods-grid">
        <div class="goods-card" v-for="item in strategyItems" :key="item.id">
          <img :src="item.img || defaultImg" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">策略</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ formatPrice(item.price) }}</div>
            <div class="goods-btn">
              <button class="buy-btn" @click="addToCart(item)">加入购物车</button>
            </div>
            <div class="admin-actions" v-if="isAdmin">
              <button class="edit-btn" @click="openEditModal(item)">编辑</button>
              <button class="delete-btn" @click="confirmDelete(item)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 基金分类（默认隐藏，登录后显示） -->
      <h2 class="section-title" id="fund" v-show="showFund">专属基金</h2>
      <div class="goods-grid" v-show="showFund">
        <div class="goods-card" v-for="item in fundItems" :key="item.id">
          <img :src="item.img || defaultImg" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">基金</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ (logged && isQualifiedInvestor) ? formatPrice(item.price) : '*****' }}</div>
            <div class="goods-btn">
              <button class="buy-btn" @click="addToCart(item)">预约认购</button>
            </div>
            <div class="admin-actions" v-if="isAdmin">
              <button class="edit-btn" @click="openEditModal(item)">编辑</button>
              <button class="delete-btn" @click="confirmDelete(item)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 投顾分类 -->
      <h2 class="section-title" id="advisor">专业投顾</h2>
      <div class="goods-grid">
        <div class="goods-card" v-for="item in advisorItems" :key="item.id">
          <img :src="item.img || defaultImg" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">投顾</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ (logged && isQualifiedInvestor) ? formatPrice(item.price) : '*****' }}</div>
            <div class="goods-btn">
              <button class="buy-btn" @click="addToCart(item)">加入购物车</button>
            </div>
            <div class="admin-actions" v-if="isAdmin">
              <button class="edit-btn" @click="openEditModal(item)">编辑</button>
              <button class="delete-btn" @click="confirmDelete(item)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 课程分类（课程有详情页） -->
      <h2 class="section-title" id="course">精品课程</h2>
      <div class="goods-grid">
        <div class="goods-card" v-for="item in courseItems" :key="item.id">
          <img :src="item.img || defaultImg" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">课程</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ formatPrice(item.price) }}</div>
            <div class="goods-btn">
              <button class="buy-btn" @click="addToCart(item)">加入购物车</button>
              <button class="detail-btn" @click="goToGoodsDetail(item)">课程详情</button>
            </div>
            <div class="admin-actions" v-if="isAdmin">
              <button class="edit-btn" @click="openEditModal(item)">编辑</button>
              <button class="delete-btn" @click="confirmDelete(item)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 书籍分类 -->
      <h2 class="section-title" id="book">专业书籍</h2>
      <div class="goods-grid">
        <div class="goods-card" v-for="item in bookItems" :key="item.id">
          <img :src="item.img || defaultImg" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">书籍</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ formatPrice(item.price) }}</div>
            <div class="goods-btn">
              <button class="buy-btn" @click="addToCart(item)">加入购物车</button>
            </div>
            <div class="admin-actions" v-if="isAdmin">
              <button class="edit-btn" @click="openEditModal(item)">编辑</button>
              <button class="delete-btn" @click="confirmDelete(item)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 人才分类 -->
      <h2 class="section-title" id="talent">量化人才</h2>
      <div class="goods-grid">
        <div class="goods-card" v-for="item in talentItems" :key="item.id">
          <img :src="item.img || defaultImg" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">人才</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ formatPrice(item.price) }}</div>
            <div class="goods-btn">
              <button class="buy-btn" @click="addToCart(item)">咨询对接</button>
            </div>
            <div class="admin-actions" v-if="isAdmin">
              <button class="edit-btn" @click="openEditModal(item)">编辑</button>
              <button class="delete-btn" @click="confirmDelete(item)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 银行产品分类 -->
      <h2 class="section-title" id="bank">银行产品</h2>
      <div class="goods-grid">
        <div class="goods-card" v-for="item in bankItems" :key="item.id">
          <img :src="item.img || defaultImg" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">银行</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ formatPrice(item.price) }}</div>
            <div class="goods-btn">
              <button class="buy-btn" @click="addToCart(item)">立即购买</button>
            </div>
            <div class="admin-actions" v-if="isAdmin">
              <button class="edit-btn" @click="openEditModal(item)">编辑</button>
              <button class="delete-btn" @click="confirmDelete(item)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 保险产品分类 -->
      <h2 class="section-title" id="insurance">保险产品</h2>
      <div class="goods-grid">
        <div class="goods-card" v-for="item in insuranceItems" :key="item.id">
          <img :src="item.img || defaultImg" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">保险</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ formatPrice(item.price) }}</div>
            <div class="goods-btn">
              <button class="buy-btn" @click="addToCart(item)">立即投保</button>
            </div>
            <div class="admin-actions" v-if="isAdmin">
              <button class="edit-btn" @click="openEditModal(item)">编辑</button>
              <button class="delete-btn" @click="confirmDelete(item)">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增/编辑商品弹窗 -->
    <div class="product-modal" v-if="showAddProductModal || showEditProductModal">
      <div class="product-modal-box">
        <span class="close-modal" @click="closeProductModal">×</span>
        <h2 class="modal-title">{{ showEditProductModal ? '编辑商品' : '新增商品' }}</h2>
        <form class="product-form" @submit.prevent="submitProduct">
          <!-- 基础信息 -->
          <div class="form-section">
            <div class="section-title">基础信息</div>
            <div class="form-group">
              <label>商品类型 *</label>
              <select v-model="productForm.type" required>
                <option value="">请选择类型</option>
                <option value="factor">因子</option>
                <option value="strategy">策略</option>
                <option value="fund">基金</option>
                <option value="advisor">投顾</option>
                <option value="course">课程</option>
                <option value="book">书籍</option>
                <option value="talent">人才</option>
                <option value="bank">银行产品</option>
                <option value="insurance">保险产品</option>
              </select>
            </div>
            <div class="form-group">
              <label>商品名称 *</label>
              <input type="text" v-model="productForm.name" placeholder="请输入商品名称" required />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>售价 *</label>
                <input type="number" v-model.number="productForm.price" placeholder="售价" step="0.01" min="0" required />
              </div>
              <div class="form-group">
                <label>原价</label>
                <input type="number" v-model.number="productForm.original_price" placeholder="原价（可选）" step="0.01" min="0" />
              </div>
            </div>
            <div class="form-group">
              <label>商品图片</label>
              <input type="file" accept="image/*" @change="onImageChange" />
              <div class="field-hint">仅支持本地图片上传，保存后将以图片内容形式存储。</div>
              <div class="image-preview" v-if="productForm.img">
                <img :src="productForm.img" alt="图片预览" />
              </div>
            </div>
            <div class="form-group">
              <label>商品描述</label>
              <textarea v-model="productForm.description" placeholder="请输入商品描述（可选）" rows="3"></textarea>
            </div>
          </div>

          <!-- 课程详情信息（仅课程类型显示） -->
          <div class="form-section" v-if="productForm.type === 'course'">
            <div class="section-title">课程详情信息（可选）</div>
            <div class="form-row">
              <div class="form-group">
                <label>课时/时长</label>
                <input type="text" v-model="productForm.duration" placeholder="如：12课时（每课时45分钟）" />
              </div>
              <div class="form-group">
                <label>讲师</label>
                <input type="text" v-model="productForm.instructor" placeholder="如：张老师（10年经验）" />
              </div>
            </div>
            <div class="form-group">
              <label>适合人群</label>
              <input type="text" v-model="productForm.target_audience" placeholder="如：零基础新手、上班族、投资爱好者" />
            </div>
            <div class="form-group">
              <label>学习方式</label>
              <input type="text" v-model="productForm.learning_method" placeholder="如：录播视频（永久回放）+ 在线答疑" />
            </div>
            <div class="form-group">
              <label>开课时间</label>
              <input type="text" v-model="productForm.start_time" placeholder="如：购买后立即开课" />
            </div>
            <div class="form-group">
              <label>课程大纲 <span class="hint">（JSON格式，每项包含 title 和 items 数组）</span></label>
              <textarea v-model="productForm.outline" placeholder='[{"title":"第1章：入门","items":["1.1 基础概念","1.2 实操练习"]}]' rows="4"></textarea>
            </div>
            <div class="form-group">
              <label>课程详细介绍</label>
              <textarea v-model="productForm.detail_content" placeholder="详细的课程介绍文字（支持纯文本）" rows="4"></textarea>
            </div>
            <div class="form-group">
              <label>常见问题 <span class="hint">（JSON格式，问答对数组）</span></label>
              <textarea v-model="productForm.faq" placeholder='[{"q":"需要什么基础？","a":"零基础即可"},{"q":"有效期多长？","a":"永久有效"}]' rows="3"></textarea>
            </div>
          </div>

          <div class="form-group checkbox-group">
            <label>
              <input type="checkbox" v-model="productForm.is_active" />
              上架状态
            </label>
          </div>
          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="closeProductModal">取消</button>
            <button type="submit" class="submit-btn" :disabled="productSubmitting">
              {{ productSubmitting ? '提交中...' : (showEditProductModal ? '保存修改' : '创建商品') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div class="confirm-modal" v-if="showDeleteConfirm">
      <div class="confirm-box">
        <h3>确认删除</h3>
        <p>确定要删除商品 "{{ deleteTargetProduct?.name }}" 吗？</p>
        <p class="delete-hint">（商品将被下架，不会物理删除）</p>
        <div class="confirm-actions">
          <button class="cancel-btn" @click="showDeleteConfirm = false">取消</button>
          <button class="delete-confirm-btn" @click="doDeleteProduct" :disabled="deleting">
            {{ deleting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart.js'
import FooterComponent from '@/components/FooterComponent.vue'
import { useAuth } from '@/composables/useAuth'
import { 
  getProducts, 
  createProduct, 
  updateProduct, 
  deleteProduct,
  formatPrice as serviceFormatPrice,
  ProductTypeName
} from '@/services/productService'

// 使用全局认证
const { logged, userText, isQualifiedInvestor, isAdmin, openLoginModal, logout, requireAuth, initAuth } = useAuth()

const showFund = ref(false)
const showUserMenu = ref(false)
const searchQuery = ref('')
const activeCategory = ref('factor')
const loading = ref(true)
const defaultImg = 'https://picsum.photos/400/300?random=0'

// 商品数据（从后端获取）
const allProducts = ref([])

// 按类型过滤商品
const factorItems = computed(() => allProducts.value.filter(p => p.type === 'factor'))
const strategyItems = computed(() => allProducts.value.filter(p => p.type === 'strategy'))
const fundItems = computed(() => allProducts.value.filter(p => p.type === 'fund'))
const advisorItems = computed(() => allProducts.value.filter(p => p.type === 'advisor'))
const courseItems = computed(() => allProducts.value.filter(p => p.type === 'course'))
const bookItems = computed(() => allProducts.value.filter(p => p.type === 'book'))
const talentItems = computed(() => allProducts.value.filter(p => p.type === 'talent'))
const bankItems = computed(() => allProducts.value.filter(p => p.type === 'bank'))
const insuranceItems = computed(() => allProducts.value.filter(p => p.type === 'insurance'))
  
// 购物车徽章显示
const cartBadgeCount = computed(() => cartStore.totalItems)

const router = useRouter()
const cartStore = useCartStore()

// 管理员相关状态
const showAddProductModal = ref(false)
const showEditProductModal = ref(false)
const showDeleteConfirm = ref(false)
const productSubmitting = ref(false)
const deleting = ref(false)
const editingProductId = ref(null)
const deleteTargetProduct = ref(null)

// 商品表单
const productForm = ref({
  type: '',
  name: '',
  price: 0,
  original_price: null,
  img: '',
  description: '',
  duration: '',
  target_audience: '',
  learning_method: '',
  start_time: '',
  instructor: '',
  outline: '',
  detail_content: '',
  faq: '',
  is_active: true
})

// 格式化价格
function formatPrice(price) {
  return serviceFormatPrice(price)
}

// 加载商品数据
async function loadProducts() {
  loading.value = true
  try {
    // 默认只加载上架商品（管理员也一样，删除即不显示）
    const result = await getProducts()
    if (result.success && result.data) {
      allProducts.value = result.data
      
      // --- 用于演示：如果没有银行或保险产品，添加示例数据 ---
      const hasBank = allProducts.value.some(p => p.type === 'bank')
      const hasInsurance = allProducts.value.some(p => p.type === 'insurance')
      
      if (!hasBank) {
        allProducts.value.push(
          { id: 'mock-bank-1', type: 'bank', name: '稳健优选理财30天', price: 10000, img: 'https://picsum.photos/id/20/400/300', description: '低风险，稳健收益' },
          { id: 'mock-bank-2', type: 'bank', name: '招财宝90天定存', price: 50000, img: 'https://picsum.photos/id/160/400/300', description: '中低风险，收益可观' },
          { id: 'mock-bank-3', type: 'bank', name: '大额存单3年期', price: 200000, img: 'https://picsum.photos/id/180/400/300', description: '保本保息，安心之选' }
        )
      }
      
      if (!hasInsurance) {
        allProducts.value.push(
          { id: 'mock-ins-1', type: 'insurance', name: '安康百万医疗险', price: 365, img: 'https://picsum.photos/id/531/400/300', description: '每年仅需365元，享百万保障' },
          { id: 'mock-ins-2', type: 'insurance', name: '出行无忧意外险', price: 99, img: 'https://picsum.photos/id/619/400/300', description: '商旅出行必备，全方位守护' },
          { id: 'mock-ins-3', type: 'insurance', name: '家庭财产综合险', price: 188, img: 'https://picsum.photos/id/96/400/300', description: '守护温馨家园，防盗防灾' }
        )
      }
      // -----------------------------------------------------

    } else {
      console.error('Failed to load products:', result.message)
    }
  } catch (error) {
    console.error('Error loading products:', error)
  } finally {
    loading.value = false
  }
}

// 搜索功能
function performSearch() {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) {
    loadProducts()
    return
  }
  // 本地过滤
  allProducts.value = allProducts.value.filter(p => 
    p.name.toLowerCase().includes(query) || 
    (p.description && p.description.toLowerCase().includes(query))
  )
}

function goHome() { router.push('/') }

function goToGoodsDetail(item) {
  // 首先检查用户是否已登录
  if (!requireAuth()) {
    alert('请先登录后再查看商品详情和购买。')
    return
  }
  
  // 如果是基金或投顾分类，需要检查合格投资者认证
  if ((item.type === 'fund' || item.type === 'advisor') && !isQualifiedInvestor.value) {
    alert('该产品仅对合格投资者开放，请先前往个人主页完成合格投资者认证。')
    return
  }
  
  router.push(`/shop/goods-detail/${item.id}`)
}

// 添加商品到购物车
function addToCart(item) {
  if (!requireAuth()) {
    alert('请先登录后再添加商品到购物车')
    return
  }
  
  // 如果是基金或投顾产品，检查合格投资者认证
  if ((item.type === 'fund' || item.type === 'advisor') && !isQualifiedInvestor.value) {
    alert('该产品仅对合格投资者开放，请先前往个人主页完成合格投资者认证。')
    return
  }
  
  // 创建购物车商品对象
  const cartItem = {
    id: item.id,
    name: item.name,
    price: formatPrice(item.price),
    rawPrice: item.price,
    img: item.img || defaultImg,
    type: item.type
  }
  
  cartStore.addToCart(cartItem)
  
  const productTypeName = ProductTypeName[item.type] || '商品'
  alert(`已成功添加 ${productTypeName} 产品到购物车！`)
}

// ============ 管理员功能 ============

function resetProductForm() {
  productForm.value = {
    type: '',
    name: '',
    price: 0,
    original_price: null,
    img: '',
    description: '',
    duration: '',
    target_audience: '',
    learning_method: '',
    start_time: '',
    instructor: '',
    outline: '',
    detail_content: '',
    faq: '',
    is_active: true
  }
}

function closeProductModal() {
  showAddProductModal.value = false
  showEditProductModal.value = false
  editingProductId.value = null
  resetProductForm()
}

function openEditModal(item) {
  editingProductId.value = item.id
  productForm.value = {
    type: item.type,
    name: item.name,
    price: item.price,
    original_price: item.original_price || null,
    img: item.img || '',
    description: item.description || '',
    duration: item.duration || '',
    target_audience: item.target_audience || '',
    learning_method: item.learning_method || '',
    start_time: item.start_time || '',
    instructor: item.instructor || '',
    outline: item.outline || '',
    detail_content: item.detail_content || '',
    faq: item.faq || '',
    is_active: item.is_active
  }
  showEditProductModal.value = true
}

function onImageChange(event) {
  const file = event?.target?.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = () => {
    productForm.value.img = String(reader.result || '')
  }
  reader.readAsDataURL(file)
}

async function submitProduct() {
  if (!productForm.value.type || !productForm.value.name || productForm.value.price <= 0) {
    alert('请填写完整的商品信息')
    return
  }

  productSubmitting.value = true
  try {
    if (showEditProductModal.value && editingProductId.value) {
      // 更新商品
      const result = await updateProduct(editingProductId.value, productForm.value)
      if (result.success) {
        alert('商品更新成功！')
        closeProductModal()
        await loadProducts()
      } else {
        alert('更新失败: ' + (result.message || '未知错误'))
      }
    } else {
      // 创建商品
      const result = await createProduct(productForm.value)
      if (result.success) {
        alert('商品创建成功！')
        closeProductModal()
        await loadProducts()
      } else {
        alert('创建失败: ' + (result.message || '未知错误'))
      }
    }
  } catch (error) {
    console.error('Submit product error:', error)
    alert('操作失败，请稍后重试')
  } finally {
    productSubmitting.value = false
  }
}

function confirmDelete(item) {
  deleteTargetProduct.value = item
  showDeleteConfirm.value = true
}

async function doDeleteProduct() {
  if (!deleteTargetProduct.value) return
  
  deleting.value = true
  try {
    const result = await deleteProduct(deleteTargetProduct.value.id)
    if (result.success) {
      alert('商品已删除（下架）')
      // 从本地列表中移除该商品，避免重新加载后仍显示
      const deletedId = deleteTargetProduct.value.id
      allProducts.value = allProducts.value.filter(p => p.id !== deletedId)
      showDeleteConfirm.value = false
      deleteTargetProduct.value = null
    } else {
      alert('删除失败: ' + (result.message || '未知错误'))
    }
  } catch (error) {
    console.error('Delete product error:', error)
    alert('删除失败，请稍后重试')
  } finally {
    deleting.value = false
  }
}

// ============ 生命周期 ============

onMounted(async () => {
  await initAuth()
  
  if (logged.value) {
    showFund.value = true
  }
  
  await loadProducts()
})

let menuTimeout = null
let hideTimeout = null

function onMenuEnter() {
  if (!logged.value) return
  clearTimeout(hideTimeout)
  menuTimeout = setTimeout(() => {
    showUserMenu.value = true
  }, 300)
}

function onMenuLeave() {
  clearTimeout(menuTimeout)
  hideTimeout = setTimeout(() => {
    if (showUserMenu.value) {
      showUserMenu.value = false
    }
  }, 200)
}

function onDropdownEnter() {
  clearTimeout(hideTimeout)
}

function onDropdownLeave() {
  hideTimeout = setTimeout(() => {
    showUserMenu.value = false
  }, 200)
}

function toggleUserMenu() { 
  if (!logged.value) {
    openLoginModal()
    showUserMenu.value = false
  } else {
    clearTimeout(menuTimeout)
    clearTimeout(hideTimeout)
    showUserMenu.value = !showUserMenu.value
  }
}

function handleLogout() {
  logout()
  showFund.value = false
  showUserMenu.value = false
  loadProducts() // 重新加载（隐藏下架商品）
}

function goToUserProfile() {
  showUserMenu.value = false
  router.push('/profile')
}

function goToCart() {
  if (!requireAuth()) {
    alert('请先登录后查看购物车')
    return
  }
  router.push('/shop/cart')
}

function goToOrders() {
  if (!requireAuth()) {
    alert('请先登录后查看订单')
    return
  }
  router.push('/shop/orders')
}

function go(id) {
  activeCategory.value = id
  const el = document.getElementById(id)
  if (el) window.scrollTo({ top: el.offsetTop - 100, behavior: 'smooth' })
}
</script>

<style scoped>
/* 直接复用原页面样式（简化并保留核心） */
*{margin:0;padding:0;box-sizing:border-box;font-family:"微软雅黑",sans-serif}
body{background-color:#fff8f0;color:#333}
.login-modal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.8);display:flex;justify-content:center;align-items:center;z-index:9999}
.login-box{width:90%;max-width:400px;background:white;border-radius:10px;padding:30px;position:relative;border:2px solid #ff7f24}
.close-login{position:absolute;top:15px;right:15px;font-size:24px;color:#ff7f24;cursor:pointer}
.login-title{font-size:22px;color:#ff7f24;text-align:center;margin-bottom:20px;font-weight:bold}
.login-form{display:flex;flex-direction:column;gap:15px}
.login-form input{padding:12px 15px;border:1px solid #ffb380;border-radius:6px}
.login-btn{background-color:#ff7f24;color:white;border:none;padding:12px 0;border-radius:6px;cursor:pointer}
.login-btn:hover{background-color:#ff6a00}
.login-tips{ text-align:center;font-size:14px;color:#666;margin-top:10px }
.error-tips{color:#ff4500;text-align:center}
.header{background-color:#ff7f24;padding:12px 20px;color:white;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:99}
.logo{font-size:22px;font-weight:bold;color:#ffffff;cursor:pointer}
.header-opt{display:flex;align-items:center;gap:20px}
.header-opt a{color:white;text-decoration:none;font-size:14px;position:relative}
.cart-link { position: relative; }
.header-opt{position:relative}
.user-menu-container{position:relative;display:inline-block}
.header-opt .user-btn{background-color:white;color:#ffffff;padding:6px 12px;border-radius:4px;cursor:pointer;position:relative}
.user-menu-container:hover .user-btn{background-color:#f5f5f5}
.user-dropdown{position:absolute;top:100%;right:0;background-color:white;border:1px solid #ddd;border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,0.15);z-index:1000;margin-top:5px;min-width:120px}
.dropdown-item{padding:8px 12px;cursor:pointer;font-size:14px;color:#333;border-bottom:1px solid #f0f0f0}
.dropdown-item:hover{background-color:#f5f5f5}
.dropdown-item.logout{color:#ff4444;border-bottom:none}
.dropdown-item.logout:hover{background-color:#ffe6e6}
.search-bar{padding:15px 20px;background-color:white;display:flex;gap:10px;align-items:center}
.search-bar input{flex:1;padding:10px 15px;border:1px solid #ffb380;border-radius:6px;outline:none}
.search-btn{background-color:#ff7f24;color:white;border:none;padding:10px 25px;border-radius:6px}
.category-nav{background-color:#ff9933;padding:12px 20px;overflow-x:auto;white-space:nowrap}
.category-item{display:inline-block;color:white;text-decoration:none;padding:6px 18px;margin-right:8px;border-radius:4px;font-size:15px;cursor:pointer}
.category-item.active{background-color:#ff7f24;font-weight:bold}
.container{max-width:1200px;margin:0 auto;padding:20px}
.section-title{font-size:20px;color:#ff7f24;border-left:1px solid #ff7f24;padding-left:10px;margin:20px 0 15px}
/* 指定分类标题使用白色字体以匹配设计，并整体左移微调视觉对齐 */
#factor.section-title,
#strategy.section-title,
#fund.section-title,
#advisor.section-title,
#course.section-title,
#book.section-title,
#talent.section-title,
#bank.section-title,
#insurance.section-title {
  color: #ffffff;
  transform: translateX(-1px);
}
.goods-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:20px;margin-bottom:30px}
.goods-card{background-color:white;border-radius:8px;overflow:hidden;border:1px solid #ffb380;transition:transform .2s}
.goods-card:hover{transform:translateY(-5px);box-shadow:0 4px 12px rgba(255,127,36,.15)}
.goods-img{width:100%;height:160px;object-fit:cover}
.goods-info{padding:15px}
.goods-name{font-size:16px;margin-bottom:8px;color:#333;display:-webkit-box;-webkit-line-clamp:2;line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.goods-tag{display:inline-flex;align-items:center;justify-content:center;height:24px;line-height:1;background-color:#ff7f24;color:#ffffff;font-size:12px;padding:0 8px;border-radius:4px;margin-bottom:8px;vertical-align:middle;transform:translateX(-1px)}
.goods-price{font-size:18px;color:#ff7f24;font-weight:bold;margin-bottom:10px;display:block}
.category-item.fund{display:none}
.buy-btn,.detail-btn{flex:1;padding:8px 0;border-radius:4px;font-size:14px;cursor:pointer;border:none}
.buy-btn{background-color:#ff7f24;color:white}
.detail-btn{background-color:white;color:#ff7f24;border:1px solid #ff7f24}
.footer{background-color:#ff7f24;color:white;text-align:center;padding:20px;margin-top:40px}

/* 动态风险提示样式 */
.risk-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
}

.risk-box {
  width: 90%;
  max-width: 500px;
  background: white;
  border-radius: 10px;
  padding: 30px;
  position: relative;
  border: 3px solid #ff9933;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.risk-icon {
  font-size: 40px;
  text-align: center;
  margin-bottom: 15px;
}

.risk-title {
  font-size: 24px;
  color: #ff4500;
  text-align: center;
  margin-bottom: 20px;
  font-weight: bold;
}

.risk-content {
  margin-bottom: 25px;
  line-height: 1.6;
}

.risk-content p {
  margin-bottom: 15px;
  color: #333;
}

.risk-content ul {
  padding-left: 20px;
  margin-bottom: 15px;
}

.risk-content li {
  margin-bottom: 8px;
  color: #666;
}

.risk-confirm-btn {
  background-color: #ff7f24;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  display: block;
  margin: 0 auto;
  transition: background-color 0.3s;
}

.risk-confirm-btn:hover {
  background-color: #ff6a00;
}
/* 购物车徽章样式 */
.cart-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ff4d4f;
  color: white;
  border-radius: 10px;
  min-width: 18px;
  height: 18px;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  line-height: 1;
}

/* 购物车链接悬停效果 */
.cart-link:hover {
  opacity: 0.8;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #ff7f24;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #ffb380;
  border-top-color: #ff7f24;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 管理员按钮 */
.admin-btn {
  background-color: #52c41a;
  color: white !important;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  text-decoration: none;
}

.admin-btn:hover {
  background-color: #389e0d;
}

/* 管理员操作按钮 */
.admin-actions {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #ddd;
}

.edit-btn, .delete-btn {
  flex: 1;
  padding: 6px 0;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  border: none;
}

.edit-btn {
  background-color: #1890ff;
  color: white;
}

.edit-btn:hover {
  background-color: #096dd9;
}

.delete-btn {
  background-color: #ff4d4f;
  color: white;
}

.delete-btn:hover {
  background-color: #cf1322;
}

/* 商品弹窗 */
.product-modal, .confirm-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
}

.product-modal-box {
  width: 90%;
  max-width: 500px;
  background: white;
  border-radius: 10px;
  padding: 30px;
  position: relative;
  max-height: 90vh;
  overflow-y: auto;
}

.close-modal {
  position: absolute;
  top: 15px;
  right: 20px;
  font-size: 28px;
  color: #999;
  cursor: pointer;
}

.close-modal:hover {
  color: #ff7f24;
}

.modal-title {
  font-size: 22px;
  color: #ff7f24;
  text-align: center;
  margin-bottom: 25px;
  font-weight: bold;
}

.product-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #ff7f24;
}

.checkbox-group {
  flex-direction: row;
  align-items: center;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-group input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 10px;
}

.cancel-btn, .submit-btn {
  flex: 1;
  padding: 12px 0;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  font-weight: 500;
}

.cancel-btn {
  background-color: #f0f0f0;
  color: #666;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.submit-btn {
  background-color: #ff7f24;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background-color: #ff6a00;
}

.submit-btn:disabled {
  background-color: #ffb380;
  cursor: not-allowed;
}

/* 表单分区样式 */
.form-section {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #eee;
}

.form-section:last-of-type {
  border-bottom: none;
}

.section-title {
  font-size: 14px;
  color: #ff7f24;
  font-weight: 600;
  margin-bottom: 15px;
  padding-left: 8px;
  border-left: 3px solid #ff7f24;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-row .form-group {
  flex: 1;
}

.form-group .hint {
  font-size: 11px;
  color: #999;
  font-weight: normal;
}

.field-hint {
  font-size: 12px;
  color: #999;
}

.image-preview {
  margin-top: 8px;
  border: 1px dashed #eee;
  border-radius: 6px;
  padding: 8px;
  background: #fafafa;
}

.image-preview img {
  width: 100%;
  max-height: 180px;
  object-fit: cover;
  border-radius: 4px;
  display: block;
}

/* 删除确认弹窗 */
.confirm-box {
  width: 90%;
  max-width: 400px;
  background: white;
  border-radius: 10px;
  padding: 30px;
  text-align: center;
}

.confirm-box h3 {
  font-size: 20px;
  color: #ff4d4f;
  margin-bottom: 15px;
}

.confirm-box p {
  color: #333;
  margin-bottom: 10px;
}

.delete-hint {
  font-size: 12px;
  color: #999;
}

.confirm-actions {
  display: flex;
  gap: 15px;
  margin-top: 25px;
}

.delete-confirm-btn {
  flex: 1;
  padding: 12px 0;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  background-color: #ff4d4f;
  color: white;
}

.delete-confirm-btn:hover:not(:disabled) {
  background-color: #cf1322;
}

.delete-confirm-btn:disabled {
  background-color: #ffccc7;
  cursor: not-allowed;
}

</style>
