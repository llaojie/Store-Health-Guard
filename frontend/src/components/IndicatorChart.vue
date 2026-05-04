<template>
  <div class="indicator-chart" ref="chartRef" style="height: 400px;"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { getIndicatorHistory } from '../api'

const props = defineProps({ storeId: { type: [String, Number], required: true } })
const chartRef = ref(null)
let chart = null

const initChart = async () => {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)

  try {
    const { data } = await getIndicatorHistory(props.storeId, 30)
    const dates = data.map(d => d.date)

    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['日营业额', '毛利率', '人力成本占比', '盈亏平衡点'] },
      grid: { left: 60, right: 60, bottom: 40 },
      xAxis: { type: 'category', data: dates },
      yAxis: [
        { type: 'value', name: '营业额(元)', position: 'left' },
        { type: 'value', name: '比率(%)', position: 'right', axisLabel: { formatter: v => (v * 100).toFixed(0) + '%' } },
      ],
      series: [
        {
          name: '日营业额', type: 'bar', data: data.map(d => d.daily_revenue),
          itemStyle: { color: '#409eff' },
        },
        {
          name: '盈亏平衡点', type: 'line', data: data.map(d => d.breakeven_point),
          lineStyle: { type: 'dashed', color: '#f56c6c' }, symbol: 'none',
        },
        {
          name: '毛利率', type: 'line', yAxisIndex: 1,
          data: data.map(d => d.gross_margin),
          itemStyle: { color: '#67c23a' },
        },
        {
          name: '人力成本占比', type: 'line', yAxisIndex: 1,
          data: data.map(d => d.labor_cost_rate),
          itemStyle: { color: '#e6a23c' },
        },
      ],
    })
  } catch (e) {
    console.error('加载图表数据失败', e)
  }
}

onMounted(initChart)
watch(() => props.storeId, initChart)
</script>
