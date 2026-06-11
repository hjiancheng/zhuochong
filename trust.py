"""信任度系统 - 随时间增长，极少数情况下降"""
from logger import logger
from datetime import datetime


class TrustSystem:
    """信任度——单向增长但极少数恶意行为可触发下降"""

    def __init__(self):
        self._trust = 0.0  # 0-100
        self._days_together = 0
        self._last_day_check = datetime.now().date()
        self._total_interactions = 0
        logger.info("信任度系统初始化: 0%")

    @property
    def trust(self) -> float:
        return self._trust

    @property
    def trust_level(self) -> str:
        t = self._trust
        if t >= 100:
            return "完全信任"
        elif t >= 75:
            return "很信任"
        elif t >= 50:
            return "开始信任"
        elif t >= 25:
            return "逐渐亲近"
        else:
            return "还在观察"

    @property
    def trust_description(self) -> str:
        t = self._trust
        if t >= 100:
            return "真正的伙伴感——我会一直在这里"
        elif t >= 75:
            return "偶尔提起过去的回忆，完全放松"
        elif t >= 50:
            return "完全放松，暴露真实性格"
        elif t >= 25:
            return "开始主动靠近，不那么害羞了"
        else:
            return "猫有点害羞、话少、保持距离"

    def on_new_day(self):
        """每天自然增长一点信任"""
        today = datetime.now().date()
        if today != self._last_day_check:
            self._days_together += 1
            if self._trust < 100:
                # 基础增长：每天0.3-0.5点
                gain = 0.3 + min(0.2, self._total_interactions * 0.002)
                self._trust = min(100, self._trust + gain)
                logger.debug(f"信任度自然增长: +{gain:.2f} → {self._trust:.1f}%")
            self._last_day_check = today
            self._total_interactions = 0

    def on_interaction(self, event_type: str = "general"):
        """互动时增加信任"""
        self._total_interactions += 1
        if self._trust < 100:
            gains = {
                "pet": 0.5,
                "chat": 0.3,
                "milestone": 1.0,
                "long_accompany": 0.8,
                "general": 0.1,
            }
            gain = gains.get(event_type, 0.1)
            self._trust = min(100, self._trust + gain)

    def on_abuse(self):
        """仅极少数恶意行为触发下降"""
        self._trust = max(0, self._trust - 2.0)
        logger.warning(f"信任度因恶意行为下降: -2.0 → {self._trust:.1f}%")

    def save_state(self) -> dict:
        return {
            "trust": self._trust,
            "days_together": self._days_together,
            "last_day_check": self._last_day_check.isoformat(),
        }

    def restore_state(self, data: dict):
        self._trust = data.get("trust", 0)
        self._days_together = data.get("days_together", 0)
        if "last_day_check" in data:
            self._last_day_check = datetime.fromisoformat(data["last_day_check"]).date()
        logger.info(f"信任度恢复: {self._trust:.1f}%")
