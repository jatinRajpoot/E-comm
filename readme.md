# E-comm

Flask-based e-commerce demo application with product browsing, cart, checkout, and user accounts backed by SQLite.

## Features
- Product catalog with search, categories, and sorting
- Product detail pages with related items
- Cart management with quantity updates and promo codes
- Checkout flow and order history
- User registration/login with profile and address management
- Newsletter subscription

## Tech Stack
- Python 3
- Flask, Flask-Login, Flask-SQLAlchemy
- SQLite
- Jinja2 templates, HTML/CSS

## Project Structure
- `app.py` — main Flask app and routes
- `models.py` — database models
- `db_init.py` — database reset and seed data
- `templates/` — HTML templates
- `static/` — CSS and image assets

## Prerequisites
- Python 3.9+ (3.10+ recommended for longer support and better performance)

## Setup (Create a Virtual Environment)
From the project root:

### macOS/Linux
```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows (PowerShell)
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### Windows (CMD)
```cmd
py -m venv .venv
.venv\Scripts\activate
```

## Install Dependencies
```bash
pip install -r requirements.txt
```

## Run the App
```bash
python app.py
```

Then open: `http://127.0.0.1:5000`

## Database and Seed Data
- The app uses `sqlite:///ecommerce_v2.db`.
- On startup, the app auto-creates tables and seeds demo data if fewer than 15 products exist.
- To reset and re-seed manually:
```bash
python db_init.py
```

### Demo Account
- Email: `test@example.com`
- Password: `password123`

## Notes on Images
The `/static/images/<filename>` route in `app.py` maps filenames to an external artifact directory. If you want to use local images instead, update `artifact_dir` in `app.py` and place assets in `static/images/`.

## Useful Commands (All-in-One)
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
