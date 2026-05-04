<template>
  <div class="traffic-light-panel">
    <el-row :gutter="12">
      <el-col :span="4" v-for="ind in indicators" :key="ind.name">
        <div class="light-card" :class="'border-' + ind.level">
          <div class="light-dot" :class="'dot-' + ind.level"></div>
          <div class="ind-name">{{ getMeta(ind.name)?.name || ind.name }}</div>
          <div class="ind-value">
            {{ formatValue(ind.value, ind.name) }}
            <span class="ind-unit">{{ ind.unit }}</span>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
const props = defineProps({ indicators: { type: Array, default: () => [] } })

const META = {
  daily_revenue: { name: '日营业额' },
  tc: { name: '交易单数' },
  ac: { name: '客单价' },
  food_cost_rate: { name: '食材成本率' },
  labor_cost_rate: { name: '人力成本占比' },
  rent_cost_rate: { name: '租金占比' },
  turnover_rate: { name: '翻台率' },
  ping_efficiency_daily: { name: '日坪效' },
  revenue_per_labor_hour: { name: '营收人效' },
  gross_margin: { name: '毛利率' },
  net_margin: { name: '净利润率' },
  sssg: { name: '同店增长率' },
}

const getMeta = (key) => META[key] || null

const formatValue = (val, key) => {
  if (val == null) return '--'
  const rateKeys = ['food_cost_rate', 'labor_cost_rate', 'rent_cost_rate', 'gross_margin', 'net_margin', 'overtime_rate', 'sssg']
  if (rateKeys.includes(key)) return (val * 100).toFixed(1) + '%'
  if (key === 'daily_revenue' || key === 'ac' || key === 'ping_efficiency_daily' || key === 'revenue_per_labor_hour') return val.toLocaleString()
  return val
}
</script>

<style scoped>
.traffic-light-panel { margin: 10px 0; }
.light-card { padding: 12px 8px; text-align: center; border-radius: 8px; border: 2px solid #ddd; transition: all 0.3s; }
.border-green { border-color: #67c23a; background: #f0f9eb; }
.border-yellow { border-color: #e6a23c; background: #fdf6ec; }
.border-red { border-color: #f56c6c; background: #fef0f0; }
.light-dot { width: 14px; height: 14px; border-radius: 50%; margin: 0 auto 8px; }
.dot-green { background: #67c23a; }
.dot-yellow { background: #e6a23c; animation: pulse 2s infinite; }
.dot-red { background: #f56c6c; animation: pulse 1s infinite; }
.ind-name { font-size: 11px; color: #666; margin-bottom: 4px; white-space: nowrap; }
.ind-value { font-size: 18px; font-weight: bold; color: #333; }
.ind-unit { font-size: 11px; color: #999; font-weight: normal; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
</style>
