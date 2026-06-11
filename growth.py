"""成长系统 - 蛋→幼猫→成猫→完全体"""
from logger import logger
from datetime import datetime, timedelta
import json
import os


class GrowthSystem:
    """管理猫的成长阶段"""

    STAGES = {
        "egg":     {"index": 0, "name": "蛋", "size": 0.3, "min_hours": 0, "min_interactions": 0},
        "kitten":  {"index": 1, "name": "幼猫", "size": 0.6, "min_hours": 0, "min_interactions": 5},
        "adult":   {"index": 2, "name": "成猫", "size": 1.0, "min_hours": 168, "min_interactions": 50},
        "master":  {"index": 3, "name": "完全体", "size": 1.0, "min_hours": 720, "min_interactions": 200},
    }

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.birth_time = datetime.now()
        self._interaction_count = 0
        self._hatched = False
        self._current_stage = "egg"
        os.makedirs(data_dir, exist_ok=True)
        self._load_egg_state()

    # ── 属性 ──

    @property
    def stage(self) -> str:
        return self._current_stage

    @property
    def is_egg(self) -> bool:
        return self._current_stage == "egg"

    @property
    def is_kitten(self) -> bool:
        return self._current_stage == "kitten"

    @property
    def is_adult(self) -> bool:
        return self._current_stage in ("adult", "master")

    @property
    def interaction_count(self) -> int:
        return self._interaction_count

    @property
    def age_hours(self) -> float:
        return max(0, (datetime.now() - self.birth_time).total_seconds() / 3600)

    @property
    def age_days(self) -> int:
        return max(1, int(self.age_hours / 24))

    @property
    def cat_years(self) -> int:
        """猫龄换算：1天≈4猫天，但起步15猫岁"""
        return max(1, int(15 + self.age_days * 4 / 30))

    @property
    def display_size(self) -> float:
        return self.STAGES[self._current_stage]["size"]

    @property
    def progress_text(self) -> str:
        """成长进度文本"""
        if self.is_egg:
            left = max(0, self.STAGES["kitten"]["min_interactions"] - self._interaction_count)
            return f"还需要 {left} 次互动才能孵化…"
        elif self.is_kitten:
            days_left = max(0, 7 - self.age_days)
            return f"距离变成成猫还有 {days_left} 天…"
        elif self._current_stage == "adult":
            days_left = max(0, 30 - self.age_days)
            return f"距离完全体还有 {days_left} 天…"
        else:
            return f"已经陪伴了 {self.age_days} 天"

    # ── 互动计数 ──

    def record_interaction(self, event_type: str = "general"):
        """记录一次互动"""
        self._interaction_count += 1
        self._save_egg_state()
        self._check_growth()

    def _check_growth(self):
        """检查是否满足进阶条件"""
        old_stage = self._current_stage
        hours = self.age_hours
        interactions = self._interaction_count

        stage_order = ["egg", "kitten", "adult", "master"]
        idx = stage_order.index(self._current_stage)

        for next_idx in range(idx + 1, len(stage_order)):
            next_stage = stage_order[next_idx]
            reqs = self.STAGES[next_stage]
            if hours >= reqs["min_hours"] and interactions >= reqs["min_interactions"]:
                self._current_stage = next_stage
                logger.info(f"🎉 成长进阶: {old_stage} → {next_stage} "
                           f"(hours={hours:.1f}, interactions={interactions})")
                if next_stage == "kitten" and not self._hatched:
                    self._hatched = True
                    logger.info("🥚 蛋孵化！")

    # ── 持久化 ──

    def _save_egg_state(self):
        if not self._hatched:
            state = {
                "interactions": self._interaction_count,
                "first_interaction": self.birth_time.isoformat(),
            }
            try:
                with open(os.path.join(self.data_dir, "egg_state.json"), "w", encoding="utf-8") as f:
                    json.dump(state, f, ensure_ascii=False)
            except Exception as e:
                logger.error(f"保存蛋状态失败: {e}")

    def _load_egg_state(self):
        path = os.path.join(self.data_dir, "egg_state.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                self._interaction_count = state.get("interactions", 0)
                logger.info(f"蛋状态已恢复: 互动{self._interaction_count}次")
            except Exception as e:
                logger.error(f"加载蛋状态失败: {e}")

    def save_state(self) -> dict:
        return {
            "stage": self._current_stage,
            "birth_time": self.birth_time.isoformat(),
            "interaction_count": self._interaction_count,
            "hatched": self._hatched,
        }

    def restore_state(self, data: dict):
        self._current_stage = data.get("stage", "egg")
        self._interaction_count = data.get("interaction_count", 0)
        self._hatched = data.get("hatched", False)
        if "birth_time" in data:
            self.birth_time = datetime.fromisoformat(data["birth_time"])
        logger.info(f"成长状态恢复: {self._current_stage}, 互动{self._interaction_count}次")
