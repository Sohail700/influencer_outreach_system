from src.filtering import classify
from src.models import Influencer


def make_influencer(**kwargs):
    base = dict(
        influencer_id="abc",
        name="Example Tech Creator",
        platform="YouTube",
        profile_url="https://youtube.com/channel/abc",
        followers=20000,
        engagement_rate=3.2,
        niche="Technology",
        content_themes="Web Development, Python, AI / ML",
        contact_email="Not Found",
        bio="Python and web development tutorials with AI experiments.",
        recent_content=["React Project Tutorial", "Building an AI App"],
    )
    base.update(kwargs)
    return Influencer(**base)


def test_qualified_creator_passes():
    result = classify(make_influencer(), 5000, 100000, 0.5, 60)
    assert result.status == "Passed"
    assert result.score >= 60


def test_low_engagement_creator_fails():
    result = classify(make_influencer(engagement_rate=0.1), 5000, 100000, 0.5, 60)
    assert result.status == "Failed"
    assert "engagement" in result.filter_reason


def test_large_creator_fails_micro_range():
    result = classify(make_influencer(followers=250000), 5000, 100000, 0.5, 60)
    assert result.status == "Failed"
    assert "outside" in result.filter_reason
