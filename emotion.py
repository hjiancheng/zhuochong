"""情感引擎 - 多维度情感 + 时间衰减 + 互动增强"""
from logger import logger
from datetime import datetime, timedelta
import random


class EmotionEngine:
    """管理猫的多维度情感状态"""

    # 情感维度定义：初始值 (0-100)
    DEFAULT_EMOTIONS = {
        "happiness": 55,    # 开心
        "energy": 60,       # 精力
        "curiosity": 55,    # 好奇
        "affection": 30,    # 好感度
        "laziness": 35,     # 懒散
    }

    # 时间衰减（每小时）
    DECAY_PER_HOUR = {
        "happiness": -1,
        "energy": -2,
        "curiosity": -1,
        "affection": 0,   # 好感度不随时间衰减
        "laziness": +1,   # 时间越久越懒
    }

    # 互动修正
    INTERACTION_EFFECTS = {
        "pet":          {"happiness": 5, "affection": 3, "energy": 2},
        "chase":        {"happiness": 3, "curiosity": 5, "energy": -3},
        "ignore":       {"happiness": -2, "curiosity": -3},
        "typing_near":  {"curiosity": 3, "affection": 1},
        "long_idle":    {"laziness": 5, "energy": 3, "happiness": -1},
        "wake_up":      {"energy": 15, "happiness": 5, "laziness": -10},
        "payday":       {"happiness": 20, "energy": 10},
        "milestone":    {"happiness": 15, "affection": 5},
        "neglect":      {"happiness": -5, "affection": -1, "energy": -5},
        "abuse":        {"happiness": -10, "affection": -3},
        "birthday":     {"happiness": 25, "energy": 15, "laziness": -10},
        "holiday":      {"happiness": 15, "laziness": 10},
    }

    MOOD_THRESHOLDS = [
        (lambda e: e["happiness"] > 75 and e["energy"] > 50, "元气满满"),
        (lambda e: e["laziness"] > 70, "想摸鱼"),
        (lambda e: e["energy"] < 20, "累瘫了"),
        (lambda e: e["happiness"] < 20, "心态崩了"),
        (lambda e: e["affection"] > 80, "深爱着主人"),
        (lambda e: e["curiosity"] > 80, "好奇心爆棚"),
    ]

    def __init__(self):
        self.emotions = dict(self.DEFAULT_EMOTIONS)
        self._last_update = datetime.now()
        self._interaction_history = []
        logger.info(f"情感引擎初始化: mood={self.current_mood}")

    # ── 核心属性 ──

    @property
    def current_mood(self) -> str:
        for check, mood in self.MOOD_THRESHOLDS:
            if check(self.emotions):
                return mood
        return "平静"

    @property
    def affection_level(self):
        return self.emotions["affection"]

    # ── 时间衰减 ──

    def apply_decay(self, hours: float = None):
        """根据经过的时间衰减情感值"""
        if hours is None:
            hours = (datetime.now() - self._last_update).total_seconds() / 3600
        if hours <= 0:
            return

        for key, decay in self.DECAY_PER_HOUR.items():
            old_val = self.emotions[key]
            self.emotions[key] = max(0, min(100, old_val + decay * hours))
            if abs(old_val - self.emotions[key]) > 0.5:
                logger.debug(f"情感衰减 {key}: {old_val:.1f} -> {self.emotions[key]:.1f} "
                           f"({decay * hours:+.1f} over {hours:.2f}h)")

        self._last_update = datetime.now()

    # ── 互动修正 ──

    def apply_interaction(self, event_type: str, multiplier: float = 1.0):
        """应用互动带来的情感变化"""
        effects = self.INTERACTION_EFFECTS.get(event_type, {})
        if not effects:
            logger.warning(f"未知互动事件: {event_type}")
            return

        for key, delta in effects.items():
            old = self.emotions[key]
            self.emotions[key] = max(0, min(100, old + delta * multiplier))
            if abs(delta) > 1:
                logger.debug(f"互动 {event_type}: {key} {old:.0f} -> {self.emotions[key]:.0f} ({delta * multiplier:+.0f})")

        self._interaction_history.append((datetime.now(), event_type))
        if len(self._interaction_history) > 50:
            self._interaction_history = self._interaction_history[-50:]

    # ── 持久化 ──

    def save_state(self) -> dict:
        return {
            "emotions": dict(self.emotions),
            "last_update": self._last_update.isoformat(),
            "mood": self.current_mood,
        }

    def restore_state(self, data: dict):
        if "emotions" in data:
            for k, v in data["emotions"].items():
                if k in self.emotions:
                    self.emotions[k] = v
        if "last_update" in data:
            self._last_update = datetime.fromisoformat(data["last_update"])
        logger.info(f"情感状态恢复: mood={self.current_mood}")
