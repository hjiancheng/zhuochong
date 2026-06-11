"""开发者重置工具 - 清除宠物数据用于测试"""
import os, shutil, sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROFILE = os.path.join(DATA_DIR, "profile.json")
PROFILE_ENC = os.path.join(DATA_DIR, "profile.enc")
MEMORY_DB = os.path.join(DATA_DIR, "pet_memory.db")
STATE_FILE = os.path.join(DATA_DIR, "pet_state.json")
EGG_STATE = os.path.join(DATA_DIR, "egg_state.json")
WIZARD_PROGRESS = os.path.join(DATA_DIR, "wizard_progress.json")
USER_PROFILE = os.path.join(DATA_DIR, "user_profile.json")
CLEAN_EXIT = os.path.join(DATA_DIR, ".clean_exit")


def reset_all():
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
    os.makedirs(DATA_DIR, exist_ok=True)
    print("✅ 已完全重置。下次启动将弹出创猫向导。")


def reset_profile():
    for f in [PROFILE, PROFILE_ENC, WIZARD_PROGRESS, EGG_STATE]:
        if os.path.exists(f):
            os.remove(f)
    print("✅ 档案已清除。猫的身份将被重新设定。")


def reset_memory():
    for f in [MEMORY_DB]:
        if os.path.exists(f):
            os.remove(f)
    print("✅ 记忆已清除。猫还是那只猫，只是忘记了过往。")


def reset_state():
    for f in [STATE_FILE, EGG_STATE, CLEAN_EXIT]:
        if os.path.exists(f):
            os.remove(f)
    print("✅ 状态已重置。猫回到初始位置和情感。")


def reset_user_profile():
    if os.path.exists(USER_PROFILE):
        os.remove(USER_PROFILE)
    print("✅ 用户档案已清除。猫将重新了解主人。")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--profile": reset_profile()
        elif arg == "--memory": reset_memory()
        elif arg == "--state": reset_state()
        elif arg == "--user": reset_user_profile()
        else: reset_all()
    else:
        reset_all()
