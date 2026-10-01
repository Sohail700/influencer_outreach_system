# Assignment → Repository mapping

| Assignment requirement | Where to demonstrate it |
|---|---|
| Discover 50+ micro-influencers | `src/youtube_discovery.py`, `run_pipeline.py` |
| 5k–100k definition | `src/config.py`, `src/filtering.py` |
| Filter/classify | `src/filtering.py` |
| Pass/fail + why | `status`, `score`, `filter_reason` in CSV |
| Profile enrichment | `src/youtube_discovery.py`, `src/enrichment.py` |
| Email must be sourced / Not Found | `_extract_email()` in `src/youtube_discovery.py` |
| Email pitch 60–90 words | `src/personalization.py` |
| Instagram DM 15–30 words | `src/personalization.py` |
| Dynamic personalization | Recent titles/themes are included in the LLM prompt |
| Sending layer | `src/outreach.py` |
| Email only when valid | `contact_email != Not Found` gate |
| Prevent duplicates | SQLite `outreach_log.influencer_id` primary key + `already_sent()` |
| Outreach log | `out/outreach_log.csv` + `out/outreach.db` |
| Manual/simulated Instagram workflow | Streamlit notice + no Instagram API bypass |
| README documentation | `README.md` |
| Demo | `app.py`, `docs/DEMO_SCRIPT.md` |
| Engineering quality | modular `src/` package + tests + GitHub Actions |
| Scalability | API batching, adapters, CSV/SQLite storage, configurable target |
