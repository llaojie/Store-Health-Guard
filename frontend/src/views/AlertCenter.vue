<template>
  <div class="alert-center" v-loading="loading">
    <h1>🔔 预警中心</h1>

    <!-- 筛选 -->
    <el-form :inline="true" class="filter-form">
      <el-form-item label="预警等级">
        <el-select v-model="filters.level" clearable placeholder="全部">
          <el-option label="🔴 紧急" value="red" />
          <el-option label="🟡 警告" value="yellow" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="filters.status" clearable placeholder="全部">
          <el-option label="待处理" value="open" />
          <el-option label="处理中" value="processing" />
          <el-option label="已解决" value="resolved" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="loadAlerts">查询</el-button>
      </el-form-item>
    </el-form>

    <!-- 预警列表 -->
    <el-table :data="alerts" stripe>
      <el-table-column label="等级" width="100">
        <template #default="{ row }">
          <el-tag :type="row.level === 'red' ? 'danger' : 'warning'" effect="dark">
            {{ row.level === 'red' ? '🔴 紧急' : '🟡 警告' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="rule_id" label="规则ID" width="80" />
      <el-table-column prop="rule_name" label="预警名称" min-width="200" />
      <el-table-column prop="indicator" label="指标" width="150" />
      <el-table-column label="当前值" width="100">
        <template #default="{ row }">
          {{ row.indicator_value != null ? (row.indicator_value * 100).toFixed(1) + '%' : '--' }}
        </template>
      </el-table-column>
      <el-table-column prop="alert_date" label="日期" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.status === 'open'" size="small" type="primary" @click="openResolve(row)">
            处理
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 处理对话框 -->
    <el-dialog v-model="showResolveDialog" title="处理预警" width="500px">
      <el-form :model="resolveForm" label-width="100px">
        <el-form-item label="根因分析">
          <el-input v-model="resolveForm.root_cause" type="textarea" :rows="4" placeholder="5Why分析结果..." />
        </el-form-item>
        <el-form-item label="改善计划">
          <el-input v-model="resolveForm.action_plan" type="textarea" :rows="4" placeholder="SMART改善计划..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showResolveDialog = false">取消</el-button>
        <el-button type="primary" @click="doResolve">确认处理</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { getAlerts, resolveAlert } from '../api'

const alerts = ref([])
const loading = ref(false)
const showResolveDialog = ref(false)
const currentAlert = ref(null)

const filters = reactive({ level: '', status: 'open' })
const resolveForm = reactive({ root_cause: '', action_plan: '' })

const statusType = (s) => ({ open: 'danger', processing: 'warning', resolved: 'success', closed: 'info' }[s] || '')
const statusLabel = (s) => ({ open: '待处理', processing: '处理中', resolved: '已解决', closed: '已关闭' }[s] || s)

const loadAlerts = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.level) params.level = filters.level
    if (filters.status) params.status = filters.status
    const { data } = await getAlerts(params)
    alerts.value = data
  } finally {
    loading.value = false
  }
}

const openResolve = (alert) => {
  currentAlert.value = alert
  resolveForm.root_cause = ''
  resolveForm.action_plan = ''
  showResolveDialog.value = true
}

const doResolve = async () => {
  if (!currentAlert.value) return
  await resolveAlert(currentAlert.value.id, resolveForm)
  showResolveDialog.value = false
  loadAlerts()
}

onMounted(loadAlerts)
</script>

<style scoped>
.alert-center { padding: 20px; }
.filter-form { margin: 16px 0; }
</style>
