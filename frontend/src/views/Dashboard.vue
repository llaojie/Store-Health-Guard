<template>
  <div class="dashboard">
    <h1>🏪 门店健康总览</h1>

    <!-- 门店卡片 -->
    <el-row :gutter="20" v-loading="loading">
      <el-col :span="8" v-for="store in stores" :key="store.id">
        <el-card class="store-card" @click="goDetail(store.id)" shadow="hover">
          <div class="card-header">
            <h3>{{ store.name }}</h3>
            <el-tag :type="getBizTagType(store.biz_type)">{{ store.biz_type }}</el-tag>
          </div>
          <div class="card-body">
            <p>📍 {{ store.address || '未设置地址' }}</p>
            <p>📐 {{ store.area }}㎡ · {{ store.seat_count }}座</p>
            <div v-if="dashboards[store.id]" class="health-badge">
              <span class="score" :class="'level-' + dashboards[store.id].overall_status">
                {{ dashboards[store.id].health_score }}分
              </span>
              <span class="status-dot" :class="'dot-' + dashboards[store.id].overall_status"></span>
            </div>
            <div v-else class="health-badge">
              <span class="score level-green">--</span>
            </div>
          </div>
          <div v-if="dashboards[store.id]?.active_alerts?.length" class="alert-count">
            <el-badge :value="dashboards[store.id].active_alerts.length" type="danger">
              <el-button size="small" text>查看预警</el-button>
            </el-badge>
          </div>
        </el-card>
      </el-col>

      <!-- 新增门店 -->
      <el-col :span="8">
        <el-card class="store-card add-card" @click="showAddDialog = true" shadow="hover">
          <div class="add-content">
            <el-icon :size="40"><Plus /></el-icon>
            <p>添加门店</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 新增门店对话框 -->
    <el-dialog v-model="showAddDialog" title="添加门店" width="500px">
      <el-form :model="newStore" label-width="100px">
        <el-form-item label="门店名称">
          <el-input v-model="newStore.name" />
        </el-form-item>
        <el-form-item label="门店编号">
          <el-input v-model="newStore.code" />
        </el-form-item>
        <el-form-item label="业态">
          <el-select v-model="newStore.biz_type" placeholder="选择业态">
            <el-option label="快餐" value="fast_food" />
            <el-option label="茶饮" value="tea_drink" />
            <el-option label="咖啡" value="coffee" />
            <el-option label="小吃" value="snack" />
            <el-option label="火锅" value="hotpot" />
          </el-select>
        </el-form-item>
        <el-form-item label="面积(㎡)">
          <el-input-number v-model="newStore.area" />
        </el-form-item>
        <el-form-item label="座位数">
          <el-input-number v-model="newStore.seat_count" />
        </el-form-item>
        <el-form-item label="月租金">
          <el-input-number v-model="newStore.monthly_rent" :step="1000" />
        </el-form-item>
        <el-form-item label="月固定成本">
          <el-input-number v-model="newStore.monthly_fixed_cost" :step="1000" />
        </el-form-item>
        <el-form-item label="目标毛利率">
          <el-input-number v-model="newStore.target_gross_margin" :min="0" :max="1" :step="0.01" :precision="2" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="newStore.address" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addStore">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus } from '@element-plus/icons-vue'
import { getStores, getDashboard, createStore } from '../api'

const router = useRouter()
const stores = ref([])
const dashboards = ref({})
const loading = ref(false)
const showAddDialog = ref(false)

const newStore = ref({
  name: '', code: '', biz_type: 'tea_drink',
  area: 60, seat_count: 20, monthly_rent: 20000,
  monthly_fixed_cost: 80000, target_gross_margin: 0.58, address: ''
})

const getBizTagType = (type) => {
  const map = { fast_food: 'warning', tea_drink: 'success', coffee: '', snack: 'info', hotpot: 'danger' }
  return map[type] || ''
}

const goDetail = (id) => router.push(`/store/${id}`)

const addStore = async () => {
  await createStore(newStore.value)
  showAddDialog.value = false
  loadStores()
}

const loadStores = async () => {
  loading.value = true
  try {
    const { data } = await getStores()
    stores.value = data
    // 加载每个门店的仪表盘数据
    for (const store of data) {
      try {
        const dash = await getDashboard(store.id)
        dashboards.value[store.id] = dash.data
      } catch {
        // 门店可能还没有数据
      }
    }
  } finally {
    loading.value = false
  }
}

onMounted(loadStores)
</script>

<style scoped>
.dashboard { padding: 20px; }
.store-card { margin-bottom: 20px; cursor: pointer; transition: all 0.3s; }
.store-card:hover { transform: translateY(-4px); }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header h3 { margin: 0; font-size: 16px; }
.card-body p { color: #666; font-size: 13px; margin: 6px 0; }
.health-badge { margin-top: 12px; display: flex; align-items: center; gap: 8px; }
.score { font-size: 28px; font-weight: bold; }
.score.level-green { color: #67c23a; }
.score.level-yellow { color: #e6a23c; }
.score.level-red { color: #f56c6c; }
.status-dot { width: 12px; height: 12px; border-radius: 50%; }
.dot-green { background: #67c23a; }
.dot-yellow { background: #e6a23c; }
.dot-red { background: #f56c6c; animation: pulse 1.5s infinite; }
.alert-count { margin-top: 8px; }
.add-card { display: flex; align-items: center; justify-content: center; min-height: 180px; }
.add-content { text-align: center; color: #999; }
.add-content p { margin-top: 8px; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
</style>
