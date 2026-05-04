"""健康度计算引擎 - 核心业务逻辑

根据业态配置的阈值，计算每个指标的健康状态，并汇总门店综合健康度评分。
"""
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from schemas.store import IndicatorHealth, IndicatorOut


def load_biz_config() -> dict:
    """加载业态配置"""
    config_path = Path(__file__).parent.parent / "config" / "biz_types.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


CONFIG = load_biz_config()


def get_biz_type_name(biz_type: str) -> str:
    """获取业态中文名"""
    biz = CONFIG.get("biz_types", {}).get(biz_type, {})
    return biz.get("name", biz_type)


def _get_indicator_config(biz_type: str, indicator_name: str) -> dict:
    """获取某业态下某指标的配置"""
    biz = CONFIG.get("biz_types", {}).get(biz_type, {})
    return biz.get("indicators", {}).get(indicator_name, {})


def judge_rate(value: float, config: dict) -> str:
    """判断比率型指标的健康等级 (如成本率、毛利率)

    config 格式: {healthy: [low, high], warning: [low, high], danger: [low, high]}
    """
    if value is None:
        return "green"

    healthy = config.get("healthy")
    warning = config.get("warning")
    danger = config.get("danger")

    if healthy and healthy[0] <= value <= healthy[1]:
        return "green"
    if warning and warning[0] <= value <= warning[1]:
        return "yellow"
    if danger and danger[0] <= value <= danger[1]:
        return "red"

    # 如果没有精确匹配区间，做边界判断
    if healthy and value < healthy[0]:
        # 低于健康下限，可能更优也可能更差
        if indicator_is_lower_better("cost"):
            return "green"  # 成本类越低越好
        return "red"
    if healthy and value > healthy[1]:
        if indicator_is_lower_better("margin"):
            return "green"  # 毛利率越高越好
        return "red"

    return "green"


def indicator_is_lower_better(category: str) -> bool:
    """判断指标是否越低越好"""
    return category in ("cost", "rate_cost")


# 指标元数据：名称、单位、计算逻辑、评判方式
INDICATOR_META = {
    "daily_revenue": {"name": "日营业额", "unit": "元", "category": "revenue"},
    "tc": {"name": "交易单数(TC)", "unit": "单", "category": "revenue"},
    "ac": {"name": "客单价(AC)", "unit": "元", "category": "revenue"},
    "food_cost_rate": {"name": "食材成本率", "unit": "%", "category": "cost"},
    "labor_cost_rate": {"name": "人力成本占比", "unit": "%", "category": "cost"},
    "rent_cost_rate": {"name": "租金成本占比", "unit": "%", "category": "cost"},
    "turnover_rate": {"name": "翻台率", "unit": "次/天", "category": "efficiency"},
    "ping_efficiency_daily": {"name": "日坪效", "unit": "元/㎡/日", "category": "efficiency"},
    "overtime_rate": {"name": "出餐超时率", "unit": "%", "category": "efficiency"},
    "revenue_per_labor_hour": {"name": "营收人效", "unit": "元/时", "category": "efficiency"},
    "gross_margin": {"name": "毛利率", "unit": "%", "category": "profit"},
    "net_margin": {"name": "净利润率", "unit": "%", "category": "profit"},
    "net_profit": {"name": "净利润", "unit": "元", "category": "profit"},
    "sssg": {"name": "同店增长率", "unit": "%", "category": "profit"},
}


