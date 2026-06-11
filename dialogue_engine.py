"""本地对话引擎 - 组合式台词系统（模板+变量池→8000+有效输出）"""
from logger import logger
from datetime import datetime
import random
import hashlib
import json
import os


class DialogueEngine:
    """组合式对话生成——不依赖API"""

    def __init__(self, presets_dir="presets"):
        self.presets_dir = presets_dir
        self.templates = {}
        self.fragments = {}
        self.identities = {}
        self.quirks = {}
        self._recent_hashes = []  # 最近20条已说台词
        self._load_presets()
        logger.info(f"对话引擎初始化: {len(self.templates)}场景模板")

    def _load_presets(self):
        """加载所有预设"""
        # 加载台词模板
        dialogues_path = os.path.join(self.presets_dir, "dialogues.json")
        if os.path.exists(dialogues_path):
            with open(dialogues_path, "r", encoding="utf-8") as f:
                self.templates = json.load(f)

        # 加载变量片段
        fragments_path = os.path.join(self.presets_dir, "fragments.json")
        if os.path.exists(fragments_path):
            with open(fragments_path, "r", encoding="utf-8") as f:
                self.fragments = json.load(f)

        # 加载身份台词
        id_path = os.path.join(self.presets_dir, "identities.json")
        if os.path.exists(id_path):
            with open(id_path, "r", encoding="utf-8") as f:
                self.identities = json.load(f)

        # 加载癖好定义
        quirk_path = os.path.join(self.presets_dir, "quirks.json")
        if os.path.exists(quirk_path):
            with open(quirk_path, "r", encoding="utf-8") as f:
                self.quirks = json.load(f)

    def generate(self, trigger: str, personality, emotion, time_ctx: dict,
                 user_profile=None, growth=None, memory=None) -> str | None:
        """
        核心方法：根据触发场景生成一句台词
        返回 None 表示本轮不说话（沉默权）
        """
        # 沉默权：30%概率不回应（只做动作）
        silence_chance = personality.get("silence_chance", 0.3)
        if random.random() < silence_chance and trigger not in ("milestone", "hatch", "birthday"):
            return None

        # 获取该场景的模板
        scene_templates = self.templates.get(trigger, [])
        if not scene_templates:
            scene_templates = self.templates.get("idle_talk", [])

        if not scene_templates:
            return self._fallback_dialogue(personality, emotion)

        # 随机选一个模板
        template = random.choice(scene_templates)
        if isinstance(template, dict):
            tpl = template.get("text", template.get("template", ""))
        else:
            tpl = str(template)

        # 填充变量
        text = self._fill_template(tpl, personality, emotion, time_ctx, user_profile, growth)

        # 去重检查（最近20条）
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self._recent_hashes:
            # 重试最多3次
            for _ in range(3):
                if isinstance(template, dict):
                    tpl = random.choice(scene_templates)
                    if isinstance(tpl, dict):
                        tpl = tpl.get("text", tpl.get("template", ""))
                text = self._fill_template(tpl, personality, emotion, time_ctx, user_profile, growth)
                text_hash = hashlib.md5(text.encode()).hexdigest()
                if text_hash not in self._recent_hashes:
                    break

        # 记录哈希
        self._recent_hashes.append(text_hash)
        if len(self._recent_hashes) > 20:
            self._recent_hashes.pop(0)

        return text

    def _fill_template(self, template: str, personality, emotion, time_ctx,
                       user_profile, growth) -> str:
        """填充模板中的变量"""
        text = template

        # {name}
        frag = self.fragments.get("name", ["小橘", "主人", "喵"])
        text = text.replace("{name}", random.choice(frag))

        # {time_word}
        frag = self.fragments.get("time_word", ["现在", "这时候"])
        time_word = random.choice(frag)
        # 根据实际时间覆盖
        hour = time_ctx.get("hour", 12)
        if 5 <= hour < 8:
            time_word = random.choice(["一大早", "天刚亮", "早上"])
        elif 8 <= hour < 12:
            time_word = random.choice(["上午了", "该干活了", "早上好"])
        elif 12 <= hour < 14:
            time_word = random.choice(["中午了", "午饭时间", "该吃饭了"])
        elif 14 <= hour < 18:
            time_word = random.choice(["下午了", "一下午了", "快下班了"])
        elif 18 <= hour < 22:
            time_word = random.choice(["晚上了", "天黑了", "该休息了"])
        elif hour >= 22 or hour < 5:
            time_word = random.choice(["都这么晚了", "凌晨了", "深夜了"])
        text = text.replace("{time_word}", time_word)

        # {mood_word}
        frag = self.fragments.get("mood_word", ["挺好的", "还行"])
        text = text.replace("{mood_word}", random.choice(frag))

        # {action_word}
        frag = self.fragments.get("action_word", ["忙呢", "在干活"])
        text = text.replace("{action_word}", random.choice(frag))

        # {care_word}
        frag = self.fragments.get("care_word", ["歇会儿吧", "喝口水"])
        text = text.replace("{care_word}", random.choice(frag))

        # {emoji}
        frag = self.fragments.get("emoji", ["", "~"])
        emoji = random.choice(frag)
        talk_style = personality.get_talk_style_config() if hasattr(personality, 'get_talk_style_config') else {}
        # 高冷系减少emoji
        if talk_style.get("tone") == "aloof":
            emoji = "" if random.random() < 0.7 else emoji
        text = text.replace("{emoji}", emoji)

        # {meow} - 根据话风决定是否加喵
        meow = "" if random.random() < 0.5 else "喵"
        if talk_style.get("tone") == "aloof":
            meow = ""
        elif talk_style.get("meow_rate", 0.3) > 0.5:
            meow = "喵" if random.random() < 0.7 else "喵~"
        text = text.replace("{meow}", meow)

        # {cat_age} - 猫岁
        if growth:
            cat_years = growth.cat_years if hasattr(growth, 'cat_years') else 1
            text = text.replace("{cat_age}", str(cat_years))

        # 其他通用替换
        text = text.replace("{learned_name}", "主人")
        text = text.replace("{learned_birthday}", "那天")

        return text

    def _fallback_dialogue(self, personality, emotion) -> str:
        """兜底台词"""
        fallbacks = [
            "喵~", "嗯？", "……", "（看着你）",
            "（打了个哈欠）", "（尾巴摇了摇）", "喵！",
            "（歪头）", "…", "呼噜呼噜…",
        ]
        return random.choice(fallbacks)

    def get_dialogue_for_state(self, state: str, personality, emotion,
                               time_ctx: dict, user_profile=None, growth=None) -> str | None:
        """根据行为状态返回对应台词"""
        trigger_map = {
            "chase": "chase_mouse",
            "sleep": "sleep_talk",
            "watch": "owner_typing",
            "wander": "wander_talk",
            "idle": "idle_talk",
            "react": "click_reaction",
        }
        trigger = trigger_map.get(state, "idle_talk")

        # 时间感知的问候
        hour = time_ctx.get("hour", 12)
        dow = time_ctx.get("day_of_week", 3)
        if state in ("idle", "wander"):
            if hour in (7, 8, 9) and random.random() < 0.1:
                trigger = "morning_greeting"
            elif hour >= 22 and random.random() < 0.15:
                trigger = "late_night"
            elif dow == 0 and random.random() < 0.05:
                trigger = "monday_blues"
            elif dow == 4 and hour >= 16 and random.random() < 0.08:
                trigger = "friday_joy"

        return self.generate(trigger, personality, emotion, time_ctx, user_profile, growth)
