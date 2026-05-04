"""Pydantic Schemas - 请求/响应模型"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ========== Store ==========
class StoreCreate(BaseModel):
    name: str
    code: str
    biz_type: str = Field(..., description="业态: fast_food/tea_drink/coffee/snack/hotpot")
    area: Optional[float] = None
    seat_count: Optional[int] = None
    open_date: Optional[date] = None
    address: Optional[str] = None
    monthly_rent: Optional[float] = None
    monthly_fixed_cost: Optional[float] = None
    target_gross_margin: Optional[float] = None


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    biz_type: Optional[str] = None
    area: Optional[float] = None
    seat_count: Optional[int] = None
    monthly_rent: Optional[float] = None
    monthly_fixed_cost: Optional[float] = None
    target_gross_margin: Optional[float] = None
    is_active: Optional[int] = None


class StoreOut(StoreCreate):
    id: int
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== IndicatorRecord ==========
class IndicatorInput(BaseModel):
    """指标录入"""
    store_code: str
    record_date: date
    period: str = "daily"

    # 收入类
    daily_revenue: Optional[float] = None
    tc: Optional[int] = None
    ac: Optional[float] = None
    dine_in_revenue: Optional[float] = None
    delivery_revenue: Optional[float] = None

    # 成本类
    food_cost: Optional[float] = None
    labor_cost: Optional[float] = None
    total_labor_hours: Optional[float] = None

    # 效率类
    turnover_rate: Optional[float] = None
    overtime_rate: Optional[float] = None

    # 盈利类
    net_profit: Optional[float] = None
    sssg: Optional[float] = None


class IndicatorOut(BaseModel):
    id: int
    store_id: int
    record_date: date
    period: str
    daily_revenue: Optional[float] = None
    tc: Optional[int] = None
    ac: Optional[float] = None
    food_cost_rate: Optional[float] = None
    labor_cost_rate: Optional[float] = None
    rent_cost_rate: Optional[float] = None
    turnover_rate: Optional[float] = None
    ping_efficiency_daily: Optional[float] = None
    overtime_rate: Optional[float] = None
    revenue_per_labor_hour: Optional[float] = None
    gross_margin: Optional[float] = None
    net_profit: Optional[float] = None
    net_margin: Optional[float] = None
    sssg: Optional[float] = None
    breakeven_point: Optional[float] = None
    safety_margin: Optional[float] = None

    class Config:
        from_attributes = True


# ========== Alert ==========
class AlertOut(BaseModel):
    id: int
    store_id: int
    alert_date: date
    level: str
    rule_id: str
    rule_name: str
    indicator: Optional[str] = None
    indicator_value: Optional[float] = None
    threshold: Optional[float] = None
    status: str
    root_cause: Optional[str] = None
    action_plan: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertResolve(BaseModel):
    """预警处理"""
    root_cause: Optional[str] = None
    action_plan: Optional[str] = None


# ========== Health Dashboard ==========
class IndicatorHealth(BaseModel):
    """单个指标的健康状态"""
    name: str
    value: Optional[float] = None
    unit: str = ""
    level: str = "green"  # green/yellow/red
    healthy_range: Optional[str] = None
    warning_range: Optional[str] = None
    danger_range: Optional[str] = None


class StoreHealthDashboard(BaseModel):
    """门店健康度仪表盘"""
    store_id: int
    store_name: str
    store_code: str
    biz_type: str
    biz_type_name: str
    record_date: date
    overall_status: str = "green"  # 综合状态
    health_score: float = 100.0    # 健康度评分 0-100
    indicators: List[IndicatorHealth] = []
    active_alerts: List[AlertOut] = []
    survival_check: dict = {}       # 六大保命条件


# ========== Diagnosis ==========
class BreakevenInput(BaseModel):
    """盈亏平衡计算输入"""
    monthly_rent: float = Field(..., description="月租金")
    monthly_labor: float = Field(..., description="月人工成本")
    monthly_utility: float = Field(..., description="月水电杂费")
    gross_margin: float = Field(..., description="综合毛利率, 如0.4")
    daily_revenue: Optional[float] = Field(None, description="实际日营业额")


class BreakevenResult(BaseModel):
    daily_fixed_cost: float
    breakeven_point: float
    actual_revenue: Optional[float] = None
    safety_margin: Optional[float] = None
    status: str  # green/yellow/red


class FiveWhyInput(BaseModel):
    """5Why分析输入"""
    indicator: str = Field(..., description="异常指标名")
    problem: str = Field(..., description="问题描述")


class FiveWhyStep(BaseModel):
    step: int
    question: str
    answer: str


class FiveWhyResult(BaseModel):
    indicator: str
    problem: str
    steps: List[FiveWhyStep] = []
    root_cause: str = ""
    smart_action: str = ""


class EfficiencyMatrixInput(BaseModel):
    """人效体检矩阵输入"""
    revenue_per_labor_hour: float = Field(..., description="营收人效(元/时)")
    labor_cost_rate: float = Field(..., description="人力成本占比, 如0.22")
    biz_type: str = Field(default="tea_drink", description="业态")


class EfficiencyMatrixResult(BaseModel):
    quadrant: str  # lean/obese/anemic/emergency
    quadrant_name: str
    revenue_level: str  # high/low
    cost_level: str     # low/high
    diagnosis: str
    action: str
