"""预警管理 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from config.database import DATABASE_URL, ENGINE_KWARGS
from schemas.store import AlertOut, AlertResolve
from services import store_service

router = APIRouter()
engine = create_engine(DATABASE_URL, **ENGINE_KWARGS)


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[AlertOut])
def list_alerts(
    store_id: int = None,
    level: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取预警列表，支持按门店/等级/状态筛选"""
    from models.store import AlertRecord
    query = db.query(AlertRecord)
    if store_id:
        query = query.filter(AlertRecord.store_id == store_id)
    if level:
        query = query.filter(AlertRecord.level == level)
    if status:
        query = query.filter(AlertRecord.status == status)
    return query.order_by(AlertRecord.alert_date.desc()).offset(skip).limit(limit).all()


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """获取预警详情"""
    from models.store import AlertRecord
    alert = db.query(AlertRecord).filter(AlertRecord.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="预警记录不存在")
    return alert


@router.put("/{alert_id}/resolve", response_model=AlertOut)
def resolve_alert(alert_id: int, data: AlertResolve, db: Session = Depends(get_db)):
    """处理预警 - 填写根因和改善计划"""
    alert = store_service.resolve_alert(
        db, alert_id,
        root_cause=data.root_cause,
        action_plan=data.action_plan
    )
    if not alert:
        raise HTTPException(status_code=404, detail="预警记录不存在")
    return alert
