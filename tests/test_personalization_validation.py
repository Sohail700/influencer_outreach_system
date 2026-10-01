import pytest

from src.models import PersonalizedMessage
from src.personalization import validate_message


def test_invalid_email_length_is_rejected():
    msg = PersonalizedMessage(
        influencer_id="1",
        influencer_name="Creator",
        email="creator@example.com",
        email_subject="Collaboration",
        email_pitch="too short",
        instagram_dm="hello this is also too short",
        generated_at="now",
    )
    with pytest.raises(ValueError):
        validate_message(msg)
