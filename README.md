# Store Health Guard 🏥

> 餐饮门店健康度预警系统 — 基于10大核心指标体系，实现门店经营数据监测、分级预警、智能诊断

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Vue](https://img.shields.io/badge/Vue-3.5+-green.svg)](https://vuejs.org)

## 📸 系统预览

> 💡 **在线体验**: 下载 [demo.html](demo.html) 双击打开即可在浏览器中体验完整界面，无需安装任何环境！

```
┌──────────────────────────────────────────────────────┐
│  🏥 门店健康卫士    门店总览 │ 预警中心 │ 诊断工具   │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                │
│  │XX茶饮·万象城│ │XX咖啡·科技园│ │XX快餐·福田│  [+添加门店] │
│  │ 92分 🟢  │ │ 78分 🟡  │ │ 45分 🔴  │                │
│  └─────────┘ └─────────┘ └─────────┘                │
│                                                      │
│  🚦 核心指标红绿灯                                    │
│  🟢营业额  🟢TC  🟡AC  🟢食材率  🔴人力率  🟢租金率    │
│                                                      │
│  📈 指标趋势 (30天)                                   │
│  ▇▇▆▇▅▆▇▇▆▅  ← 营业额 vs 盈亏平衡线               │
│                                                      │
│  🛡️ 六大保命条件: ✅✅❌✅✅✅                         │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## 🎯 核心功能

### 1. 10大核心指标监测
基于餐杰咨询门店经营指标体系，覆盖四大维度：

| 维度 | 指标 |
|------|------|
| 收入类 | 营业额、交易单数(TC)、客单价(AC) |
| 成本类 | 食材成本率、人力成本占比、租金成本占比 |
| 效率类 | 翻台率、坪效、营收人效、出餐超时率 |
| 盈利类 | 毛利率、净利润率、同店增长率(SSSG) |

### 2. 三级预警机制
- 🔴 **红灯（紧急）**：2小时内上报，如毛利率<45%、人力成本>30%
- 🟡 **黄灯（警告）**：当日整改，如人力成本20%-25%、食材率连续3期上涨
- 🟢 **绿灯（健康）**：常规月度复盘

### 3. 智能诊断工具
- **快速生死诊断**：5分钟算出盈亏平衡点与安全边际
- **5Why根因分析**：预设行业模板，连续追问直达管理根源
- **人效体检矩阵**：四象限定位（精益区/肥胖区/贫血区/急救区）

### 4. 多业态支持
内置快餐、茶饮、咖啡、小吃、火锅五种业态的差异化阈值：

| 业态 | 毛利率健康区间 | 人效健康线 | 人效标杆 |
|------|--------------|-----------|---------|
| 茶饮 | 53%-62% | ≥200元/时 | 行业标杆 283 |
| 咖啡 | 65%-75% | ≥180元/时 | 行业标杆 220 |
| 快餐 | 58%-64% | ≥180元/时 | 行业标杆 237 |
| 火锅 | 55%-65% | ≥130元/时 | 行业标杆 206 |

### 5. 单店模型六大保命条件
自动检查：悲观预估(70/80原则) → 综合毛利率≥65% → 租金<15% → 人力<20% → 半变动<6% → 投入<0.5万/㎡

## 🛠 技术栈

```
后端: Python 3.10+ / FastAPI / SQLAlchemy / PyYAML
前端: Vue 3 / Element Plus / ECharts / Vite
数据库: SQLite(开发) / PostgreSQL(生产)
部署: Docker / docker-compose
```

## 🚀 快速开始

### 方式一：Docker 一键启动（推荐）

```bash
git clone https://github.com/your-username/store-health-guard.git
cd store-health-guard
docker-compose up -d
```

访问: http://localhost:3000

### 方式二：本地开发

```bash
# 启动后端
cd backend
pip install -r requirements.txt
python data/seed.py    # 初始化种子数据
python main.py         # 启动 API 服务 → http://localhost:8000

# 启动前端
cd frontend
npm install
npm run dev            # 启动前端 → http://localhost:3000
```

## 📁 项目结构

```
store-health-guard/
├── backend/
│   ├── main.py                  # FastAPI 入口
│   ├── requirements.txt
│   ├── config/
│   │   ├── biz_types.yaml       # 📋 业态参考值 & 预警规则配置
│   │   └── database.py
│   ├── models/
│   │   └── store.py             # SQLAlchemy 数据模型
│   ├── schemas/
│   │   └── store.py             # Pydantic 请求/响应模型
│   ├── services/
│   │   ├── health_engine.py     # 🧠 健康度计算引擎
│   │   ├── alert_engine.py      # 🔔 预警引擎
│   │   ├── diagnosis.py         # 🔬 诊断工具（生死诊断/5Why/人效矩阵）
│   │   └── store_service.py     # CRUD
│   ├── api/
│   │   ├── stores.py            # 门店管理 API
│   │   ├── health.py            # 健康度监测 API
│   │   ├── alerts.py            # 预警管理 API
│   │   └── diagnosis.py         # 诊断工具 API
│   └── data/
│       └── seed.py              # 种子数据
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.vue
│       ├── router/
│       ├── views/
│       │   ├── Dashboard.vue    # 门店总览
│       │   ├── StoreDetail.vue  # 门店健康仪表盘
│       │   ├── AlertCenter.vue  # 预警中心
│       │   └── Diagnosis.vue    # 诊断工具
│       ├── components/
│       │   ├── TrafficLightPanel.vue  # 红绿灯面板
│       │   └── IndicatorChart.vue     # 指标趋势图
│       └── api/
│           └── index.js
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 📡 API 文档

启动后端后访问: http://localhost:8000/api/docs

核心接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stores` | 门店列表 |
| POST | `/api/stores` | 创建门店 |
| GET | `/api/health/dashboard/{store_id}` | 门店健康度仪表盘 |
| POST | `/api/health/indicators` | 录入指标数据（自动触发预警） |
| GET | `/api/health/history/{store_id}` | 指标历史趋势 |
| GET | `/api/alerts` | 预警列表 |
| PUT | `/api/alerts/{id}/resolve` | 处理预警 |
| POST | `/api/diagnosis/breakeven` | 盈亏平衡点计算 |
| POST | `/api/diagnosis/five-why` | 5Why根因分析 |
| POST | `/api/diagnosis/efficiency-matrix` | 人效体检矩阵 |

## 🔧 自定义配置

### 修改业态阈值

编辑 `backend/config/biz_types.yaml`，为每个业态调整指标的健康值/警戒值/危险值区间：

```yaml
biz_types:
  tea_drink:
    indicators:
      food_cost_rate:
        healthy: [0.35, 0.45]    # 健康区间
        warning: [0.45, 0.50]    # 警戒区间
        danger: [0.50, 1.0]      # 危险区间
```

### 修改预警规则

在同一文件中编辑 `alert_rules` 部分：

```yaml
alert_rules:
  red:
    - id: "R001"
      name: "营业额低于盈亏平衡点"
      indicator: "daily_revenue"
      condition: "value < breakeven_point"
      response_time: "2h"
```

### 切换数据库

```bash
# 开发环境（默认 SQLite）
DATABASE_URL=sqlite:///./store_health.db

# 生产环境（PostgreSQL）
DATABASE_URL=postgresql://user:password@localhost:5432/store_health
```

## 📐 核心公式速查

```
净利润 = (TC × AC × 毛利率) - 固定成本
日盈亏平衡点 = 月固定成本 ÷ 综合毛利率 ÷ 30天
安全边际 = (实际营业额 - 盈亏平衡点) ÷ 盈亏平衡点
毛利率 = (营业额 - 食材成本) ÷ 营业额
营收人效 = 月度总营收 ÷ 总工时
成本红线 = 人力 + 租金 + 水电燃杂 + 食材成本 ≤ 营业额70%
```

## 🙏 致谢

指标体系与行业数据来源于：
- 餐杰咨询《门店经营必修课：10大核心指标与数据化管控实战指南》
- 餐饮行业公开经营指标与标杆数据

## 📄 License

[MIT License](LICENSE)

---

**⭐ 如果这个项目对你有帮助，欢迎 Star！**
