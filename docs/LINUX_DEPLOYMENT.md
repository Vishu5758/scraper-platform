# Linux Server Deployment Guide

## Overview

The scraper-platform-v5.0 is **fully compatible with Linux servers**. This guide covers deployment on Linux systems.

## ✅ Linux Compatibility Status

### Cross-Platform Code ✅
- **Path Handling**: Uses `pathlib.Path` (cross-platform) ✅
- **File Operations**: All file operations use Python standard library ✅
- **No Windows Dependencies**: No Windows-specific code in Python modules ✅
- **Docker Support**: Full Docker Compose setup for Linux ✅

### Platform-Specific Files
- `scripts/setup_and_run_alfabeta.bat` - Windows-only (optional)
- `scripts/setup_and_run_alfabeta.sh` - Linux equivalent (created)

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, CentOS 8+, or similar)
- **Python**: 3.11+ (Python 3.11-slim used in Docker)
- **Node.js**: 18+ (for frontend dashboard)
- **Docker**: 20.10+ (optional, for containerized deployment)
- **Docker Compose**: 2.0+ (optional)

### Required Services
- **PostgreSQL**: 15+ (or use Docker Compose)
- **Redis**: 7+ (optional, for caching)
- **Airflow**: 2.5+ (for orchestration)

## Deployment Options

### Option 1: Docker Compose (Recommended)

#### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd scraper-platform

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f api
```

#### Services Included
- **API**: FastAPI backend (port 8000)
- **PostgreSQL**: Database (port 5432)
- **Redis**: Cache (port 6379)

#### Frontend Dashboard
```bash
cd frontend-dashboard
npm install
npm run build
# Serve with nginx or similar
```

### Option 2: Native Linux Installation

#### 1. Install System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip nodejs npm postgresql redis-server

# CentOS/RHEL
sudo yum install -y python3.11 python3-pip nodejs npm postgresql15 redis
```

#### 2. Setup Python Environment
```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Setup Database
```bash
# Create database
sudo -u postgres psql << EOF
CREATE DATABASE scraper_db;
CREATE USER scraper_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE scraper_db TO scraper_user;
EOF

# Run migrations
psql -U scraper_user -d scraper_db -f db/migrations/001_init.sql
# ... run all migrations in order
```

#### 4. Configure Environment
```bash
# Copy example env
cp .env.example .env

# Edit .env with your settings
nano .env
```

Required environment variables:
```bash
# Database
DATABASE_URL=postgresql://scraper_user:password@localhost:5432/scraper_db

# API
API_HOST=0.0.0.0
API_PORT=8000

# Secrets (use Vault or environment)
ALFABETA_USER_1=your_username
ALFABETA_PASS_1=your_password
```

#### 5. Run API Server
```bash
# Development
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Production (with gunicorn)
pip install gunicorn
gunicorn src.api.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 6. Setup Frontend Dashboard
```bash
cd frontend-dashboard
npm install
npm run build

# Serve with nginx
sudo cp -r dist/* /var/www/html/scraper-dashboard/
```

#### 7. Setup Airflow (Optional)
```bash
# Install Airflow
pip install apache-airflow

# Initialize Airflow
export AIRFLOW_HOME=/opt/airflow
airflow db init

# Copy DAGs
cp -r dags/* $AIRFLOW_HOME/dags/

# Start Airflow
airflow webserver -p 8080 &
airflow scheduler &
```

### Option 3: Systemd Service (Production)

#### Create API Service
```bash
sudo nano /etc/systemd/system/scraper-api.service
```

```ini
[Unit]
Description=Scraper Platform API
After=network.target postgresql.service

[Service]
Type=simple
User=scraper
WorkingDirectory=/opt/scraper-platform
Environment="PATH=/opt/scraper-platform/.venv/bin"
ExecStart=/opt/scraper-platform/.venv/bin/gunicorn src.api.app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable and Start
```bash
sudo systemctl daemon-reload
sudo systemctl enable scraper-api
sudo systemctl start scraper-api
sudo systemctl status scraper-api
```

## Linux-Specific Considerations

### 1. File Permissions
```bash
# Ensure proper permissions
chmod +x scripts/setup_and_run_alfabeta.sh
chmod -R 755 sessions/ output/ logs/
```

### 2. Selenium/Chrome Setup
```bash
# Install Chrome/Chromium
sudo apt-get install -y chromium-browser chromium-chromedriver

