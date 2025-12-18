# Labortrovilo - Python Version

Job scraping platform built with Python, Playwright, and SQLAlchemy.

## Structure

- `engine.py` - Main scraping engine with Playwright integration
- `models.py` - SQLAlchemy database models (Jobs, Companies)
- `schemas.py` - Pydantic validation schemas
- `database.py` - Database configuration and session management
- `config.py` - Centralized configuration settings
- `requirements.txt` - Python dependencies

## Setup

1. **Create a virtual environment:**
```bash
python -m venv venv
```

2. **Activate the virtual environment:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install Playwright browsers:**
```bash
playwright install chromium
```

## Usage

Run the scraping engine:
```bash
python engine.py
```

## Database Schema

### Jobs Table
- `id` - Primary key
- `title` - Job title
- `company_id` - Foreign key to Companies
- `company_name` - Company name (denormalized)
- `raw_description` - Original job description
- `cleaned_stack` - Extracted tech stack
- `salary_min` - Minimum salary
- `salary_max` - Maximum salary
- `source_url` - Job posting URL (unique)
- `posted_date` - When the job was posted
- `scraped_at` - When we scraped it
- `updated_at` - Last update timestamp

### Companies Table
- `id` - Primary key
- `name` - Company name (unique)
- `growth_score` - Company growth metric
- `industry` - Industry classification
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## Features

✅ Playwright for modern web scraping
✅ SQLAlchemy ORM with SQLite database
✅ Pydantic validation before DB insertion
✅ Duplicate prevention by URL
✅ Async/await support
✅ Context managers for DB sessions
✅ Company relationship tracking

## Customization

The extraction logic in `engine.py` needs to be customized for specific job sites. Update the `extract_job_data` method with the correct CSS selectors for your target website.

## Environment Variables

Create a `.env` file for custom configuration:
```
DATABASE_URL=sqlite:///./labortrovilo.db
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000
```
