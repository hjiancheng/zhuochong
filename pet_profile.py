"""宠物档案管理 - 读写 profile.json"""
from logger import logger
import json
import os


DEFAULT_PROFILE = {
    "name": "小橘",
    "created_at": "",
    "birthday": "06-11",
    "zodiac": "gemini",
    "_version": "2.0.0",
    "appearance": {
        "species": "cat",
        "fur_color": "orange",
        "eye_color": "gold",
        "accessory": "badge"
    },
    "personality": {
        "hobbies": ["爱吃", "爱聊天"],
        "habits": ["黏人", "话多"],
        "talk_style": "吐槽系",
        "identity": "程序猫",
        "quirks": ["追尾狂魔"]
    }
}

# 物种名称 + 毛色映射
SPECIES_NAMES = {
    "cat": "🐱猫", "dog": "🐶狗", "rabbit": "🐰兔", "bear": "🐻熊",
    "chick": "🐤小鸡", "hamster": "🐹仓鼠", "fox": "🦊狐狸", "penguin": "🐧企鹅",
    "custom_jia": "💛(嘉怡姐)定制",
}
SPECIES_FUR_NAMES = {
    "cat": {"orange":"橘猫","ragdoll":"布偶","cow":"奶牛","calico":"三花","black":"纯黑","white":"纯白","pink":"粉猫","cream":"奶油"},
    "dog": {"golden":"金毛","corgi":"柯基","husky":"哈士奇","samoyed":"萨摩耶","brown":"棕犬","spot":"斑点"},
    "rabbit": {"white":"白兔","grey":"灰兔","brown":"棕兔","black":"黑兔","spot":"花兔","pink":"粉兔"},
    "bear": {"brown":"棕熊","panda":"熊猫","polar":"北极熊","black":"黑熊","honey":"蜂蜜熊","red":"红熊"},
    "chick": {"yellow":"小黄鸡","white":"小白鸡","brown":"棕鸡","black":"黑鸡","pink":"粉鸡","orange":"橙鸡"},
    "hamster": {"golden":"金丝熊","silver":"银狐","pudding":"布丁","white":"银白","grey":"灰灰","black":"黑黑"},
    "fox": {"red":"赤狐","white":"白狐","grey":"灰狐","black":"黑狐","golden":"金狐","coral":"珊瑚狐"},
    "penguin": {"emperor":"帝企鹅","blue":"蓝企鹅","rock":"岩企鹅","gentoo":"巴布亚","baby":"灰宝宝","pink":"粉企鹅"},
    "custom_jia": {"default":"(嘉怡姐)定制"},
}


class PetProfile:
    """管理猫的绝密档案"""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.path = os.path.join(data_dir, "profile.json")
        os.makedirs(data_dir, exist_ok=True)

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def create(self, data: dict):
        """创建档案——只写一次"""
        data["_version"] = "1.0.0"
        from datetime import datetime
        data["created_at"] = datetime.now().isoformat()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"宠物档案已创建: {data.get('name', '未知')}")

    def load(self) -> dict | None:
        """加载档案"""
        if not self.exists():
            return None
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"档案加载失败: {e}")
            return None

    def verify_integrity(self) -> bool:
        """验证档案完整性"""
        data = self.load()
        if data is None:
            return False
        required = ["name", "appearance", "personality", "_version"]
        for key in required:
            if key not in data:
                logger.warning(f"档案缺少必要字段: {key}")
                return False
        return True

    def get_readonly_display(self) -> str:
        """只读展示档案内容"""
        data = self.load()
        if not data:
            return "无档案"
        a = data.get("appearance", {})
        p = data.get("personality", {})
        species = a.get("species", "cat")
        species_name = SPECIES_NAMES.get(species, "🐱猫")
        fur_name_map = SPECIES_FUR_NAMES.get(species, {})
        eye_names = {"blue": "蓝眼", "green": "绿眼", "gold": "金眼", "odd": "异瞳"}
        return (
            f"{species_name} 名字：{data['name']}\n"
            f"🎨 毛色：{fur_name_map.get(a.get('fur_color'), a.get('fur_color'))} | "
            f"👁 {eye_names.get(a.get('eye_color'), a.get('eye_color'))} | "
            f"🧣 {a.get('accessory', '无')}\n"
            f"❤ 爱好：{', '.join(p.get('hobbies', []))}\n"
            f"🎭 习惯：{', '.join(p.get('habits', []))}\n"
            f"💬 话风：{p.get('talk_style', '喵系')}\n"
            f"🏷 身份：{p.get('identity', '摸鱼')}\n"
            f"🎂 生日：{data.get('birthday', '未知')} | ♊ {data.get('zodiac', '')}\n"
            f"🎲 癖好：{', '.join(p.get('quirks', []))}"
        )
