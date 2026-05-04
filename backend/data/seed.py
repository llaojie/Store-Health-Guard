"""初始种子数据 - 创建示例门店和指标数据"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.store import Base, Store, IndicatorRecord
from config.database import DATABASE_URL, ENGINE_KWARGS
from datetime import date
from services.health_engine import compute_derived_indicators


def seed():
    engine = create_engine(DATABASE_URL, **ENGINE_KWARGS)
    Base.metadata.create_all(bind=engine)

    with Session(bind=engine) as db:
        # 检查是否已有数据
        if db.query(Store).first():
            print("已有数据，跳过种子数据")
            return

        # 创建示例门店
        stores = [
            Store(
                name="XX茶饮·万象城店", code="CY-001", biz_type="tea_drink",
                area=80, seat_count=30, open_date=date(2025, 3, 15),
                address="深圳市罗湖区万象城B1层",
                monthly_rent=25000, monthly_fixed_cost=95000,
                target_gross_margin=0.58,
            ),
            Store(
                name="XX咖啡·科技园店", code="CF-001", biz_type="coffee",
                area=45, seat_count=12, open_date=date(2025, 6, 1),
                address="深圳市南山区科技园T3栋1层",
                monthly_rent=18000, monthly_fixed_cost=68000,
                target_gross_margin=0.68,
            ),
            Store(
                name="XX快餐·福田店", code="KS-001", biz_type="fast_food",
                area=120, seat_count=60, open_date=date(2024, 12, 1),
                address="深圳市福田区皇庭广场3层",
                monthly_rent=40000, monthly_fixed_cost=135000,
                target_gross_margin=0.60,
            ),
        ]
        for s in stores:
            db.add(s)
        db.commit()

        # 为每个门店创建模拟数据
        import random
        for store in stores:
            for days_ago in range(30, 0, -1):
                record_date = date(2026, 4, 30) - __import__("datetime").timedelta(days=days_ago)

                # 根据业态生成模拟数据
                if store.biz_type == "tea_drink":
                    daily_revenue = random.uniform(6000, 12000)
                    tc = random.randint(250, 450)
                    food_cost = daily_revenue * random.uniform(0.35, 0.45)
                    labor_cost = daily_revenue * random.uniform(0.18, 0.24)
                elif store.biz_type == "coffee":
                    daily_revenue = random.uniform(5000, 10000)
                    tc = random.randint(150, 300)
                    food_cost = daily_revenue * random.uniform(0.25, 0.32)
                    labor_cost = daily_revenue * random.uniform(0.17, 0.22)
                else:  # fast_food
                    daily_revenue = random.uniform(11000, 18000)
                    tc = random.randint(350, 600)
                    food_cost = daily_revenue * random.uniform(0.30, 0.38)
                    labor_cost = daily_revenue * random.uniform(0.18, 0.22)

                record_dict = {
                    "store_id": store.id,
                    "record_date": record_date,
                    "period": "daily",
                    "daily_revenue": round(daily_revenue, 2),
                    "tc": tc,
                    "food_cost": round(food_cost, 2),
                    "labor_cost": round(labor_cost, 2),
                    "total_labor_hours": round(daily_revenue / random.uniform(160, 220), 1),
                    "turnover_rate": round(random.uniform(1.8, 4.5), 2),
                    "overtime_rate": round(random.uniform(0.02, 0.08), 4),
                }

                store_dict = {
                    "monthly_rent": store.monthly_rent,
                    "monthly_fixed_cost": store.monthly_fixed_cost,
                    "target_gross_margin": store.target_gross_margin,
                    "area": store.area,
                }
                record_dict = compute_derived_indicators(record_dict, store_dict)

                # 移除 store_id 避免重复
                sid = record_dict.pop("store_id")
                record = IndicatorRecord(store_id=sid, **record_dict)
                db.add(record)

        db.commit()
        print(f"种子数据创建完成: {len(stores)} 家门店, 每家30天数据")


if __name__ == "__main__":
    seed()
