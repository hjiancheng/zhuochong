"""记忆系统 - SQLite 双层记忆（短期+长期），FTS5检索"""
from logger import logger
from datetime import datetime, timedelta
from db import Database
import json


class MemorySystem:
    """猫的记忆——与用户共同的回忆"""

    SHORT_TERM_LIMIT = 20  # 内存中保留的最近对话数

    def __init__(self, db: Database):
        self.db = db
        self._short_term = []  # [(role, content, time), ...]
        self._load_recent()
        logger.info(f"记忆系统初始化: 短期记忆{len(self._short_term)}条")

    def _load_recent(self):
        """从数据库加载最近对话到短期记忆"""
        try:
            c = self.db.conn.cursor()
            c.execute("SELECT role, content, created_at FROM conversations ORDER BY created_at DESC LIMIT ?",
                     (self.SHORT_TERM_LIMIT,))
            rows = c.fetchall()
            self._short_term = [(r[0], r[1], r[2]) for r in reversed(rows)]
        except Exception as e:
            logger.error(f"加载对话历史失败: {e}")

    # ── 对话记忆 ──

    def add_conversation(self, role: str, content: str, trigger: str = None):
        """添加一条对话记录"""
        self._short_term.append((role, content, datetime.now().isoformat()))
        if len(self._short_term) > self.SHORT_TERM_LIMIT:
            self._short_term.pop(0)

        try:
            self.db.conn.execute(
                "INSERT INTO conversations (role, content, trigger_event) VALUES (?, ?, ?)",
                (role, content, trigger)
            )
            self.db.conn.commit()
        except Exception as e:
            logger.error(f"保存对话失败: {e}")

    def get_recent_conversations(self, n: int = 10) -> list:
        """获取最近n条对话"""
        return self._short_term[-n:]

    def get_recent_summary(self) -> str:
        """获取最近对话的摘要"""
        if not self._short_term:
            return "还没有说过话。"
        recent = self._short_term[-5:]
        lines = []
        for role, content, _ in recent:
            prefix = "猫" if role == "pet" else "主人"
            lines.append(f"{prefix}: {content[:30]}")
        return " | ".join(lines)

    # ── 事件记忆 ──

    def add_memory(self, mem_type: str, content: str, importance: float = 0.5, notable: bool = False):
        """添加一条记忆"""
        time_tag = datetime.now().strftime("%H:%M")
        try:
            self.db.conn.execute(
                "INSERT INTO memories (type, content, importance, time_tag, notable) VALUES (?, ?, ?, ?, ?)",
                (mem_type, content, importance, time_tag, 1 if notable else 0)
            )
            # 同步到FTS
            self.db.conn.execute(
                "INSERT INTO memories_fts (content) VALUES (?)",
                (content,)
            )
            self.db.conn.commit()
            logger.debug(f"记忆已添加: [{mem_type}] {content[:40]}")
        except Exception as e:
            logger.error(f"添加记忆失败: {e}")

    def search_memories(self, keyword: str, limit: int = 5) -> list:
        """FTS5 全文搜索记忆"""
        try:
            c = self.db.conn.cursor()
            # 直接从 FTS5 表搜索，获取 rowid 后回查 memories
            c.execute(
                "SELECT m.content, m.importance, m.time_tag FROM memories m "
                "INNER JOIN memories_fts fts ON fts.rowid = m.id "
                "WHERE memories_fts MATCH ? "
                "ORDER BY m.importance DESC LIMIT ?",
                (keyword, limit)
            )
            return c.fetchall()
        except Exception as e:
            logger.error(f"记忆搜索失败: {e}")
            return []

    def get_notable_memories(self, tag: str = None, limit: int = 5) -> list:
        """获取标记为notable的记忆"""
        try:
            c = self.db.conn.cursor()
            if tag:
                c.execute(
                    "SELECT content, tags FROM diary WHERE notable=1 AND tags LIKE ? ORDER BY created_at DESC LIMIT ?",
                    (f"%{tag}%", limit)
                )
            else:
                c.execute(
                    "SELECT content, tags FROM diary WHERE notable=1 ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                )
            return c.fetchall()
        except Exception as e:
            logger.error(f"获取notable记忆失败: {e}")
            return []

    # ── 行为模式记忆 ──

    def record_behavior_pattern(self, pattern_type: str, avg_time: str, confidence: float, data_points: int):
        """记录观察到的用户行为模式"""
        try:
            self.db.conn.execute(
                "INSERT OR REPLACE INTO behavior_patterns (pattern_type, avg_time, confidence, data_points) "
                "VALUES (?, ?, ?, ?)",
                (pattern_type, avg_time, confidence, str(data_points))
            )
            self.db.conn.commit()
        except Exception as e:
            logger.error(f"记录行为模式失败: {e}")

    def get_behavior_pattern(self, pattern_type: str) -> tuple | None:
        """获取特定行为模式"""
        try:
            c = self.db.conn.cursor()
            c.execute(
                "SELECT avg_time, confidence FROM behavior_patterns WHERE pattern_type=?",
                (pattern_type,)
            )
            return c.fetchone()
        except:
            return None

    # ── 定期浓缩（模拟） ──

    def summarize_old_conversations(self, threshold: int = 50):
        """当对话超过阈值时，生成摘要记忆"""
        try:
            c = self.db.conn.cursor()
            c.execute("SELECT COUNT(*) FROM conversations")
            count = c.fetchone()[0]
            if count > threshold:
                # 取最旧的 batch 生成摘要
                c.execute("SELECT content FROM conversations ORDER BY created_at ASC LIMIT 20")
                old = c.fetchall()
                summary = f"早期对话摘要（共{len(old)}条）: " + "；".join(
                    [row[0][:20] + "..." for row in old[:5]]
                )
                self.add_memory("summary", summary, importance=0.3)
                logger.info(f"对话摘要已生成 ({count}条总对话)")
        except Exception as e:
            logger.error(f"对话摘要生成失败: {e}")

    # ── 统计 ──

    def get_stats(self) -> dict:
        """获取记忆统计"""
        try:
            c = self.db.conn.cursor()
            c.execute("SELECT COUNT(*) FROM conversations")
            total_convos = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM memories")
            total_memories = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM diary")
            total_diary = c.fetchone()[0]
            return {
                "conversations": total_convos,
                "memories": total_memories,
                "diary_entries": total_diary,
            }
        except:
            return {"conversations": 0, "memories": 0, "diary_entries": 0}