# Or use Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb

# Install ChromeDriver
CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
sudo unzip /tmp/chromedriver.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

### 3. Path Separators
✅ **No Issues**: All code uses `pathlib.Path` which handles path separators automatically.

### 4. Line Endings
✅ **No Issues**: Python handles both `\n` and `\r\n` correctly.

### 5. Process Management
```bash
# Use systemd for production
# Use supervisor for process management
# Use Docker for containerization
```

## Verification Checklist

### ✅ Pre-Deployment
- [ ] Python 3.11+ installed
- [ ] PostgreSQL running
- [ ] Redis running (if enabled)
- [ ] Environment variables set
- [ ] Database migrations run
- [ ] File permissions correct

### ✅ Post-Deployment
- [ ] API responds to `/health`
- [ ] Database connections work
- [ ] Frontend dashboard loads
- [ ] Airflow DAGs visible (if installed)
- [ ] Logs directory writable
- [ ] Output directory writable

## Troubleshooting

### Common Issues

#### 1. Permission Denied
```bash
# Fix permissions
sudo chown -R scraper:scraper /opt/scraper-platform
chmod +x scripts/setup_and_run_alfabeta.sh
```

#### 2. Database Connection Failed
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -U scraper_user -d scraper_db -h localhost
```

#### 3. Chrome/ChromeDriver Issues
```bash
# Use fake browser for testing
export SCRAPER_PLATFORM_FAKE_BROWSER=1

# Or install proper ChromeDriver
# See Selenium/Chrome Setup above
```

#### 4. Port Already in Use
```bash
# Find process using port
sudo lsof -i :8000
# Kill process or change port in .env
```

## Production Recommendations

### 1. Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name scraper-platform.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /dashboard {
        alias /var/www/html/scraper-dashboard;
        try_files $uri $uri/ /index.html;
    }
}
```

### 2. SSL/TLS
```bash
# Use Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d scraper-platform.example.com
```

### 3. Firewall
```bash
# Allow required ports
sudo ufw allow 8000/tcp  # API
sudo ufw allow 5432/tcp  # PostgreSQL (internal only)
sudo ufw allow 6379/tcp  # Redis (internal only)
sudo ufw allow 8080/tcp  # Airflow (if exposed)
```

### 4. Monitoring
- Use systemd journal: `journalctl -u scraper-api -f`
- Use Prometheus metrics: `http://localhost:8000/metrics`
- Use log aggregation: Configure Loki/Promtail

## Security Considerations

### 1. Secrets Management
- Use HashiCorp Vault (configured in `config/secrets/`)
- Never commit secrets to git
- Use environment variables for sensitive data

### 2. Database Security
- Use strong passwords
- Restrict network access
- Enable SSL connections

### 3. API Security
- Use HTTPS in production
- Implement authentication (add to FastAPI)
- Rate limiting (configured in resource_manager)

## Performance Tuning

### 1. Database
```sql
-- Optimize PostgreSQL
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
```

### 2. Python
```bash
# Use multiple workers
gunicorn src.api.app:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 3. Redis
```bash
# Configure Redis persistence
# Edit /etc/redis/redis.conf
```

## Conclusion

✅ **The scraper-platform-v5.0 is fully Linux-compatible and ready for production deployment on Linux servers.**

All code uses cross-platform libraries and patterns. The only Windows-specific file is the optional `.bat` script, which has a Linux equivalent (`.sh`).

**Recommended Deployment:**
- **Development**: Docker Compose
- **Staging**: Native Linux with systemd
- **Production**: Native Linux with systemd + Nginx reverse proxy

---

**Last Updated:** 2024-12-19

