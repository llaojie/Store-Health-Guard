<template>
  <div class="diagnosis-page">
    <h1>🔬 诊断工具</h1>

    <el-tabs v-model="activeTab">
      <!-- 快速生死诊断 -->
      <el-tab-pane label="快速生死诊断" name="breakeven">
        <el-card>
          <template #header><h3>💰 盈亏平衡点计算器</h3></template>
          <p class="desc">输入核心数据，1分钟算出门店"生死账"</p>
          <el-form :model="beForm" label-width="130px" class="diag-form">
            <el-form-item label="月租金(元)">
              <el-input-number v-model="beForm.monthly_rent" :step="1000" :min="0" />
            </el-form-item>
            <el-form-item label="月人工成本(元)">
              <el-input-number v-model="beForm.monthly_labor" :step="1000" :min="0" />
            </el-form-item>
            <el-form-item label="月水电杂费(元)">
              <el-input-number v-model="beForm.monthly_utility" :step="500" :min="0" />
            </el-form-item>
            <el-form-item label="综合毛利率">
              <el-input-number v-model="beForm.gross_margin" :min="0.01" :max="0.99" :step="0.01" :precision="2" />
            </el-form-item>
            <el-form-item label="实际日营业额(元)">
              <el-input-number v-model="beForm.daily_revenue" :step="500" :min="0" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="calcBE">计算</el-button>
            </el-form-item>
          </el-form>

          <div v-if="beResult" class="result-box" :class="'result-' + beResult.status">
            <h4>诊断结果</h4>
            <p>日固定成本: <strong>{{ beResult.daily_fixed_cost.toLocaleString() }}</strong> 元</p>
            <p>日盈亏平衡点: <strong>{{ beResult.breakeven_point.toLocaleString() }}</strong> 元</p>
            <p v-if="beResult.actual_revenue != null">
              实际日营业额: <strong>{{ beResult.actual_revenue.toLocaleString() }}</strong> 元
            </p>
            <p v-if="beResult.safety_margin != null">
              安全边际: <strong>{{ (beResult.safety_margin * 100).toFixed(1) }}%</strong>
            </p>
            <el-tag v-if="beResult.status" :type="beStatusType" size="large" effect="dark">
              {{ beStatusLabel }}
            </el-tag>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 5Why根因分析 -->
      <el-tab-pane label="5Why根因分析" name="fiveWhy">
        <el-card>
          <template #header><h3>🔍 5Why根因分析</h3></template>
          <el-form :model="fwForm" label-width="100px" class="diag-form">
            <el-form-item label="异常指标">
              <el-select v-model="fwForm.indicator" @change="onIndicatorChange">
                <el-option
                  v-for="item in fwIndicators"
                  :key="item.indicator"
                  :label="item.problem"
                  :value="item.indicator"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="问题描述">
              <el-input v-model="fwForm.problem" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="doFiveWhy">分析</el-button>
            </el-form-item>
          </el-form>

          <div v-if="fwResult" class="result-box">
            <h4>5Why 追问链</h4>
            <el-timeline>
              <el-timeline-item
                v-for="step in fwResult.steps"
                :key="step.step"
                :timestamp="'第' + step.step + '问'"
                placement="top"
              >
                <p class="fw-q">❓ {{ step.question }}</p>
                <p class="fw-a">💡 {{ step.answer }}</p>
              </el-timeline-item>
            </el-timeline>
            <el-divider />
            <p><strong>🎯 根因:</strong> {{ fwResult.root_cause }}</p>
            <p><strong>📋 SMART行动:</strong> {{ fwResult.smart_action }}</p>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 人效体检矩阵 -->
      <el-tab-pane label="人效体检矩阵" name="matrix">
        <el-card>
          <template #header><h3>📊 人效体检矩阵</h3></template>
          <el-form :model="mxForm" label-width="130px" class="diag-form">
            <el-form-item label="营收人效(元/时)">
              <el-input-number v-model="mxForm.revenue_per_labor_hour" :step="10" :min="0" />
            </el-form-item>
            <el-form-item label="人力成本占比">
              <el-input-number v-model="mxForm.labor_cost_rate" :min="0" :max="1" :step="0.01" :precision="2" />
            </el-form-item>
            <el-form-item label="业态">
              <el-select v-model="mxForm.biz_type">
                <el-option label="茶饮" value="tea_drink" />
                <el-option label="咖啡" value="coffee" />
                <el-option label="快餐" value="fast_food" />
                <el-option label="火锅" value="hotpot" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="doMatrix">诊断</el-button>
            </el-form-item>
          </el-form>

          <div v-if="mxResult" class="result-box" :class="'result-' + mxResult.quadrant">
            <h4>{{ mxResult.quadrant_name }}</h4>
            <p>{{ mxResult.diagnosis }}</p>
            <p><strong>👉 行动建议:</strong> {{ mxResult.action }}</p>
            <div class="ref-values" v-if="mxResult.reference">
              <span>死亡线: {{ mxResult.reference.death_line }}元/时</span> |
              <span>健康线: {{ mxResult.reference.healthy_line }}元/时</span> |
              <span>标杆值: {{ mxResult.reference.benchmark }}元/时</span>
            </div>
          </div>

          <!-- 四象限图 -->
          <div class="matrix-visual">
            <div class="matrix-grid">
              <div class="cell lean" :class="{ active: mxResult?.quadrant === 'lean' }">A区·精益区<br/>维持+冲刺标杆</div>
              <div class="cell obese" :class="{ active: mxResult?.quadrant === 'obese' }">B区·肥胖区<br/>立即优化编制</div>
              <div class="cell anemic" :class="{ active: mxResult?.quadrant === 'anemic' }">C区·贫血区<br/>警惕服务崩塌</div>
              <div class="cell emergency" :class="{ active: mxResult?.quadrant === 'emergency' }">D区·急救区<br/>限时重组方案</div>
            </div>
            <div class="axis-label y-axis">人效 ↑</div>
            <div class="axis-label x-axis">人力成本占比 →</div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { calcBreakeven, fiveWhyAnalysis, efficiencyMatrix, getFiveWhyIndicators } from '../api'

