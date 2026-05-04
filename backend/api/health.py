"""健康度监测 API - 仪表盘、指标录入、健康评估"""
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from config.database import DATABASE_URL, ENGINE_KWARGS
from models.store import Store
from schemas.store import (
    IndicatorInput, IndicatorOut, StoreHealthDashboard, IndicatorHealth
)
from services import store_service
from services.health_engine import (
    compute_derived_indicators, evaluate_indicator,
    compute_health_score, check_survival_conditions,
    get_biz_type_name, INDICATOR_META
)
from services.alert_engine import evaluate_alerts

router = APIRouter()
engine = create_engine(DATABASE_URL, **ENGINE_KWARGS)


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


@router.post("/indicators", response_model=IndicatorOut)
def submit_indicators(data: IndicatorInput, db: Session = Depends(get_db)):
    """录入指标数据，自动计算派生指标并触发预警"""
    store = store_service.get_store_by_code(db, data.store_code)
    if not store:
        raise HTTPException(status_code=404, detail=f"门店编号 {data.store_code} 不存在")

    # 计算派生指标
    store_dict = {
        "monthly_rent": store.monthly_rent,
        "monthly_fixed_cost": store.monthly_fixed_cost,
        "target_gross_margin": store.target_gross_margin,
        "area": store.area,
    }
    record_dict = data.model_dump(exclude={"store_code"})
    record_dict = compute_derived_indicators(record_dict, store_dict)

    # 保存记录
    record_dict["store_id"] = store.id
    record = store_service.create_indicator_record(db, record_dict)

    # 触发预警检查
    _check_and_create_alerts(db, store.id, record_dict, record_dict.get("breakeven_point"))

    return record


@router.get("/dashboard/{store_id}", response_model=StoreHealthDashboard)
def get_health_dashboard(store_id: int, db: Session = Depends(get_db)):
    """获取门店健康度仪表盘"""
    store = store_service.get_store(db, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="门店不存在")

    latest = store_service.get_latest_indicator(db, store_id)
    if not latest:
        return StoreHealthDashboard(
            store_id=store.id,
            store_name=store.name,
            store_code=store.code,
            biz_type=store.biz_type,
            biz_type_name=get_biz_type_name(store.biz_type),
            record_date=date.today(),
            overall_status="green",
            health_score=100.0,
            indicators=[],
            active_alerts=[],
            survival_check={},
        )

    # 评估每个指标
    indicator_keys = [
        "daily_revenue", "tc", "ac",
        "food_cost_rate", "labor_cost_rate", "rent_cost_rate",
        "turnover_rate", "ping_efficiency_daily", "revenue_per_labor_hour",
        "gross_margin", "net_margin", "sssg"
    ]

    indicator_list = []
    for key in indicator_keys:
        value = getattr(latest, key, None)
        level, range_desc = evaluate_indicator(store.biz_type, key, value)
        meta = INDICATOR_META.get(key, {})
        indicator_list.append(IndicatorHealth(
            name=key,
            value=value,
            unit=meta.get("unit", ""),
            level=level,
            healthy_range=range_desc.split("|")[0].strip() if range_desc else None,
            warning_range=range_desc.split("|")[1].strip() if len(range_desc.split("|")) > 1 else None,
            danger_range=range_desc.split("|")[2].strip() if len(range_desc.split("|")) > 2 else None,
        ))

    # 综合评分
    score, overall = compute_health_score(indicator_list)

    # 活跃预警
    active_alerts = store_service.get_active_alerts(db, store_id)

    # 六大保命条件
    store_dict = {
        "area": store.area,
        "total_investment": None,  # 可扩展
    }
    record_dict = {c.name: getattr(latest, c.name) for c in latest.__table__.columns}
    survival = check_survival_conditions(store_dict, record_dict)

    return StoreHealthDashboard(
        store_id=store.id,
        store_name=store.name,
        store_code=store.code,
        biz_type=store.biz_type,
        biz_type_name=get_biz_type_name(store.biz_type),
        record_date=latest.record_date,
        overall_status=overall,
        health_score=score,
        indicators=indicator_list,
        active_alerts=active_alerts,
        survival_check=survival,
    )


@router.get("/history/{store_id}")
def get_indicator_history(store_id: int, days: int = 30, db: Session = Depends(get_db)):
    """获取门店指标历史趋势"""
    records = store_service.get_indicator_history(db, store_id, days)
    return [
        {
            "date": r.record_date.isoformat(),
            "daily_revenue": r.daily_revenue,
            "tc": r.tc,
            "ac": r.ac,
            "food_cost_rate": r.food_cost_rate,
            "labor_cost_rate": r.labor_cost_rate,
            "gross_margin": r.gross_margin,
            "net_margin": r.net_margin,
            "turnover_rate": r.turnover_rate,
            "ping_efficiency_daily": r.ping_efficiency_daily,
            "revenue_per_labor_hour": r.revenue_per_labor_hour,
            "breakeven_point": r.breakeven_point,
            "safety_margin": r.safety_margin,
        }
        for r in records
    ]


def _check_and_create_alerts(db, store_id, record_dict, breakeven_point):
    """检查预警并创建记录"""
    triggered = evaluate_alerts(record_dict, breakeven_point)
    for alert in triggered:
        store_service.create_alert_record(db, {
            "store_id": store_id,
            "alert_date": record_dict.get("record_date", date.today()),
            "level": alert["level"],
            "rule_id": alert["rule_id"],
            "rule_name": alert["rule_name"],
            "indicator": alert["indicator"],
            "indicator_value": alert["indicator_value"],
            "threshold": alert["threshold"],
        })
