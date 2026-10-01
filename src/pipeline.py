from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from .config import Settings
from .enrichment import enrich
from .filtering import apply_filters
from .models import Influencer, PersonalizedMessage
from .outreach import OutreachSender, OutreachTracker
from .personalization import generate_message
from .youtube_discovery import YouTubeDiscovery


class OutreachPipeline:
    def __init__(self, settings: Settings, output_dir: str = "out"):
        self.settings = settings
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tracker = OutreachTracker(str(self.output_dir / "outreach.db"))

    @staticmethod
    def _export_influencers(rows: list[Influencer], path: Path) -> None:
        data = [r.to_dict() for r in rows]
        pd.DataFrame(data).to_csv(path, index=False)
        with open(path.with_suffix(".json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _export_messages(rows: list[PersonalizedMessage], path: Path) -> None:
        pd.DataFrame([asdict(r) for r in rows]).to_csv(path, index=False)

    def run(self, target: int | None = None, skip_llm: bool = False) -> tuple[list[Influencer], list[Influencer], list[PersonalizedMessage]]:
        target = target or self.settings.discovery_target
        discovery = YouTubeDiscovery(self.settings.youtube_api_key)
        discovered = discovery.collect(
            target=target,
            min_followers=self.settings.min_followers,
            max_followers=self.settings.max_followers,
            recent_video_count=self.settings.recent_video_count,
        )
        enriched = enrich(discovered)
        classified = apply_filters(
            enriched,
            self.settings.min_followers,
            self.settings.max_followers,
            self.settings.min_engagement_rate,
            self.settings.min_score,
        )
        shortlist = [i for i in classified if i.status == "Passed"]
        messages: list[PersonalizedMessage] = []
        for influencer in shortlist:
            if skip_llm:
                continue
            messages.append(generate_message(influencer, self.settings.openai_api_key, self.settings.openai_model))

        self._export_influencers(classified, self.output_dir / "all_influencers.csv")
        self._export_influencers(shortlist, self.output_dir / "shortlisted_influencers.csv")
        if messages:
            self._export_messages(messages, self.output_dir / "personalized_messages.csv")
        self.tracker.export_csv(str(self.output_dir / "outreach_log.csv"))
        return classified, shortlist, messages

    def sending_layer(self, messages: list[PersonalizedMessage], dry_run: bool = True, limit: int | None = None) -> list[str]:
        sender = OutreachSender(
            tracker=self.tracker,
            smtp_host=self.settings.smtp_host,
            smtp_port=self.settings.smtp_port,
            smtp_username=self.settings.smtp_username,
            smtp_password=self.settings.smtp_password,
            smtp_from=self.settings.smtp_from,
        )
        selected = messages[:limit] if limit else messages
        results = []
        for message in selected:
            results.append(sender.simulate(message) if dry_run else sender.send(message))
        self.tracker.export_csv(str(self.output_dir / "outreach_log.csv"))
        return results
