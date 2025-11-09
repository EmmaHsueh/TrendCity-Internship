# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

TWSE Crawler is a Python CLI tool that fetches institutional investor trading data from Taiwan Stock Exchange (TWSE) and stores it in MongoDB. It retrieves two types of reports: T86 (daily net buy/sell by institution) and BFI82U (daily trading amount statistics).

## Running Commands

### CLI Usage
The module is run as a Python package with subcommands:

```bash
# Fetch single date
python -m . t86 --date 2024-01-15
python -m . bfi82u --date 2024-01-15
python -m . both --date 2024-01-15

# Fetch date range
python -m . t86 --start 2024-01-01 --end 2024-01-31 --sleep 0.6
python -m . both --start 2024-01-01 --end 2024-01-31 --sleep 1.0
```

Parameters:
- `--date`: Single date in YYYY-MM-DD format
- `--start` / `--end`: Date range (both required)
- `--sleep`: Delay between requests in seconds (default: 0.6)

### Configuration
Set environment variables or create `.env`:
- `MONGODB_URI`: MongoDB connection string (default: `mongodb://localhost:27017/`)
- `MONGODB_DB`: Database name (default: `twse`)

## Architecture

### Data Flow
```
CLI Entry (__main__.py)
    ↓
API Client (twse_api.py) → Fetch JSON from TWSE endpoints
    ↓
Database Layer (db.py) → Upsert to MongoDB with unique indexes
```

### Module Structure

**__main__.py** - CLI entry point
- Parses subcommands (t86/bfi82u/both) and date arguments
- Calls `ensure_indexes()` on startup to create unique indexes
- For date ranges, iterates through dates with configurable sleep between requests
- Entry function: `run_one(date, want_t86, want_bfi82u)` orchestrates fetch and upsert

**twse_api.py** - TWSE API client
- `fetch_t86(date)`: Fetches T86 report (daily net buy/sell per stock)
  - Returns list of dicts, one per stock with standardized fields: `date`, `stock_code`, `stock_name`
  - Preserves official Chinese field names with comma-separated strings
- `fetch_bfi82u(date)`: Fetches BFI82U report (daily trading amount aggregates)
  - Returns single dict with structure: `{date, fields, rows}`
- Both functions return empty/None on holidays or non-trading days
- Implements retry logic (3 attempts with 0.6s sleep)
- Uses certifi for SSL verification with fallback to verify=False on SSL errors

**db.py** - MongoDB data layer
- `ensure_indexes()`: Creates unique compound indexes
  - `t86`: (date, stock_code) - one record per stock per day
  - `bfi82u`: (date) - one record per day
- `upsert_t86(docs)`: Bulk upsert using UpdateOne with (date, stock_code) as key
- `upsert_bfi82u(doc)`: Single upsert with date as key
- Uses global singleton MongoClient connection

**config.py** - Environment configuration
- Loads `.env` using python-dotenv
- Provides `get_mongo_uri()` and `get_db_name()`

### Data Model

**t86 collection**:
- Each document represents one stock's data for one trading day
- Unique index: (date, stock_code)
- Contains official TWSE fields plus: `date` (YYYY-MM-DD), `stock_code`, `stock_name`
- Numeric values stored as strings with thousand separators (e.g., "1,234,567")

**bfi82u collection**:
- Each document represents aggregate trading amounts for one trading day
- Unique index: (date)
- Structure: `{date: "YYYY-MM-DD", fields: [...], rows: [{field: value, ...}]}`

### Idempotency & Error Handling

- Unique indexes + upsert operations ensure rerunning commands won't create duplicates
- API failures or non-trading days return empty results without errors
- Fixed retry strategy (3 attempts) for transient network issues
- SSL verification with fallback mechanism for certificate issues
