from __future__ import annotations

import argparse

from src.config import Settings
from src.pipeline import OutreachPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="AI micro-influencer outreach pipeline")
    parser.add_argument("--target", type=int, default=None, help="Number of micro-influencers to discover")
    parser.add_argument("--min-followers", type=int, default=None)
    parser.add_argument("--max-followers", type=int, default=None)
    parser.add_argument("--recent-videos", type=int, default=None)
    parser.add_argument("--skip-llm", action="store_true")
    parser.add_argument("--send", action="store_true", help="Actually send emails via SMTP; otherwise use dry-run simulation")
    parser.add_argument("--limit", type=int, default=None, help="Maximum emails to send/simulate")
    args = parser.parse_args()

    base = Settings()
    settings = Settings(
        youtube_api_key=base.youtube_api_key,
        openai_api_key=base.openai_api_key,
        openai_model=base.openai_model,
        min_followers=args.min_followers if args.min_followers is not None else base.min_followers,
        max_followers=args.max_followers if args.max_followers is not None else base.max_followers,
        min_engagement_rate=base.min_engagement_rate,
        min_score=base.min_score,
        discovery_target=args.target if args.target is not None else base.discovery_target,
        recent_video_count=args.recent_videos if args.recent_videos is not None else base.recent_video_count,
        smtp_host=base.smtp_host,
        smtp_port=base.smtp_port,
        smtp_username=base.smtp_username,
        smtp_password=base.smtp_password,
        smtp_from=base.smtp_from,
    )

    pipeline = OutreachPipeline(settings)
    all_rows, shortlist, messages = pipeline.run(target=settings.discovery_target, skip_llm=args.skip_llm)
    print(f"Discovered/enriched: {len(all_rows)}")
    print(f"Passed filter: {len(shortlist)}")
    print(f"Personalized messages: {len(messages)}")

    if messages:
        results = pipeline.sending_layer(messages, dry_run=not args.send, limit=args.limit)
        print(f"Outreach results: {results}")

    print("Outputs written to ./out")


if __name__ == "__main__":
    main()
