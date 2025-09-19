# Deployment Guide

This guide covers different ways to deploy BookForge for production use.

## 🚀 Quick Deploy Options

### Option 1: Local Development

```bash
# Install and run locally
pip install bookforge
bookforge serve --host 0.0.0.0 --port 8000
```

### Option 2: Docker (Recommended)

```bash
# Pull and run official image
docker run -p 8000:8000 bookforge/bookforge:latest

# Or build from source
git clone https://github.com/eristoddle/bookforge.git
cd bookforge
docker build -t bookforge .
docker run -p 8000:8000 bookforge
```

### Option 3: Cloud Platforms

- **Heroku**: One-click deploy button
- **Railway**: Git-based deployment
- **DigitalOcean App Platform**: Container deployment
- **AWS Fargate**: Serverless containers
- **Google Cloud Run**: Pay-per-use serverless

## 🐳 Docker Deployment

### Basic Dockerfile

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bookforge/ ./bookforge/
COPY *.py ./

# Create directories for file storage
RUN mkdir -p temp_books generated_epubs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "bookforge.main"]
```

### Docker Compose for Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  bookforge:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
      - EPUB_VALIDATION=true
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./data/generated_epubs:/app/generated_epubs
      - ./data/temp_books:/app/temp_books
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - bookforge
    restart: unless-stopped

volumes:
  redis_data:
```

### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream bookforge {
        server bookforge:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=2r/s;

    server {
        listen 80;
        server_name your-domain.com;

        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

        # File upload limits
        client_max_body_size 50M;
        client_body_timeout 60s;

        # Gzip compression
        gzip on;
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://bookforge;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts for long-running requests
            proxy_connect_timeout 60s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
        }

        # File upload endpoints
        location /api/v1/generate/ {
            limit_req zone=upload burst=5 nodelay;
            proxy_pass http://bookforge;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Extended timeouts for uploads
            proxy_connect_timeout 60s;
            proxy_send_timeout 600s;
            proxy_read_timeout 600s;
        }

        # Static files and web interface
        location / {
            proxy_pass http://bookforge;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## ☁️ Cloud Deployments

### AWS ECS Fargate

```json
{
  "family": "bookforge-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "bookforge",
      "image": "bookforge/bookforge:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DEBUG",
          "value": "false"
        },
        {
          "name": "EPUB_VALIDATION",
          "value": "true"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/bookforge",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 10
      }
    }
  ]
}
```

### Google Cloud Run

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/bookforge', '.']

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/bookforge']

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'bookforge'
      - '--image'
      - 'gcr.io/$PROJECT_ID/bookforge'
      - '--platform'
      - 'managed'
      - '--region'
      - 'us-central1'
      - '--allow-unauthenticated'
      - '--memory'
      - '1Gi'
      - '--cpu'
      - '1'
      - '--concurrency'
      - '80'
      - '--timeout'
      - '300'
```

### Heroku

```yaml
# heroku.yml
build:
  docker:
    web: Dockerfile

run:
  web: python -m bookforge.main --host 0.0.0.0 --port $PORT
```

```json
// app.json
{
  "name": "BookForge",
  "description": "Beautiful EPUB generation service",
  "image": "heroku/python",
  "repository": "https://github.com/eristoddle/bookforge",
  "keywords": ["epub", "ebook", "markdown", "publishing"],
  "env": {
    "DEBUG": {
      "description": "Enable debug mode",
      "value": "false"
    },
    "EPUB_VALIDATION": {
      "description": "Enable EPUB validation",
      "value": "true"
    }
  },
  "formation": {
    "web": {
      "quantity": 1,
      "size": "standard-1x"
    }
  },
  "buildpacks": [
    {
      "url": "heroku/python"
    }
  ]
}
```

## 🔒 Security Configuration

### Environment Variables

```bash
# .env.production
DEBUG=false
LOG_LEVEL=WARNING

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,api.your-domain.com

# File limits
MAX_FILE_SIZE=100MB
MAX_CONCURRENT_JOBS=5
JOB_TIMEOUT=600

# GitHub integration
GITHUB_TOKEN=your-github-token

# Storage
TEMP_DIR=/var/lib/bookforge/temp
OUTPUT_DIR=/var/lib/bookforge/output

# Database (if using)
DATABASE_URL=postgresql://user:pass@localhost/bookforge

# Redis
REDIS_URL=redis://localhost:6379/0

# EPUB validation
EPUB_VALIDATION=true
EPUBCHECK_PATH=/usr/local/bin/epubcheck.jar
```

### Firewall Rules

```bash
# Ubuntu/Debian firewall setup
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 8000/tcp   # Block direct access to app
sudo ufw enable
```

### SSL/TLS Setup with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring and Logging

### Prometheus Metrics

```python
# Add to bookforge/monitoring.py
from prometheus_client import Counter, Histogram, generate_latest

epub_generations = Counter('bookforge_epub_generations_total', 'Total EPUB generations')
generation_duration = Histogram('bookforge_generation_duration_seconds', 'EPUB generation duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Logging Configuration

```yaml
# logging.yml
version: 1
disable_existing_loggers: false

formatters:
  default:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  json:
    format: '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: default
    stream: ext://sys.stdout

  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: json
    filename: /var/log/bookforge/app.log
    maxBytes: 10485760
    backupCount: 5

loggers:
  bookforge:
    level: DEBUG
    handlers: [console, file]
    propagate: false

root:
  level: INFO
  handlers: [console]
```

## 🚦 Health Checks and Monitoring

### Advanced Health Check

```python
@app.get("/health/detailed")
async def detailed_health():
    checks = {
        "database": check_database(),
        "redis": check_redis(),
        "storage": check_storage(),
        "epubcheck": check_epubcheck()
    }

    all_healthy = all(checks.values())

    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }
```

### Uptime Monitoring

```bash
# Simple uptime script
#!/bin/bash
# uptime-check.sh

URL="https://your-domain.com/health"
EMAIL="admin@your-domain.com"

if ! curl -f -s "$URL" > /dev/null; then
    echo "BookForge is down!" | mail -s "Alert: BookForge Down" "$EMAIL"
fi
```

## 🔄 Backup and Recovery

### Database Backup

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/bookforge"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup job data
docker exec bookforge_redis redis-cli BGSAVE
docker cp bookforge_redis:/data/dump.rdb "$BACKUP_DIR/redis_$DATE.rdb"

# Backup generated EPUBs
tar -czf "$BACKUP_DIR/epubs_$DATE.tar.gz" /data/generated_epubs/

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.rdb" -mtime +30 -delete
```

### Disaster Recovery

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
RESTORE_DIR="/tmp/bookforge_restore"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Stop services
docker-compose down

# Restore data
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

# Copy restored data
cp -r "$RESTORE_DIR"/* /data/

# Restart services
docker-compose up -d

echo "Restore completed"
```

## 📈 Scaling Considerations

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  bookforge:
    build: .
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - bookforge

  redis:
    image: redis:7-alpine

# Scale with: docker-compose up --scale bookforge=3
```

### Load Balancer Configuration

```nginx
# nginx-lb.conf
upstream bookforge_backend {
    least_conn;
    server bookforge_1:8000;
    server bookforge_2:8000;
    server bookforge_3:8000;
}

server {
    listen 80;

    location / {
        proxy_pass http://bookforge_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

This deployment guide provides everything needed to run BookForge in production, from simple Docker deployments to enterprise-scale cloud infrastructure.