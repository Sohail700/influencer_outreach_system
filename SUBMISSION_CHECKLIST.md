# EDXSO Assignment 1 — Submission Checklist

Before submitting, make sure these are true:

- [ ] `python run_pipeline.py --target 50` completed successfully.
- [ ] `out/all_influencers.csv` contains at least 50 real discovered influencers.
- [ ] No guessed/fabricated emails or engagement rates.
- [ ] `Not Found` is used for unavailable email addresses.
- [ ] `out/shortlisted_influencers.csv` contains passed creators with reasons/scores.
- [ ] `out/personalized_messages.csv` contains email + Instagram DM for shortlisted creators.
- [ ] Email pitches are 60–90 words.
- [ ] Instagram DMs are 15–30 words.
- [ ] `out/outreach_log.csv` demonstrates dry-run/sent status and duplicate prevention.
- [ ] Streamlit dashboard was opened and tested.
- [ ] At least 3 screenshots or a short 2–3 minute screen recording was captured.
- [ ] `.env` is not committed.
- [ ] `pytest -q` passes.
- [ ] GitHub README explains stack, APIs/tools, data source, methodology, filtering, enrichment, AI prompt, personalization, sending, limitations, and setup.

## Recommended final repository contents

```text
README.md
SUBMISSION_CHECKLIST.md
requirements.txt
.env.example
run_pipeline.py
app.py
src/
tests/
docs/DEMO_SCRIPT.md
out/all_influencers.csv
out/shortlisted_influencers.csv
out/personalized_messages.csv
out/outreach_log.csv
.github/workflows/test.yml
```
