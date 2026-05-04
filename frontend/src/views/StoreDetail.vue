<template>
  <div class="store-detail" v-loading="loading">
    <el-page-header @back="$router.push('/')" :content="dashboard?.store_name || '加载中...'" />

    <div v-if="dashboard" class="content">
      <!-- 顶部概览 -->
      <el-row :gutter="20" class="overview">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-label">综合健康度</div>
            <div class="stat-value" :class="'text-' + dashboard.overall_status">
              {{ dashboard.health_score }}
            </div>
            <div class="stat-unit">分</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-label">业态</div>
            <div class="stat-value">{{ dashboard.biz_type_name }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-label">活跃预警</div>
            <div class="stat-value text-red">{{ dashboard.active_alerts.length }}</div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-label">数据日期</div>
            <div class="stat-value small">{{ dashboard.record_date }}</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 指标红绿灯面板 -->
      <el-card class="section-card">
        <template #header><h3>🚦 核心指标红绿灯</h3></template>
        <TrafficLightPanel :indicators="dashboard.indicators" />
      </el-card>

      <!-- 指标趋势图 -->
      <el-card class="section-card">
        <template #header><h3>📈 指标趋势</h3></template>
        <IndicatorChart :store-id="storeId" />
      </el-card>

      <!-- 六大保命条件 -->
      <el-card class="section-card">
        <template #header><h3>🛡️ 单店模型六大连命条件</h3></template>
        <el-table :data="survivalList" stripe>
          <el-table-column prop="name" label="条件" width="200" />
          <el-table-column prop="rule" label="标准" width="200" />
          <el-table-column prop="value" label="当前值" width="150" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.pass ? 'success' : 'danger'">
                {{ row.pass ? '✅ 达标' : '❌ 未达标' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 活跃预警 -->
      <el-card v-if="dashboard.active_alerts.length" class="section-card">
        <template #header><h3>⚠️ 活跃预警</h3></template>
        <el-table :data="dashboard.active_alerts" stripe>
          <el-table-column label="等级" width="80">
            <template #default="{ row }">
              <el-tag :type="row.level === 'red' ? 'danger' : 'warning'">
                {{ row.level === 'red' ? '🔴 紧急' : '🟡 警告' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="rule_name" label="预警项" />
          <el-table-column prop="indicator_value" label="当前值" width="120" />
          <el-table-column prop="threshold" label="阈值" width="120" />
          <el-table-column prop="alert_date" label="日期" width="120" />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getDashboard } from '../api'
import TrafficLightPanel from '../components/TrafficLightPanel.vue'
import IndicatorChart from '../components/IndicatorChart.vue'

const route = useRoute()
const storeId = computed(() => route.params.id)
const dashboard = ref(null)
const loading = ref(false)

const survivalList = computed(() => {
  if (!dashboard.value?.survival_check) return []
  return Object.entries(dashboard.value.survival_check).map(([key, val]) => ({
    key,
    name: val.name,
    rule: val.rule,
    value: val.value || val.note || '--',
    pass: val.pass,
  }))
})

const loadData = async () => {
  loading.value = true
  try {
    const { data } = await getDashboard(storeId.value)
    dashboard.value = data
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.store-detail { padding: 20px; }
.overview { margin: 20px 0; }
.stat-card { text-align: center; padding: 10px; }
.stat-label { color: #999; font-size: 13px; }
.stat-value { font-size: 32px; font-weight: bold; margin: 8px 0; }
.stat-value.small { font-size: 18px; }
.stat-unit { color: #999; font-size: 13px; }
.text-green { color: #67c23a; }
.text-yellow { color: #e6a23c; }
.text-red { color: #f56c6c; }
.section-card { margin-bottom: 20px; }
.section-card h3 { margin: 0; }
</style>
