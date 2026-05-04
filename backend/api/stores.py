"""门店管理 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from config.database import DATABASE_URL, ENGINE_KWARGS
from models.store import Store
from schemas.store import StoreCreate, StoreUpdate, StoreOut
from services import store_service

router = APIRouter()

engine = create_engine(DATABASE_URL, **ENGINE_KWARGS)


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[StoreOut])
def list_stores(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取门店列表"""
    return store_service.get_stores(db, skip=skip, limit=limit)


@router.post("", response_model=StoreOut)
def create_store(store_in: StoreCreate, db: Session = Depends(get_db)):
    """创建门店"""
    existing = store_service.get_store_by_code(db, store_in.code)
    if existing:
        raise HTTPException(status_code=400, detail=f"门店编号 {store_in.code} 已存在")
    return store_service.create_store(db, store_in.model_dump())


@router.get("/{store_id}", response_model=StoreOut)
def get_store(store_id: int, db: Session = Depends(get_db)):
    """获取门店详情"""
    store = store_service.get_store(db, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="门店不存在")
    return store


@router.put("/{store_id}", response_model=StoreOut)
def update_store(store_id: int, store_in: StoreUpdate, db: Session = Depends(get_db)):
    """更新门店信息"""
    store = store_service.get_store(db, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="门店不存在")
    return store_service.update_store(db, store, store_in.model_dump(exclude_unset=True))


@router.delete("/{store_id}")
def delete_store(store_id: int, db: Session = Depends(get_db)):
    """删除门店"""
    store = store_service.get_store(db, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="门店不存在")
    db.delete(store)
    db.commit()
    return {"message": "已删除"}
