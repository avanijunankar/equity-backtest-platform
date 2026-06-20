#!/usr/bin/env bash
# Complete setup script for Equity Backtesting Platform
set -e
cd "$(dirname "$0")/.."

echo "=== 1. Start PostgreSQL (Docker, port 5433) ==="
docker compose up -d
sleep 6

echo "=== 2. Backend setup ==="
cd backend
python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install -r requirements.txt -q

cat > .env << 'EOF'
USE_DATABASE=true
DATABASE_URL=postgresql://backtest_user:backtest_pass@localhost:5433/equity_backtest
DATABASE_CONNECT_TIMEOUT=5
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
LOG_LEVEL=INFO
EOF

echo "=== 3. Initialize DB tables ==="
python -m scripts.init_db

echo "=== 4. Load data ==="
echo "Option A: Real Yahoo Finance (run when API available):"
echo "  python -m scripts.ingest_data --all"
echo ""
echo "Option B: Bootstrap data now (if Yahoo rate-limited):"
python -m scripts.load_demo_to_db

echo ""
echo "=== 5. Start servers ==="
echo "Backend:  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
echo "Frontend: cd frontend && npm install && npm run dev"
echo ""
echo "App: http://localhost:3000"
