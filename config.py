"""全局配置。所有 key 从 .env 读取；没配 key 时自动进入演示模式(MOCK)。"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 文本模型 DeepSeek
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()

    # 图像模型 火山方舟 Seedream（可选）
    ARK_API_KEY = os.getenv("ARK_API_KEY", "").strip()
    ARK_BASE_URL = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3").strip()
    ARK_IMAGE_MODEL = os.getenv("ARK_IMAGE_MODEL", "doubao-seedream-3-0-t2i-250415").strip()

    FORCE_MOCK = os.getenv("FORCE_MOCK", "0").strip() == "1"

    @classmethod
    def text_mock(cls) -> bool:
        """没有 DeepSeek key 或强制 mock 时，文本走演示样例。"""
        return cls.FORCE_MOCK or not cls.DEEPSEEK_API_KEY

    @classmethod
    def image_enabled(cls) -> bool:
        """有火山 key 且未强制 mock 时，才真去生成场景图。"""
        return bool(cls.ARK_API_KEY) and not cls.FORCE_MOCK
