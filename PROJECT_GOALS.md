# MDPI Campaign Automator: Goals and Accomplishments

## Project goal

Provide a GUI-driven workflow for preparing an MDPI journal outreach list:

1. Let the operator enter MDPI credentials, one or more article-search keywords, and a year range in the Streamlit GUI.
2. Open MDPI's direct login page, sign in using the entered credentials, and retain the same visible browser session.
3. Search each keyword through MDPI's own search interface, apply the requested years, select 200 results per page, and export each results page as Tab-delimited data.
4. Process the downloaded data into an Excel workbook with:
   - **Raw Data**: downloaded article/export fields.
   - **final sheet**: one row per author with a corresponding email and paper title.
5. Deduplicate papers by DOI, falling back to normalized title, and omit author entries without a corresponding email.
6. Keep the workflow observable and human-paced: wait for pages and UI changes to settle, verify key selections before export, keep the browser available for inspection, and remove temporary TSV files after processing.

## Accomplishments to date

### Implemented

- Created a Streamlit GUI with inputs for login credentials, start/end years, and newline-separated keywords.
- Added progress reporting and a download control for the generated Excel workbook.
- Implemented a visible Playwright browser session retained by the Streamlit session so the browser is not closed after a campaign error or completion.
- Added direct navigation to `https://auth.mdpi.com/login` and the observed `#username`, `#password`, and **Continue** login controls.
- Added a post-login transition that handles the SUSY profile/manuscript landing page: wait briefly for an automatic return to MDPI, then open MDPI home in the same browser session if it remains on SUSY.
- Added a check for MDPI's home-page `#q` keyword field, with a useful diagnostic error containing the current URL and page title if the search form does not appear.
- Implemented GUI-keyword search, old/new search-results view handling, requested year filtering, 200-results-per-page selection, pagination, Tab-delimited export, and waits around major page updates.
- Added checks to wait for selectable result rows and verify the selected count before exporting, to avoid knowingly exporting an incomplete page.
- Implemented paper deduplication and author/email row shaping for the two-sheet workbook.
- Added temporary export parsing and cleanup so the intermediate TSV is not retained after processing.

### Verified

- Python compilation has passed after the recent workflow changes.
- Editor diagnostics reported no issues in `scraper.py` or `streamlit_app.py` at the last check.
- A focused test passed for the SUSY-to-MDPI-home fallback.
- A focused data transformation check passed for deduplication and one-row-per-author/email output.
- The Streamlit app has been started locally and returned HTTP 200 at `http://127.0.0.1:8501`.
- The public/unauthenticated legacy-results interface was previously exercised: year filtering, 200/page, select-all, Tab-delimited selection, and a 200-row export were observed.

## Not yet verified / remaining work

- A complete authenticated campaign has not yet been confirmed end-to-end using the current GUI flow.
- It is not yet confirmed that an authenticated Tab-delimited MDPI export contains author email addresses. The public test export did not include an email field. The app should report the missing column rather than infer addresses.
- MDPI can change its login redirects, search markup, export controls, and result-loading behavior; live validation is still required after the operator retries the GUI workflow.
- Review the resulting workbook for author/email alignment and confirm it meets the operator's intended outreach format.

## Data and credential handling notes

- Credentials are entered in the GUI at run time and are not included in this document or intended to be hard-coded into source files.
- The campaign only produces a workbook from fields actually present in the export; it must not fabricate or infer missing contact details.
- Temporary TSV files are intended to be deleted after parsing. The final workbook is retained for the operator to download.