const activeTab = ref('breakeven')

// ===== 盈亏平衡 =====
const beForm = reactive({
  monthly_rent: 30000, monthly_labor: 45000,
  monthly_utility: 12000, gross_margin: 0.40, daily_revenue: 8000
})
const beResult = ref(null)
const beStatusType = computed(() => ({ green: 'success', yellow: 'warning', red: 'danger' }[beResult.value?.status] || ''))
const beStatusLabel = computed(() => ({ green: '🟢 健康', yellow: '🟡 警戒', red: '🔴 危险' }[beResult.value?.status] || ''))

const calcBE = async () => {
  const { data } = await calcBreakeven(beForm)
  beResult.value = data
}

// ===== 5Why =====
const fwForm = reactive({ indicator: 'food_cost_rate', problem: '' })
const fwIndicators = ref([])
const fwResult = ref(null)

const onIndicatorChange = (val) => {
  const found = fwIndicators.value.find(i => i.indicator === val)
  if (found) fwForm.problem = found.problem
}

const doFiveWhy = async () => {
  const { data } = await fiveWhyAnalysis(fwForm)
  fwResult.value = data
}

// ===== 人效矩阵 =====
const mxForm = reactive({ revenue_per_labor_hour: 200, labor_cost_rate: 0.22, biz_type: 'tea_drink' })
const mxResult = ref(null)

const doMatrix = async () => {
  const { data } = await efficiencyMatrix(mxForm)
  mxResult.value = data
}

onMounted(async () => {
  try {
    const { data } = await getFiveWhyIndicators()
    fwIndicators.value = data
    if (data.length) { fwForm.indicator = data[0].indicator; fwForm.problem = data[0].problem }
  } catch {}
})
</script>

<style scoped>
.diagnosis-page { padding: 20px; }
.desc { color: #666; font-size: 13px; margin-bottom: 16px; }
.diag-form { max-width: 500px; }
.result-box { margin-top: 20px; padding: 20px; border-radius: 8px; background: #f8f9fa; }
.result-green { border-left: 4px solid #67c23a; }
.result-yellow { border-left: 4px solid #e6a23c; }
.result-red, .result-emergency { border-left: 4px solid #f56c6c; }
.result-lean { border-left: 4px solid #67c23a; }
.result-obese { border-left: 4px solid #e6a23c; }
.result-anemic { border-left: 4px solid #409eff; }
.fw-q { color: #409eff; margin: 4px 0; }
.fw-a { color: #333; margin: 4px 0; font-weight: 500; }
.matrix-visual { margin-top: 30px; position: relative; }
.matrix-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2px; max-width: 400px; }
.cell { padding: 20px; text-align: center; font-size: 13px; border-radius: 4px; opacity: 0.5; transition: all 0.3s; }
.cell.active { opacity: 1; transform: scale(1.05); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
.lean { background: #e1f3d8; }
.obese { background: #faecd8; }
.anemic { background: #d9ecff; }
.emergency { background: #fde2e2; }
.axis-label { color: #999; font-size: 12px; }
.y-axis { position: absolute; left: -20px; top: 50%; transform: rotate(-90deg); }
.x-axis { text-align: center; margin-top: 8px; }
.ref-values { margin-top: 10px; color: #888; font-size: 12px; }
.ref-values span { margin: 0 8px; }
</style>
