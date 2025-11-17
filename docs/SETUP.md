# Setup Guide - Socket Communication System

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Setup](#docker-setup)
4. [Database Setup](#database-setup)
5. [Running Tests](#running-tests)
6. [Troubleshooting](#troubleshooting)

---

## 1. Prerequisites

### Required Software
- Python 3.10 or higher
- Git
- Docker & Docker Compose (optional)
- pip (Python package manager)

### Verify Installation
```bash
python --version    # Should be 3.10+
git --version
docker --version    # Optional
```

---

## 2. Local Development Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/EndlessMelody/socket-video_streaming-project.git
cd socket-video_streaming-project
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
# Default values:
HOST=127.0.0.1
PORT=5555
DB_NAME=chat_server.db
```

### Step 5: Initialize Database
```bash
python -c "from server.database.db_manager import DatabaseManager; DatabaseManager()"
```

### Step 6: Run Server
```bash
python server/socket_server.py
```

### Step 7: Run Client (In another terminal)
```bash
python client/socket_client.py
```

---

## 3. Docker Setup

### Build and Run with Docker Compose
```bash
# Build images
docker-compose -f docker/docker-compose.yml build

# Run containers
docker-compose -f docker/docker-compose.yml up

# Run in background
docker-compose -f docker/docker-compose.yml up -d

# Stop containers
docker-compose -f docker/docker-compose.yml down
```

### Manual Docker Build
```bash
# Build server image
docker build -t socket-server -f docker/Dockerfile .

# Run server container
docker run -p 5555:5555 socket-server
```

---

## 4. Database Setup

### SQLite (Default)
SQLite database is created automatically on first run.

Location: `./chat_server.db`

### Schema Verification
```bash
python -c "
from server.database.db_manager import DatabaseManager
db = DatabaseManager()
# Database initialized successfully
"
```

### PostgreSQL (Optional - Production)
1. Install PostgreSQL
2. Create database:
```sql
CREATE DATABASE socket_chat;
CREATE USER chat_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE socket_chat TO chat_user;
```

3. Update `.env`:
```
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=socket_chat
DB_USER=chat_user
DB_PASSWORD=your_password
```

---

## 5. Running Tests

### Run All Tests
```bash
pytest tests/
```

### Run with Coverage
```bash
pytest --cov=server --cov=client tests/
```

### Run Specific Test File
```bash
pytest tests/test_server.py -v
```

### Run with Detailed Output
```bash
pytest tests/ -v --tb=short
```

---

## 6. Troubleshooting

### Issue: Port Already in Use
```bash
# Windows - Find process using port
netstat -ano | findstr :5555
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5555
kill -9 <PID>
```

### Issue: Module Not Found
```bash
# Ensure virtual environment is activated
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Issue: Database Lock
```bash
# Close all connections and restart server
# Delete database file (WARNING: loses data)
rm chat_server.db
python -c "from server.database.db_manager import DatabaseManager; DatabaseManager()"
```

### Issue: Connection Refused
- Check if server is running
- Verify HOST and PORT in `.env`
- Check firewall settings
- Try localhost instead of 127.0.0.1

### Issue: Import Errors
```bash
# Add project root to PYTHONPATH
# Windows
set PYTHONPATH=%PYTHONPATH%;.

# Linux/Mac
export PYTHONPATH="${PYTHONPATH}:."
```

---

## 7. Development Workflow

### Branch Strategy
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push to remote
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

### Code Quality Checks
```bash
# Format code
black server/ client/

# Lint code
pylint server/ client/

# Type checking
mypy server/ client/
```

---

## 8. Next Steps

After setup:
1. Read [Architecture Documentation](ARCHITECTURE.md)
2. Check [API Reference](API.md)
3. Review [User Guide](USER_GUIDE.md)
4. Start coding!

---

**Need Help?**
- Check Issues on GitHub
- Contact team members
- Review meeting minutes
