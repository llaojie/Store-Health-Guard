"""门店服务 - CRUD 操作"""
from sqlalchemy.orm import Session
from models.store import Store, IndicatorRecord, AlertRecord


# ========== Store CRUD ==========

def get_store(db: Session, store_id: int) -> Store | None:
    return db.query(Store).filter(Store.id == store_id).first()


def get_store_by_code(db: Session, code: str) -> Store | None:
    return db.query(Store).filter(Store.code == code).first()


def get_stores(db: Session, skip: int = 0, limit: int = 100) -> list[Store]:
    return db.query(Store).offset(skip).limit(limit).all()


def create_store(db: Session, store_data: dict) -> Store:
    store = Store(**store_data)
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


def update_store(db: Session, store: Store, update_data: dict) -> Store:
    for key, value in update_data.items():
        if value is not None:
            setattr(store, key, value)
    db.commit()
    db.refresh(store)
    return store


# ========== IndicatorRecord CRUD ==========

def create_indicator_record(db: Session, record_data: dict) -> IndicatorRecord:
    record = IndicatorRecord(**record_data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_latest_indicator(db: Session, store_id: int) -> IndicatorRecord | None:
    return (
        db.query(IndicatorRecord)
        .filter(IndicatorRecord.store_id == store_id)
        .order_by(IndicatorRecord.record_date.desc())
        .first()
    )


def get_indicator_history(db: Session, store_id: int, days: int = 30) -> list[IndicatorRecord]:
    from datetime import timedelta
    from sqlalchemy import desc
    cutoff = db.query(IndicatorRecord.record_date).filter(
        IndicatorRecord.store_id == store_id
    ).order_by(desc(IndicatorRecord.record_date)).offset(days).first()

    query = db.query(IndicatorRecord).filter(IndicatorRecord.store_id == store_id)
    if cutoff:
        query = query.filter(IndicatorRecord.record_date >= cutoff[0])
    return query.order_by(IndicatorRecord.record_date).all()


# ========== AlertRecord CRUD ==========

def create_alert_record(db: Session, alert_data: dict) -> AlertRecord:
    alert = AlertRecord(**alert_data)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_active_alerts(db: Session, store_id: int) -> list[AlertRecord]:
    return (
        db.query(AlertRecord)
        .filter(AlertRecord.store_id == store_id, AlertRecord.status == "open")
        .order_by(AlertRecord.alert_date.desc())
        .all()
    )


def resolve_alert(db: Session, alert_id: int, root_cause: str = None, action_plan: str = None) -> AlertRecord:
    from datetime import datetime
    alert = db.query(AlertRecord).filter(AlertRecord.id == alert_id).first()
    if alert:
        alert.status = "resolved"
        alert.root_cause = root_cause
        alert.action_plan = action_plan
        alert.resolved_at = datetime.utcnow()
        db.commit()
        db.refresh(alert)
    return alert
