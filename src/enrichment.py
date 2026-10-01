from __future__ import annotations

from .models import Influencer


def enrich(influencers: list[Influencer]) -> list[Influencer]:
    """Keep enrichment conservative and source-backed.

    The YouTube public Data API does not provide creator audience age/gender analytics.
    Those fields therefore remain explicitly unavailable rather than guessed.
    """
    enriched: list[Influencer] = []
    for influencer in influencers:
        geography = "Not Available"
        description = influencer.bio.lower()
        for marker, label in [
            ("india", "India"),
            ("united states", "United States"),
            ("usa", "United States"),
            ("uk", "United Kingdom"),
            ("united kingdom", "United Kingdom"),
            ("canada", "Canada"),
        ]:
            if marker in description:
                geography = label
                break
        enriched.append(influencer.__class__(**{**influencer.__dict__, "audience_geography": geography}))
    return enriched