def compute_derived_indicators(record: dict, store: dict) -> dict:
    """计算派生指标

    Args:
        record: 原始录入数据
        store: 门店基础信息

    Returns:
        补充了派生字段的 record
    """
    # 食材成本率
    if record.get("food_cost") and record.get("daily_revenue"):
        record["food_cost_rate"] = round(record["food_cost"] / record["daily_revenue"], 4)

    # 客单价
    if record.get("daily_revenue") and record.get("tc"):
        record["ac"] = round(record["daily_revenue"] / record["tc"], 2)

    # 人力成本占比 (假设 labor_cost 是月度，需要换算日均)
    # 简化处理：如果录入的是日数据，labor_cost 即为日人力成本
    if record.get("labor_cost") and record.get("daily_revenue"):
        record["labor_cost_rate"] = round(record["labor_cost"] / record["daily_revenue"], 4)

    # 租金成本占比
    if store.get("monthly_rent") and record.get("daily_revenue"):
        daily_rent = store["monthly_rent"] / 30
        record["rent_cost_rate"] = round(daily_rent / record["daily_revenue"], 4)

    # 毛利率
    if record.get("daily_revenue") and record.get("food_cost"):
        record["gross_margin"] = round((record["daily_revenue"] - record["food_cost"]) / record["daily_revenue"], 4)

    # 净利润率
    if record.get("net_profit") and record.get("daily_revenue"):
        record["net_margin"] = round(record["net_profit"] / record["daily_revenue"], 4)

    # 日坪效
    if record.get("daily_revenue") and store.get("area"):
        record["ping_efficiency_daily"] = round(record["daily_revenue"] / store["area"], 2)

    # 营收人效
    if record.get("daily_revenue") and record.get("total_labor_hours"):
        record["revenue_per_labor_hour"] = round(record["daily_revenue"] / record["total_labor_hours"], 2)

    # 盈亏平衡点
    gross_margin = record.get("gross_margin") or store.get("target_gross_margin") or 0.5
    if store.get("monthly_fixed_cost") and gross_margin > 0:
        record["breakeven_point"] = round(store["monthly_fixed_cost"] / gross_margin / 30, 2)

    # 安全边际
    if record.get("daily_revenue") and record.get("breakeven_point") and record["breakeven_point"] > 0:
        record["safety_margin"] = round(
            (record["daily_revenue"] - record["breakeven_point"]) / record["breakeven_point"], 4
        )

    return record


def evaluate_indicator(biz_type: str, indicator_key: str, value: Optional[float]) -> Tuple[str, str]:
    """评估单个指标的健康等级

    Returns:
        (level, range_description)
    """
    if value is None:
        return "green", "无数据"

    cfg = _get_indicator_config(biz_type, indicator_key)
    meta = INDICATOR_META.get(indicator_key, {})
    unit = meta.get("unit", "")

    # 比率类指标（成本率、毛利率、净利润率）
    rate_indicators = {"food_cost_rate", "labor_cost_rate", "rent_cost_rate",
                       "gross_margin", "net_margin", "overtime_rate"}

    if indicator_key in rate_indicators and cfg:
        level = judge_rate(value, cfg)
        desc_parts = []
        if cfg.get("healthy"):
            desc_parts.append(f"健康: {cfg['healthy'][0]*100:.0f}%-{cfg['healthy'][1]*100:.0f}%")
        if cfg.get("warning"):
            desc_parts.append(f"警戒: {cfg['warning'][0]*100:.0f}%-{cfg['warning'][1]*100:.0f}%")
        if cfg.get("danger"):
            desc_parts.append(f"危险: {cfg['danger'][0]*100:.0f}%-{cfg['danger'][1]*100:.0f}%")
        return level, " | ".join(desc_parts)

    # 盈亏平衡点相关
    if indicator_key == "daily_revenue":
        # 通过安全边际判断
        return "green", f"当前: {value:,.0f}{unit}"

    # 人效
    if indicator_key == "revenue_per_labor_hour" and cfg:
        death = cfg.get("death_line", 0)
        healthy = cfg.get("healthy_line", 0)
        benchmark = cfg.get("benchmark", 0)
        if value < death:
            return "red", f"死亡线: <{death} | 健康: ≥{healthy} | 标杆: {benchmark}"
        elif value < healthy:
            return "yellow", f"死亡线: <{death} | 健康: ≥{healthy} | 标杆: {benchmark}"
        else:
            return "green", f"死亡线: <{death} | 健康: ≥{healthy} | 标杆: {benchmark}"

    # 同店增长率
    if indicator_key == "sssg":
        if value < -0.05:
            return "red", "健康: >0% | 警戒: -5%~0% | 危险: <-5%"
        elif value < 0:
            return "yellow", "健康: >0% | 警戒: -5%~0% | 危险: <-5%"
        else:
            return "green", "健康: >0% | 警戒: -5%~0% | 危险: <-5%"

    return "green", ""


