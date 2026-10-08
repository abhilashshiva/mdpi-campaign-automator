import re
import time
from datetime import date
from pathlib import Path
import urllib.parse

import pandas as pd
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

EMAIL_PATTERN = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
PAGE_SETTLE_MS = 3000

class MDPIBrowserSession:
    def __init__(self):
        self._playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def get_page(self):
        if self.browser is not None and self.browser.is_connected():
            if self.page is None or self.page.is_closed():
                self.page = self.context.new_page()
            return self.page

        self._playwright = sync_playwright().start()
        self.browser = self._playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context(
            accept_downloads=True,
            viewport={"width": 1440, "height": 1000},
        )
        self.context.set_default_navigation_timeout(45000)
        self.page = self.context.new_page()
        return self.page

def _progress(progress_callback, message):
    if progress_callback:
        progress_callback(message)

def _normalized_title(value):
    return re.sub(r"\W+", " ", str(value).casefold()).strip()

def _normalized_doi(value):
    doi = str(value).strip().casefold()
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    return doi.rstrip(".,; ")

def _build_campaign_dataframes(dataframes):
    raw_df = pd.concat(dataframes, ignore_index=True).fillna("")
    
    # Find exact columns
    title_col = next((col for col in raw_df.columns if "title" in str(col).casefold()), None)
    author_col = next((col for col in raw_df.columns if "author" in str(col).casefold() and "email" not in str(col).casefold()), None)
    email_col = next((col for col in raw_df.columns if "email" in str(col).casefold()), None)
    doi_col = next((col for col in raw_df.columns if "doi" in str(col).casefold()), None)

    if email_col is None:
        raise ValueError("The MDPI export does not contain an author email column! Please make sure the session is signed in properly.")
    if title_col is None or author_col is None:
        raise ValueError("Missing Title or Author column in the export.")

    # Deduplicate raw rows by DOI or Title
    dedupe_keys = []
    for index, row in raw_df.iterrows():
        doi = _normalized_doi(row[doi_col]) if doi_col is not None else ""
        title = _normalized_title(row[title_col])
        dedupe_keys.append(("doi", doi) if doi else (("title", title) if title else ("row", index)))
    raw_df = raw_df.loc[~pd.Series(dedupe_keys).duplicated().to_numpy()].reset_index(drop=True)

    # Clean rows matching user's manual Word macro
    clean_rows = []
    seen_author_rows = set()
    for _, row in raw_df.iterrows():
        title = str(row[title_col]).strip()
        # Split authors by ';' and remove commas, matching the Word Ctrl+H workflow
        authors = [
            author.strip().replace(",", "")
            for author in str(row[author_col]).split(";")
            if author.strip()
        ]
        emails = EMAIL_PATTERN.findall(str(row[email_col]))

        # Pair each author with their email
        for author, email in zip(authors, emails):
            dedupe_value = (_normalized_doi(row[doi_col]) if doi_col is not None else "") or _normalized_title(title)
            clean_key = (dedupe_value, author.casefold(), email.casefold())
            if clean_key in seen_author_rows:
                continue
            seen_author_rows.add(clean_key)
            clean_rows.append({"Title": title, "Author": author, "Email": email})

    return raw_df, pd.DataFrame(clean_rows, columns=["Title", "Author", "Email"])


def _ensure_legacy_view(page):
    # Attempt to click anything that says 'old version' to force the legacy view
    page.evaluate("""() => {
        let links = Array.from(document.querySelectorAll('a, button'));
        let directLink = links.find(el => el.textContent && el.textContent.toLowerCase().includes('old version'));
        if (directLink) { directLink.click(); return; }
        
        let containers = Array.from(document.querySelectorAll('div, p, span, section'));
        // Find the most specific container that has the text
        let validContainers = containers.filter(el => el.textContent && el.textContent.toLowerCase().includes('access the old version'));
        if (validContainers.length > 0) {
            // Sort by text length to find the innermost container
            validContainers.sort((a, b) => a.textContent.length - b.textContent.length);
            let a = validContainers[0].querySelector('a');
            if (a) { a.click(); return; }
        }
        
        let returnOldBtn = document.querySelector('button[data-track-id="return-old"]');
        if (returnOldBtn) { returnOldBtn.click(); return; }
    }""")

