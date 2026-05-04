"""诊断工具 API - 盈亏平衡计算、5Why分析、人效体检矩阵"""
from fastapi import APIRouter
from schemas.store import (
    BreakevenInput, BreakevenResult,
    FiveWhyInput, FiveWhyResult, FiveWhyStep,
    EfficiencyMatrixInput, EfficiencyMatrixResult
)
from services.diagnosis import (
    calc_breakeven, get_five_why_template, evaluate_efficiency_matrix
)

router = APIRouter()


@router.post("/breakeven", response_model=BreakevenResult)
def calculate_breakeven(data: BreakevenInput):
    """快速生死诊断 - 计算盈亏平衡点与安全边际

    公式:
    - 日固定成本 = (月租金 + 月人工 + 月水电杂费) / 30
    - 日盈亏平衡点 = 日固定成本 / 毛利率
    - 安全边际 = (实际营业额 - 盈亏平衡点) / 盈亏平衡点
    """
    result = calc_breakeven(
        monthly_rent=data.monthly_rent,
        monthly_labor=data.monthly_labor,
        monthly_utility=data.monthly_utility,
        gross_margin=data.gross_margin,
        daily_revenue=data.daily_revenue,
    )
    if "error" in result:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/five-why", response_model=FiveWhyResult)
def five_why_analysis(data: FiveWhyInput):
    """5Why根因分析 - 获取行业模板或自定义分析

    支持的指标: food_cost_rate, labor_cost_rate, gross_margin,
               turnover_rate, daily_revenue
    """
    template = get_five_why_template(data.indicator)
    steps = [
        FiveWhyStep(step=i+1, question=s["question"], answer=s["answer"])
        for i, s in enumerate(template.get("steps", []))
    ]

    # 如果用户提供了自定义问题描述，覆盖模板
    problem = data.problem or template.get("problem", "")

    return FiveWhyResult(
        indicator=data.indicator,
        problem=problem,
        steps=steps,
        root_cause=template.get("root_cause", ""),
        smart_action=template.get("smart_action", ""),
    )


@router.post("/efficiency-matrix", response_model=EfficiencyMatrixResult)
def efficiency_matrix(data: EfficiencyMatrixInput):
    """人效体检矩阵 - 四象限诊断

    A区(精益区): 人效高+成本低 → 维持+冲刺标杆
    B区(肥胖区): 人效高+成本高 → 立即优化编制
    C区(贫血区): 人效低+成本低 → 警惕服务崩塌
    D区(急救区): 人效低+成本高 → 限时重组方案
    """
    return evaluate_efficiency_matrix(
        revenue_per_labor_hour=data.revenue_per_labor_hour,
        labor_cost_rate=data.labor_cost_rate,
        biz_type=data.biz_type,
    )


@router.get("/five-why/indicators")
def list_five_why_indicators():
    """获取支持5Why模板的指标列表"""
    from services.diagnosis import FIVE_WHY_TEMPLATES
    return [
        {"indicator": k, "problem": v["problem"]}
        for k, v in FIVE_WHY_TEMPLATES.items()
    ]
