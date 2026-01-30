# Victoria Flyer Compare (Python)

A Victoria-focused flyer deals app:
- Scrapes flyer items near a postal code (Flipp/Wishabi backend)
- Stores to SQLite (can switch to Postgres)
- Serves FastAPI endpoints for search & comparison
- Provides Streamlit UI for quick browsing

## Quick start
```bash
python -m venv .venv
# PowerShell:
# .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

copy .env.example .env

python scripts/init_db.py
python scripts/scrape_now.py

# API
uvicorn app.api.main:app --reload

# UI
streamlit run app/ui/streamlit_app.py
```

## GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your_repo_url>
git push -u origin main
```
