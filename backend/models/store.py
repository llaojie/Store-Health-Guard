"""数据模型 - 门店、指标记录、预警记录"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, Float, String, Date, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Store(Base):
    """门店信息"""
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="门店名称")
    code = Column(String(50), unique=True, nullable=False, comment="门店编号")
    biz_type = Column(String(50), nullable=False, comment="业态: fast_food/tea_drink/coffee/snack/hotpot")
    area = Column(Float, comment="营业面积(㎡)")
    seat_count = Column(Integer, comment="座位数")
    open_date = Column(Date, comment="开业日期")
    address = Column(String(255), comment="地址")
    monthly_rent = Column(Float, comment="月租金(元)")
    monthly_fixed_cost = Column(Float, comment="月固定成本(元) - 含租金+人工+水电杂费")
    target_gross_margin = Column(Float, comment="目标综合毛利率")
    is_active = Column(Integer, default=1, comment="是否营业中")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    indicators = relationship("IndicatorRecord", back_populates="store", cascade="all, delete-orphan")
    alerts = relationship("AlertRecord", back_populates="store", cascade="all, delete-orphan")


class IndicatorRecord(Base):
    """指标记录 - 每日/每月的指标快照"""
    __tablename__ = "indicator_records"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    record_date = Column(Date, nullable=False, comment="记录日期")
    period = Column(String(20), default="daily", comment="周期: daily/monthly")

    # 收入类
    daily_revenue = Column(Float, comment="日营业额")
    tc = Column(Integer, comment="交易单数")
    ac = Column(Float, comment="客单价")
    dine_in_revenue = Column(Float, comment="堂食收入")
    delivery_revenue = Column(Float, comment="外卖收入")

    # 成本类
    food_cost = Column(Float, comment="食材成本(元)")
    food_cost_rate = Column(Float, comment="食材成本率")
    labor_cost = Column(Float, comment="人力成本(元)")
    labor_cost_rate = Column(Float, comment="人力成本占比")
    rent_cost_rate = Column(Float, comment="租金成本占比")

    # 效率类
    turnover_rate = Column(Float, comment="翻台率(次/天)")
    ping_efficiency_daily = Column(Float, comment="日坪效(元/㎡/日)")
    overtime_rate = Column(Float, comment="出餐超时率")
    revenue_per_labor_hour = Column(Float, comment="营收人效(元/时)")
    total_labor_hours = Column(Float, comment="总工时")

    # 盈利类
    gross_margin = Column(Float, comment="毛利率")
    net_profit = Column(Float, comment="净利润(元)")
    net_margin = Column(Float, comment="净利润率")
    sssg = Column(Float, comment="同店增长率")

    # 计算字段
    breakeven_point = Column(Float, comment="日盈亏平衡点")
    safety_margin = Column(Float, comment="安全边际")

    # 元数据
    extra = Column(JSON, comment="扩展字段")
    created_at = Column(DateTime, default=datetime.utcnow)

    store = relationship("Store", back_populates="indicators")


class AlertRecord(Base):
    """预警记录"""
    __tablename__ = "alert_records"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    alert_date = Column(Date, nullable=False, comment="预警日期")
    level = Column(String(10), nullable=False, comment="预警等级: red/yellow")
    rule_id = Column(String(10), nullable=False, comment="规则ID: R001/Y001...")
    rule_name = Column(String(100), nullable=False, comment="规则名称")
    indicator = Column(String(50), comment="关联指标")
    indicator_value = Column(Float, comment="指标当前值")
    threshold = Column(Float, comment="阈值")
    status = Column(String(20), default="open", comment="状态: open/processing/resolved/closed")
    root_cause = Column(Text, comment="根因分析(5Why)")
    action_plan = Column(Text, comment="改善计划")
    resolved_at = Column(DateTime, comment="解决时间")
    created_at = Column(DateTime, default=datetime.utcnow)

    store = relationship("Store", back_populates="alerts")
