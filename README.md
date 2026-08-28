# DPBoss Betting App

This project contains a full-stack betting app with a Flask backend and React frontend.

## Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Notes

- Uses SQLite by default for local development.
- The development admin account is configured via environment variables.
- Frontend uses VITE_API_URL from `.env`.