def compute_health_score(indicators: List[IndicatorHealth]) -> Tuple[float, str]:
    """计算门店综合健康度评分

    评分规则:
    - 每个指标满分 100 分
    - green = 100, yellow = 60, red = 20
    - 加权平均（成本类和盈利类权重更高）
    - 综合等级: ≥80 green, ≥50 yellow, <50 red
    """
    if not indicators:
        return 100.0, "green"

    weight_map = {
        "daily_revenue": 15,
        "tc": 5,
        "ac": 5,
        "food_cost_rate": 12,
        "labor_cost_rate": 12,
        "rent_cost_rate": 8,
        "turnover_rate": 8,
        "ping_efficiency_daily": 5,
        "revenue_per_labor_hour": 5,
        "gross_margin": 10,
        "net_margin": 10,
        "sssg": 5,
    }

    level_score = {"green": 100, "yellow": 60, "red": 20}

    total_weight = 0
    weighted_sum = 0

    for ind in indicators:
        w = weight_map.get(ind.name, 5)
        s = level_score.get(ind.level, 100)
        weighted_sum += s * w
        total_weight += w

    score = round(weighted_sum / total_weight, 1) if total_weight > 0 else 100.0

    if score >= 80:
        return score, "green"
    elif score >= 50:
        return score, "yellow"
    else:
        return score, "red"


def check_survival_conditions(store: dict, latest_record: dict) -> dict:
    """检查单店模型六大保命条件"""
    results = {}

    # S001: 悲观性营业额预估 (70/80原则) - 需要有预估数据，简化判断
    results["S001"] = {
        "name": "悲观性营业额预估",
        "rule": "采用70/80原则",
        "pass": True,  # 需要用户输入预估数据才能判断
        "note": "需录入预估营业额进行比对"
    }

    # S002: 菜单综合毛利率 ≥65%
    gm = latest_record.get("gross_margin")
    results["S002"] = {
        "name": "菜单综合毛利率",
        "rule": "≥65%",
        "pass": gm is not None and gm >= 0.65,
        "value": f"{gm*100:.1f}%" if gm else "无数据"
    }

    # S003: 租金占比 <15%
    rcr = latest_record.get("rent_cost_rate")
    results["S003"] = {
        "name": "租金占比",
        "rule": "<15%",
        "pass": rcr is not None and rcr < 0.15,
        "value": f"{rcr*100:.1f}%" if rcr else "无数据"
    }

    # S004: 人力成本占比 <20%
    lcr = latest_record.get("labor_cost_rate")
    results["S004"] = {
        "name": "人均产值(人力成本占比)",
        "rule": "<20%",
        "pass": lcr is not None and lcr < 0.20,
        "value": f"{lcr*100:.1f}%" if lcr else "无数据"
    }

    # S005: 半变动成本占比 <6%
    results["S005"] = {
        "name": "半变动成本占比",
        "rule": "<6%",
        "pass": True,
        "note": "需录入半变动成本数据"
    }

    # S006: 综合平米投入 <0.5万元/㎡
    area = store.get("area")
    investment = store.get("total_investment")
    if area and investment:
        per_sqm = investment / area
        results["S006"] = {
            "name": "综合平米投入",
            "rule": "<0.5万元/㎡",
            "pass": per_sqm < 5000,
            "value": f"{per_sqm:.0f}元/㎡"
        }
    else:
        results["S006"] = {
            "name": "综合平米投入",
            "rule": "<0.5万元/㎡",
            "pass": True,
            "note": "需录入总投资额"
        }

    return results
