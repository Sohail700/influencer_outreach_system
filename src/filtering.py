from __future__ import annotations

from dataclasses import replace

from .models import Influencer


TECH_TERMS = {
    "web development", "python", "javascript", "react", "next.js", "backend", "frontend",
    "software", "programming", "coding", "developer", "machine learning", "ai", "llm",
    "aws", "azure", "gcp", "docker", "kubernetes", "devops", "cybersecurity", "security",
}


def _term_hits(text: str) -> int:
    lower = text.lower()
    return sum(1 for term in TECH_TERMS if term in lower)


def classify(influencer: Influencer, min_followers: int, max_followers: int, min_er: float, min_score: int) -> Influencer:
    follower_fit = min_followers <= influencer.followers <= max_followers
    relevance_hits = _term_hits(f"{influencer.content_themes} {influencer.bio} {' '.join(influencer.recent_content)}")
    niche_relevance = min(30, relevance_hits * 5)
    follower_score = 20 if follower_fit else 0
    engagement_score = 20 if influencer.engagement_rate >= max(min_er, 2.0) else 14 if influencer.engagement_rate >= min_er else 0
    content_score = 20 if relevance_hits >= 4 else 15 if relevance_hits >= 2 else 8 if relevance_hits == 1 else 0
    completeness_score = 10
    if influencer.contact_email == "Not Found":
        completeness_score -= 3
    if influencer.website == "Not Available":
        completeness_score -= 1

    score = max(0, niche_relevance + follower_score + engagement_score + content_score + completeness_score)
    reasons = []
    if not follower_fit:
        reasons.append("outside 5,000–100,000 subscriber range")
    if influencer.engagement_rate < min_er:
        reasons.append(f"engagement {influencer.engagement_rate:.2f}% below {min_er:.2f}%")
    if relevance_hits == 0:
        reasons.append("weak technology content relevance")
    if influencer.contact_email == "Not Found":
        reasons.append("public contact email not found")

    status = "Passed" if follower_fit and influencer.engagement_rate >= min_er and score >= min_score and relevance_hits > 0 else "Failed"
    if status == "Passed":
        reason = f"Passed hard filters; score={score}/100; technology-relevance signals={relevance_hits}."
    else:
        reason = "; ".join(reasons) or f"score={score}/100 below threshold {min_score}."

    return replace(influencer, status=status, filter_reason=reason, score=score)


def apply_filters(influencers: list[Influencer], min_followers: int, max_followers: int, min_er: float, min_score: int) -> list[Influencer]:
    return [classify(i, min_followers, max_followers, min_er, min_score) for i in influencers]
