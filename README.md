# AI Micro-Influencer Outreach System

A submission-ready prototype for EDXSO AI Engineer Intern – Assignment 1.

The system implements the requested flow:

**Discovery → Data Collection → Filtering → Enrichment → AI Personalization → Review → Sending/Simulation → Tracking**

Initial implementation uses **YouTube + Python** for Technology-focused micro-influencer discovery. The design is adapter-based so another platform can be added later without changing the filtering, personalization, or tracking layers.

## Assignment coverage

| Requirement | Implementation |
|---|---|
| 50+ influencers | YouTube Data API discovery across multiple technology queries; continues until 50+ eligible micro-influencers are collected |
| Micro-influencer range | Default 5,000–100,000 followers/subscribers |
| Filtering | Niche, follower count, content relevance, engagement rate, geography when available |
| Pass/fail + reason | Deterministic scoring/filter engine writes `status` and `filter_reason` |
| Enrichment | Profile metrics, niche, themes, email from public channel description only, optional website/social links when present |
| Missing email | Explicitly recorded as `Not Found`; never guessed |
| Email pitch | LLM-generated, constrained to 60–90 words |
| Instagram DM | LLM-generated, constrained to 15–30 words; only simulated/manual delivery |
| Sending layer | SMTP sender + dry-run simulator |
| Duplicate prevention | SQLite uniqueness check before sending |
| Outreach log | SQLite + CSV export |
| Demo | Streamlit dashboard |
| Documentation | This README + architecture/prompt docs |

The assignment explicitly requires that unavailable contact information be marked `Not Found`, not generated or guessed. fileciteturn0file0L70-L74

## Architecture

```text
YouTube Data API
      │
      ▼
 DiscoveryAdapter
      │
      ▼
 Channel metadata + recent videos
      │
      ├── deterministic metrics (followers, engagement)
      ├── keyword classifier (niche/themes)
      └── public-email extraction from description
      │
      ▼
 Filtering / classification
      │
      ▼
 Shortlist CSV / JSON
      │
      ▼
 OpenAI Responses API
      │
      ▼
 Personalized email + DM
      │
      ▼
 Review / Streamlit
      │
      ├── dry-run sending
      └── SMTP sending
      │
      ▼
 SQLite outreach tracker
```

## Tech stack

- Python 3.11+
- YouTube Data API v3
- OpenAI Responses API (optional during local setup; required for LLM personalization path)
- SQLite (Python standard library)
- `requests`
- `pandas`
- `python-dotenv`
- `streamlit`
- `pytest`

YouTube's `search.list` endpoint supports channel searches with query terms and pagination; channel metadata/statistics are available through `channels.list`. The current YouTube API documentation notes that `search.list` has a 100-unit quota cost and `channels.list` has a 1-unit cost, so the code batches calls and keeps discovery query counts configurable. citeturn563967search0turn563967search1turn563967search4

OpenAI's current API documentation recommends the Responses API for new integrations; the older Assistants API was sunset on August 26, 2026. citeturn257376search0

## Project structure

```text
influencer-outreach-system/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── Makefile
├── app.py
├── run_pipeline.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── youtube_discovery.py
│   ├── filtering.py
│   ├── enrichment.py
│   ├── personalization.py
│   ├── outreach.py
│   └── pipeline.py
├── tests/
│   ├── test_filtering.py
│   └── test_personalization_validation.py
├── data/
│   └── .gitkeep
└── out/
    └── .gitkeep
```

## 1. Prerequisites

Install:

- Python 3.11 or newer
- A Google Cloud project with **YouTube Data API v3** enabled
- An OpenAI API key for real LLM message generation
- SMTP credentials only when you want real email sending

Do not commit secrets. The `.env` file is ignored by Git.

## 2. Create the project locally

```bash
git clone <YOUR_GITHUB_REPO_URL>
cd influencer-outreach-system
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 3. Configure API keys

Copy the example environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Fill in:

```env
YOUTUBE_API_KEY=your_youtube_data_api_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.6-luna

