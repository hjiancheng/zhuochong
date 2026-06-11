"""自主意志 - 猫根据内在驱动力自主决定行为"""
from logger import logger
import random


class AutonomyEngine:
    """猫不是等指令的机器人——它有自己的想法"""

    # 驱动力初始值 (0-1)
    DEFAULT_DRIVES = {
        "curiosity":    0.5,   # 好奇心
        "hunger":       0.0,   # 饥饿（API猫）
        "boredom":      0.3,   # 无聊
        "social":       0.4,   # 社交欲
        "sleepiness":   0.2,   # 困意
        "playfulness":  0.5,   # 贪玩
    }

    # 驱动力增长率（每小时）
    DRIVE_GAIN_PER_HOUR = {
        "boredom": 0.08,
        "social": 0.04,
        "sleepiness": 0.12,
        "curiosity": 0.02,
        "hunger": 0.0,
        "playfulness": 0.03,
    }

    # 行为定义
    ACTIONS = {
        "approach_curious":  {"drives": {"curiosity": 0.7}, "anim": "idle"},
        "play_alone":        {"drives": {"boredom": 0.7}, "anim": "chase_tail"},
        "approach_social":   {"drives": {"social": 0.7}, "anim": "walk"},
        "go_sleep":          {"drives": {"sleepiness": 0.8}, "anim": "sleep"},
        "beg_food":          {"drives": {"hunger": 0.7}, "anim": "sit"},
        "chase_mouse":       {"drives": {"playfulness": 0.8}, "anim": "walk"},
        "idle_wander":       {"drives": {"boredom": 0.5}, "anim": "walk"},
        "stretch":           {"drives": {"sleepiness": 0.4}, "anim": "stretch"},
    }

    def __init__(self):
        self.drives = dict(self.DEFAULT_DRIVES)
        self._recent_actions = []  # 最多5条
        self._hours_since_last_update = 0
        logger.info("自主意志引擎初始化")

    # ── 驱动力管理 ──

    def apply_time(self, hours: float):
        """时间经过，驱动力自然变化"""
        self._hours_since_last_update += hours
        for key, gain in self.DRIVE_GAIN_PER_HOUR.items():
            self.drives[key] = min(1.0, self.drives[key] + gain * hours)

    def apply_event(self, drive_name: str, delta: float):
        """事件影响特定驱动力"""
        self.drives[drive_name] = max(0, min(1.0, self.drives[drive_name] + delta))

    def reset_drive(self, drive_name: str):
        """行为完成后重置对应驱动力"""
        if drive_name in self.drives:
            self.drives[drive_name] = 0.0

    # ── 决策 ──

    def decide_action(self, personality, emotion) -> str | None:
        """
        综合驱动力 + 性格 + 情感 → 选择一个自主行为
        返回 action_name 或 None（什么都不做）
        """
        candidates = []
        for action_name, definition in self.ACTIONS.items():
            # 检查驱动条件
            meets_all = True
            total_score = 0
            for drive_name, threshold in definition["drives"].items():
                if self.drives.get(drive_name, 0) < threshold:
                    meets_all = False
                    break
                total_score += (self.drives[drive_name] - threshold)

            if meets_all:
                # 性格修正
                score = total_score
                if "sleep" in action_name:
                    score *= personality.get("sleep_chance", 1.0)
                if "play" in action_name or "chase" in action_name:
                    score *= personality.get("playfulness_base", 0.5)
                if "social" in action_name or "approach" in action_name:
                    score *= personality.get("social_base", 0.5)

                # 去重：排除最近3次
                if action_name not in self._recent_actions[-3:]:
                    candidates.append((action_name, score))

        if not candidates:
            return None

        # 选择得分最高的
        chosen = max(candidates, key=lambda x: x[1])
        action_name = chosen[0]

        # 记录
        self._recent_actions.append(action_name)
        if len(self._recent_actions) > 5:
            self._recent_actions.pop(0)

        # 重置被满足的驱动力
        for drive_name in self.ACTIONS[action_name]["drives"]:
            self.reset_drive(drive_name)

        logger.debug(f"自主决策: {action_name} (候选{len(candidates)}个, 得分{chosen[1]:.2f})")
        return action_name

    def get_anim_for_action(self, action_name: str) -> str:
        return self.ACTIONS.get(action_name, {}).get("anim", "idle")

    # ── 持久化 ──

    def save_state(self) -> dict:
        return {"drives": dict(self.drives)}

    def restore_state(self, data: dict):
        if "drives" in data:
            for k, v in data["drives"].items():
                if k in self.drives:
                    self.drives[k] = v
        logger.info(f"自主意志状态恢复")
