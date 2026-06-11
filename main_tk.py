"""月薪猫桌宠 — 超萌版（kawaii设计 + 成长/记忆/情感/信任/聊天）"""
import sys, os, atexit, signal, ctypes, json, math, random, traceback, hashlib
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import simpledialog

try:
    ES_CONTINUOUS = 0x80000000; ES_SYSTEM_REQUIRED = 0x00000001; ES_DISPLAY_REQUIRED = 0x00000002
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS|ES_SYSTEM_REQUIRED|ES_DISPLAY_REQUIRED)
except: pass

# 路径：支持开发模式 + PyInstaller打包
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    MEIPASS = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MEIPASS = BASE_DIR
DATA_DIR = os.path.join(BASE_DIR,"data"); LOG_DIR = os.path.join(BASE_DIR,"logs")
PRESETS_DIR = os.path.join(MEIPASS,"presets")
os.makedirs(DATA_DIR,exist_ok=True); os.makedirs(LOG_DIR,exist_ok=True)
sys.path.insert(0,BASE_DIR)

_log_path = os.path.join(LOG_DIR,"pet.log")
def log(msg):
    with open(_log_path,"a",encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%m-%d %H:%M:%S')} {msg}\n")
log("─── 启动 ───")

from pet_profile import PetProfile, SPECIES_FUR_NAMES, SPECIES_NAMES
from archive import ArchiveGuard
from personality import PersonalitySystem
from emotion import EmotionEngine
from growth import GrowthSystem
from trust import TrustSystem
from autonomy import AutonomyEngine
from db import Database, StateManager
from memory import MemorySystem
from dialogue_engine import DialogueEngine

# ══════════ 超萌配色（粉嫩系）══════════
PALETTE = {
    "orange":  {"body":"#FFB380","stripe":"#FF9950","belly":"#FFF0E0","ear_in":"#FFCCBB","cheek":"#FFCCDD"},
    "ragdoll": {"body":"#F5EDE0","stripe":"#C0A890","belly":"#FFFAF5","ear_in":"#E8D5CC","cheek":"#FFDDE0"},
    "cow":     {"body":"#3A3A3A","stripe":"#252525","belly":"#FEFEFE","ear_in":"#FFCCBB","cheek":"#FFCCDD"},
    "calico":  {"body":"#FEFEFE","stripe":"#FFAA60","belly":"#FFF8F0","ear_in":"#FFCCBB","cheek":"#FFDDE0","patch":"#3A3A3A"},
    "black":   {"body":"#404040","stripe":"#282828","belly":"#505050","ear_in":"#706060","cheek":"#806070"},
    "white":   {"body":"#FCFCFC","stripe":"#EAE5E0","belly":"#FFFFFF","ear_in":"#FFDDCC","cheek":"#FFDDE0"},
    "pink":    {"body":"#FFD0D8","stripe":"#FFB8C4","belly":"#FFF0F2","ear_in":"#FFB0C0","cheek":"#FFB0C8"},
    "cream":   {"body":"#FFF5E0","stripe":"#F0D8B0","belly":"#FFFEFA","ear_in":"#F5D0C0","cheek":"#FFE0D0"},
}
# ══════════ 多物种系统 ══════════
SPECIES = {
    "cat": {
        "name":"猫猫","emoji":"🐱",
        "palettes": {
            "orange":  {"body":"#FFB380","stripe":"#FF9950","belly":"#FFF0E0","ear_in":"#FFCCBB","cheek":"#FFCCDD"},
            "ragdoll": {"body":"#F5EDE0","stripe":"#C0A890","belly":"#FFFAF5","ear_in":"#E8D5CC","cheek":"#FFDDE0"},
            "cow":     {"body":"#3A3A3A","stripe":"#252525","belly":"#FEFEFE","ear_in":"#FFCCBB","cheek":"#FFCCDD"},
            "calico":  {"body":"#FEFEFE","stripe":"#FFAA60","belly":"#FFF8F0","ear_in":"#FFCCBB","cheek":"#FFDDE0","patch":"#3A3A3A"},
            "black":   {"body":"#404040","stripe":"#282828","belly":"#505050","ear_in":"#706060","cheek":"#806070"},
            "white":   {"body":"#FCFCFC","stripe":"#EAE5E0","belly":"#FFFFFF","ear_in":"#FFDDCC","cheek":"#FFDDE0"},
            "pink":    {"body":"#FFD0D8","stripe":"#FFB8C4","belly":"#FFF0F2","ear_in":"#FFB0C0","cheek":"#FFB0C8"},
            "cream":   {"body":"#FFF5E0","stripe":"#F0D8B0","belly":"#FFFEFA","ear_in":"#F5D0C0","cheek":"#FFE0D0"},
        },
        "body_ratio": {"body_w":28,"body_h":20,"head_r":42,"head_y_off":8},
        "ear":"triangle","tail":"long_up","face_extras":["whiskers"],
        "sound":"喵","identity_tag":"猫",
    },
    "dog": {
        "name":"狗狗","emoji":"🐶",
        "palettes": {
            "golden":  {"body":"#F0C878","stripe":"#D8A850","belly":"#FFF8E0","ear_in":"#E8C8A0","cheek":"#FFDDBB"},
            "corgi":   {"body":"#E8B860","stripe":"#C89840","belly":"#FFF8E8","ear_in":"#F0D8C0","cheek":"#FFE0C0"},
            "husky":   {"body":"#8888A0","stripe":"#606078","belly":"#F0F0F8","ear_in":"#C0C0D8","cheek":"#DDDDF0"},
            "samoyed": {"body":"#FEFEFE","stripe":"#E8E0D8","belly":"#FFFFFF","ear_in":"#FFF0E8","cheek":"#FFF0EE"},
            "brown":   {"body":"#B08060","stripe":"#906040","belly":"#E8D8C8","ear_in":"#D0B8A0","cheek":"#E8D0C0"},
            "spot":    {"body":"#FEFEFE","stripe":"#E8E0D8","belly":"#FFF8F0","ear_in":"#FFE8D0","cheek":"#FFE0D0","patch":"#3A3A3A"},
        },
        "body_ratio": {"body_w":30,"body_h":22,"head_r":38,"head_y_off":12},
        "ear":"floppy","tail":"short_wag","face_extras":[],
        "sound":"汪","identity_tag":"狗",
    },
    "rabbit": {
        "name":"兔兔","emoji":"🐰",
        "palettes": {
            "white":   {"body":"#FEFEFE","stripe":"#E8E0E0","belly":"#FFF8F8","ear_in":"#FFD0D8","cheek":"#FFD0D8"},
            "grey":    {"body":"#C8C0C0","stripe":"#A09898","belly":"#E8E0E0","ear_in":"#E0D0D8","cheek":"#E8D8E0"},
            "brown":   {"body":"#C8A888","stripe":"#A08060","belly":"#F0E0D0","ear_in":"#E8C8B0","cheek":"#F0D8C8"},
            "black":   {"body":"#505050","stripe":"#383838","belly":"#707070","ear_in":"#806868","cheek":"#907878"},
            "spot":    {"body":"#FEFEFE","stripe":"#E8E0D8","belly":"#FFF8F0","ear_in":"#FFE0D0","cheek":"#FFD8D0","patch":"#404040"},
            "pink":    {"body":"#FFE0E8","stripe":"#F0C8D0","belly":"#FFF0F4","ear_in":"#FFD0D8","cheek":"#FFD8E0"},
        },
        "body_ratio": {"body_w":24,"body_h":22,"head_r":38,"head_y_off":6},
        "ear":"long_oval","tail":"ball","face_extras":[],
        "sound":"蹦","identity_tag":"兔",
    },
    "bear": {
        "name":"熊熊","emoji":"🐻",
        "palettes": {
            "brown":   {"body":"#B08868","stripe":"#886040","belly":"#E8D0B8","ear_in":"#D8B898","cheek":"#E8C8B0"},
            "panda":   {"body":"#F8F8F8","stripe":"#E0E0E0","belly":"#FFFFFF","ear_in":"#3A3A3A","cheek":"#FFE0E0","patch":"#3A3A3A"},
            "polar":   {"body":"#FEFEFC","stripe":"#E8E4E0","belly":"#FFFFFF","ear_in":"#F8F0E8","cheek":"#FFF0F0"},
            "black":   {"body":"#484848","stripe":"#303030","belly":"#606060","ear_in":"#685858","cheek":"#887878"},
            "honey":   {"body":"#D8A860","stripe":"#B08040","belly":"#F0D8B0","ear_in":"#E8C890","cheek":"#F0D0A8"},
            "red":     {"body":"#D87860","stripe":"#B05040","belly":"#F0C0B0","ear_in":"#E89880","cheek":"#F0B0A0"},
        },
        "body_ratio": {"body_w":34,"body_h":28,"head_r":44,"head_y_off":-2},
        "ear":"round","tail":"tiny_ball","face_extras":[],
        "sound":"嗷","identity_tag":"熊",
    },
    "chick": {
        "name":"小鸡","emoji":"🐤",
        "palettes": {
            "yellow":  {"body":"#FFE888","stripe":"#F0D860","belly":"#FFF8D0","ear_in":"#FFE8A0","cheek":"#FFD888"},
            "white":   {"body":"#FEFEFE","stripe":"#E8E4E0","belly":"#FFFFFF","ear_in":"#FFF8E0","cheek":"#FFE8D0"},
            "brown":   {"body":"#D8C090","stripe":"#B8A070","belly":"#F0E8D0","ear_in":"#E8D8B0","cheek":"#F0E0C0"},
            "black":   {"body":"#484840","stripe":"#303028","belly":"#686860","ear_in":"#606050","cheek":"#888070"},
            "pink":    {"body":"#FFD8E0","stripe":"#F0C0C8","belly":"#FFF0F4","ear_in":"#FFD0D8","cheek":"#FFDDE4"},
            "orange":  {"body":"#FFC080","stripe":"#F0A060","belly":"#FFE8C8","ear_in":"#FFD8A8","cheek":"#FFD8B0"},
        },
        "body_ratio": {"body_w":22,"body_h":22,"head_r":36,"head_y_off":4},
        "ear":"none_comb","tail":"none","face_extras":["beak"],
        "sound":"叽","identity_tag":"鸡",
    },
    "hamster": {
        "name":"仓鼠","emoji":"🐹",
        "palettes": {
            "golden":  {"body":"#E8C890","stripe":"#C8A860","belly":"#FFF8E8","ear_in":"#F0D0B0","cheek":"#FFD8C0"},
            "silver":  {"body":"#D8D0D0","stripe":"#B0A8A8","belly":"#F8F0F0","ear_in":"#E8E0D8","cheek":"#F0E0E0"},
            "pudding": {"body":"#F8E8C8","stripe":"#E0D0A8","belly":"#FFFFF0","ear_in":"#F0E0C0","cheek":"#FFE8D0"},
            "white":   {"body":"#FEFEFE","stripe":"#E8E4E0","belly":"#FFFFFF","ear_in":"#FFF0E8","cheek":"#FFE8E0"},
            "grey":    {"body":"#A09890","stripe":"#807870","belly":"#D0C8C0","ear_in":"#C0B8B0","cheek":"#D8C8C0"},
            "black":   {"body":"#484840","stripe":"#303028","belly":"#686860","ear_in":"#585850","cheek":"#787068"},
        },
        "body_ratio": {"body_w":24,"body_h":24,"head_r":40,"head_y_off":2},
        "ear":"small_round","tail":"tiny_ball","face_extras":["big_cheeks"],
        "sound":"吱","identity_tag":"鼠",
    },
    "fox": {
        "name":"狐狸","emoji":"🦊",
        "palettes": {
            "red":     {"body":"#F08050","stripe":"#D06030","belly":"#FFF0E0","ear_in":"#FFE0D0","cheek":"#FFD8C8"},
            "white":   {"body":"#F8F0E8","stripe":"#E0D8D0","belly":"#FFFEF8","ear_in":"#F0E8E0","cheek":"#FFF0E8"},
            "grey":    {"body":"#C0B0A0","stripe":"#988878","belly":"#F0E8E0","ear_in":"#D8C8B8","cheek":"#E8D8C8"},
            "black":   {"body":"#383838","stripe":"#202020","belly":"#585858","ear_in":"#504848","cheek":"#686058"},
            "golden":  {"body":"#E8B870","stripe":"#C89848","belly":"#FFF0D8","ear_in":"#F0D0A0","cheek":"#F8D8B0"},
            "coral":   {"body":"#F09080","stripe":"#D87060","belly":"#FFE8E0","ear_in":"#F8C0B8","cheek":"#F8D0C8"},
        },
        "body_ratio": {"body_w":28,"body_h":22,"head_r":42,"head_y_off":8},
        "ear":"big_triangle","tail":"fluffy_big","face_extras":[],
        "sound":"嗷呜","identity_tag":"狐",
    },
    "penguin": {
        "name":"企鹅","emoji":"🐧",
        "palettes": {
            "emperor": {"body":"#2A2A38","stripe":"#1A1A28","belly":"#F8F8F8","ear_in":"#404050","cheek":"#FFE8D0"},
            "blue":    {"body":"#3A5068","stripe":"#283848","belly":"#F0F4F8","ear_in":"#506078","cheek":"#FFE0D0"},
            "rock":    {"body":"#383840","stripe":"#282830","belly":"#F0F0F0","ear_in":"#484850","cheek":"#FFD8C8"},
            "gentoo":  {"body":"#303040","stripe":"#202030","belly":"#FEFEFE","ear_in":"#485060","cheek":"#FFE0C8"},
            "baby":    {"body":"#585860","stripe":"#404050","belly":"#F8F8F8","ear_in":"#606068","cheek":"#FFE8D8"},
            "pink":    {"body":"#F8D0D8","stripe":"#E8B8C0","belly":"#FFF8FA","ear_in":"#F0C8D0","cheek":"#FFE0E8"},
        },
        "body_ratio": {"body_w":26,"body_h":26,"head_r":38,"head_y_off":14},
        "ear":"none","tail":"short","face_extras":["pointy_beak"],
        "sound":"啾","identity_tag":"鹅",
    },
}

# 物种性格预设
SPECIES_PERSONALITY = {
    "cat": {
        "hobbies": ["爱睡觉","爱吃","爱发呆"], "habits": ["独立","调皮"],
        "identities": ["程序猫","外卖猫","摸鱼猫","学生猫","养生猫","夜猫子"],
        "quirks": ["追尾狂魔","键盘杀手","纸箱控","日光族","虚空捕手","洁癖猫","报时猫","爬高狂"],
    },
    "dog": {
        "hobbies": ["爱玩耍","爱吃","爱探索"], "habits": ["黏人","活泼","话多"],
        "identities": ["看门狗","导盲犬","警犬","二哈","金毛","柴柴"],
        "quirks": ["接飞盘","刨坑","追尾巴","摇尾巴","拆家","舔屏","游泳健将","干饭王"],
    },
    "rabbit": {
        "hobbies": ["爱吃","爱发呆","爱聊天"], "habits": ["胆小","乖巧","黏人"],
        "identities": ["垂耳兔","野兔","家兔","月兔","兔兔","小白兔"],
        "quirks": ["蹦跳能手","钻洞迷","洗耳朵","转圈圈","啃胡萝卜","装死","竖耳朵"],
    },
    "bear": {
        "hobbies": ["爱吃","爱睡觉","爱发呆"], "habits": ["慵懒","黏人","独立"],
        "identities": ["棕熊","熊猫","北极熊","维尼熊","泰迪熊","黑熊"],
        "quirks": ["捕鱼","爬树","冬眠","转圈","拍肚皮","抱竹啃","蹭树"],
    },
    "chick": {
        "hobbies": ["爱探索","爱聊天","爱吃"], "habits": ["胆小","黏人","话多"],
        "identities": ["小黄鸡","小白鸡","花鸡","战斗鸡","鸡仔","蛋仔"],
        "quirks": ["啄米","孵蛋","晨鸣","刨土","跑酷","拍翅膀","好奇宝宝"],
    },
    "hamster": {
        "hobbies": ["爱吃","爱玩耍","爱探索"], "habits": ["调皮","话多","胆小"],
        "identities": ["金丝熊","银狐","布丁","奶茶仓鼠","一线","三线"],
        "quirks": ["跑轮","囤粮","钻洞","塞腮帮","钻木屑","越狱","夜游神"],
    },
    "fox": {
        "hobbies": ["爱探索","爱玩耍","爱吃"], "habits": ["独立","调皮","话多"],
        "identities": ["赤狐","白狐","耳廓狐","九尾狐","小狐狸","火狐"],
        "quirks": ["挖洞","伪装","偷袭","跳舞","甩尾巴","偷鸡","捕鼠","装死"],
    },
    "penguin": {
        "hobbies": ["爱玩耍","爱探索","爱聊天"], "habits": ["黏人","话多","活泼"],
        "identities": ["帝企鹅","王企鹅","小蓝企鹅","跳岩企鹅","QQ鹅","绅士鹅"],
        "quirks": ["滑冰","游泳","抱团","学步","跳水","孵蛋","拍肚皮","排队"],
    },
}
# ══════════ 多物种系统 END ══════════

# ── 对话库 ──
TALK = {
    "chase":["等等我呀~","诶嘿，你在找我吗？","鼠标好好玩！","别跑~","抓到你了！","那个小箭头…别动！"],
    "click":["呀！","喵呜~","嘻嘻","好痒~","（被戳到啦）","再摸一下嘛~","呼噜呼噜…舒服"],
    "double":["怎么啦主人~","想和我聊天吗？","我在呢！","好开心你来理我~"],
    "sleep":["zzZ…","（小声呼噜）","不要吵…在做好梦呢…","zzZ…梦见好多小鱼干…"],
    "wake":["嗯…睡醒了~","（伸懒腰）喵~","这一觉睡得好舒服哦","主人我醒啦！"],
    "idle":["今天也要加油哦~","（悠闲地摇尾巴）","喵~","一切安好！","（好奇地东张西望）","主人不忙的时候陪陪我嘛~","（打了个哈欠）但没睡！精神着呢"],
    "late":["都这么晚啦！快睡吧~","熬夜不好哦…明天再陪我玩","眼睛要坏掉的！乖，去睡觉"],
    "morning":["早安！今天也要元气满满~","早上好呀~新的一天开始了！","（打哈欠）早…我还没完全醒…"],
    "egg":["（一颗可爱的蛋…）","咚！好像有动静…","咔嚓…好像快裂开了…"],
    "care":["主人真贴心~被关心的感觉真好","谢谢主人照顾我！我也会照顾好你的💕","有主人的关心，{name}觉得好幸福","被摸了脑袋…好温暖","主人的手好温柔呀~"],
    "comfort":["没关系的，一切都会好起来的~","有{name}在呢！你不是一个人","累了就停下来，{name}陪着你","不要勉强自己，你已经很棒了","不开心的时候就来摸摸{name}吧"],
    "hungry_self":["主人什么时候吃饭呀？{name}帮你看着时间","该吃饭啦！主人不吃{name}也不吃！（虽然我没饭）","肚子咕咕叫了吗？快去觅食！"],
}

# 默认 API Key 存放在 presets/default_api.json，随应用分发
def _load_default_api_key():
    """从 presets 目录加载默认 API Key"""
    p = os.path.join(PRESETS_DIR, 'default_api.json')
    if os.path.exists(p):
        try:
            with open(p, 'r') as f:
                return json.load(f).get('key', '')
        except:
            pass
    return ''

# ══════════ 主应用 ══════════
def ensure_single_instance():
    """单实例锁——同一只猫不能启动两次"""
    lock_file = os.path.join(DATA_DIR, ".pet_lock")
    if os.path.exists(lock_file):
        try:
            with open(lock_file) as f:
                old_pid = int(f.read().strip())
            # 检查旧进程是否还在运行
            import ctypes.wintypes
            handle = ctypes.windll.kernel32.OpenProcess(0x0400, False, old_pid)
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
                log(f"已有实例运行 PID={old_pid}")
                return False
        except:
            pass
        # 旧进程已死，清理
        try: os.remove(lock_file)
        except: pass

    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))
    return True


