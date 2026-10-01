from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any


@dataclass
class Influencer:
    influencer_id: str
    name: str
    platform: str
    profile_url: str
    followers: int
    engagement_rate: float
    niche: str
    content_themes: str
    contact_email: str
    website: str = "Not Available"
    audience_age: str = "Not Available"
    audience_gender: str = "Not Available"
    audience_geography: str = "Not Available"
    bio: str = ""
    recent_content: list[str] = field(default_factory=list)
    source: str = "YouTube Data API"
    retrieved_at: str = ""
    status: str = ""
    filter_reason: str = ""
    score: int = 0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["recent_content"] = " | ".join(self.recent_content)
        return data


@dataclass
class PersonalizedMessage:
    influencer_id: str
    influencer_name: str
    email: str
    email_subject: str
    email_pitch: str
    instagram_dm: str
    generated_at: str