def run_mdpi_campaign(
    email,
    password,
    start_year,
    end_year,
    keywords,
    progress_callback=None,
    browser_session=None,
):
    today = date.today()
    if end_year > today.year:
        raise ValueError(f"The end year {end_year} is in the future. Choose {today.year} or earlier.")
    if start_year > end_year:
        raise ValueError("The start year must be earlier than or equal to the end year.")

    all_dataframes = []
    session = browser_session or MDPIBrowserSession()
    page = session.get_page()

    _progress(progress_callback, "Opening MDPI login page: https://auth.mdpi.com/login")
    page.goto("https://auth.mdpi.com/login", wait_until="domcontentloaded")
    
    # Check if login form is present
    if page.locator("#username").count() > 0:
        _progress(progress_callback, "Filling credentials...")
        page.locator("#username").fill(email)
        time.sleep(0.5)
        page.locator("#password").fill(password)
        time.sleep(0.5)
        page.get_by_role("button", name="Continue").click()
        
        try:
            page.wait_for_url(lambda u: "auth.mdpi.com/login" not in str(u), timeout=30000)
            _progress(progress_callback, f"Login successful, landed on: {page.url}")
        except PlaywrightTimeoutError:
            raise RuntimeError("Login timed out. Check the browser window.")
            
    time.sleep(PAGE_SETTLE_MS / 1000)

    for keyword in keywords:
        # Step 1: Visit generic search page to force the old version cookie
        encoded_kw = urllib.parse.quote_plus(keyword)
        _progress(progress_callback, f"Initiating search for '{keyword}'...")
        page.goto(f"https://www.mdpi.com/search?q={encoded_kw}", wait_until="domcontentloaded")
        
        try:
            page.wait_for_function("""() => document.querySelectorAll('.article-item').length > 0 || Array.from(document.querySelectorAll('a, button, span')).some(el => el.textContent && el.textContent.toLowerCase().includes('old version'))""", timeout=15000)
        except Exception:
            pass

        filtered_url = f"https://www.mdpi.com/search?q={encoded_kw}&year_from={start_year}&year_to={end_year}&page_count=200&sort=pubdate&page_no=1"
        _progress(progress_callback, f"Applying filters via direct URL: {start_year}-{end_year}, 200 items/page...")
        page.goto(filtered_url, wait_until="domcontentloaded")
        
        _ensure_legacy_view(page)
        
        try:
            page.locator(".article-item").first.wait_for(state="visible", timeout=20000)
        except PlaywrightTimeoutError:
            if "Search Results (0)" in page.locator("body").inner_text():
                _progress(progress_callback, f"No results found for '{keyword}'.")
                continue
            raise RuntimeError(f"Failed to load legacy search results for '{keyword}'.")

        # Step 3: Find out how many pages there are
        hrefs = page.locator('#exportArticles .pages a[href*="page_no="]').evaluate_all("(links) => links.map((l) => l.href)")
        page_numbers = [int(m.group(1)) for h in hrefs if (m := re.search(r"[?&]page_no=(\d+)", h))]
        page_count = max(page_numbers, default=1)
        _progress(progress_callback, f"Found {page_count} pages of results for '{keyword}'.")

        for p in range(1, page_count + 1):
            page_url = f"https://www.mdpi.com/search?q={encoded_kw}&year_from={start_year}&year_to={end_year}&page_count=200&sort=pubdate&page_no={p}"
            if p > 1:
                _progress(progress_callback, f"Loading page {p}...")
                page.goto(page_url, wait_until="domcontentloaded")
                _ensure_legacy_view(page)
                page.locator(".article-item").first.wait_for(state="visible", timeout=20000)

            # Extra safety check: click Sign In if it appears
            sign_in_link = page.locator("a", has_text=re.compile(r"^\s*Sign In\s*$", re.IGNORECASE))
            if sign_in_link.count() and sign_in_link.first.is_visible():
                _progress(progress_callback, "Clicking 'Sign In' to authorize export...")
                sign_in_link.first.click(force=True)
                time.sleep(3)
                
                # If it asks for credentials again
                if page.locator("#username").count() > 0 and page.locator("#username").first.is_visible():
                    _progress(progress_callback, "MDPI requested credentials again. Re-authenticating...")
                    page.locator("#username").fill(email)
                    time.sleep(0.5)
                    page.locator("#password").fill(password)
                    time.sleep(0.5)
                    page.get_by_role("button", name="Continue").click()
                    try:
                        page.wait_for_url(lambda u: "auth.mdpi.com/login" not in str(u), timeout=30000)
                    except PlaywrightTimeoutError:
                        pass
                
                page.goto(page_url, wait_until="domcontentloaded")
                page.locator(".article-item").first.wait_for(state="visible", timeout=20000)

            # Scroll to load all articles
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

            _progress(progress_callback, f"Exporting page {p}/{page_count} to tab-delimited format...")
            
            # First, expand the export options dropdown
            if page.locator('a.export-options-show').count() > 0:
                page.locator('a.export-options-show').first.click(force=True)
            time.sleep(1)
            
            # Check 'Select All'
            if page.locator('#selectUnselectAll').count() > 0:
                page.locator('#selectUnselectAll').first.check(force=True)
            time.sleep(1)
            
            # Set format to Tab-delimited using the Chosen UI
            format_dropdown = page.locator("select[name='format_top'] + .chosen-container").first
            if format_dropdown.count() > 0:
                format_dropdown.locator("a.chosen-single").first.click(force=True)
                time.sleep(1)
                format_dropdown.locator(".chosen-results li", has_text=re.compile(r"^\s*Tab-delimited\s*$")).first.click(force=True)
                time.sleep(1)

            with page.expect_download(timeout=30000) as dl_info:
                page.locator('#articleBrowserExport_top').first.click(force=True)
            
            dl = dl_info.value
            dl_path = Path(dl.path())
            try:
                df = pd.read_csv(dl_path, sep="\t", dtype=str, keep_default_na=False, encoding="utf-8-sig")
                all_dataframes.append(df)
            except Exception as e:
                raise RuntimeError(f"Could not read the downloaded TSV for '{keyword}', page {p}.") from e
            finally:
                if dl_path.exists():
                    dl_path.unlink()

            _progress(progress_callback, f"Successfully downloaded and read {len(df)} records from page {p}.")

    if not all_dataframes:
        raise ValueError("No data was downloaded for any keywords.")

    _progress(progress_callback, "Processing data and applying Word macro rules (splitting semicolons, removing commas)...")
    raw_df, final_df = _build_campaign_dataframes(all_dataframes)
    
    if final_df.empty:
        raise ValueError("MDPI exports were downloaded, but no author rows had a matched email address. Ensure you are signed in.")

    output_filename = "Campaign_Results.xlsx"
    _progress(progress_callback, f"Saving {len(raw_df)} raw papers and {len(final_df)} clean author entries to {output_filename}...")
    
    with pd.ExcelWriter(output_filename, engine="openpyxl") as writer:
        raw_df.to_excel(writer, sheet_name="Raw Data", index=False)
        final_df.to_excel(writer, sheet_name="final sheet", index=False)

    return output_filename
