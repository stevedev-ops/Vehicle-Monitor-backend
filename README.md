# Vehicle Monitor — Backend REST API

Production Django REST Framework backend for the **Vehicle Monitor & Fleet Intelligence** platform. Configured for cloud deployment on **Render** with PostgreSQL, Gunicorn, WhiteNoise, and CORS support.

---

## 🛠️ Tech Stack

- **Framework:** Django 6 / Django REST Framework
- **WSGI Server:** Gunicorn
- **Database:** PostgreSQL (with SQLite fallback for local development)
- **Static Asset Serving:** WhiteNoise
- **CORS Handling:** `django-cors-headers` (configured for Vercel frontend domains)

---

## 🚀 Deploy to Render

### Method 1: Blueprint Deployment (Recommended)
This repository includes a `render.yaml` specification that sets up both the Web Service and Managed PostgreSQL database automatically.

1. Go to your [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** > **Blueprint**.
3. Connect your GitHub account and select `stevedev-ops/Vehicle-Monitor-backend`.
4. Click **Apply**. Render will automatically provision:
   - A Python Web Service running Gunicorn.
   - A PostgreSQL database linked via `DATABASE_URL`.
   - Runs `build.sh` (installs requirements, collects static files, applies migrations).

### Method 2: Manual Web Service Setup
1. Create a **New PostgreSQL** database on Render (e.g. `vehicle-monitor-db`).
2. Create a **New Web Service** connected to `stevedev-ops/Vehicle-Monitor-backend`.
3. Configure the service settings:
   - **Environment:** `Python`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn petrol_backend.wsgi:application`
4. Add the following **Environment Variables**:
   - `PYTHON_VERSION`: `3.12.0`
   - `DEBUG`: `False`
   - `SECRET_KEY`: *[Generate a secure random string]*
   - `DATABASE_URL`: *[Internal Database Connection String from Render Postgres]*
   - `RENDER_EXTERNAL_HOSTNAME`: *(Optional, auto-provided by Render)*

---

## 📡 API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | API Health & Service Index |
| `/admin/` | `GET/POST` | Django Admin Portal |
| `/api/vehicles/` | `GET/POST` | Vehicle fleet management |
| `/api/fuel-entries/` | `GET/POST` | Fuel consumption logs & calculations |
| `/api/services/` | `GET/POST` | Vehicle maintenance history |
| `/api/reminders/` | `GET/POST` | Service interval reminders |
| `/api/expenses/` | `GET/POST` | Non-fuel operating costs (TCO) |
| `/api/vehicle-documents/` | `GET/POST` | Insurance, inspection, logbooks |
| `/api/owner-documents/` | `GET/POST` | Driver licences & credentials |

---

## 💻 Local Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. (Optional) Populate database with sample telemetry
python seed_db.py

# 5. Start development server
python manage.py runserver
```
API will be accessible at `http://localhost:8000/`.
