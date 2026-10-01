# 2–3 minute demo script

## 1. Explain the goal (15 seconds)

“This system discovers technology micro-influencers on YouTube, filters them using measurable criteria, enriches their records from public metadata, uses an LLM to personalize an email and Instagram DM, then simulates or sends email outreach while preventing duplicates.”

## 2. Show discovery (30 seconds)

Open the Streamlit dashboard and point out:

- 50+ discovered creators
- YouTube profile URLs
- subscriber counts
- recent-content signals
- retrieval timestamp/source

## 3. Show filtering (30 seconds)

Open `all_influencers.csv` and demonstrate that every row has:

- `status`
- `score`
- `filter_reason`
- `engagement_rate`

Explain that the hard micro-influencer range is 5,000–100,000 subscribers and the system never hides why a creator failed.

## 4. Show enrichment (20 seconds)

Select a creator with a public email and another without one. Explain that the second record says `Not Found`; the system never guesses an email address.

## 5. Show personalization (30 seconds)

Open the Message Review section and show both:

- 60–90 word email
- 15–30 word Instagram DM

Point out the recent-video/content-theme references.

## 6. Show outreach safety (20 seconds)

Run the dry-run. Show `out/outreach_log.csv` and explain that duplicate successful sends are blocked by a SQLite primary key check.

## 7. Close (15 seconds)

“The architecture is modular: discovery, enrichment, filtering, personalization, sending, and tracking are separate components, so the same system can be extended from 50 to 500+ creators or another social platform.”
