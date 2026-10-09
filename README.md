# MDPI Campaign Automator 🚀

An end-to-end automated tool designed for harvesting, filtering, and structuring author leads from MDPI research publications for targeted monthly mass-mailing campaigns.

Built with **Python**, **Streamlit**, and **Playwright**.

---

## 🌟 Key Features

- **Automated MDPI Authentication**: Log in seamlessly to your MDPI/SUSY account.
- **Multi-Keyword Search**: Automatically search multiple related keywords across a custom multi-year range (e.g., last 3 years: 2024–2026).
- **A/B Test & Legacy View Bypass**: Detects MDPI's new web interface and automatically switches to the legacy layout to ensure full export option availability.
- **Bulk TSV Download & Page Traversal**: Requests maximum density (200 articles per page) and iterates through all available result pages automatically.
- **Anti-Bot Human Jitter & Stealth**:
  - Randomized interaction delays (`_human_delay`) mimicking realistic human mouse movement and typing.
  - Realistic scroll behavior to trigger lazy-loaded elements.
  - Chrome user-agent spoofing.
- **Intelligent Data Cleaning Pipeline**:
  - Replaces manual Word macro workflows natively in Pandas.
  - Reorders final output columns strictly to `Email` (Col A), `Author` (Col B), `Title` (Col C).
  - Deduplicates author entries strictly by `Email`.
  - Removes generic consumer emails (e.g., `@gmail.com`).
  - Removes numeric-prefixed emails (e.g., `123john@...`).
  - Removes low-income/specific country TLDs (`.in`, `.pk`, `.ir`, `.iq`, `.et`, `.bd`, `.ng`, `.tw`).
  - Applies character length validation on both **Emails** and **Author Names** (retains only length between 5 and 39 characters).
  - Sorts final results alphabetically (A → Z) by Email.
- **Dynamic File Naming**: Saves outputs with timestamped names (e.g., `endoscope_2026-10-09_15-30-00.xlsx`) containing both **Raw Data** and **Final Cleaned Sheet** to prevent file locking and permission errors.

---

## 🛠️ Project Structure

```text
mdpi_campaign_automator/
│
├── app.py                # Main Streamlit web application interface
├── scraper.py            # Playwright browser automation & Pandas cleaning pipeline
├── requirements.txt      # Required Python dependencies
├── README.md             # Project documentation
└── .gitignore            # Excludes outputs, cache, and sensitive data
```

---

## ⚡ Quick Start

### 1. Prerequisites
Make sure you have Python 3.9+ installed on your system.

### 2. Installation
Clone the repository and install the dependencies:

```bash
git clone https://github.com/abhilashshiva/mdpi-campaign-automator.git
cd mdpi-campaign-automator

# Install Python requirements
pip install -r requirements.txt

# Install Playwright Chromium browser binaries
playwright install chromium
```

### 3. Running the App
Launch the Streamlit web dashboard:

```bash
streamlit run app.py
```

Open the local URL provided by Streamlit (usually `http://localhost:8501`), enter your MDPI credentials, keywords, and year ranges, and click **Start Campaign**.

---

## 📊 Data Hygiene & Cleaning Rules

The automated data processing pipeline enforces the following rules on the generated Excel spreadsheet:

| Rule | Description |
| :--- | :--- |
| **Column Ordering** | Column A: `Email`, Column B: `Author`, Column C: `Title` |
| **Deduplication** | De-duplicates strictly on the `Email` column |
| **Gmail Exclusion** | Filters out any email addresses ending in `@gmail.com` |
| **Numeric Filter** | Filters out emails starting with numbers (0–9) |
| **TLD Exclusion** | Filters out `.in`, `.pk`, `.ir`, `.iq`, `.et`, `.bd`, `.ng`, `.tw` |
| **Length Filter** | Removes Email & Author entries with length `< 5` or `>= 40` characters |
| **Alphabetical Sort** | Sorts the entire clean dataset A → Z by Email address |

---

## 📄 Output Excel File Format

Each generated Excel workbook includes two sheets:
1. **`Raw Data`**: Complete unmodified export from MDPI.
2. **`final sheet`**: Fully cleaned, filtered, de-duplicated, and sorted author lead list ready for immediate mass mailing.

---

## 🛡️ License

This project is intended for internal campaign automation and research lead collection.
