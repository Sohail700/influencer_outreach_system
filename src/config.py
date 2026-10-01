from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    youtube_api_key: str = os.getenv("YOUTUBE_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
    min_followers: int = int(os.getenv("MIN_FOLLOWERS", "5000"))
    max_followers: int = int(os.getenv("MAX_FOLLOWERS", "100000"))
    min_engagement_rate: float = float(os.getenv("MIN_ENGAGEMENT_RATE", "0.5"))
    min_score: int = int(os.getenv("MIN_SCORE", "60"))
    discovery_target: int = int(os.getenv("DISCOVERY_TARGET", "50"))
    recent_video_count: int = int(os.getenv("RECENT_VIDEO_COUNT", "8"))
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("SMTP_FROM", "")
