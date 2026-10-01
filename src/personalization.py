from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from .models import Influencer, PersonalizedMessage


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+[\w'-]*\b", text or ""))


def validate_message(message: PersonalizedMessage) -> None:
    email_words = _word_count(message.email_pitch)
    dm_words = _word_count(message.instagram_dm)
    if not 60 <= email_words <= 90:
        raise ValueError(f"Email must be 60–90 words; got {email_words}")
    if not 15 <= dm_words <= 30:
        raise ValueError(f"Instagram DM must be 15–30 words; got {dm_words}")


SYSTEM_PROMPT = """
You write ethical, concise creator outreach for a technology brand.
Use only the creator facts supplied in the input. Never invent sponsorship history,
metrics, demographics, recent videos, companies, or contact information.
Return valid JSON with keys: email_subject, email_pitch, instagram_dm.
Email pitch: 60-90 words exactly.
Instagram DM: 15-30 words exactly.
The email must naturally reference the creator's technology niche/content themes,
a recent content signal, the relevant audience, a proposed collaboration, and the value proposition.
The DM must sound natural and specific rather than generic.
Do not use markdown in message content.
""".strip()


def _fallback(influencer: Influencer) -> PersonalizedMessage:
    recent = influencer.recent_content[0] if influencer.recent_content else "recent technology content"
    theme = influencer.content_themes.split(", ")[0] if influencer.content_themes else "technology"
    email = (
        f"Hi {influencer.name}, I’ve been following your {theme.lower()} content, especially “{recent}.” "
        f"Your practical, creator-led approach makes your channel a strong context for a technology collaboration. "
        f"We’d like to explore a sponsored integration or UGC concept built around the topics your audience already follows. "
        f"We can provide a clear brief, creative flexibility, and a paid collaboration aligned to your content style. "
        f"Would you be open to a quick conversation about the concept and deliverables?"
    )
    dm = f"Hi {influencer.name}, loved your recent {theme.lower()} content. Your audience looks relevant for a paid tech collaboration—open to details?"
    msg = PersonalizedMessage(
        influencer_id=influencer.influencer_id,
        influencer_name=influencer.name,
        email=influencer.contact_email,
        email_subject=f"Collaboration idea for {influencer.name}",
        email_pitch=email,
        instagram_dm=dm,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    # Fallback must still satisfy the assignment's length limits.
    if 60 <= _word_count(msg.email_pitch) <= 90 and 15 <= _word_count(msg.instagram_dm) <= 30:
        return msg
    # Safe deterministic shortening/extension path.
    while _word_count(msg.email_pitch) < 60:
        msg.email_pitch += " We think the format could fit naturally with your current programming-focused content."
    while _word_count(msg.instagram_dm) < 15:
        msg.instagram_dm += " Happy to share the brief and budget."
    msg.email_pitch = " ".join(msg.email_pitch.split())
    msg.instagram_dm = " ".join(msg.instagram_dm.split())
    if _word_count(msg.email_pitch) > 90 or _word_count(msg.instagram_dm) > 30:
        raise ValueError("Fallback could not satisfy the required message lengths")
    return msg


def generate_message(influencer: Influencer, api_key: str, model: str) -> PersonalizedMessage:
    if not api_key:
        return _fallback(influencer)

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    payload = {
        "name": influencer.name,
        "platform": influencer.platform,
        "niche": influencer.niche,
        "content_themes": influencer.content_themes,
        "subscriber_count": influencer.followers,
        "engagement_rate": influencer.engagement_rate,
        "recent_content": influencer.recent_content[:5],
        "bio": influencer.bio[:1200],
        "audience_geography": influencer.audience_geography,
        "collaboration_angle": "paid technology sponsorship / UGC / affiliate campaign",
        "brand_value_proposition": "a paid partnership with a clear brief and creative flexibility",
    }
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
    )
    raw = response.output_text.strip()
    data = json.loads(raw)
    msg = PersonalizedMessage(
        influencer_id=influencer.influencer_id,
        influencer_name=influencer.name,
        email=influencer.contact_email,
        email_subject=str(data["email_subject"]).strip(),
        email_pitch=str(data["email_pitch"]).strip(),
        instagram_dm=str(data["instagram_dm"]).strip(),
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
    validate_message(msg)
    return msg
