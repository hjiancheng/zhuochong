"""SQLite 数据库管理 + 状态持久化"""
import sqlite3
import os
import json
import shutil
from datetime import datetime
from logger import logger


class Database:
    """管理 pet_memory.db 的创建、迁移、备份"""

    DB_VERSION = 1

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.db_path = os.path.join(data_dir, "pet_memory.db")
        self.conn = None
        self._init_db()

    def _init_db(self):
        """初始化数据库和表结构"""
        backup_path = os.path.join(self.data_dir, "backup")
        os.makedirs(backup_path, exist_ok=True)

        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA foreign_keys=ON")
            self._create_tables()
            self._check_backup()
            logger.info(f"数据库初始化完成: {self.db_path}")
        except sqlite3.DatabaseError as e:
            logger.error(f"数据库损坏，尝试从备份恢复: {e}")
            self._restore_from_backup()

    def _create_tables(self):
        c = self.conn.cursor()
        # 对话记录
        c.execute("""CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            trigger_event TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        # 记忆
        c.execute("""CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            content TEXT NOT NULL,
            importance REAL DEFAULT 0.5,
            time_tag TEXT,
            notable INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_recalled TIMESTAMP,
            recall_count INTEGER DEFAULT 0
        )""")
        # 行为模式
        c.execute("""CREATE TABLE IF NOT EXISTS behavior_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern_type TEXT,
            avg_time TEXT,
            confidence REAL DEFAULT 0.0,
            data_points TEXT
        )""")
        # 宠物状态
        c.execute("""CREATE TABLE IF NOT EXISTS pet_state (
            id INTEGER PRIMARY KEY,
            state_json TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        # 日记
        c.execute("""CREATE TABLE IF NOT EXISTS diary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT UNIQUE,
            content TEXT,
            notable INTEGER DEFAULT 0,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        # FTS5 全文搜索
        c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(content)")
        # 版本
        c.execute("CREATE TABLE IF NOT EXISTS db_meta (key TEXT PRIMARY KEY, value TEXT)")
        c.execute("INSERT OR IGNORE INTO db_meta VALUES ('version', ?)", (str(self.DB_VERSION),))
        self.conn.commit()

    def _check_backup(self):
        """每日备份检查"""
        today = datetime.now().strftime("%Y%m%d")
        backup_dir = os.path.join(self.data_dir, "backup")
        today_backup = os.path.join(backup_dir, f"pet_memory_{today}.db")
        if not os.path.exists(today_backup):
            try:
                shutil.copy2(self.db_path, today_backup)
                # 只保留最近7个备份
                backups = sorted([
                    f for f in os.listdir(backup_dir)
                    if f.startswith("pet_memory_") and f.endswith(".db")
                ], reverse=True)
                for old in backups[7:]:
                    os.remove(os.path.join(backup_dir, old))
                logger.info(f"数据库已备份: {today_backup}")
            except Exception as e:
                logger.error(f"备份失败: {e}")

    def _restore_from_backup(self):
        """从最新备份恢复"""
        backup_dir = os.path.join(self.data_dir, "backup")
        backups = sorted([
            f for f in os.listdir(backup_dir)
            if f.startswith("pet_memory_") and f.endswith(".db")
        ], reverse=True)
        if backups:
            latest = os.path.join(backup_dir, backups[0])
            shutil.copy2(latest, self.db_path)
            logger.info(f"数据库已从备份恢复: {backups[0]}")
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        else:
            logger.warning("无可用备份，创建新数据库")
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._create_tables()

    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            logger.info("数据库已关闭")


class StateManager:
    """管理宠物状态的保存和恢复"""

    def __init__(self, data_dir="data"):
        self.state_path = os.path.join(data_dir, "pet_state.json")
        self.egg_state_path = os.path.join(data_dir, "egg_state.json")
        self.clean_exit_path = os.path.join(data_dir, ".clean_exit")
        os.makedirs(data_dir, exist_ok=True)

    def was_clean_exit(self) -> bool:
        """检查上次是否为正常退出"""
        existed = os.path.exists(self.clean_exit_path)
        if existed:
            try:
                os.remove(self.clean_exit_path)
            except:
                pass
        return existed

    def save_state(self, state_modules: dict):
        """保存所有模块的状态"""
        state = {}
        for module_name, module in state_modules.items():
            if hasattr(module, "save_state"):
                state[module_name] = module.save_state()
        try:
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            logger.debug("状态已保存")
        except Exception as e:
            logger.error(f"状态保存失败: {e}")

    def load_state(self) -> dict:
        """加载保存的状态"""
        if not os.path.exists(self.state_path):
            return {}
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            logger.info("状态已加载")
            return state
        except Exception as e:
            logger.error(f"状态加载失败: {e}")
            return {}

    def save_window_position(self, x, y):
        """保存窗口位置"""
        pos = {"window_x": x, "window_y": y}
        state = self.load_state() if os.path.exists(self.state_path) else {}
        state["window_position"] = pos
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def load_window_position(self) -> tuple | None:
        """加载窗口位置"""
        state = self.load_state()
        pos = state.get("window_position", {})
        if "window_x" in pos and "window_y" in pos:
            return pos["window_x"], pos["window_y"]
        return None
