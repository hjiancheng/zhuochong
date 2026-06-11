"""绝密档案加密验证 - SHA256 篡改检测"""
from logger import logger
import hashlib
import os


class ArchiveGuard:
    """守护宠物档案的完整性"""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.sig_path = os.path.join(data_dir, ".profile.sig")

    def sign(self, profile_path: str):
        """对档案文件签名"""
        if not os.path.exists(profile_path):
            return False
        with open(profile_path, "rb") as f:
            content = f.read()
        sig = hashlib.sha256(content).hexdigest()
        with open(self.sig_path, "w") as f:
            f.write(sig)
        logger.info("档案签名已生成")
        return True

    def verify(self, profile_path: str) -> bool:
        """验证档案是否被篡改"""
        if not os.path.exists(profile_path):
            return False
        if not os.path.exists(self.sig_path):
            # 首次运行，没有签名 → 生成签名
            return self.sign(profile_path)

        with open(profile_path, "rb") as f:
            content = f.read()
        current_hash = hashlib.sha256(content).hexdigest()

        with open(self.sig_path, "r") as f:
            stored_hash = f.read().strip()

        if current_hash != stored_hash:
            logger.warning("🔒 档案完整性验证失败——可能被篡改！")
            return False

        logger.debug("档案完整性验证通过")
        return True

    def is_locked(self) -> bool:
        """检查档案是否已被锁定"""
        return os.path.exists(os.path.join(self.data_dir, "profile.json")) and \
               os.path.exists(self.sig_path)
