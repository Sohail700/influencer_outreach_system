from __future__ import annotations

import re
import time
from datetime import datetime, timezone
from typing import Iterable

import requests

from .models import Influencer


class YouTubeAPIError(RuntimeError):
    pass


TECH_QUERIES = [
    "web development",
    "python programming",
    "javascript tutorial",
    "react developer",
    "software engineering",
    "AI tools",
    "machine learning",
    "cloud computing",
    "cybersecurity",
    "coding projects",
    "developer productivity",
    "DevOps",
]

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
URL_RE = re.compile(r"https?://[^\s)\]>]+", re.I)


class YouTubeDiscovery:
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str, session: requests.Session | None = None, timeout: int = 20):
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY is required")
        self.api_key = api_key
        self.session = session or requests.Session()
        self.timeout = timeout

    def _get(self, path: str, params: dict) -> dict:
        params = {**params, "key": self.api_key}
        response = self.session.get(f"{self.BASE_URL}/{path}", params=params, timeout=self.timeout)
        if response.status_code != 200:
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            raise YouTubeAPIError(f"YouTube API {response.status_code}: {detail}")
        return response.json()

    def discover_channel_ids(self, target: int, queries: Iterable[str] = TECH_QUERIES) -> list[str]:
        found: list[str] = []
        seen: set[str] = set()
        for query in queries:
            page_token = None
            for _ in range(2):
                params = {
                    "part": "snippet",
                    "q": query,
                    "type": "channel",
                    "maxResults": 50,
                    "order": "relevance",
                }
                if page_token:
                    params["pageToken"] = page_token
                data = self._get("search", params)
                for item in data.get("items", []):
                    channel_id = item.get("id", {}).get("channelId")
                    if channel_id and channel_id not in seen:
                        seen.add(channel_id)
                        found.append(channel_id)
                        if len(found) >= target * 4:
                            return found
                page_token = data.get("nextPageToken")
                if not page_token:
                    break
                time.sleep(0.1)
        return found

    def fetch_channels(self, channel_ids: list[str]) -> list[dict]:
        results: list[dict] = []
        for start in range(0, len(channel_ids), 50):
            chunk = channel_ids[start:start + 50]
            data = self._get(
                "channels",
                {
                    "part": "snippet,statistics,contentDetails,topicDetails",
                    "id": ",".join(chunk),
                },
            )
            results.extend(data.get("items", []))
        return results

    def fetch_recent_videos(self, uploads_playlist_id: str, count: int = 8) -> list[dict]:
        if not uploads_playlist_id:
            return []
        data = self._get(
            "playlistItems",
            {
                "part": "contentDetails,snippet",
                "playlistId": uploads_playlist_id,
                "maxResults": min(count, 50),
            },
        )
        ids = [i.get("contentDetails", {}).get("videoId") for i in data.get("items", [])]
        ids = [i for i in ids if i]
        if not ids:
            return []
        stats = self._get("videos", {"part": "snippet,statistics", "id": ",".join(ids[:50])})
        return stats.get("items", [])

    @staticmethod
    def _extract_email(text: str) -> str:
        match = EMAIL_RE.search(text or "")
        return match.group(0) if match else "Not Found"

    @staticmethod
    def _extract_website(text: str) -> str:
        for url in URL_RE.findall(text or ""):
            if "youtube.com" not in url.lower() and "youtu.be" not in url.lower():
                return url.rstrip(".,")
        return "Not Available"

    @staticmethod
    def _themes(texts: list[str]) -> str:
        joined = " ".join(texts).lower()
        keyword_map = {
            "Web Development": ["react", "next.js", "javascript", "frontend", "backend", "html", "css"],
            "Python": ["python", "django", "flask", "pandas"],
            "AI / ML": ["ai", "machine learning", "ml", "llm", "chatgpt", "generative"],
            "Cloud / DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "devops", "terraform"],
            "Cybersecurity": ["cyber", "security", "pentest", "ethical hacking", "infosec"],
            "Programming / Career": ["coding", "programming", "developer", "software engineer", "career"],
        }
        hits = [theme for theme, words in keyword_map.items() if any(w in joined for w in words)]
        return ", ".join(hits[:4]) if hits else "Technology / Programming"

    def collect(self, target: int, min_followers: int, max_followers: int, recent_video_count: int = 8) -> list[Influencer]:
        candidate_ids = self.discover_channel_ids(target)
        channels = self.fetch_channels(candidate_ids)
        influencers: list[Influencer] = []
        retrieved_at = datetime.now(timezone.utc).isoformat()

        for channel in channels:
            stats = channel.get("statistics", {})
            snippet = channel.get("snippet", {})
            details = channel.get("contentDetails", {})
            try:
                followers = int(stats.get("subscriberCount", 0))
            except (TypeError, ValueError):
                followers = 0
            if not (min_followers <= followers <= max_followers):
                continue

            title = snippet.get("title", "Unknown channel")
            description = snippet.get("description", "")
            uploads_id = details.get("relatedPlaylists", {}).get("uploads", "")
            videos = self.fetch_recent_videos(uploads_id, recent_video_count)

            likes = []
            comments = []
            recent_titles = []
            for video in videos:
                vstats = video.get("statistics", {})
                try:
                    likes.append(int(vstats.get("likeCount", 0)))
                except (TypeError, ValueError):
                    likes.append(0)
                try:
                    comments.append(int(vstats.get("commentCount", 0)))
                except (TypeError, ValueError):
                    comments.append(0)
                recent_titles.append(video.get("snippet", {}).get("title", "Untitled video"))

            avg_interactions = ((sum(likes) / len(likes)) + (sum(comments) / len(comments))) if videos else 0
            engagement_rate = round((avg_interactions / followers) * 100, 2) if followers else 0.0

            texts = [title, description, *recent_titles]
            themes = self._themes(texts)
            profile_url = f"https://www.youtube.com/channel/{channel.get('id')}"
            influencers.append(
                Influencer(
                    influencer_id=channel.get("id", ""),
                    name=title,
                    platform="YouTube",
                    profile_url=profile_url,
                    followers=followers,
                    engagement_rate=engagement_rate,
                    niche="Technology",
                    content_themes=themes,
                    contact_email=self._extract_email(description),
                    website=self._extract_website(description),
                    bio=description[:1500],
                    recent_content=recent_titles,
                    source="YouTube Data API",
                    retrieved_at=retrieved_at,
                )
            )
            if len(influencers) >= target:
                break
        return influencers
