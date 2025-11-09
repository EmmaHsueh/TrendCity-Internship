# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Taiwan Stock Exchange (TWSE) web scraping project focused on collecting institutional investor trading data (三大法人買賣超日報). The codebase implements three different approaches to fetch the same data from TWSE's T86 endpoint.

## Development Environment

**Virtual Environment Setup:**
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies for different approaches
pip install requests urllib3                        # For Method 1
pip install beautifulsoup4 lxml                     # Additional for Method 2
pip install selenium                                # Additional for Method 3 (not recommended)
```

## Three Crawler Approaches

### Method 1: JSON API (Recommended - twse_crawler.py)
- **Fastest and most stable**
- Uses TWSE's official JSON API endpoint
- Date format: `YYYYMMDD` (e.g., "20251023")
- Run: `python twse_crawler.py`
- Output: Terminal display only (no file saving by default)

### Method 2: HTML Parsing (twse_html_simple_crawler.py)
- **Best for structured output with headers**
- Requests HTML response and parses with BeautifulSoup
- Date format: `YYYYMMDD` (e.g., "20251023")
- Run: `python twse_html_simple_crawler.py`
- Output: Auto-saves to `twse_html_data_YYYYMMDD.json` with structured format:
  ```json
  {
    "params": {
      "query_date": "YYYYMMDD",
      "headers": [...]  // Extracted from <thead>
    },
    "data": [...]       // Extracted from <tbody>
  }
  ```

### Method 3: Selenium (twse_html_crawler.py)
- **Currently has technical issues** - cannot locate page elements
- Date format: `YYYY/MM/DD` (e.g., "2025/10/23")
- Not recommended for use

## API Details

**Endpoint:** `https://www.twse.com.tw/rwd/zh/fund/T86`

**Parameters:**
- `date`: YYYYMMDD format
- `selectType`: 'ALL' | 'ALLBUT0999' | 'STOCK' | 'ETF'
- `response`: 'json' | 'html'

**SSL Handling:** All scripts use `verify=False` to bypass SSL verification issues with TWSE's certificate.

## Data Structure

All methods fetch data with 19 fields:
1. 證券代號 (Security Code)
2. 證券名稱 (Security Name)
3-5. 外陸資 data (Foreign investors, excluding proprietary)
6-8. 外資自營商 data (Foreign proprietary)
9-11. 投信 data (Investment trust)
12-18. 自營商 data (Dealers - self-trading and hedging)
19. 三大法人買賣超股數 (Total institutional net buy/sell)

## Common Modifications

**Change query date:**
```python
# Methods 1 & 2
date = "20251023"  # YYYYMMDD

# Method 3
date = "2025/10/23"  # YYYY/MM/DD
```

**Adjust number of records:**
```python
# Current: returns first 10 records
records = data['data'][:10]

# Get all records
records = data['data'][:]
```

**Change query type:**
```python
params = {
    'date': date_str,
    'selectType': 'ALLBUT0999',  # Exclude warrants
    'response': 'json'
}
```

## Important Notes

- **Date Constraint:** TWSE data only available from 2012/05/02 (民國101年5月2日) onwards
- **Trading Days Only:** Queries return data only for business days
- **Rate Limiting:** Avoid excessive requests to TWSE servers (add `time.sleep(3)` between batch requests)
- **ROC Calendar:** The TWSE system uses ROC (Republic of China) calendar dates internally; year 114 = 2025 AD

## Documentation Files

- `api_crawler_README.md` - Method 1 (JSON API) detailed guide
- `t86_README.md` - Comprehensive comparison of all three methods
- Both READMEs contain extensive examples for MongoDB integration, batch queries, and pandas analysis