MIN_FOLLOWERS=5000
MAX_FOLLOWERS=100000
MIN_ENGAGEMENT_RATE=0.5
MIN_SCORE=60
DISCOVERY_TARGET=50
RECENT_VIDEO_COUNT=8

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_sender@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=your_sender@gmail.com
```

For Gmail SMTP, use an **App Password** rather than your normal account password when the account supports it.

## 4. Run the full discovery/enrichment pipeline

```bash
python run_pipeline.py --target 50
```

This generates:

```text
out/all_influencers.csv
out/shortlisted_influencers.csv
out/personalized_messages.csv
out/outreach_log.csv
out/outreach.db
```

The pipeline stores the retrieval timestamp and source URL for traceability.

### Useful options

```bash
python run_pipeline.py --target 50 --min-followers 5000 --max-followers 100000
python run_pipeline.py --target 75 --recent-videos 10
python run_pipeline.py --target 50 --skip-llm
```

`--skip-llm` is useful for validating discovery/filtering without spending LLM credits. It creates placeholder messages marked as requiring generation and should not be used as the final personalization submission.

## 5. Run the demo UI

```bash
streamlit run app.py
```

The dashboard lets you:

- inspect the discovered dataset
- see pass/fail reasons
- inspect shortlisted profiles
- review personalized email/DM text
- simulate outreach without sending anything
- view the outreach log

## 6. Sending layer

The assignment requires selecting only influencers with valid emails, retrieving the personalized email, recording status, preventing duplicates, and maintaining an outreach log. fileciteturn0file0L121-L128

### Safe default: simulation

The app and pipeline default to **dry-run**. It records what would be sent without sending an email.

### Real SMTP sending

To send a single approved email from the command line:

```bash
python run_pipeline.py --send --limit 1
```

Only records with a real email and no previous successful send are eligible. Duplicates are blocked by the SQLite tracker.

For Instagram DMs the project does **not** attempt to bypass Meta/Instagram restrictions. The assignment explicitly says to use a simulated/manual workflow when automated sending is not technically or legally available. fileciteturn0file0L129-L131

## 7. Personalization logic

Each influencer is given structured context:

- name / channel
- niche
- content themes
- channel description
- recent content titles
- subscriber count
- engagement rate
- audience geography when available
- proposed collaboration angle

The LLM is instructed to create two different messages for each qualified profile:

- email: 60–90 words
- Instagram DM: 15–30 words

The assignment requires messages to reference signals such as niche, style/recent content, relevant audience, collaboration, and value proposition rather than using a fixed generic template. fileciteturn0file0L76-L108

## 8. Data quality rules

The implementation intentionally avoids invented data:

1. If an email is not found in the public channel description, the value is `Not Found`.
2. Engagement rate is calculated from recent public video likes/comments and the API-reported subscriber count.
3. Audience age/gender are set to `Not Available` unless a future connector supplies documented audience analytics.
4. Geography is only populated when it is available from metadata/query context; otherwise `Not Available`.
5. The output contains `source` and `retrieved_at` fields.

The assignment explicitly warns against fabricated influencer information, guessed email addresses, or fake engagement metrics. fileciteturn0file0L242-L246

## 9. How the filtering works

A candidate must first be inside the configured micro-influencer range. The scoring model then checks:

- follower/subscriber range
- Technology relevance
- minimum engagement rate
- profile/content relevance
- optional geography match

Default scoring:

```text
Niche relevance       30 points
Follower fit          20 points
Engagement            20 points
Content relevance     20 points
Data completeness     10 points
--------------------------------
Total                 100 points
```

A candidate passes when the score is at least `MIN_SCORE` and the required hard filters are satisfied.

## 10. Running tests

```bash
pytest -q
```

The tests cover the filter decision logic and message-length validation.

## 11. GitHub submission steps

Create a new repository on GitHub, for example:

`ai-micro-influencer-outreach-system`

Then:

```bash
git init
git add .
git commit -m "Build AI micro-influencer outreach pipeline"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/ai-micro-influencer-outreach-system.git
git push -u origin main
```

Before pushing, verify:

```bash
git status
```

Make sure `.env` is **not** shown as a tracked file.

## 12. What to submit to EDXSO

Use the GitHub repository as the main submission. Include:

- working source code
- `README.md`
- generated `out/all_influencers.csv` (50+ real records)
- generated `out/shortlisted_influencers.csv`
- generated `out/personalized_messages.csv`
- generated `out/outreach_log.csv`
- screenshots or a short demo video of the Streamlit dashboard
- a brief note describing the test run date, query set, and API/tool usage

The assignment's submission list explicitly asks for the GitHub/project files, README, working demo/screenshots/video, influencer dataset, sample personalized messages, automation workflow when applicable, setup instructions, and APIs/tools used. fileciteturn0file0L231-L240

## Limitations

- YouTube search relevance is algorithmic, so discovery results can change over time.
- Subscriber counts are rounded by YouTube in the API response. citeturn563967search1
- Audience demographics such as age/gender are not available from the public Data API and therefore are not invented.
- Public email extraction is intentionally conservative.
- Instagram DM delivery is simulated/manual by design.
- Real email sending requires the user's own SMTP credentials and explicit execution of the send command.

## Suggested demo flow

1. Launch Streamlit.
2. Show a discovery run with 50+ candidates.
3. Filter to `Technology` and show pass/fail reasons.
4. Open a shortlisted profile and show the source metrics.
5. Show the generated 60–90 word email and 15–30 word DM.
6. Click/execute dry-run sending.
7. Show the SQLite/CSV outreach log and duplicate prevention.

This directly demonstrates the requested end-to-end workflow rather than a static presentation. fileciteturn0file0L155-L158
