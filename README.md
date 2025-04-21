# 15night

## Quick Start Guide

### Option 1: Run MySQL in Docker, Backend on Host

```sh
# Start just the MySQL database in Docker
docker-compose up -d mysql

# Setup backend locally
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python scripts/add_sample_data.py

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Run Both MySQL and Backend in Docker

```sh
# Start both MySQL and backend services in Docker
docker-compose up -d

# Run migrations and add sample data
docker exec 15night_backend alembic upgrade head
docker exec 15night_backend python scripts/add_sample_data.py
```

### Setup the Frontend (in a separate terminal)
```sh
cd frontend
npm install
npm run dev
```

## Development Notes

- Backend API is available at `http://localhost:8000/api`
- API docs available at `http://localhost:8000/docs`
- Frontend dev server runs at `http://localhost:5173`
- MySQL database is accessible at `localhost:3306`
  - Database: cs15night
  - User: root
  - Password: root

## Troubleshooting Docker Issues

If you encounter Docker connection errors like:

```
error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.46/containers/json": open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified
```

Try the following:

1. Make sure Docker Desktop is running
2. Restart Docker Desktop
3. In PowerShell, try running: `& 'C:\Program Files\Docker\Docker\DockerCli.exe' -SwitchDaemon`
4. Restart your computer

On Windows, you can also try running in CMD or PowerShell instead of Bash:

```
docker-compose up -d
```

## Database Management
```sh
cd backend
alembic revision --autogenerate -m "Add new field"
alembic upgrade head
```

# Project Setup

This project uses Docker for development environment setup.

## Prerequisites

- Docker
- Docker Compose

## Setup Instructions

1. Clone this repository
2. Make the setup script executable:
   ```bash
   chmod +x setup.sh
   ```

3. Run the setup script:
   ```bash
   ./setup.sh
   ```

4. The script will:
   - Create necessary directories
   - Build and start Docker containers
   - Initialize the MySQL database

5. Access your application:
   - Backend: http://localhost:3000
   - MySQL: localhost:3306
     - Database: mydb
     - User: myuser
     - Password: mypassword

## Development Workflow

- Your backend code is mounted as a volume, so changes will be reflected immediately
- Database data is persisted in a Docker volume

## Manual Commands

If you need to run commands manually:

```bash
# Start containers
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Access MySQL
docker exec -it mysql mysql -u myuser -pmypassword mydb
```
