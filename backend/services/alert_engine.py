"""预警引擎 - 根据规则自动触发预警"""
import yaml
from pathlib import Path
from datetime import date
from typing import List, Optional


def load_alert_rules() -> dict:
    """加载预警规则"""
    config_path = Path(__file__).parent.parent / "config" / "biz_types.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("alert_rules", {})


RULES = load_alert_rules()


def evaluate_alerts(indicators: dict, breakeven_point: Optional[float] = None) -> List[dict]:
    """评估指标数据，返回触发的预警列表

    Args:
        indicators: 指标键值对 {indicator_name: value}
        breakeven_point: 日盈亏平衡点

    Returns:
        触发的预警列表 [{level, rule_id, rule_name, indicator, indicator_value, threshold}]
    """
    triggered = []

    # ===== 红色预警 =====
    for rule in RULES.get("red", []):
        result = _check_rule(rule, indicators, breakeven_point)
        if result:
            triggered.append(result)

    # ===== 黄色预警 =====
    for rule in RULES.get("yellow", []):
        result = _check_rule(rule, indicators, breakeven_point)
        if result:
            triggered.append(result)

    return triggered


def _check_rule(rule: dict, indicators: dict, breakeven_point: Optional[float] = None) -> Optional[dict]:
    """检查单条规则是否触发"""
    rule_id = rule["id"]
    indicator = rule.get("indicator", "")
    condition = rule["condition"]

    # 获取指标值
    value = indicators.get(indicator)

    # 特殊处理：盈亏平衡点相关
    if indicator == "daily_revenue" and breakeven_point:
        if "breakeven_point" in condition and value is not None:
            if rule_id == "R001":
                # 营业额低于盈亏平衡点
                if value < breakeven_point:
                    return {
                        "level": rule_id.startswith("R") and "red" or "yellow",
                        "rule_id": rule_id,
                        "rule_name": rule["name"],
                        "indicator": indicator,
                        "indicator_value": value,
                        "threshold": breakeven_point,
                    }
            elif rule_id == "Y001":
                # 安全边际不足
                if breakeven_point <= value < breakeven_point * 1.2:
                    return {
                        "level": "yellow",
                        "rule_id": rule_id,
                        "rule_name": rule["name"],
                        "indicator": indicator,
                        "indicator_value": value,
                        "threshold": breakeven_point * 1.2,
                    }
        return None

    # 通用条件解析
    if value is None:
        return None

    triggered = _evaluate_condition(condition, value, indicators)
    if triggered:
        return {
            "level": "red" if rule_id.startswith("R") else "yellow",
            "rule_id": rule_id,
            "rule_name": rule["name"],
            "indicator": indicator,
            "indicator_value": value,
            "threshold": _extract_threshold(condition),
        }

    return None


def _evaluate_condition(condition: str, value: float, indicators: dict) -> bool:
    """简易条件解析器"""
    # value < 0.45
    if condition.startswith("value < "):
        threshold = float(condition.split("< ")[1])
        return value < threshold

    # value > 0.30
    if condition.startswith("value > "):
        threshold = float(condition.split("> ")[1])
        return value > threshold

    # 0.20 <= value <= 0.25
    if "<= value <=" in condition:
        parts = condition.split()
        low = float(parts[0])
        high = float(parts[-1])
        return low <= value <= high

    # 0.45 <= value < 0.50
    if "<= value <" in condition:
        parts = condition.replace("<=", "").replace("<", "").split("value")
        low = float(parts[0].strip())
        high = float(parts[1].strip())
        return low <= value < high

    # -0.05 <= value < 0
    if "value <" in condition and "<=" in condition:
        try:
            left = condition.split("value")[0].strip().replace("<=", "")
            low = float(left)
            right = condition.split("<")[1].strip()
            high = float(right)
            return low <= value < high
        except (ValueError, IndexError):
            return False

    # consecutive_rise >= 3  (需要历史数据, 简化处理)
    if "consecutive_rise" in condition:
        return False  # 需要历史数据模块支持

    # consecutive_decline_months >= 2 (需要历史数据)
    if "consecutive_decline" in condition:
        return False

    return False


def _extract_threshold(condition: str) -> Optional[float]:
    """从条件表达式中提取阈值"""
    import re
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", condition)
    if numbers:
        return float(numbers[-1])
    return None
