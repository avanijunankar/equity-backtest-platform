# Deployment

## Local Development

```bash
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # USE_DATABASE=false

cd ../frontend && npm install
cp .env.local.example .env.local
```

## Production Backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Production Frontend

```bash
npm run build && npm start
```

Set `NEXT_PUBLIC_API_URL` to your backend URL.

## Docker (optional)

Build images separately for backend/frontend. Mount `.env` for database credentials.

## Environment Checklist

- [ ] `USE_DATABASE=true` when DB ready
- [ ] `DATABASE_URL` points to remote PostgreSQL
- [ ] `CORS_ORIGINS` includes frontend URL
- [ ] Data ingested via `scripts/ingest_data.py`
- [ ] Firewall allows port 5432 (DB) and 8000 (API)
