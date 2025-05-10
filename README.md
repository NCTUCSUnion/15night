# 15night

## Quick Start

### Frontend Setup
```sh
cd frontend
npm install
npm run dev
```

### Backend Setup
```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Setup
```sh
docker run --name mysql-local -e MYSQL_ROOT_PASSWORD=root -p 3306:3306 -d mysql:latest
cd backend
alembic revision --autogenerate -m "Add new field"
alembic upgrade head
```

## Deployment Instructions
```sh
docker compose -f docker‑compose.prod.yaml up -d
```