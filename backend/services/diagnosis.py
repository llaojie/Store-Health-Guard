"""诊断工具 - 快速生死诊断、5Why根因分析、人效体检矩阵"""
import yaml
from pathlib import Path
from typing import List, Optional


def load_biz_config() -> dict:
    config_path = Path(__file__).parent.parent / "config" / "biz_types.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


CONFIG = load_biz_config()


# ========== 快速生死诊断 ==========

def calc_breakeven(monthly_rent: float, monthly_labor: float,
                   monthly_utility: float, gross_margin: float,
                   daily_revenue: Optional[float] = None) -> dict:
    """计算盈亏平衡点与安全边际

    Args:
        monthly_rent: 月租金
        monthly_labor: 月人工成本
        monthly_utility: 月水电杂费
        gross_margin: 综合毛利率 (如 0.4)
        daily_revenue: 实际日营业额 (可选)

    Returns:
        {daily_fixed_cost, breakeven_point, actual_revenue, safety_margin, status}
    """
    if gross_margin <= 0:
        return {"error": "毛利率必须大于0"}

    daily_fixed_cost = (monthly_rent + monthly_labor + monthly_utility) / 30
    breakeven_point = daily_fixed_cost / gross_margin

    result = {
        "daily_fixed_cost": round(daily_fixed_cost, 2),
        "breakeven_point": round(breakeven_point, 2),
    }

    if daily_revenue is not None:
        safety_margin = (daily_revenue - breakeven_point) / breakeven_point
        result["actual_revenue"] = daily_revenue
        result["safety_margin"] = round(safety_margin, 4)

        if safety_margin >= 0.3:
            result["status"] = "green"
        elif safety_margin >= 0:
            result["status"] = "yellow"
        else:
            result["status"] = "red"

    return result


# ========== 5Why 根因分析 ==========

# 预设的5Why分析模板（基于餐饮行业常见问题）
FIVE_WHY_TEMPLATES = {
    "food_cost_rate": {
        "problem": "食材成本率超标",
        "steps": [
            {"question": "为什么食材成本率超标？", "answer": "食材损耗/浪费严重"},
            {"question": "为什么食材损耗严重？", "answer": "订货量经常超出实际消耗"},
            {"question": "为什么订货量超出消耗？", "answer": "缺乏科学的订货预估工具"},
            {"question": "为什么缺乏订货工具？", "answer": "店长未掌握千元用量订货法"},
            {"question": "为什么店长未掌握？", "answer": "总部未纳入店长必修考核"},
        ],
        "root_cause": "总部培训体系缺失，千元用量订货法未纳入店长考核",
        "smart_action": "30天内引入千元用量订货法，完成全员培训，将鲜果月度损耗率从8%降至5%以内"
    },
    "labor_cost_rate": {
        "problem": "人力成本占比超标",
        "steps": [
            {"question": "为什么人力成本占比超标？", "answer": "排班不合理，闲时人员过多"},
            {"question": "为什么排班不合理？", "answer": "排班凭经验，未参考小时级营业额预测"},
            {"question": "为什么未参考预测？", "answer": "缺乏智能排班工具和数据"},
            {"question": "为什么缺乏工具？", "answer": "门店未部署数字化排班系统"},
            {"question": "为什么未部署？", "answer": "总部对数字化投入优先级不足"},
        ],
        "root_cause": "数字化排班系统缺失，排班仍靠经验",
        "smart_action": "60天内上线智能排班模块，以人效≥业态健康线为目标，将人力成本占比降至20%以内"
    },
    "gross_margin": {
        "problem": "毛利率低于警戒线",
        "steps": [
            {"question": "为什么毛利率低于警戒线？", "answer": "产品定价无法覆盖食材成本"},
            {"question": "为什么定价无法覆盖？", "answer": "折扣促销力度过大/低价外卖占比过高"},
            {"question": "为什么折扣力度大？", "answer": "为冲营业额盲目做活动，未算ROI"},
            {"question": "为什么未算ROI？", "answer": "缺乏促销效果评估机制"},
            {"question": "为什么缺乏评估机制？", "answer": "运营团队未建立促销ROI核算流程"},
        ],
        "root_cause": "促销活动缺乏ROI核算，盲目打折侵蚀毛利",
        "smart_action": "立即暂停无效促销，建立促销ROI评估机制，毛利率低于45%的活动不予审批"
    },
    "turnover_rate": {
        "problem": "翻台率持续偏低",
        "steps": [
            {"question": "为什么翻台率偏低？", "answer": "客流量不足，空台率高"},
            {"question": "为什么客流量不足？", "answer": "门店营销吸引力下降，老客流失"},
            {"question": "为什么老客流失？", "answer": "产品创新不足，消费体验下降"},
            {"question": "为什么产品创新不足？", "answer": "未建立周期性上新机制"},
            {"question": "为什么未建立上新机制？", "answer": "研发与门店运营脱节"},
        ],
        "root_cause": "产品研发与门店运营脱节，缺乏周期性上新机制",
        "smart_action": "建立月度上新流程，结合千元用量优化产品结构，通过流量新品提升TC"
    },
    "daily_revenue": {
        "problem": "营业额低于盈亏平衡点",
        "steps": [
            {"question": "为什么营业额低于盈亏平衡点？", "answer": "日均客流严重不足"},
            {"question": "为什么客流不足？", "answer": "选址偏差/商圈衰退/竞对分流"},
            {"question": "为什么选址出现偏差？", "answer": "选址时未做充分的商圈调研"},
            {"question": "为什么未充分调研？", "answer": "开发流程缺乏数据化选址标准"},
            {"question": "为什么缺乏标准？", "answer": "总部开发体系不完善"},
        ],
        "root_cause": "选址模型缺陷，开发流程缺乏数据化标准",
        "smart_action": "立即评估门店止损可行性；如可挽救，30天内启动地推+会员储值双线引流"
    },
}