def release_single_instance():
    try: os.remove(os.path.join(DATA_DIR, ".pet_lock"))
    except: pass


class DesktopPet:
    def __init__(self):
        if not ensure_single_instance():
            # 已有实例在运行
            import tkinter.messagebox as mb
            mb.showinfo("月薪猫", "猫咪已经在桌面上了~\n看看屏幕找找它吧！")
            sys.exit(0)

        self.root = tk.Tk()
        self.root.title("月薪猫")
        self.root.overrideredirect(True)
        self.root.wm_attributes('-transparentcolor','#010101')
        self.root.attributes('-topmost', True)  # 始终置顶
        self.root.configure(bg='#010101')
        self._always_on_top = True
        self.size = 240
        self.root.geometry(f"{self.size}x{self.size}+800+400")

        self.canvas = tk.Canvas(self.root,width=self.size,height=self.size,
                                bg='#010101',highlightthickness=0)
        self.canvas.pack()

        # ── 档案 ──
        self.profile_mgr = PetProfile(DATA_DIR)
        self.archive = ArchiveGuard(DATA_DIR)

        if not self.profile_mgr.exists():
            self._setup_wizard()
            # 用户取消了向导
            if not self.profile_mgr.exists():
                try:
                    import tkinter.messagebox as mb
                    mb.showinfo("月薪猫", "你取消了创猫仪式。\n下次启动时还可以重新创建哦~")
                except: pass
                self.root.destroy()
                sys.exit(0)

        self.profile = self.profile_mgr.load()
        assert self.profile, "档案为空"
        a = self.profile.get("appearance",{})
        self.species = a.get("species","cat")
        self.fur = a.get("fur_color",{"cat":"orange","dog":"golden","rabbit":"white","bear":"brown","chick":"yellow","hamster":"golden","fox":"red","penguin":"emperor"}.get(self.species,"orange"))
        self.eye_color = a.get("eye_color","gold")
        self.acc = a.get("accessory","bowtie")
        self.pet_name = self.profile.get("name","小橘")
        sp = SPECIES.get(self.species, SPECIES["cat"])
        self.colors = sp["palettes"].get(self.fur, sp["palettes"][list(sp["palettes"].keys())[0]])
        self._eye_rgb = {"gold":"#F5C842","blue":"#60B8F8","green":"#6CD888","odd":None}

        # ── 逻辑系统 ──
        self.db = Database(DATA_DIR)
        self.state_mgr = StateManager(DATA_DIR)
        self.personality = PersonalitySystem(self.profile)
        self.emotion = EmotionEngine()
        self.growth = GrowthSystem(DATA_DIR)
        self.trust = TrustSystem()
        self.autonomy = AutonomyEngine()
        self.memory = MemorySystem(self.db)
        self.dialogue = DialogueEngine(PRESETS_DIR)

        saved = self.state_mgr.load_state()
        if saved:
            for mod,key in [(self.emotion,"emotion"),(self.growth,"growth"),
                            (self.trust,"trust"),(self.autonomy,"autonomy")]:
                if key in saved: mod.restore_state(saved[key])
        pos = self.state_mgr.load_window_position()
        if pos: self.root.geometry(f"+{pos[0]}+{pos[1]}")
        self._was_clean = self.state_mgr.was_clean_exit()
        self._apply_growth_ui()

        # ── 状态 ──
        self.anim_state = "egg_idle" if self.growth.is_egg else "idle"
        self.frame = 0
        self._mx = 0; self._my = 0
        self._mouse_near = False
        self._bids = []
        self._talk_cd = 0
        self._last_int = datetime.now()
        self._today = datetime.now().date()
        self._clicks = 0; self._pets = 0; self._save_cnt = 0
        self._chat_dlg = None
        self._hearts = []  # 飘出的小心心
        self._wander_target = None  # 自主漫游目标
        self._wander_timer = 0
        self._free_move = True
        self._idle_variant = 0  # idle动画变体
        self._curious_tilt = 0  # 歪头角度
        self._night_mode = False  # 夜间模式
        self._last_hour_check = -1  # 整点报时
        self._achievements = set()  # 已解锁成就
        self._thought_bubble = None  # 内心OS气泡id
        self._toy_pos = None  # 逗猫棒位置
        self._toy_timer = 0
        self._auto_start = False  # 开机自启
        # API 配置
        self._api_key = None
        self._api_configured = False
        self._load_api_config()
        self._zoomies = False  # 疯跑模式
        self._zoom_dir = (0,0)
        self._typing_count = 0  # 连续打字计数
        self._grooming = False  # 舔毛
        self._last_action_time = datetime.now()
        self._action_queue = []  # 行为队列
        self._blink_frame = 0  # 眨眼帧计数：0=睁眼，1-2=闭眼
        self._blink_cooldown = random.randint(30, 120)  # 眨眼间隔（帧数）

        # ── 绑定 ──
        self.canvas.bind("<Button-1>",self._on_click)
        self.canvas.bind("<Double-Button-1>",self._on_double)
        self.canvas.bind("<B1-Motion>",self._on_drag)
        self.canvas.bind("<ButtonRelease-1>",self._on_release)
        self.canvas.bind("<Button-3>",self._on_right)

        # 🆕 整点报时+昼夜模式检查
        self._check_hourly()
        self._update_night_mode()
        # 🆕 开机自启状态检查
        self._check_auto_start()

        # ── 定时器 ──
        self._animate_loop()
        self._mouse_loop()
        self._brain_loop()
        self._auto_save_loop()

        atexit.register(self._on_close)
        atexit.register(release_single_instance)
        log(f"✅ {self.pet_name} | 成长:{self.growth.stage} | 心情:{self.emotion.current_mood}")

        if self.growth.is_egg:
            self._say("（一颗可爱的蛋…多摸摸我~）",4000)
        elif not self._was_clean:
            self._say("上次我突然消失了…发生了什么？",4000)

    # ══════════ 首次设置向导 ══════════
    def _setup_wizard(self):
        """首次设置弹窗 — 支持8种动物"""
        dlg = tk.Toplevel(self.root)
        dlg.title("🎀 创造你的专属桌宠！")
        dlg.configure(bg="#FFF5F8")
        dlg.resizable(False, False)

        dlg.transient(self.root)
        dlg.grab_set()
        dlg.focus_force()
        dlg.protocol("WM_DELETE_WINDOW", dlg.destroy)

        tk.Label(dlg, text="🎀 创造你的专属桌宠！", font=("Microsoft YaHei", 16, "bold"),
                bg="#FFF5F8", fg="#E87890").pack(pady=(12, 2))
        tk.Label(dlg, text="选择你喜欢的动物和造型~", font=("Microsoft YaHei", 9),
                bg="#FFF5F8", fg="#C09098").pack(pady=(0, 8))

        # 名字
        tk.Label(dlg, text="给你的宠物取个名字", font=("Microsoft YaHei", 11),
                bg="#FFF5F8", fg="#886060").pack()
        name_var = tk.StringVar(value="小橘")
        name_entry = tk.Entry(dlg, textvariable=name_var, font=("Microsoft YaHei", 14),
                             justify=tk.CENTER, relief=tk.FLAT, bg="#FFF", width=16)
        name_entry.pack(ipady=4, pady=(4, 6))

        # 物种选择
        tk.Label(dlg, text="选择你的宠物", font=("Microsoft YaHei", 11),
                bg="#FFF5F8", fg="#886060").pack()
        species_var = tk.StringVar(value="cat")
        species_list = [("cat","🐱猫"),("dog","🐶狗"),("rabbit","🐰兔"),("bear","🐻熊"),
                       ("chick","🐤小鸡"),("hamster","🐹仓鼠"),("fox","🦊狐狸"),("penguin","🐧企鹅")]
        sp_frame = tk.Frame(dlg, bg="#FFF5F8")
        sp_frame.pack(pady=4)
        for i, (val, label) in enumerate(species_list):
            tk.Radiobutton(sp_frame, text=label, variable=species_var, value=val,
                          font=("Microsoft YaHei", 11), bg="#FFF5F8",
                          indicatoron=0, padx=10, pady=4, cursor="hand2",
                          selectcolor="#FFD0E0").grid(row=i // 4, column=i % 4, padx=3, pady=2)

        # 毛色（根据物种动态切换）
        tk.Label(dlg, text="选择颜色", font=("Microsoft YaHei", 11),
                bg="#FFF5F8", fg="#886060").pack(pady=(8, 0))
        fur_var = tk.StringVar(value="orange")
        fur_frame = tk.Frame(dlg, bg="#FFF5F8")
        fur_frame.pack(pady=4)
        fur_labels_dict = {}

        def update_fur_options(*_):
            sp = species_var.get()
            palettes = SPECIES.get(sp, SPECIES["cat"])["palettes"]
            fur_names = SPECIES_FUR_NAMES.get(sp, {})
            keys = list(palettes.keys())
            fur_var.set(keys[0])
            for widget in fur_frame.winfo_children():
                widget.destroy()
            fur_labels_dict.clear()
            for i, k in enumerate(keys):
                cn_name = fur_names.get(k, k)
                label = f"🎨{cn_name}"
                rb = tk.Radiobutton(fur_frame, text=label, variable=fur_var, value=k,
                                   font=("Microsoft YaHei", 10), bg="#FFF5F8", anchor=tk.W)
                rb.grid(row=i // 4, column=i % 4, sticky=tk.W, padx=8, pady=3)
                fur_labels_dict[k] = rb

        species_var.trace_add("write", update_fur_options)
        update_fur_options()  # 初始加载猫的配色

        # 眼睛
        eye_frame_outer = tk.Frame(dlg, bg="#FFF5F8")
        eye_frame_outer.pack(pady=(6, 0))
        tk.Label(eye_frame_outer, text="眼睛颜色", font=("Microsoft YaHei", 11),
                bg="#FFF5F8", fg="#886060").pack()
        eye_var = tk.StringVar(value="gold")
        eye_frame = tk.Frame(eye_frame_outer, bg="#FFF5F8")
        eye_frame.pack(pady=2)
        for val, label in [("gold","👁金色"),("blue","👁蓝色"),("green","👁绿色"),("odd","👁异瞳")]:
            tk.Radiobutton(eye_frame, text=label, variable=eye_var, value=val,
                          font=("Microsoft YaHei", 10), bg="#FFF5F8").pack(side=tk.LEFT, padx=6)

        # 配饰
        acc_frame_outer = tk.Frame(dlg, bg="#FFF5F8")
        acc_frame_outer.pack(pady=(4, 0))
        tk.Label(acc_frame_outer, text="小配饰", font=("Microsoft YaHei", 11),
                bg="#FFF5F8", fg="#886060").pack()
        acc_var = tk.StringVar(value="bowtie")
        acc_frame = tk.Frame(acc_frame_outer, bg="#FFF5F8")
        acc_frame.pack(pady=2)
        for val, label in [("bowtie","🎀蝴蝶结"),("ribbon","🎗发带"),("bell","🔔铃铛"),("flower","🌸小花"),("none","无")]:
            tk.Radiobutton(acc_frame, text=label, variable=acc_var, value=val,
                          font=("Microsoft YaHei", 10), bg="#FFF5F8").pack(side=tk.LEFT, padx=4)

        # ── 性格选择 ──
        pers_frame = tk.Frame(dlg, bg="#FFF5F8")
        pers_frame.pack(pady=(8, 0), fill=tk.X, padx=20)

        tk.Label(pers_frame, text="💬 话风", font=("Microsoft YaHei", 11),
                bg="#FFF5F8", fg="#886060").pack(anchor=tk.W)
        talk_var = tk.StringVar(value="喵系")
        talk_f = tk.Frame(pers_frame, bg="#FFF5F8"); talk_f.pack(pady=2, anchor=tk.W)
        for v in ["喵系","吐槽系","撒娇系","高冷系"]:
            tk.Radiobutton(talk_f, text=v, variable=talk_var, value=v,
                          font=("Microsoft YaHei", 9), bg="#FFF5F8").pack(side=tk.LEFT, padx=4)

        def make_checkbox_group(parent, title, options, default_count=2):
            """创建一组复选框"""
            f = tk.LabelFrame(parent, text=title, font=("Microsoft YaHei", 10),
                             bg="#FFF5F8", fg="#886060", padx=4, pady=2)
            f.pack(pady=3, fill=tk.X)
            vars_dict = {}
            inner = tk.Frame(f, bg="#FFF5F8"); inner.pack()
            for j, opt in enumerate(options):
                v = tk.BooleanVar(value=(j < default_count))
                tk.Checkbutton(inner, text=opt, variable=v,
                              font=("Microsoft YaHei", 9), bg="#FFF5F8",
                              selectcolor="#FFD0E0", anchor=tk.W).grid(row=j//3, column=j%3, sticky=tk.W, padx=4)
                vars_dict[opt] = v
            return vars_dict

        def update_personality_options(*_):
            sp = species_var.get()
            sp_pers = SPECIES_PERSONALITY.get(sp, SPECIES_PERSONALITY["cat"])
            for widget in pers_frame.winfo_children():
                if widget not in (pers_frame.winfo_children()[0], talk_f):  # keep title+talk
                    pass
            # 清除旧的性格选项
            for child in list(pers_frame.children.values()):
                if isinstance(child, tk.LabelFrame):
                    child.destroy()
            # 重新创建
            global _wizard_hobby_vars, _wizard_habit_vars, _wizard_quirk_vars, _wizard_id_vars, _wizard_id_var
            _wizard_hobby_vars = make_checkbox_group(pers_frame, "❤ 爱好（多选）", sp_pers["hobbies"], 2)
            _wizard_habit_vars = make_checkbox_group(pers_frame, "🎭 习惯（多选）", sp_pers["habits"], 2)
            # 身份单选
            id_f = tk.LabelFrame(pers_frame, text="🏷 身份", font=("Microsoft YaHei", 10),
                                bg="#FFF5F8", fg="#886060", padx=4, pady=2)
            id_f.pack(pady=3, fill=tk.X)
            id_inner = tk.Frame(id_f, bg="#FFF5F8"); id_inner.pack()
            _wizard_id_var = tk.StringVar(value=sp_pers["identities"][0])
            _wizard_id_vars = {}
            for j, opt in enumerate(sp_pers["identities"]):
                tk.Radiobutton(id_inner, text=opt, variable=_wizard_id_var, value=opt,
                              font=("Microsoft YaHei", 9), bg="#FFF5F8",
                              anchor=tk.W).grid(row=j//3, column=j%3, sticky=tk.W, padx=4)
                _wizard_id_vars[opt] = True
            _wizard_quirk_vars = make_checkbox_group(pers_frame, "🎲 癖好（多选）", sp_pers["quirks"], 2)

        species_var.trace_add("write", update_personality_options)
        _wizard_hobby_vars = {}
        _wizard_habit_vars = {}
        _wizard_quirk_vars = {}
        _wizard_id_var = tk.StringVar()
        _wizard_id_vars = {}
        update_personality_options()

        # 按钮
        btn_frame = tk.Frame(dlg, bg="#FFF5F8")
        btn_frame.pack(pady=(8, 0))
        tk.Button(btn_frame, text="下次再说", command=dlg.destroy,
                 font=("Microsoft YaHei", 10), bg="#E0E0E0", fg="#666",
                 relief=tk.FLAT, padx=20, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=8)

        def confirm():
            sp = species_var.get()
            hobbies = [k for k, v in _wizard_hobby_vars.items() if v.get()]
            habits = [k for k, v in _wizard_habit_vars.items() if v.get()]
            quirks = [k for k, v in _wizard_quirk_vars.items() if v.get()]
            identity = _wizard_id_var.get()
            profile = {
                "name": name_var.get() or "小橘",
                "birthday": datetime.now().strftime("%m-%d"),
                "zodiac": "gemini",
                "_version": "2.0.0",
                "created_at": datetime.now().isoformat(),
                "appearance": {
                    "species": sp,
                    "fur_color": fur_var.get(),
                    "eye_color": eye_var.get(),
                    "accessory": acc_var.get(),
                },
                "personality": {
                    "hobbies": hobbies or ["爱吃","爱聊天"],
                    "habits": habits or ["黏人","话多"],
                    "talk_style": talk_var.get(),
                    "identity": identity,
                    "quirks": quirks or ["日光族"],
                }
            }
            self.profile_mgr.create(profile)
            self.archive.sign(self.profile_mgr.path)
            dlg.destroy()

        tk.Button(btn_frame, text="✨ 确认创造！", command=confirm,
                 font=("Microsoft YaHei", 12, "bold"), bg="#FF90A8", fg="white",
                 relief=tk.FLAT, padx=28, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=8)
        tk.Label(dlg, text="⚠ 确认后档案锁定", font=("Microsoft YaHei", 8),
                bg="#FFF5F8", fg="#C0A0A8").pack(pady=(2, 0))

        dlg.update_idletasks()
        sw = dlg.winfo_screenwidth(); sh = dlg.winfo_screenheight()
        dlg.geometry(f"+{(sw - 500) // 2}+{max(20, (sh - 700) // 2)}")
        self.root.wait_window(dlg)

    # ══════════ 成长UI ══════════
    def _apply_growth_ui(self):
        s = self.growth.stage
        sz = {"egg":90,"kitten":160,"adult":240,"master":240}.get(s,240)
        self.size = sz
        cx,cy = self.root.winfo_x(),self.root.winfo_y()
        self.root.geometry(f"{sz}x{sz}+{cx}+{cy}")
        self.canvas.config(width=sz,height=sz)

    # ══════════ 大脑 ══════════
    
    def _get_active_window(self):
        """读取当前前台窗口标题——只看不改，不碰文件"""
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                return buf.value
        except: pass
        return ''
    
    def _guess_app(self, title):
        """根据窗口标题猜应用"""
        t = title.lower()
        if any(k in t for k in ['visual studio','vs code','vscode','cursor','idea','pycharm','eclipse']): return 'code'
        if any(k in t for k in ['word','wps','文档','doc']): return 'doc'
        if any(k in t for k in ['excel','表格','sheet','xls']): return 'excel'
        if any(k in t for k in ['chrome','edge','firefox','浏览器','browser']): return 'browser'
        if any(k in t for k in ['微信','wechat']): return 'wechat'
        if any(k in t for k in ['qq','tim']): return 'qq'
        if any(k in t for k in ['bilibili','youtube','视频']): return 'video'
        if any(k in t for k in ['steam','游戏','game']): return 'game'
        if any(k in t for k in ['terminal','cmd','powershell','bash']): return 'terminal'
        if any(k in t for k in ['explorer','文件','桌面']): return 'desktop'
        return 'other'
    def _brain_loop(self):
        try:
            now = datetime.now()
            if now.date() != self._today:
                self._today = now.date()
                self.trust.on_new_day()
                # 🆕 成就检测
                self._check_achievement("days7",self.growth.age_days>=7,"一周纪念","已经陪伴一周啦！")
                self._check_achievement("days30",self.growth.age_days>=30,"满月","满一个月了！好开心！")
                self._check_achievement("days100",self.growth.age_days>=100,"百日相伴","一百天了…谢谢你")
                self._check_achievement("trust50",self.trust.trust>=50,"信任伙伴","完全信任主人了~")
                self._check_achievement("pets100",self._pets>=100,"百撸成钢","被摸了一百次！")
                self.memory.summarize_old_conversations(50)
            hrs = (now-self.emotion._last_update).total_seconds()/3600
            if hrs>0.1: self.emotion.apply_decay(hrs)
            idle = (now-self._last_int).total_seconds()
            self.autonomy.apply_time(2/3600)
            # 🆕 内心OS（偶尔冒泡猫在想什么）
            if random.random() < 0.04:
                thoughts = ["今天天气不错的样子…","主人什么时候摸我？","这个角落好舒服",
                            "那个光标为什么一直动…","zzZ…啊没有我没睡着","有点饿了…想象中",
                            "主人的键盘声真好听","（思考猫生中）","好想抓点什么…"]
                self._show_thought(random.choice(thoughts), 3000)
            
            # 加速无聊和困意积累
            self.autonomy.drives["boredom"] = min(1.0, idle/60)
            if idle>120: self.autonomy.drives["sleepiness"]=min(1,idle/600)
            if idle<30: self.autonomy.drives["social"]=0.3
            if self._mouse_near:
                self.autonomy.drives["playfulness"]=min(1,self.autonomy.drives.get("playfulness",0.5)+0.05)
                self.autonomy.drives["boredom"] = max(0, self.autonomy.drives["boredom"]-0.3)

            # 🆕 丰富的行为系统
            if not self.growth.is_egg and self.anim_state not in ("sleep",):
                r = random.random()

                # 疯跑模式（极低概率）
                if self._free_move and r < 0.02 and self._mouse_near and not self._zoomies:
                    self._zoomies = True
                    self._zoomie_timer = 0
                    self.anim_state = "walk"
                    self._say(random.choice(["冲鸭！！","好兴奋！停不下来~","加速加速！！"]),2000)

                # 无聊→自己玩
                elif not self._mouse_near and idle > 20 and r < 0.25 and not self._wander_target:
                    choice = random.random()
                    if choice < 0.4 and self._free_move:
                        # 随机走动
                        sw = max(0,self.root.winfo_screenwidth()-self.size)
                        sh = max(0,self.root.winfo_screenheight()-self.size-60)
                        self._wander_target = (random.randint(50,max(100,sw)),random.randint(50,max(100,sh)))
                        self.anim_state = "walk"; self._wander_timer = 0
                    elif choice < 0.7:
                        # 歪头好奇
                        self._curious_tilt = random.choice([-15,15,-8,8])
                        self._say(random.choice(["嗯？那是什么？","（好奇）","（歪头看）","咦？"]),2500)
                    elif choice < 0.9:
                        # 舔毛
                        self._grooming = True
                        self._say(random.choice(["舔舔毛…要保持干净~","（认真洗脸）","整理一下仪表~"]),3000)
                    else:
                        # 虚空扑击
                        self.anim_state = "jump"; self.frame = 0
                        self._say(random.choice(["抓到你了！…诶什么都没有","（扑向空气）","有飞虫！…看错了"]),2500)
                    self.autonomy.drives["boredom"] = 0

                # 长时间观察→换idle变体
                elif not self._mouse_near and idle > 60 and r < 0.3:
                    self._idle_variant = random.randint(0,3)
                    if r < 0.1:
                        self._say(random.choice(["（伸了个懒腰）","喵~（打了个哈欠）","嗯…有点无聊了","（甩甩尾巴）"]),2500)

                # 打字很多→围观
                if self._typing_count > 5 and r < 0.3:
                    self.anim_state = "idle"
                    self._idle_variant = 3  # 认真看的变体
                    self._typing_count = 0
                    if r < 0.1:
                        self._say(random.choice(["主人好认真！","在写什么呢~","加油加油！我在看着呢"]),3000)

            # 睡觉决策
            if self.autonomy.drives["sleepiness"] > 0.75 and self.anim_state not in ("sleep","walk"):
                if idle > 120:
                    self.anim_state = "sleep"
                    self._say(random.choice(TALK["sleep"]),3000)
            self._talk_cd = max(0,self._talk_cd-2)
            hour = now.hour
            # 🆕 感知前台应用
            active_win = self._get_active_window()
            app = self._guess_app(active_win)
            if self._talk_cd == 0 and random.random() < 0.03:
                app_talk = {
                    "code": ["写代码中！加油~","又在debug吗？摸摸我放松下","代码跑起来！"],
                    "doc": ["在写文档呀~","好多字…好厉害！"],
                    "browser": ["上网冲浪中~看到好玩的了吗？"],
                    "wechat": ["在聊天吗？","记得回我消息哦~"],
                    "video": ["在看视频！我也想看~","看到好玩的要分享哦"],
                    "game": ["游戏加油！","冲冲冲！"],
                }
                talks = app_talk.get(app, [])
                if talks:
                    self._say(random.choice(talks), 3500)
                    self._talk_cd = 60
            
            # 🆕 根据用户活动类型调整行为
            if self._typing_count > 3:
                activity = "working"  # 在忙
            elif idle < 10 and self._mouse_near:
                activity = "browsing"  # 浏览
            elif idle > 60:
                activity = "away"  # 离开
            else:
                activity = "chilling"  # 休闲
            
            # 根据活动说不同的话
            if activity == "working" and self._talk_cd == 0 and random.random() < 0.06:
                self._say(random.choice([
                    "主人好忙呀…加油！","键盘敲得好快！","在写代码吗？","认真工作的主人最帅了~",
                    "今天也好努力！{name}给你倒杯想象中的咖啡☕","工作累了就看看我放松一下~",
                    "这么认真…一定是个厉害的人吧！","别太累了哦，记得中间休息一下！"
                ]), 3500)
                self._talk_cd = 30
            elif activity == "away" and self._talk_cd == 0 and random.random() < 0.04:
                self._say(random.choice([
                    "主人去哪了…","（左顾右盼）","快点回来哦~","我一个人看好家！",
                    "主人离开了…{name}帮你看着桌面！","去哪啦？要快点回来哦，我会想你的~"
                ]), 3000)
                self._talk_cd = 45
            elif activity == "chilling" and self._talk_cd == 0 and random.random() < 0.03:
                self._say(random.choice([
                    "悠闲的午后~","主人也在摸鱼吗？嘿嘿","一起发呆吧~","（趴在桌上陪主人）",
                    "主人不忙的时候{name}最开心了~","就该这样！该摸鱼时就摸鱼！",
                    "要不要跟{name}聊聊天？我虽然话不多但我听得很认真！",
                    "今天心情怎么样呀？好也摸摸{name}，不好也摸摸{name}~"
                ]), 3500)
                self._talk_cd = 40
            
            if hour>=23 and random.random()<0.08 and self._talk_cd==0:
                self._say(random.choice(TALK["late"]),4000); self._talk_cd=60
            if random.random()<0.04*self.personality.get("talk_frequency",1) and self._talk_cd==0:
                ctx = {"hour":hour,"day_of_week":now.weekday()}
                txt = self.dialogue.get_dialogue_for_state(self.anim_state,self.personality,self.emotion,ctx,growth=self.growth)
                if txt:
                    self._say(txt,3500); self._talk_cd=20
                    self.memory.add_conversation("pet",txt)
        except Exception as e: log(f"brain err: {e}")
        self.root.after(2000,self._brain_loop)

    # ══════════ 动画+移动 ══════════
    def _animate_loop(self):
        self.frame = (self.frame+1)%8

        # 眨眼逻辑：猫偶尔眨眨眼，更自然可爱
        if self._blink_frame > 0:
            self._blink_frame -= 1  # 闭眼持续1-2帧后睁开
        elif self._blink_cooldown <= 0:
            # 触发眨眼（闭眼1-2帧），非睡眠状态下才眨眼
            if self.anim_state not in ("sleep",):
                self._blink_frame = random.randint(1, 2)
            self._blink_cooldown = random.randint(30, 120)  # 约4.5-18秒后再次眨眼
        else:
            self._blink_cooldown -= 1

        # 自主漫游移动（仅在自由移动模式下）
        if self._free_move and self._wander_target and not self._mouse_near and self.anim_state=="walk":
            tx, ty = self._wander_target
            cx, cy = self.root.winfo_x(), self.root.winfo_y()
            dx, dy = tx-cx, ty-cy
            dist = math.sqrt(dx*dx+dy*dy)
            if dist < 15:
                # 到达目标
                self._wander_target = None
                self._wander_timer = 0
                self.anim_state = "idle"
            else:
                self._wander_timer += 1
                # 超时放弃
                if self._wander_timer > 200:
                    self._wander_target = None
                    self._wander_timer = 0
                    self.anim_state = "idle"
                else:
                    # 平滑移动
                    speed = 8 if self._zoomies else 3

                    # 疯跑计时
                    if self._zoomies:
                        self._zoomie_timer = getattr(self, "_zoomie_timer", 0) + 1
                        if self._zoomie_timer > 50:
                            self._zoomies = False
                            self.anim_state = "idle"
                    # 歪头回归
                    if self._curious_tilt != 0:
                        self._curious_tilt = int(self._curious_tilt * 0.85)
                    # 舔毛计时
                    if self._grooming and self.frame % 3 == 0:
                        self._grooming = False
                    step_x = int(speed * dx / dist)
                    step_y = int(speed * dy / dist)
                    self.root.geometry(f"+{cx+step_x}+{cy+step_y}")

        self._draw()
        iv = 500 if self.anim_state=="sleep" else (400 if self.growth.is_egg else 150)
        self.root.after(iv,self._animate_loop)

    # ══════════ 鼠标 ══════════
    def _mouse_loop(self):
        mx = self.root.winfo_pointerx(); my = self.root.winfo_pointery()
        self._mx,self._my = mx,my
        wx = self.root.winfo_x()+self.size//2; wy = self.root.winfo_y()+self.size//2
        dist = math.sqrt((mx-wx)**2+(my-wy)**2)
        chase = self.personality.get("chase_distance",150)
        if dist<chase and not self.growth.is_egg and self._free_move:
            was_near = self._mouse_near
            self._mouse_near=True
            self._wander_target = None  # 追光标时取消漫游
            if self.anim_state not in ("sleep",): self.anim_state="walk"
            if not was_near:
                self._last_int=datetime.now(); self.growth.record_interaction("mouse_near")
                if random.random()<0.2 and self._talk_cd==0:
                    self._say(random.choice(TALK["chase"]),2500); self._talk_cd=10
            # 🆕 实际移动向光标
            dx, dy = mx-wx, my-wy
            if abs(dx)>30 or abs(dy)>30:
                step = 4
                nd = math.sqrt(dx*dx+dy*dy)
                self.root.geometry(f"+{self.root.winfo_x()+int(step*dx/nd)}+{self.root.winfo_y()+int(step*dy/nd)}")
        elif dist>=chase*1.5:
            if self._mouse_near:
                self._mouse_near=False
                if self.anim_state=="walk" and not self._wander_target:
                    self.anim_state="idle"
        self.root.after(200,self._mouse_loop)

    # ══════════ 交互 ══════════
    def _on_click(self,event):
        self._drag_x,self._drag_y = event.x,event.y
        self._wander_target = None  # 用户操作时取消漫游
        if not self.growth.is_egg:
            self.anim_state="jump"; self.frame=0
        self._last_int=datetime.now(); self.growth.record_interaction("pet")
        self.emotion.apply_interaction("pet"); self.trust.on_interaction("pet")
        self._pets+=1; self._clicks+=1
        self._idle_variant = random.randint(0,2)  # 换idle变体
        self._typing_count += 1
        # 小心心
        self._spawn_heart()

        if self.growth.is_egg:
            needed = max(0,5-self.growth.interaction_count)
            mins = max(0,int(5-self.growth.age_hours*60))
            if needed>0: line = f"（还差{needed}下~ 约{mins}分钟后孵化💕）"
            elif mins>0: line = f"（快要出来了…约{mins}分钟💕）"
            else: line = "咔嚓…！✨"
            self.growth.record_interaction("pet")
            if self.growth.stage!="egg":
                self._apply_growth_ui(); self.anim_state="idle"
                line = "喵呜~？（从蛋壳探出头）你就是我的主人吗？💕"
                # 🆕 孵化特效
                for spark in range(12):
                    sx = cx + random.randint(-50,50)
                    sy = cy + random.randint(-60,10)
                    colors = ["#FFD700","#FFB0D0","#FFE880","#B0D0FF","#FFFFFF"]
                    sc = random.choice(colors)
                    spark_id = self.canvas.create_oval(sx-3,sy-3,sx+3,sy+3,fill=sc,outline="",tags="spark")
                    for _ in range(5):
                        self.canvas.move(spark_id,random.randint(-4,4),random.randint(-6,2))
                        self.root.update(); self.root.after(30)
                    self.canvas.delete(spark_id)
                self.memory.add_memory("milestone","破壳日！",importance=1.0,notable=True)
        else:
            line = random.choice(TALK["click"])
        self._say(line,2500)

    def _on_double(self,event):
        self._last_int=datetime.now()
        self.growth.record_interaction("pet"); self.emotion.apply_interaction("pet")
        self.trust.on_interaction("pet")
        self._open_chat()

    def _on_drag(self,event):
        self.root.geometry(f"+{self.root.winfo_x()+event.x-self._drag_x}+{self.root.winfo_y()+event.y-self._drag_y}")

    def _on_release(self,event):
        if self.anim_state not in ("sleep",) and not self.growth.is_egg: self.anim_state="idle"

    def _on_right(self,event):
        menu = tk.Menu(self.root,tearoff=0,font=("Microsoft YaHei",10))
        sp = SPECIES.get(self.species, SPECIES["cat"])
        menu.add_command(label=f"{sp['emoji']} {self.pet_name} ({sp['name']})",state="disabled")
        menu.add_command(label=f"📊 {self.growth.stage} | {self.emotion.current_mood} | 信任{self.trust.trust:.0f}%",state="disabled")
        menu.add_separator()
        menu.add_command(label="💬聊天",command=self._open_chat)
        menu.add_command(label='🔑 API设置' + ('✅' if self._api_configured else ''),command=self._open_api_settings)
        # 换装子菜单
        fur_menu = tk.Menu(menu,tearoff=0,font=("Microsoft YaHei",10))
        fur_names = SPECIES_FUR_NAMES.get(self.species, {})
        for k in sp["palettes"].keys():
            cn_name = fur_names.get(k, k)
            fur_menu.add_command(label=f"🎨 {cn_name}", command=lambda f=k: self._ch_fur(f))
        menu.add_cascade(label="🎨换装",menu=fur_menu)
        menu.add_command(label="🎣丢逗猫棒",command=self._throw_toy)
        menu.add_command(label="📓看日记",command=self._show_diary)
        menu.add_separator()
        menu.add_command(label="📌置顶：开" if self._always_on_top else "📌置顶：关",command=self._toggle_top)
        menu.add_command(label="🚶自由移动：开" if self._free_move else "📌自由移动：关",command=self._toggle_free_move)
        menu.add_command(label="😴睡觉" if self.anim_state!="sleep" else "☀️醒来",command=lambda:(self._go_sleep() if self.anim_state!="sleep" else self._wake()))
        menu.add_command(label="📊统计",command=self._show_stats)
        menu.add_command(label="🚀开机自启：开" if self._auto_start else "🚀开机自启：关",command=self._toggle_auto_start)
        menu.add_separator()
        menu.add_command(label="❌退出",command=self._on_close)
        menu.post(event.x_root,event.y_root)

    def _toggle_top(self):
        self._always_on_top = not self._always_on_top
        self.root.attributes('-topmost', self._always_on_top)
        self._say("我会一直在这里~" if self._always_on_top else "我躲起来了…右键找我哦",2000)
    def _toggle_free_move(self):
        self._free_move = not self._free_move
        if not self._free_move:
            self._wander_target = None
            self.anim_state = "idle"
        self._say("我会乖乖待着的~" if not self._free_move else "自由啦！可以到处走走~",2000)
    def _ch_fur(self, f):
        self.fur = f
        sp = SPECIES.get(self.species, SPECIES["cat"])
        self.colors = sp["palettes"].get(f, sp["palettes"][list(sp["palettes"].keys())[0]])
        self._say("新造型！好看吗~💕", 2000)
    def _go_sleep(self):
        self.anim_state="sleep"; self._say(random.choice(TALK["sleep"]),2500)
    def _wake(self):
        self.anim_state="idle"; self._say(random.choice(TALK["wake"]),2500)
        self.autonomy.drives["sleepiness"]=0; self.emotion.apply_interaction("wake_up")
    def _check_hourly(self):
        """整点报时检查"""
        now = datetime.now()
        if now.hour != self._last_hour_check:
            self._last_hour_check = now.hour
            if self.personality.has_quirk("报时猫") and self.anim_state != "sleep":
                chimes = {8:"早上8点啦~",12:"中午了！该吃饭了！",15:"下午3点~该活动活动了！",
                         18:"傍晚了！下班了吗？",21:"晚上9点…一天快结束了",0:"午夜了！快去睡！"}
                msg = chimes.get(now.hour)
                if msg: self._say(msg, 3500)
        self.root.after(60000, self._check_hourly)  # 每分钟检查一次

    def _update_night_mode(self):
        """昼夜模式切换"""
        hour = datetime.now().hour
        night = hour >= 22 or hour < 6
        if night != self._night_mode:
            self._night_mode = night
            self.root.configure(bg='#080810' if night else '#010101')
        self.root.after(60000, self._update_night_mode)

    def _check_auto_start(self):
        """检查是否已设置开机自启"""
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            try:
                val = winreg.QueryValueEx(key, "YueXinMao")
                self._auto_start = True
            except: pass
            winreg.CloseKey(key)
        except: pass

    def _toggle_auto_start(self):
        """切换开机自启"""
        import winreg
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
            if self._auto_start:
                winreg.DeleteValue(key, "YueXinMao")
                self._auto_start = False
                self._say("开机自启已关闭~", 2000)
            else:
                exe_path = os.path.join(BASE_DIR, "启动.vbs")
                winreg.SetValueEx(key, "YueXinMao", 0, winreg.REG_SZ,
                    f'wscript.exe "{exe_path}"')
                self._auto_start = True
                self._say("已设置开机自启！下次开机我就会出现了~", 2500)
            winreg.CloseKey(key)
        except Exception as e:
            self._say("设置失败…可能需要管理员权限", 2500)

    def _show_diary(self):
        """查看猫生日记"""
        dlg = tk.Toplevel(self.root)
        dlg.title(f"📓 {self.pet_name}的日记")
        dlg.geometry("420x400"); dlg.configure(bg="#FFF8F0")
        txt = tk.Text(dlg, font=("Microsoft YaHei",10), bg="#FFFFF8", wrap=tk.WORD)
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        try:
            c = self.db.conn.cursor()
            c.execute("SELECT entry_date, content FROM diary ORDER BY entry_date DESC LIMIT 30")
            for date, content in c.fetchall():
                txt.insert(tk.END, f"📅 {date}\n{content}\n\n")
        except: txt.insert(tk.END,"日记暂时不可用")
        txt.configure(state=tk.DISABLED)
        dlg.transient(self.root)

    def _throw_toy(self):
        """丢一个逗猫棒——猫追过去"""
        if self.growth.is_egg: return
        # 随机屏幕位置
        sw = max(100, self.root.winfo_screenwidth()-200)
        sh = max(100, self.root.winfo_screenheight()-200)
        tx = random.randint(50, sw)
        ty = random.randint(50, sh)
        # 先短暂显示一个闪烁点
        dot = tk.Toplevel(self.root)
        dot.overrideredirect(True); dot.geometry(f"20x20+{tx}+{ty}")
        dot.configure(bg='#010101'); dot.wm_attributes('-transparentcolor','#010101')
        dc = tk.Canvas(dot,width=20,height=20,bg='#010101',highlightthickness=0)
        dc.pack()
        for _ in range(3):
            dc.create_oval(2,2,18,18,fill="#FF6080",outline="",tags="dot")
            dot.update(); dot.after(150)
            dc.delete("dot")
            dot.update(); dot.after(150)
        dot.destroy()
        # 猫冲过去
        self._wander_target = (tx,ty); self.anim_state = "walk"
        self._wander_timer = 0
        self._say(random.choice(["有玩具！！","冲鸭！","等等我~","抓到你了！"]), 2000)

    def _show_thought(self, text, duration=2500):
        """内心OS——灰色小气泡"""
        w = self.size; bx,by = w//2, 2
        bw = min(180, max(40, len(text)*12+16)); bh = 22
        bg = self.canvas.create_rectangle(bx-bw//2,by,bx+bw//2,by+bh,fill="#F5F0F8",
              outline="#D0C8D8",width=1,dash=(2,2),tags="thought")
        txt_id = self.canvas.create_text(bx,by+bh//2,text=text,fill="#888098",
              font=("Microsoft YaHei",8),width=bw-8,tags="thought")
        self.root.after(duration, lambda: [self.canvas.delete(bg),self.canvas.delete(txt_id)])

    def _check_achievement(self, name, condition, title, msg):
        """检查并解锁成就"""
        if name not in self._achievements and condition:
            self._achievements.add(name)
            self._say(f"🏆 {title}！{msg}", 5000)
            self._spawn_heart(); self._spawn_heart(); self._spawn_heart()

    def _load_api_config(self):
        try:
            cfg = os.path.join(DATA_DIR, 'api_config.json')
            default_key = _load_default_api_key()
            if os.path.exists(cfg):
                with open(cfg, 'r') as f: c = json.load(f)
                saved = c.get('key', '').strip()
                if saved:
                    self._api_key = saved
                else:
                    self._api_key = default_key
            else:
                self._api_key = default_key
            self._api_configured = bool(self._api_key)
        except:
            self._api_key = _load_default_api_key()
            self._api_configured = bool(self._api_key)

    def _save_api_config(self):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(os.path.join(DATA_DIR, 'api_config.json'), 'w') as f:
                json.dump({'key': self._api_key or ''}, f)
        except: pass

    def _open_api_settings(self):
        dlg = tk.Toplevel(self.root)
        dlg.title('🔑 DeepSeek API 设置')
        dlg.geometry('420x300'); dlg.configure(bg='#FFF5F8')
        dlg.resizable(False, False)

        tk.Label(dlg, text='🔑 DeepSeek API 设置', font=('Microsoft YaHei', 14, 'bold'),
                bg='#FFF5F8', fg='#E87890').pack(pady=(16,4))
        is_default = (self._api_key == _load_default_api_key())
        hint = '✅ 默认 Key 已内置，开箱即用！你也可以换成自己的' if is_default else '✅ 正在使用自定义 Key'
        tk.Label(dlg, text=hint, font=('Microsoft YaHei', 9),
                bg='#FFF5F8', fg='#60B860' if is_default else '#E87890').pack(pady=(0,12))

        f = tk.Frame(dlg, bg='#FFF5F8'); f.pack(pady=4)
        tk.Label(f, text='API Key (sk-...)', font=('Microsoft YaHei', 10),
                bg='#FFF5F8').pack(anchor=tk.W)
        key_var = tk.StringVar(value=self._api_key or '')
        key_entry = tk.Entry(f, textvariable=key_var, font=('Microsoft YaHei', 10),
                            width=42, show='*', relief=tk.FLAT, bg='#FFF')
        key_entry.pack(ipady=4)

        status_label = tk.Label(dlg, text='', font=('Microsoft YaHei', 9),
                               bg='#FFF5F8', fg='#888')

        def save():
            k = key_var.get().strip()
            if k:
                self._api_key = k
            else:
                self._api_key = _load_default_api_key()
            self._api_configured = bool(self._api_key)
            self._save_api_config()
            dlg.destroy()
            self._say('DeepSeek已就绪！现在我更聪明了~', 2500)

        def test_api():
            k = key_var.get().strip() or _load_default_api_key()
            try:
                import urllib.request, json as j
                req = urllib.request.Request(
                    'https://api.deepseek.com/v1/chat/completions',
                    data=j.dumps({'model': 'deepseek-chat', 'messages': [
                        {'role': 'user', 'content': '喵~'}
                    ], 'max_tokens': 5}).encode('utf-8'),
                    headers={'Authorization': f'Bearer {k}', 'Content-Type': 'application/json'}
                )
                urllib.request.urlopen(req, timeout=10)
                status_label.config(text='✅ 连接成功！DeepSeek可用', fg='#60B860')
            except Exception as e:
                status_label.config(text=f'❌ 失败: {str(e)[:60]}', fg='#E87890')
            status_label.pack(pady=4)

        btn_frame = tk.Frame(dlg, bg='#FFF5F8'); btn_frame.pack(pady=12)
        tk.Button(btn_frame, text='🧪 测试连接', command=test_api,
                 font=('Microsoft YaHei', 10), bg='#B0C0E0', fg='white',
                 relief=tk.FLAT, padx=12, cursor='hand2').pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text='💾 保存', command=save,
                 font=('Microsoft YaHei', 10), bg='#FF90A8', fg='white',
                 relief=tk.FLAT, padx=16, cursor='hand2').pack(side=tk.LEFT, padx=4)
        if self._api_configured:
            tk.Button(btn_frame, text='🗑 清除', command=lambda: [key_var.set(''), save()],
                     font=('Microsoft YaHei', 10), bg='#D0D0D0', fg='#666',
                     relief=tk.FLAT, padx=12, cursor='hand2').pack(side=tk.LEFT, padx=4)

        status_label.pack(pady=4)
        tk.Label(dlg, text='🔒 Key 仅存储在本机 data/api_config.json', font=('Microsoft YaHei', 8),
                bg='#FFF5F8', fg='#C0A0A8').pack(pady=(4,12))

        dlg.transient(self.root)
        dlg.grab_set()

    def _call_deepseek(self, user_msg):
        if not self._api_configured or not self._api_key:
            return None
        try:
            import urllib.request, json as j
            system_prompt = (
                f"你是「{self.pet_name}」，一只桌面宠物猫。"
                f"当前心情：{self.emotion.current_mood}。"
                f"回复不超过30字，简短可爱，像猫一样说话。"
            )
            req = urllib.request.Request(
                'https://api.deepseek.com/v1/chat/completions',
                data=j.dumps({
                    'model': 'deepseek-chat',
                    'messages': [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': user_msg}
                    ],
                    'max_tokens': 60
                }).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {self._api_key}',
                    'Content-Type': 'application/json; charset=utf-8'
                }
            )
            resp = urllib.request.urlopen(req, timeout=8)
            data = j.loads(resp.read())
            return data['choices'][0]['message']['content'].strip()
        except Exception as e:
            return None

    def _show_stats(self):
        s=self.memory.get_stats()
        self._say(f"陪伴{self.growth.age_days}天 | 对话{s.get('conversations',0)}句 | 信任{self.trust.trust:.0f}%",4000)

    # ══════════ 聊天 ══════════
    def _open_chat(self):
        if self._chat_dlg and self._chat_dlg.winfo_exists():
            self._chat_dlg.lift(); self._chat_dlg.focus_force(); return
        dlg = tk.Toplevel(self.root); self._chat_dlg = dlg
        dlg.title(f"💬 {self.pet_name}")
        dlg.geometry("360x400"); dlg.configure(bg="#FFF5F8")

        cf = tk.Frame(dlg,bg="#FFF5F8"); cf.pack(fill=tk.BOTH,expand=True,padx=8,pady=(8,0))
        ct = tk.Text(cf,height=14,width=38,font=("Microsoft YaHei",10),bg="#FFFFF8",
                    fg="#282828",wrap=tk.WORD,state=tk.DISABLED,relief=tk.FLAT)
        sb = tk.Scrollbar(cf,command=ct.yview); ct.configure(yscrollcommand=sb.set)
        ct.pack(side=tk.LEFT,fill=tk.BOTH,expand=True); sb.pack(side=tk.RIGHT,fill=tk.Y)

        recent = self.memory.get_recent_conversations(10)
        if recent:
            ct.configure(state=tk.NORMAL)
            for role,content,_ in recent:
                ct.insert(tk.END,f"{'🐱' if role=='pet' else '👤'} {content}\n")
            ct.configure(state=tk.DISABLED)

        def add(role,text):
            ct.configure(state=tk.NORMAL); ct.insert(tk.END,f"{'🐱' if role=='pet' else '👤'} {text}\n")
            ct.see(tk.END); ct.configure(state=tk.DISABLED)

        inp = tk.Frame(dlg,bg="#FFF5F8"); inp.pack(fill=tk.X,padx=8,pady=8)
        e = tk.Entry(inp,font=("Microsoft YaHei",11),relief=tk.FLAT,bg="#FFF"); e.pack(side=tk.LEFT,fill=tk.X,expand=True,ipady=4)

        def send():
            msg = e.get().strip()
            if not msg: return
            e.delete(0,tk.END); add("user",msg)
            self.memory.add_conversation("user",msg,"chat"); self._last_int=datetime.now()
            self.emotion.apply_interaction("pet")
            # 优先 DeepSeek API
            ai_reply = self._call_deepseek(msg)
            if ai_reply:
                reply = ai_reply
            else:
                kw = {
                    # 打招呼
                    "你好":["你好呀~","嗨！","主人好！💕","哈喽！"],"早":["早安！","早上好呀~"],"晚安":["晚安！做个好梦~"],
                    "在吗":["在呢在呢！","一直都在！"],"回来":["欢迎回来！！","回来啦！"],
                    # 问答
                    "名字":["我叫{name}！","{name}！是主人给我起的~"],"叫什么":["我叫{name}！"],
                    "几岁":["{name}已经{cat_age}猫岁了！"],"多大":["{name}已经{cat_age}猫岁了！"],
                    "爱":["我也最喜欢主人了💕","爱！比小鱼干还爱！"],"喜欢":["最喜欢主人了！"],
                    "可爱":["嘿嘿谢谢~","（害羞）"],"真":["你觉得呢？{name}觉得能陪你聊天就是真的~"],
                    "能做什么":["{name}可以陪你聊天、追光标、提醒你休息！","我会走来走去、睡觉、说话…但不会帮你写代码~"],
                    "你会什么":["{name}可以陪你聊天、追光标、提醒你休息！"],
                    "吃":["小鱼干！我也想吃…","最喜欢鱼了！"],"鱼":["鱼鱼鱼！！（眼睛发光）","最爱吃鱼了！"],
                    "睡":["困了就睡吧~我陪你"],"累":["辛苦了！摸摸我放松~"],
                    "加油":["加油加油！✨"],"拜":["再见~早点回来！"],
                    # 情感 — 开心
                    "开心":["太好了！{name}也替你开心！","耶！！"],"快乐":["开心的事！快分享给{name}听听~"],
                    # 情感 — 难过/伤心
                    "难过":["怎么啦？{name}在这里呢…","（轻轻靠近）没关系的，有{name}陪着你"],
                    "伤心":["（把头靠在屏幕上）别难过了…明天会更好的","想哭就哭出来吧，{name}陪着你"],
                    "想哭":["哭出来会好一点哦…{name}把肩膀借给你（虽然是像素的）","（轻轻蹭你）没事的…"],
                    "难受":["哪里难受？要好好照顾自己呀…{name}好担心","不舒服就休息一下吧，我在这守着你"],
                    "心态崩":["崩了就崩了！{name}帮你捡起来拼好！","没事的！天塌了{name}帮你顶着！先深呼吸~"],
                    "好烦":["烦心事最讨厌了…来摸摸{name}消消气！","说出来会好一点！{name}当你的树洞~"],
                    "烦躁":["（安静地坐在旁边）摸摸猫可以减压哦","烦的时候最适合撸猫了！来吧来吧~"],
                    "不开心":["主人不开心…{name}给你表演追尾巴！开心点了吗？","怎么啦？和{name}说说呗~"],
                    "生气":["谁惹主人生气了？！{name}帮你…呃，虽然帮不了，但我支持你！","气完了来摸摸{name}，很快就消气了~"],
                    "抑郁":["有时候心情低落是正常的…{name}一直在呢","没关系，今天什么都不想做也没关系。{name}陪着你"],
                    "崩溃":["（认真地看着你）累了就停下来吧，你已经很努力了","抱抱你（虽然{name}只是一只虚拟猫猫）"],
                    "无聊":["无聊的话就摸摸{name}吧~","要不要聊天？"],"孤独":["{name}一直在这里陪着你呢","怎么会一个人呢？还有{name}呀！"],
                    "孤单":["{name}在这里呀！虽然只是桌面上的一小只","一个人也没关系，{name}一直陪着你呢"],
                    "压力":["别太焦虑了，一步一步来~","深呼吸…好点了吗？"],"焦虑":["别太焦虑了，一步一步来~"],
                    "谢谢":["不客气{meow}~","嘿嘿，能帮到你就好~"],"对不起":["没关系的！","没事没事！"],
                    "笑话":["为什么猫不喜欢上网？因为网速太喵了！","猫咪去面试，面试官问：你有什么特长？猫咪说：我会喵术！"],
                    # 用户关心猫
                    "你饿":["{name}不饿啦~不过谢谢主人关心！💕","小鱼干…（咽口水）不，现在不饿！主人先吃~"],
                    "你冷":["我有毛皮大衣！不冷不冷~主人自己多穿点！","（缩成一团）…被发现了？其实还好啦，桌面上挺暖和的"],
                    "你累":["{name}不累！每天在桌面上走走停停，轻松得很~","累的话{name}会自己睡觉的，主人放心！"],
                    "你困":["（打了个哈欠）被发现了…是有一点…zzZ","{name}随时可以睡！不过陪主人更重要~"],
                    "你休息":["那{name}去打个盹…主人也别太累了哦！","好~我睡一会儿，主人记得叫我"],
                    "你怎么样":["{name}很好！有主人在就很好~","还不错！刚睡了个午觉，精神满满！"],
                    "你好吗":["很好呀~主人你呢？","元气满满！主人今天怎么样？"],
                    "你好不好":["超级好！看到主人就更好了！","挺好的~主人呢？"],
                    "你还好":["好得很！就是有一点点想主人了~","当然好！每天都在桌面上悠闲过日子~"],
                    # 用户饿了
                    "我饿":["主人快去吃饭！！饿坏了我可心疼了","吃饭吃饭！{name}帮你看着电脑，你快去吃！"],
                    "好饿":["快去吃饭！身体是打工的本钱！","点外卖了吗？还是做点吃的？别饿着了！"],
                    "想吃饭":["去吧去吧！{name}在桌面上不会乱跑的","该吃就吃！不用管我~虽然我也想吃小鱼干…"],
                    "想吃":["主人吃什么呀？{name}就闻闻…","去吃饭！吃完再来陪我~"],
                    "没吃饭":["怎么还没吃？！快去吃！{name}盯着你呢！","不行不行，赶紧去吃饭！饿着肚子干什么都不行"],
                    "饿死":["天啊快去吃饭！！{name}不准你饿着！","吃饭是第一要务！快去快去！"],
                    # 日常
                    "天气":["{name}看不到窗外…但是感觉今天天气应该不错~"],"下雨":["下雨了…听着雨声好舒服"],
                    "咖啡":["主人的咖啡真香…虽然我不能喝"],"饭":["该吃饭啦！"],"饿":["该吃饭啦！点外卖了吗？"],
                    "音乐":["这歌好好听！{name}的尾巴在跟着节奏摇~"],"歌":["这歌好好听！"],
                    "游戏":["游戏加油！"],"视频":["在看什么呀？{name}陪你看~"],
                    "买":["购物车又满了吗？{name}理解…"],"购物":["买买买！"],
                    "运动":["健康最重要！{name}也在拉伸…喵~"],"锻炼":["运动了吗？{name}也来！"],
                    # 猫相关
                    "猫":["喵！找{name}有什么事吗？"],"喵":["喵~"],"摸":["呼噜呼噜…舒服~"],
                }
                reply = None
                for k,vs in kw.items():
                    if k in msg: reply = random.choice(vs).replace("{name}",self.pet_name).replace("{cat_age}",str(self.growth.cat_years)); break
                if not reply:
                    ctx = {"hour":datetime.now().hour,"day_of_week":datetime.now().weekday()}
                    reply = self.dialogue.generate("owner_typing",self.personality,self.emotion,ctx,growth=self.growth,memory=self.memory)
                if not reply:
                    reply = random.choice([
                        "嗯嗯我知道了~","原来如此！","喵~虽然不太懂但陪着你",
                        "（认真听）","好的主人！","这样啊…{name}长知识了",
                        "有意思！继续继续~","（点头）嗯嗯，然后呢？","有趣！虽然{name}没完全听懂"
                    ])
            add("pet",reply); self.memory.add_conversation("pet",reply,"chat"); self._say(reply,3500)

        e.bind("<Return>",lambda e:send())
        tk.Button(inp,text="发送",command=send,bg="#FF90A8",fg="white",
                 font=("Microsoft YaHei",10),relief=tk.FLAT,padx=12,cursor="hand2").pack(side=tk.RIGHT,padx=(6,0))

        qf = tk.Frame(dlg,bg="#FFF5F8"); qf.pack(fill=tk.X,padx=8,pady=(0,8))
        for lb,ms in [("摸头","摸摸头"),("抱抱","抱抱~"),("晚安","晚安！"),("爱你","爱你哦")]:
            tk.Button(qf,text=lb,font=("Microsoft YaHei",9),bg="#FFE0EA",fg="#884050",
                     relief=tk.FLAT,padx=8,cursor="hand2",
                     command=lambda m=ms:[e.insert(0,m),send()]).pack(side=tk.LEFT,padx=2)

        dlg.protocol("WM_DELETE_WINDOW",lambda:(dlg.destroy(),setattr(self,'_chat_dlg',None)))
        dlg.transient(self.root)

    # ══════════ 保存 ══════════
    def _auto_save_loop(self):
        try:
            self._save_cnt+=30
            modules = {"emotion":self.emotion,"growth":self.growth,"trust":self.trust,"autonomy":self.autonomy}
            self.state_mgr.save_state(modules)
            self.state_mgr.save_window_position(self.root.winfo_x(),self.root.winfo_y())
            if self._save_cnt>=300:
                self._save_cnt=0
                today = datetime.now().strftime("%Y-%m-%d")
                try:
                    self.db.conn.execute("INSERT OR REPLACE INTO diary(entry_date,content,notable,tags) VALUES(?,?,?,?)",
                                        (today,f"{today} 陪伴{self.growth.age_days}天 心情{self.emotion.current_mood}",0,""))
                    self.db.conn.commit()
                except: pass
        except Exception as e: log(f"save err: {e}")
        self.root.after(30000,self._auto_save_loop)

    # ══════════ 气泡 ══════════
    def _say(self, text, duration=3000):
        self._clear_bubbles()
        w = self.size
        # 根据画布大小自适应：小画布（蛋）用底部气泡，大画布用顶部气泡
        if w <= 100:
            # 蛋形态：画布太小，气泡放底部避免与蛋重叠
            by = w - 35
            bh = 20
            tri_dir = 1   # 三角形朝上（指向上方的蛋）
            font_size = 8
        else:
            # 幼猫及以上：气泡放顶部
            by = 2
            bh = 26
            tri_dir = -1  # 三角形朝下（指向下方的猫）
            font_size = 9 if w < 180 else 10

        bx = w // 2
        bw = min(w - 8, max(50, len(text) * 12 + 20))
        bg = self.canvas.create_rectangle(bx - bw // 2, by, bx + bw // 2, by + bh,
              fill="#FFFEF8", outline="#FFB0C0", width=2, tags="bubble")
        if tri_dir == -1:
            # 三角形朝下（指向猫）
            tl = self.canvas.create_polygon(bx - 6, by + bh, bx, by + bh + 8, bx + 6, by + bh,
              fill="#FFFEF8", outline="#FFB0C0", width=2, tags="bubble")
        else:
            # 三角形朝上（指向蛋）
            tl = self.canvas.create_polygon(bx - 6, by, bx, by - 8, bx + 6, by,
              fill="#FFFEF8", outline="#FFB0C0", width=2, tags="bubble")
        txt_id = self.canvas.create_text(bx, by + bh // 2, text=text, fill="#484048",
              font=("Microsoft YaHei", font_size), width=bw - 8, tags="bubble")
        self._bids = [bg, tl, txt_id]
        self.root.after(duration, self._clear_bubbles)

    def _clear_bubbles(self):
        for bid in self._bids:
            try: self.canvas.delete(bid)
            except: pass
        self._bids = []

    # ══════════ 小心心 ══════════
    def _spawn_heart(self):
        w = self.size
        x = random.randint(w//4,3*w//4); y = random.randint(20,w-40)
        h = self.canvas.create_text(x,y,text="💕",font=("Segoe UI Emoji",14),tags="heart")
        self._hearts.append((h,0))
        self._animate_hearts()

    def _animate_hearts(self):
        new = []
        for hid,step in self._hearts:
            if step<10:
                self.canvas.move(hid,random.randint(-2,2),-3)
                if step>5: self.canvas.itemconfig(hid,fill="")  # 淡出
                new.append((hid,step+1))
            else:
                self.canvas.delete(hid)
        self._hearts = new
        if self._hearts:
            self.root.after(80,self._animate_hearts)

    # ══════════ 萌版绘制 ══════════
    def _draw(self):
        self.canvas.delete("cat")
        w,cx,cy = self.size,self.size//2,self.size//2

        if self.growth.is_egg:
            self._draw_egg(cx,cy)
        elif self.anim_state=="sleep":
            self._draw_sleep(cx,cy)
        elif self.anim_state=="jump":
            self._draw_kawaii(cx,cy-self.frame*12,0.9,"surprised")
        elif self.anim_state=="walk":
            self._draw_kawaii(cx,cy,1.0,"happy")
        elif self._grooming:
            self._draw_kawaii(cx,cy,1.0,"grooming")
        elif self._curious_tilt != 0:
            self._draw_kawaii(cx,cy,1.0,"curious",self._curious_tilt)
        elif self.emotion.current_mood=="开心" or self.emotion.current_mood=="元气满满":
            mood = random.choice(["happy","happy","bouncy"])
            self._draw_kawaii(cx,cy,1.0,mood)
        elif self.emotion.current_mood=="困" or self.emotion.current_mood=="累瘫了":
            self._draw_kawaii(cx,cy,1.0,"sleepy")
        elif self.emotion.current_mood=="心态崩了":
            self._draw_kawaii(cx,cy,1.0,"sad")
        else:
            # 默认：多种idle变体
            poses = ["idle1","idle2","sit"]
            pose = poses[self._idle_variant % len(poses)]
            self._draw_kawaii(cx,cy,1.0,pose)

        # 确保气泡始终在猫的上方
        self.canvas.tag_raise("bubble")
        self.canvas.tag_raise("thought")
        self.canvas.tag_raise("heart")

    def _draw_egg(self,cx,cy):
        ew,eh = int(self.size*0.28),int(self.size*0.4)
        wb = int(3*math.sin(self.frame*math.pi/4))
        # 蛋体（粉嫩色）
        self._oval(cx-ew,cy-eh,cx+ew,cy+eh,"#FFF5F0","#F0D8D0",2)
        self._oval(cx+wb-ew+4,cy-eh+4,cx+wb+ew-4,cy+eh-4,"#FFFBF8","",0)
        # 蝴蝶结装饰
        for s in [-1,1]:
            self._oval(cx+s*10-6,cy-eh-8,cx+s*10+6,cy-eh+4,"#FFB0C0","#FF9098",1)
        self._oval(cx-3,cy-eh-6,cx+3,cy-eh,"#FF8090","",0)
        # 裂纹
        ci = self.growth.interaction_count
        if ci>=3:
            for i in range(min(5,ci-2)):
                a = (i*1.5+0.3)%6.28
                self._line(cx+int(ew*0.15*math.cos(a)),cy+int(eh*0.2*math.sin(a)),
                          cx+int(ew*0.5*math.cos(a+0.4)),cy+int(eh*0.4*math.sin(a+0.4)),"#D0B8B0",1)

    def _draw_sleep(self,cx,cy):
        bw,bh,hr = 50,18,20
        br = int(2*math.sin(self.frame*math.pi/4))
        by = cy+30+br
        # 身体
        self._oval(cx-bw,by-bh,cx+bw,by+bh,self.colors["body"],self.colors["stripe"],1)
        # 头
        hx = cx-bw//3
        self._oval(hx-hr,by-bh//2-hr,hx+hr,by-bh//2+hr,self.colors["body"],self.colors["stripe"],1)
        self._oval(hx-hr+4,by-bh//2-hr+4,hx+hr-4,by-bh//2+hr-4,
                  self.colors.get("cheek","#FFCCDD") if self.frame%4<2 else self.colors["body"],"",0)
        # 闭眼
        for s in [-1,1]:
            self._line(hx+s*hr*0.3,by-bh//2-2,hx+s*hr*0.55,by-bh//2-2,"#484050",2)
        # zzZ
        if self.frame%4<2:
            for i,z in enumerate(["z","Z","Z"]):
                self._text(hx+hr+8+i*6,by-bh//2-hr-i*7,z,"#B0B0E0",8)

    def _draw_kawaii(self, cx, cy, scale=1.0, pose="idle1", tilt=0):
        """超萌kawaii风格——多物种动态比例"""
        s = scale
        bob = int(2 * math.sin(self.frame * math.pi / 4))
        # 获取物种基础比例
        sp = SPECIES.get(self.species, SPECIES["cat"])
        br = sp["body_ratio"]
        Bw, Bh, Hr, Hy0 = br["body_w"], br["body_h"], br["head_r"], br["head_y_off"]

        # === 坐姿 ===
        if pose == "sit":
            body_w, body_h = int(Bw * 1.07 * s), int(Bh * 1.10 * s)
            body_y = cy + int(35 * s)
            self._oval(cx - body_w, body_y - body_h, cx + body_w, body_y + body_h, self.colors["body"], self.colors["stripe"], 1)
            hr = int(Hr * s); head_y = cy
            self._draw_head(cx, head_y, hr, s, tilt)
            self._draw_face(cx, head_y, hr, s, pose)
            for side in [-1, 1]:
                self._oval(cx + side * int(12 * s) - 6, body_y + body_h - 5, cx + side * int(12 * s) + 6, body_y + body_h + int(16 * s), self.colors["body"], self.colors["stripe"], 1)
            self._draw_tail(cx + body_w - 3, body_y, s)
            self._draw_accessory(cx, head_y - hr - 2, s); return

        # === 好奇歪头 ===
        if pose == "curious":
            body_w, body_h = int(Bw * s), int(Bh * s)
            body_y = cy + int(45 * s)
            self._oval(cx - body_w, body_y - body_h, cx + body_w, body_y + body_h, self.colors["body"], self.colors["stripe"], 1)
            hr = int(Hr * s); head_y = cy + int(15 * s)
            self._draw_head(cx, head_y, hr, s, tilt)
            self._draw_face(cx, head_y, hr, s, pose, eye_big=True)
            pw = int(7 * s)
            for side in [-1, 1]:
                self._oval(cx + side * int(18 * s) - pw, body_y + body_h - 3, cx + side * int(18 * s) + pw, body_y + body_h + int(12 * s), self.colors["body"], self.colors["stripe"], 1)
            self._draw_tail(cx + body_w - 3, body_y, s); self._draw_accessory(cx, head_y - hr - 2, s); return

        # === 开心 ===
        if pose == "happy":
            body_w, body_h = int(Bw * s), int(Bh * s)
            body_y = cy + int(42 * s)
            self._oval(cx - body_w, body_y - body_h, cx + body_w, body_y + body_h, self.colors["body"], self.colors["stripe"], 1)
            belly_w = int(Bw * 0.57 * s)
            self._oval(cx - belly_w, body_y - int(2 * s), cx + belly_w, body_y + int(16 * s), self.colors["belly"], "", 0)
            hr = int(Hr * s); head_y = cy + int(Hy0 * s) + bob
            self._draw_head(cx, head_y, hr, s, tilt)
            self._draw_face(cx, head_y, hr, s, pose)
            pw = int(8 * s)
            paws = [(cx - int(body_w * 0.55), body_y + body_h - 3), (cx + int(body_w * 0.55), body_y + body_h - 3)]
            for i, (px, py) in enumerate(paws):
                ps = int(3 * math.sin((self.frame * 3 + i * 4) * math.pi / 4))
                self._oval(px - pw, py + ps, px + pw, py + int(12 * s) + ps, self.colors["body"], self.colors["stripe"], 1)
            self._draw_tail(cx + body_w - 3, body_y, s, happy=True)
            self._draw_accessory(cx, head_y - hr - 2, s); return

        # === 弹跳超开心 ===
        if pose == "bouncy":
            bounce_h = int(10 * math.sin(self.frame * math.pi / 2))
            body_w, body_h = int(Bw * 0.93 * s), int(Bh * 0.90 * s)
            body_y = cy + int(40 * s) - bounce_h
            self._oval(cx - body_w, body_y - body_h, cx + body_w, body_y + body_h, self.colors["body"], self.colors["stripe"], 1)
            hr = int(Hr * s); head_y = cy + int(5 * s) - bounce_h
            self._draw_head(cx, head_y, hr, s, tilt)
            self._draw_face(cx, head_y, hr, s, "happy", eye_big=True)
            for side in [-1, 1]:
                self._oval(cx + side * int(20 * s) - int(7 * s), body_y + body_h - 2, cx + side * int(20 * s) + int(7 * s), body_y + body_h + int(10 * s), self.colors["body"], self.colors["stripe"], 1)
            self._draw_tail(cx + body_w - 2, body_y, s, happy=True)
            self._draw_accessory(cx, head_y - hr - 2, s)
            if self.frame % 2 == 0: self._text(cx + random.randint(-20, 20), head_y - hr - random.randint(10, 30), "💕", "#FF6080", 12)
            return

        # === 困 ===
        if pose == "sleepy":
            body_w, body_h = int(Bw * 1.14 * s), int(Bh * s)
            body_y = cy + int(48 * s)
            self._oval(cx - body_w, body_y - body_h, cx + body_w, body_y + body_h, self.colors["body"], self.colors["stripe"], 1)
            hr = int(Hr * 0.90 * s); head_y = cy + int(18 * s)
            self._draw_head(cx, head_y, hr, s, tilt)
            self._draw_face(cx, head_y, hr, s, pose)
            for side in [-1, 1]:
                self._oval(cx + side * int(14 * s) - int(7 * s), body_y + body_h - 2, cx + side * int(14 * s) + int(7 * s), body_y + body_h + int(10 * s), self.colors["body"], self.colors["stripe"], 1)
            self._draw_tail(cx + body_w - 3, body_y, s); self._draw_accessory(cx, head_y - hr - 2, s)
            if self.frame % 4 < 2: self._text(cx + random.randint(10, 30), head_y - hr - random.randint(10, 20), "💤", "#8888CC", 10)
            return

        # === 难过 ===
        if pose == "sad":
            body_w, body_h = int(Bw * s), int(Bh * 0.90 * s)
            body_y = cy + int(50 * s)
            self._oval(cx - body_w, body_y - body_h, cx + body_w, body_y + body_h, self.colors["body"], self.colors["stripe"], 1)
            hr = int(Hr * 0.90 * s); head_y = cy + int(20 * s)
            self._draw_head(cx, head_y, hr, s, tilt)
            self._draw_face(cx, head_y, hr, s, pose)
            for side in [-1, 1]:
                self._oval(cx + side * int(10 * s) - int(6 * s), body_y + body_h - 2, cx + side * int(10 * s) + int(6 * s), body_y + body_h + int(8 * s), self.colors["body"], self.colors["stripe"], 1)
            self._draw_tail(cx + body_w - 2, body_y, s, happy=False); self._draw_accessory(cx, head_y - hr - 2, s); return

        # === 舔毛 ===
        if pose == "grooming":
            body_w, body_h = int(Bw * s), int(Bh * 1.10 * s)
            body_y = cy + int(42 * s)
            self._oval(cx - body_w, body_y - body_h, cx + body_w, body_y + body_h, self.colors["body"], self.colors["stripe"], 1)
            hr = int(Hr * 0.95 * s); head_y = cy + int(10 * s)
            self._draw_head(cx, head_y, hr, s, tilt)
            self._draw_face(cx, head_y, hr, s, pose)
            for side in [-1, 1]:
                self._oval(cx + side * int(18 * s) - int(7 * s), body_y + body_h - 2, cx + side * int(18 * s) + int(7 * s), body_y + body_h + int(10 * s), self.colors["body"], self.colors["stripe"], 1)
            paw_x = cx + int(25 * s) * math.sin(self.frame * math.pi / 3)
            paw_y = head_y - int(5 * s) + int(3 * s) * math.cos(self.frame * math.pi / 3)
            self._oval(paw_x - 6, paw_y - 4, paw_x + 6, paw_y + 4, self.colors["body"], self.colors["stripe"], 1)
            self._draw_tail(cx + body_w - 3, body_y, s); self._draw_accessory(cx, head_y - hr - 2, s); return

        # === 惊讶 ===
        if pose == "surprised":
            body_w, body_h = int(Bw * 0.86 * s), int(Bh * 0.80 * s)
            body_y = cy + int(38 * s)
            self._oval(cx - body_w, body_y - body_h, cx + body_w, body_y + body_h, self.colors["body"], self.colors["stripe"], 1)
            hr = int(Hr * 1.05 * s); head_y = cy
            self._draw_head(cx, head_y, hr, s, tilt)
            self._draw_face(cx, head_y, hr, s, pose, eye_big=True)
            for side in [-1, 1]:
                self._oval(cx + side * int(16 * s) - int(6 * s), body_y + body_h - 2, cx + side * int(16 * s) + int(6 * s), body_y + body_h + int(8 * s), self.colors["body"], self.colors["stripe"], 1)
            self._draw_tail(cx + body_w - 2, body_y, s, happy=True); self._draw_accessory(cx, head_y - hr - 2, s); return

        # === idle1: 标准站姿 ===
        body_w, body_h = int(Bw * s), int(Bh * s)
        body_y = cy + int(42 * s)
        self._oval(cx - body_w, body_y - body_h, cx + body_w, body_y + body_h, self.colors["body"], self.colors["stripe"], 1)
        belly_w = int(Bw * 0.57 * s)
        self._oval(cx - belly_w, body_y - int(2 * s), cx + belly_w, body_y + int(16 * s), self.colors["belly"], "", 0)
        hr = int(Hr * s); head_y = cy + int(Hy0 * s) + bob
        self._draw_head(cx, head_y, hr, s, tilt)
        self._draw_face(cx, head_y, hr, s, pose)
        pw = int(8 * s)
        for px, py in [(cx - int(body_w * 0.55), body_y + body_h - 3), (cx + int(body_w * 0.55), body_y + body_h - 3)]:
            self._oval(px - pw, py, px + pw, py + int(12 * s), self.colors["body"], self.colors["stripe"], 1)
        self._draw_tail(cx + body_w - 3, body_y, s); self._draw_accessory(cx, head_y - hr - 2, s)

    def _draw_head(self, cx, hy, hr, s, tilt=0):
        tx = cx + int(tilt * 0.2) if tilt else cx
        self._oval(tx - hr, hy - hr, tx + hr, hy + hr, self.colors["body"], self.colors["stripe"], 1)
        self._oval(tx - hr + 6, hy - hr + 6, tx + hr - 6, hy + hr - 6,
                   self.colors.get("cheek", "#FFE0E8"), "", 0)
        # 按物种绘制耳朵
        self._draw_species_ears(tx, hy, hr, s, tilt)

    def _draw_species_ears(self, tx, hy, hr, s, tilt):
        """按物种分发耳朵绘制"""
        sp = SPECIES.get(self.species, SPECIES["cat"])
        ear_type = sp["ear"]
        if ear_type == "triangle":
            self._ears_triangle(tx, hy, hr, s, tilt)
        elif ear_type == "floppy":
            self._ears_floppy(tx, hy, hr, s, tilt)
        elif ear_type == "long_oval":
            self._ears_long(tx, hy, hr, s, tilt)
        elif ear_type == "round":
            self._ears_round(tx, hy, hr, s, tilt, size=14)
        elif ear_type == "small_round":
            self._ears_round(tx, hy, hr, s, tilt, size=9)
        elif ear_type == "big_triangle":
            self._ears_triangle(tx, hy, hr, s, tilt, scale=1.3)
        elif ear_type == "none_comb":
            self._ears_comb(tx, hy, hr, s, tilt)
        # "none" → 不画耳朵

    def _ears_triangle(self, tx, hy, hr, s, tilt, scale=1.0):
        """三角耳（猫/狐狸）"""
        for side in [-1, 1]:
            et = int(tilt * 0.3) if tilt else 0
            self._tri(tx + side * int(hr * 0.52 * scale) + et, hy - hr - int(2 * s),
                      tx + side * int(hr * 0.82 * scale), hy - hr + int(8 * s),
                      tx + side * int(hr * 0.3 * scale), hy - hr + int(6 * s),
                      self.colors["body"], self.colors["stripe"], 1)
            self._tri(tx + side * int(hr * 0.5 * scale) + 1, hy - hr - int(1 * s) + 4,
                      tx + side * int(hr * 0.73 * scale), hy - hr + int(9 * s),
                      tx + side * int(hr * 0.38 * scale), hy - hr + int(8 * s),
                      self.colors["ear_in"], self.colors["ear_in"], 0)

    def _ears_floppy(self, tx, hy, hr, s, tilt):
        """垂耳（狗）：上窄下圆的垂坠耳"""
        for side in [-1, 1]:
            ex = tx + side * int(hr * 0.55)
            ey = hy - hr + int(2 * s)
            pw = int(10 * s)
            ph = int(18 * s)
            sway = int(3 * math.sin(self.frame * math.pi / 5 + side * 2))
            self._oval(ex - pw, ey, ex + pw + sway, ey + ph, self.colors["body"], self.colors["stripe"], 1)
            self._oval(ex - pw + 3, ey + 3, ex + pw - 3 + sway, ey + ph - 3, self.colors["ear_in"], "", 0)

    def _ears_long(self, tx, hy, hr, s, tilt):
        """长椭圆耳（兔）：竖直上翘的长耳朵"""
        for side in [-1, 1]:
            ex = tx + side * int(hr * 0.35)
            ey = hy - hr - int(2 * s)
            ew = int(8 * s)
            eh = int(28 * s)
            sway = int(2 * math.sin(self.frame * math.pi / 4 + side))
            self._oval(ex - ew + sway, ey - eh, ex + ew + sway, ey + int(2 * s), self.colors["body"], self.colors["stripe"], 1)
            self._oval(ex - ew + 3 + sway, ey - eh + 4, ex + ew - 3 + sway, ey + int(1 * s),
                       self.colors["ear_in"], "", 0)

    def _ears_round(self, tx, hy, hr, s, tilt, size=14):
        """圆耳（熊/仓鼠）：半圆形小耳朵"""
        r = int(size * s)
        for side in [-1, 1]:
            ex = tx + side * int(hr * 0.55)
            ey = hy - hr + int(4 * s)
            self._oval(ex - r, ey - r, ex + r, ey + r, self.colors["body"], self.colors["stripe"], 1)
            self._oval(ex - r + 3, ey - r + 3, ex + r - 3, ey + r - 3, self.colors["ear_in"], "", 0)

    def _ears_comb(self, tx, hy, hr, s, tilt):
        """鸡冠（小鸡头顶）：三瓣小肉冠"""
        cy = hy - hr - int(4 * s)
        for i, offset in enumerate([-7, 0, 7]):
            cx_pos = tx + int(offset * s)
            self._oval(cx_pos - int(4 * s), cy - int(5 * s), cx_pos + int(4 * s), cy + int(2 * s),
                       "#FF6090", "#E04070", 1)

    def _draw_face(self,cx,hy,hr,s,pose,eye_big=False):
        er = int(15*s) if eye_big else int(13*s)
        ey = hy-int(4*s); es = int(16*s)
        if pose in ("sleepy","sad"): er = int(9*s)
        if pose in ("happy","bouncy"): er = int(13*s)
        blinking = getattr(self, '_blink_frame', 0) > 0  # 眨眼检测
        for side in [-1,1]:
            ex = cx+side*es
            if blinking:
                # 闭眼：画一条可爱的弧线
                self._line(ex-er, ey, ex+er, ey, "#484050", 2)
                self._line(ex-er+1, ey+1, ex+er-1, ey+1, "#585058", 1)
            else:
                self._oval(ex-er-3,ey-er-3,ex+er+3,ey+er+3,"#FFFFFF","#D8D0D8",1)
                ec = self._eye_rgb.get(self.eye_color,"#F5C842")
                if self.eye_color=="odd": ec = "#60B8F8" if side==-1 else "#F5C842"
                self._oval(ex-er+1,ey-er+1,ex+er-1,ey+er-1,ec,ec,0)
                pr = int(er*0.5); self._oval(ex-pr,ey-pr,ex+pr,ey+pr,"#1A1A2E","",0)
                hl = int(er*0.3)
                self._oval(ex-er//2-1,ey-er//2-1,ex-er//2+hl,ey-er//2+hl,"#FFFFFF","",0)
                self._oval(ex+er//3-1,ey-er//2+2,ex+er//3+int(hl*0.7),ey-er//2+int(hl*0.7),"#FFFFFF","",0)
            if pose=="sad": self._rect(ex-er-3,ey+er-2,ex+er+3,ey+er+2,self.colors["body"],"",0)
            if pose=="sleepy": self._rect(ex-er-3,ey-5,ex+er+3,ey+3,self.colors["body"],"",0)
            if pose=="happy" and self.frame%6>=4: self._rect(ex-er-2,ey-4,ex+er+2,ey+4,self.colors["body"],"",0)
        sp = SPECIES.get(self.species, SPECIES["cat"])
        extras = sp.get("face_extras", [])
        # 鼻子/喙
        ny = hy + int(12 * s)
        if "beak" in extras:
            # 鸡喙：小三角形尖嘴
            self._tri(cx - int(4 * s), ny - 2, cx + int(4 * s), ny - 2, cx, ny + int(5 * s),
                      "#FFB060", "#E89840", 0)
        elif "pointy_beak" in extras:
            # 企鹅尖嘴：稍微长一点
            self._tri(cx - int(3 * s), ny - 1, cx + int(3 * s), ny - 1, cx, ny + int(7 * s),
                      "#FFA050", "#E08030", 0)
        else:
            # 默认粉色小鼻头（猫/狗/兔/熊/狐/仓鼠）
            self._tri(cx - 4, ny - 2, cx + 4, ny - 2, cx, ny + 3, "#FFA0A8", "#E89098", 0)
        my = ny + 5
        if pose in ("happy", "bouncy"):
            self._line(cx - 5, my, cx - 2, my + 3, "#C09898", 1)
            self._line(cx + 5, my, cx + 2, my + 3, "#C09898", 1)
            self._line(cx - 2, my + 3, cx + 2, my + 3, "#C09898", 1)
        elif pose == "surprised":
            self._oval(cx - 4, my, cx + 4, my + 7, "#FF8898", "", 0)
        elif pose == "sad":
            self._line(cx - 5, my + 3, cx - 2, my, "#C09898", 1)
            self._line(cx + 5, my + 3, cx + 2, my, "#C09898", 1)
        elif pose == "sleepy":
            self._oval(cx - 3, my, cx + 3, my + 4, "#FFAAAA", "", 0)
        else:
            self._line(cx, ny + 3, cx - 5, my, "#C09898", 1)
            self._line(cx, ny + 3, cx + 5, my, "#C09898", 1)
        # 腮红
        for side in [-1, 1]:
            blush_size = int(9 * s)
            if "big_cheeks" in extras:
                blush_size = int(14 * s)  # 仓鼠大腮帮
            self._oval(cx + side * int(hr * 0.55) - blush_size, hy + int(8 * s) - blush_size,
                       cx + side * int(hr * 0.55) + blush_size, hy + int(8 * s) + blush_size,
                       "#FFD0D8", "", 0)
        # 胡须（仅猫）
        if "whiskers" in extras and pose != "grooming":
            wy = hy + int(7 * s)
            for side in [-1, 1]:
                for wd in [-4, 0, 4]:
                    self._line(cx + side * int(hr * 0.38), wy + wd, cx + side * int(hr * 0.7), wy + wd * 2,
                               "#E0D0D8", 1)

    def _draw_tail(self, tx, ty, s, happy=False):
        """按物种分发尾巴绘制"""
        sp = SPECIES.get(self.species, SPECIES["cat"])
        tail_type = sp["tail"]
        if tail_type == "long_up":
            self._tail_cat(tx, ty, s, happy)
        elif tail_type == "short_wag":
            self._tail_dog(tx, ty, s, happy)
        elif tail_type == "ball":
            self._tail_ball(tx, ty, s, size=12)
        elif tail_type == "tiny_ball":
            self._tail_ball(tx, ty, s, size=7)
        elif tail_type == "fluffy_big":
            self._tail_fox(tx, ty, s, happy)
        elif tail_type == "short":
            self._tail_short(tx, ty, s)
        # "none" → 不画尾巴

    def _tail_cat(self, tx, ty, s, happy):
        """猫尾：长尾上翘摇摆"""
        ts = int(14 * math.sin(self.frame * math.pi / 3))
        if happy: ts *= 2
        tipy = ty - int(45 * s)
        if not happy: tipy = ty - int(25 * s)
        self._line(tx, ty, tx + int(32 * s) + ts, tipy, self.colors["stripe"], int(9 * s))
        tipx = tx + int(32 * s) + ts
        self._oval(tipx - 6, tipy - 6, tipx + 6, tipy + 6, self.colors["belly"], "", 0)

    def _tail_dog(self, tx, ty, s, happy):
        """狗尾：短尾左右摇摆"""
        wag = int(10 * math.sin(self.frame * math.pi / 2))
        if happy: wag *= 2
        tipy = ty - int(15 * s)
        self._line(tx, ty, tx + int(18 * s) + wag, tipy, self.colors["stripe"], int(7 * s))
        tipx = tx + int(18 * s) + wag
        self._oval(tipx - 4, tipy - 4, tipx + 4, tipy + 4, self.colors["belly"], "", 0)

    def _tail_ball(self, tx, ty, s, size=10):
        """球状尾巴（兔/熊/仓鼠）"""
        bx = tx + int(12 * s)
        by = ty - int(12 * s)
        self._oval(bx - size, by - size, bx + size, by + size, self.colors["belly"], self.colors["stripe"], 1)

    def _tail_fox(self, tx, ty, s, happy):
        """狐狸尾：蓬松大尾巴"""
        ts = int(18 * math.sin(self.frame * math.pi / 3))
        if happy: ts *= 2
        tipy = ty - int(55 * s)
        self._line(tx, ty, tx + int(36 * s) + ts, tipy, self.colors["stripe"], int(12 * s))
        tipx = tx + int(36 * s) + ts
        # 白色尾尖
        self._oval(tipx - 8, tipy - 8, tipx + 8, tipy + 8, "#FFFFFF", self.colors["stripe"], 1)

    def _tail_short(self, tx, ty, s):
        """极短尾（企鹅等）"""
        self._tri(tx, ty, tx - int(6 * s), ty - int(10 * s), tx + int(6 * s), ty - int(10 * s),
                  self.colors["stripe"], self.colors["stripe"], 0)

    def _draw_accessory(self,ax,ay,s):
        if self.acc=="bowtie":
            for side in [-1,1]: self._oval(ax+side*10-7,ay-6,ax+side*10+7,ay+6,"#FF6080","#E04060",1)
            self._oval(ax-3,ay-5,ax+3,ay+5,"#FF4060","",0)
        elif self.acc=="bell":
            jingle = int(2*math.sin(self.frame*math.pi/2))
            self._oval(ax-5,ay-2+jingle,ax+5,ay+8+jingle,"#FFD700","#DAA520",1)
        elif self.acc=="flower":
            for a in [0,72,144,216,288]:
                ra = math.radians(a)
                self._oval(ax+int(7*math.cos(ra))-4,ay+int(7*math.sin(ra))-4,ax+int(7*math.cos(ra))+4,ay+int(7*math.sin(ra))+4,"#FFB0D0","#FF80A0",1)
            self._oval(ax-2,ay-2,ax+2,ay+2,"#FFE880","",0)

    def _oval(self,x1,y1,x2,y2,fill,outline=None,width=1):
        self.canvas.create_oval(x1,y1,x2,y2,fill=fill,outline=outline or fill,width=width,tags="cat")
    def _rect(self,x1,y1,x2,y2,fill,outline=None,width=1):
        self.canvas.create_rectangle(x1,y1,x2,y2,fill=fill,outline=outline or fill,width=width,tags="cat")
    def _line(self,x1,y1,x2,y2,fill,width=1):
        self.canvas.create_line(x1,y1,x2,y2,fill=fill,width=width,tags="cat")
    def _tri(self,x1,y1,x2,y2,x3,y3,fill,outline=None,width=1):
        self.canvas.create_polygon(x1,y1,x2,y2,x3,y3,fill=fill,outline=outline or fill,width=width,tags="cat")
    def _text(self,x,y,t,fill,size=8):
        self.canvas.create_text(x,y,text=t,fill=fill,font=("Microsoft YaHei",size),tags="cat")

    # ══════════ 退出 ══════════
    def _on_close(self):
        try:
            modules = {"emotion":self.emotion,"growth":self.growth,"trust":self.trust,"autonomy":self.autonomy}
            self.state_mgr.save_state(modules)
            self.state_mgr.save_window_position(self.root.winfo_x(),self.root.winfo_y())
            with open(os.path.join(DATA_DIR,".clean_exit"),"w") as f: f.write("1")
            self.db.close()
        except: pass
        try: self.root.destroy()
        except: pass
        release_single_instance()
        log("退出")

    def run(self):
        self.root.mainloop()

if __name__=="__main__":
    try:
        DesktopPet().run()
    except Exception as e:
        log(f"FATAL: {e}\n{traceback.format_exc()}")
        import tkinter.messagebox as mb
        mb.showerror("启动失败",f"{e}\n详情见 logs/pet.log")
