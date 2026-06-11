"""性格系统 - 爱好、习惯、身份、癖好、话风的参数映射"""
from logger import logger


HOBBY_MODIFIERS = {
    "爱睡觉": {"sleep_chance": 1.5, "energy_decay": 1.3, "sleepiness_gain": 1.4},
    "爱玩耍": {"chase_chance": 1.5, "wander_chance": 1.3, "random_act_chance": 1.5, "playfulness_base": 0.7},
    "爱吃":   {"food_talk_chance": 2.0, "food_memory_weight": 2.0},
    "爱发呆": {"idle_duration": 1.5, "curiosity_decay": 0.5, "boredom_gain": 0.5},
    "爱聊天": {"talk_chance": 1.5, "chat_cooldown": 0.6, "social_base": 0.8},
    "爱探索": {"wander_chance": 2.0, "wander_distance": 1.5, "edge_pause": 0.5, "curiosity_base": 0.8},
}

HABIT_MODIFIERS = {
    "黏人": {"chase_distance": 250, "wander_distance": 200, "stay_near": True, "social_base": 0.75},
    "独立": {"chase_distance": 80,  "wander_distance": 600, "stay_near": False, "social_base": 0.3},
    "话多": {"talk_frequency": 1.5, "bubble_duration": 1.3, "silence_chance": 0.15},
    "安静": {"talk_frequency": 0.3, "bubble_duration": 0.7, "silence_chance": 0.5},
    "调皮": {"random_act_chance": 2.0, "surprise_chance": 0.15, "playfulness_base": 0.8},
    "乖巧": {"random_act_chance": 0.3, "surprise_chance": 0.02, "playfulness_base": 0.3},
}

IDENTITY_DIALOGUES = {
    "程序猫": ["这 Bug 修得我要掉毛了…", "代码跑通了？！（尾巴竖起来）", "这个报错…我看不懂但我理解你的心情"],
    "外卖猫": ["该点外卖了吧？我都饿了", "今天吃啥？麻辣烫还是炸鸡？", "我闻到饭香了！（其实没有）"],
    "学生猫": ["DDL 还有多久？", "论文写完了吗…（盯）", "考试周快到了…加油！"],
    "老板猫": ["进度怎么样了？（严肃脸）", "行吧，准你摸鱼5分钟", "这个月KPI…算了不提了"],
    "摸鱼猫": ["摸鱼是打工人的基本权利！", "来一起划水～", "别装了，我知道你在摸鱼"],
    "养生猫": ["该起来活动活动了！", "多喝热水！（递杯子）", "久坐对身体不好哦"],
}

QUIRK_DEFINITIONS = {
    "追尾狂魔":    {"anim": "chase_tail", "chance": 0.05},
    "键盘杀手":    {"anim": "work", "chance": 0.08, "trigger_on": "typing"},
    "日光族":      {"day_energy": 1.3, "night_energy": 0.6},
    "纸箱控":      {"anim": "collapse", "chance": 0.03},
    "报时猫":      {"hourly_meow": True},
    "摇摆猫":      {"anim": "idle", "chance": 0.06, "extra_sway": True},
    "起床困难户":  {"wake_duration": 2.0, "stretch_chance": 0.3},
    "虚空捕手":    {"anim": "pounce", "chance": 0.04},
    "方向痴":      {"reverse_walk_chance": 0.15},
    "洁癖猫":      {"anim": "wash_face", "chance": 0.07},
}

TALK_STYLES = {
    "喵系":   {"meow_rate": 0.7, "tone": "soft", "sentence_end": "喵"},
    "吐槽系": {"meow_rate": 0.1, "tone": "sarcastic", "sentence_end": ""},
    "撒娇系": {"meow_rate": 0.4, "tone": "clingy", "sentence_end": "～"},
    "高冷系": {"meow_rate": 0.05, "tone": "aloof", "sentence_end": ""},
}


class PersonalitySystem:
    """汇总所有性格参数，为行为系统提供修正系数"""

    def __init__(self, profile):
        self.profile = profile
        self.hobbies = profile.get("personality", {}).get("hobbies", [])
        self.habits = profile.get("personality", {}).get("habits", [])
        self.identity = profile.get("personality", {}).get("identity", "摸鱼猫")
        self.quirks = profile.get("personality", {}).get("quirks", [])
        self.talk_style = profile.get("personality", {}).get("talk_style", "喵系")
        self._build_modifiers()
        logger.info(f"性格系统初始化: 爱好{self.hobbies} 习惯{self.habits} 话风{self.talk_style}")

    def _build_modifiers(self):
        self.modifiers = {}
        for hobby in self.hobbies:
            if hobby in HOBBY_MODIFIERS:
                for k, v in HOBBY_MODIFIERS[hobby].items():
                    self.modifiers[k] = self.modifiers.get(k, 1.0) * v
        for habit in self.habits:
            if habit in HABIT_MODIFIERS:
                for k, v in HABIT_MODIFIERS[habit].items():
                    if isinstance(v, bool):
                        self.modifiers[k] = v
                    else:
                        self.modifiers[k] = self.modifiers.get(k, 1.0) * v

    def get(self, key, default=1.0):
        return self.modifiers.get(key, default)

    def has_quirk(self, name):
        return name in self.quirks

    def get_talk_style_config(self):
        return TALK_STYLES.get(self.talk_style, TALK_STYLES["喵系"])

    def get_identity_lines(self):
        return IDENTITY_DIALOGUES.get(self.identity, [])

    def get_quirk_chance(self, name):
        return QUIRK_DEFINITIONS.get(name, {}).get("chance", 0.01)