def get_five_why_template(indicator: str) -> dict:
    """获取5Why分析模板"""
    return FIVE_WHY_TEMPLATES.get(indicator, {
        "problem": "指标异常",
        "steps": [
            {"question": "为什么该指标异常？", "answer": "（请填写）"},
            {"question": "为什么？", "answer": "（请填写）"},
            {"question": "为什么？", "answer": "（请填写）"},
            {"question": "为什么？", "answer": "（请填写）"},
            {"question": "为什么？", "answer": "（请填写）"},
        ],
        "root_cause": "（请根据5Why追问填写根因）",
        "smart_action": "（请制定SMART改善计划）"
    })


# ========== 人效体检矩阵 ==========

def evaluate_efficiency_matrix(revenue_per_labor_hour: float,
                                labor_cost_rate: float,
                                biz_type: str = "tea_drink") -> dict:
    """评估人效体检矩阵象限

    以「营收人效」和「人力成本占比」为双轴，四象限分类:
    A区(精益区): 人效高+成本低 → 维持+冲刺标杆
    B区(肥胖区): 人效高+成本高 → 立即优化编制
    C区(贫血区): 人效低+成本低 → 警惕服务崩塌
    D区(急救区): 人效低+成本高 → 限时重组方案
    """
    biz_cfg = CONFIG.get("biz_types", {}).get(biz_type, {})
    ind_cfg = biz_cfg.get("indicators", {}).get("revenue_per_labor_hour", {})

    healthy_line = ind_cfg.get("healthy_line", 180)
    death_line = ind_cfg.get("death_line", 120)
    benchmark = ind_cfg.get("benchmark", 250)

    revenue_high = revenue_per_labor_hour >= healthy_line
    cost_high = labor_cost_rate > 0.20

    if revenue_high and not cost_high:
        quadrant = "lean"
        quadrant_name = "A区·精益区"
        diagnosis = f"人效{revenue_per_labor_hour}元/时(≥{healthy_line})，成本{labor_cost_rate*100:.1f}%(<20%)，运营效率优秀"
        action = f"维持现状，冲刺标杆值{benchmark}元/时；探索智能排班进一步提效"
    elif revenue_high and cost_high:
        quadrant = "obese"
        quadrant_name = "B区·肥胖区"
        diagnosis = f"人效{revenue_per_labor_hour}元/时(≥{healthy_line})，但成本{labor_cost_rate*100:.1f}%(>20%)，编制冗余"
        action = "立即优化编制，推进通岗并岗，用智能排班压缩无效工时"
    elif not revenue_high and not cost_high:
        quadrant = "anemic"
        quadrant_name = "C区·贫血区"
        diagnosis = f"人效仅{revenue_per_labor_hour}元/时(<{healthy_line})，成本{labor_cost_rate*100:.1f}%(<20%)，营收不足"
        action = "警惕服务崩塌，核心是提营收：推流量新品+会员储值+线上评分提升"
    else:
        quadrant = "emergency"
        quadrant_name = "D区·急救区"
        diagnosis = f"人效仅{revenue_per_labor_hour}元/时(<{healthy_line})，成本{labor_cost_rate*100:.1f}%(>20%)，双重恶化"
        action = "限时请专家制定重组方案：同时压编制+提营收，7天内出改善方案"

    return {
        "quadrant": quadrant,
        "quadrant_name": quadrant_name,
        "revenue_level": "high" if revenue_high else "low",
        "cost_level": "high" if cost_high else "low",
        "diagnosis": diagnosis,
        "action": action,
        "reference": {
            "death_line": death_line,
            "healthy_line": healthy_line,
            "benchmark": benchmark,
        }
    }
