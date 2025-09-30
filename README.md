# JobScout: Multi‑Platform Job Scraper

A simple, scriptable job search assistant that scrapes multiple platforms (Internshala, Y Combinator – Work at a Startup, Naukri, LinkedIn) for roles and locations you specify, then exports everything to a CSV.

---

## What it does
- **Scrapes multiple job boards** in one run
- **Headless browser automation** via Selenium + Chrome
- **Flexible search** by role and location
- **CSV export** with platform, title, company, location, apply link, date

---

## Prerequisites
- **Google Chrome** installed
- **Python 3.9+** installed
- **ChromeDriver** matching your Chrome version

If you don’t have Python or Chrome yet, follow the OS-specific setup below.

---

## Quick start
1) Clone or download this project.
2) Install Python and dependencies.
3) Download ChromeDriver and place it next to `app.py`.
4) Run the script and follow the prompts.

---

## Setup on Windows

### 1. Install Python
- Download Python from the official site: `https://www.python.org/downloads/`
- During installation, check **“Add Python to PATH”**.
- Verify:
  ```bash
  python --version
  pip --version
  ```

### 2. Install Google Chrome
- Get Chrome: `https://www.google.com/chrome/`

### 3. Install dependencies
From the project folder (where `requirements.txt` is located):
```bash
pip install -r requirements.txt
```

### 4. Install ChromeDriver
- Check your Chrome version: in Chrome go to `chrome://settings/help`.
- Download the matching ChromeDriver:
  - Latest stable (official): [`https://googlechromelabs.github.io/chrome-for-testing/`](https://googlechromelabs.github.io/chrome-for-testing/)
  - Legacy archive (if needed): [`https://chromedriver.chromium.org/downloads`](https://chromedriver.chromium.org/downloads)
- Unzip and place the ChromeDriver executable as `chromedriver.exe` in the project root:
  - Folder: `h:\pro\job scrapper\`
  - File must be named: `chromedriver.exe`

> The script first tries `./chromedriver.exe` (Windows) and then `./chromedriver` (macOS/Linux). Keeping it in the project root avoids PATH issues.

---

## Setup on macOS

### 1. Install Python
- Recommended via Homebrew:
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  brew install python
  ```
- Or download from Python.org: `https://www.python.org/downloads/`
- Verify:
  ```bash
  python3 --version
  pip3 --version
  ```

### 2. Install Google Chrome
- Download: `https://www.google.com/chrome/`

### 3. Install dependencies
From the project folder:
```bash
pip3 install -r requirements.txt
```

### 4. Install ChromeDriver
- Check your Chrome version: Chrome > About Google Chrome.
- Download ChromeDriver matching your version:
  - Latest stable (official): [`https://googlechromelabs.github.io/chrome-for-testing/`](https://googlechromelabs.github.io/chrome-for-testing/)
  - Legacy archive (if needed): [`https://chromedriver.chromium.org/downloads`](https://chromedriver.chromium.org/downloads)
- Extract and place the driver in the project root and name it `chromedriver` (no extension):
  - Folder: `.../job scrapper/`
  - File must be named: `chromedriver`
- Make it executable:
  ```bash
  chmod +x ./chromedriver
  ```

> The script automatically picks `./chromedriver` on macOS/Linux.

---

## How to run
From the project directory:
```bash
# Windows
python app.py

# macOS
python3 app.py
```
Follow the prompts, e.g.:
- Role: `Python Developer`
- Location: `Mumbai` (or `Remote`)

The script will open a headless Chrome, scrape Internshala, Y Combinator, Naukri, and LinkedIn, then save a CSV like:
`jobs_Python_Developer_Mumbai_20250101.csv`

---

## Output
- CSV file with columns: `Platform, Job Title, Company, Location, Apply Link, Scraped Date`
- A quick summary of how many jobs were found per platform in the console

---

## Troubleshooting
- "Error initializing WebDriver":
  - Ensure Chrome is installed and ChromeDriver version matches Chrome
  - Ensure `chromedriver.exe` (Windows) / `chromedriver` (macOS) is in the project root
  - On macOS, run `chmod +x ./chromedriver`
- "No jobs found to save": Try broader keywords or different location
- Sites change their HTML often; occasional misses are normal
- LinkedIn has strict anti-scraping measures, results may be limited

---

## Notes
- The script runs Chrome in **headless** mode by default
- It uses multiple selectors per site to handle minor HTML changes
- For best results, keep Chrome and ChromeDriver up to date
