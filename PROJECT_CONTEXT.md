# MDPI Campaign Automator - Project Context

## 🎯 Project Goal
Automate the monthly mass mailing data collection from the MDPI journal database. The system searches for specific keywords, filters by the last 3 years, downloads the results (200 items/page, tab-delimited), and formats the data for a mail merge campaign.

## 🛠️ Tech Stack
* **GUI / Frontend:** `Streamlit` (Web-based Python UI at http://localhost:8501)
* **Web Automation:** `Playwright` (Visible Chromium browser for login and downloading)
* **Data Processing:** `Pandas` (Data cleaning and formatting into Excel)

## 📝 Changelog & Progress

### Accomplishments and validation status
- The Streamlit GUI, persistent visible Playwright browser, direct MDPI authentication entry point, keyword/year/page-size/export workflow, and two-sheet Excel transformation are implemented.
- Login may redirect to a SUSY profile or manuscript page. The current workflow waits for an automatic return to MDPI and falls back to MDPI home in the same browser session if needed.
- The current post-login home/search readiness helper includes a diagnostic error with URL and title if `#q` is not available.
- The workflow waits for results to load, attempts progressive scrolling when fewer selectable rows are present than expected, and verifies selection count before export.
- Each export is parsed as tab-delimited data and its temporary download path is deleted after parsing. The final workbook is retained.
- Local Python compilation and focused unit-style checks have passed for the updated code; Streamlit was verified responding with HTTP 200.
- Earlier public-results testing verified the legacy export controls and a 200-row Tab-delimited download. This did not validate authenticated email availability.
- See [PROJECT_GOALS.md](./PROJECT_GOALS.md) for the overall goal, implemented scope, verified behavior, and outstanding work.

### Phase 0 – Project initialized
- Created project folder and basic file structure.

### Phase 1 (GUI) – ✅ COMPLETED
- Built a modern Streamlit web interface with inputs for credentials, date filters, and keywords.
- Added progress status bars and download button for the final Excel file.

### Phase 2 (Web Scraping & Data Processing) – 🔄 IN PROGRESS
- **scraper.py** uses the direct MDPI auth page and its verified `#username`, `#password`, and **Continue** controls.
- The Streamlit GUI owns one visible Playwright browser per GUI session. It stays open after automation finishes or errors so its authentication cookies remain available for the next run.
- The automation uses a visible browser, deliberate waits after major page changes, and checks that year range, page size, and article selections have taken effect before exporting. These waits are for page readiness and user-requested pacing, not stealth or anti-bot evasion.
- Flow: Navigate directly to `https://auth.mdpi.com/login` → fill GUI credentials → wait for the login transition (which can land on SUSY) → allow the SUSY landing page to return to MDPI home, opening MDPI home in the same browser session if it remains on SUSY → wait for and verify the home-page Title / Keyword search field → search each GUI keyword through that visible search box → detect the active MDPI results version → use the legacy export view where required → set the year range and 200 results/page → wait for each update and verify it → load and verify every selectable result → select all → export Tab-delimited → process every page.
- When MDPI serves the new results UI, the scraper uses its “old version” switch in the same tab for the verified Tab-delimited export workflow; it does not close and relaunch the browser between keywords or pages.
- Searches are paginated independently per keyword. The Excel output contains all downloaded export columns in **Raw Data** and one row per author/email match in **final sheet** when an authorized email source is available.
- Papers are deduplicated by DOI, falling back to normalized title. Authors without an email at the corresponding position are omitted from the clean sheet.
- **Authentication check:** MDPI may successfully redirect the user to the SUSY manuscript upload page after sign-in. The scraper accepts the redirect away from MDPI's auth/login hosts and no longer treats a generic “Sign In / Sign Up” header link as proof of logout; it stops only if navigation returns to an auth host or the credential form is visible. The browser is retained for inspection on errors.
- **Email verification pending:** An unauthenticated 200-record Tab-delimited test returned `AUTHOR`, `TITLE`, `JOURNAL`, `LANGUANGE`, `DOCTYPE`, `KEYWORDS`, `ABSTRACT`, `AFFILIATION`, `DOI`, `PUBYEAR`, `PUBVOL`, `PUBISSUE`, `FPAGE`, `LPAGE`, `ARTNUMBER`, and `PAGENUM`, with no email column. A signed-in export still needs validation.
- **Export file handling:** Each downloaded TSV is parsed from Playwright's temporary download path and deleted immediately after a successful or failed parse. The generated Excel workbook is retained.
- **Live workflow verification:** Previously verified on the public results view: legacy export controls, the 2024–2026 filter, 200-results/page, Select all, Tab-delimited, and a 200-row TSV download. This did not verify authenticated author-email availability.
- Output: Single Excel file with **Sheet 1 = "Raw Data"** and **Sheet 2 = "final sheet"**.
- Browser runs in **visible mode** (`headless=False`) so the operator can observe and inspect login and search actions.

### Bug Fixes Applied
1. **Visible browser:** Use a visible Chromium browser for the user-operated sign-in and campaign workflow.
2. **Login flow fix:** Open the MDPI authentication page directly instead of relying on a "Sign In" link on the main site.
3. **IndentationError fix:** The `try/except/finally` blocks had broken indentation from incremental edits. Entire `scraper.py` was rewritten cleanly from scratch.
4. **SyntaxError fix:** A duplicate `except` block on line 84 was left over from a bad merge. Removed in the clean rewrite.
5. **Sign-in link timeout:** Navigate directly to `https://auth.mdpi.com/login` and wait for visible credential fields instead of searching for an exact "Sign In" text match on the home page.
6. **Auth form selectors:** Use the login page's observed `#username` and `#password` fields and its **Continue** button; report the direct-login step in the UI so the active flow is easy to verify.
7. **Search results timeout:** MDPI's refreshed search UI changed its result markup. The scraper now switches to the legacy results view, which supports year query parameters and the export flow.
8. **Search and export controls:** Verified legacy MDPI search accepts `page_count=200`, “Select all” selects the current page, and the export format control offers `Tab-delimited`.
9. **Session persistence:** The visible MDPI browser is retained in Streamlit session state and is not closed by the campaign code.

## 📌 Current Next Steps
1. Run the campaign using credentials, keywords, and years entered in the GUI.
2. Verify whether the signed-in Tab-delimited export includes author email fields.
3. Review the workbook, especially papers with missing or non-aligned author/email entries.
4. Confirm the live authenticated GUI flow end-to-end; UI selectors can vary when MDPI changes its results page.

## 📂 File Structure
```
mdpi_campaign_automator/
├── streamlit_app.py        # Streamlit Web UI (run with: streamlit run streamlit_app.py)
├── scraper.py              # Playwright automation + Pandas data processing
├── requirements.txt        # Python dependencies
├── PROJECT_CONTEXT.md      # This file (project tracker)
├── PROJECT_GOALS.md        # Project goal, accomplishments, and remaining verification
└── Campaign_Results.xlsx   # Generated output (after running the campaign)
```

---
*This file is updated after every major change so we can easily pick up where we left off.*
