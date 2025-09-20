# Deployment Guide 🚀

This guide covers various deployment options for the AI-Powered Task Management Agent.

## 🐳 Docker Deployment (Recommended)

### Prerequisites
- Docker and Docker Compose installed
- Google Gemini API key
- Domain name (optional, for production)

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd AI_PowerTMS

# Copy environment template
cp env.example .env

# Edit environment variables
nano .env
```

### 2. Production Environment Variables
```env
# Database
DATABASE_URL=postgresql://postgres:your_secure_password@postgres:5432/task_management

# AI/LLM
GEMINI_API_KEY=your_production_gemini_api_key

# Security
SECRET_KEY=your_very_secure_secret_key_here

# Environment
ENVIRONMENT=production

# Frontend
NEXT_PUBLIC_API_URL=https://your-domain.com
```

### 3. Start Services
```bash
# Build and start all services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Database Migration
```bash
# Run database migrations
docker-compose exec backend alembic upgrade head
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS ECS with Fargate

1. **Create ECR Repositories**
```bash
# Create repositories for backend and frontend
aws ecr create-repository --repository-name ai-task-management-backend
aws ecr create-repository --repository-name ai-task-management-frontend
```

2. **Build and Push Images**
```bash
# Build and tag images
docker build -t ai-task-management-backend ./backend
docker build -t ai-task-management-frontend ./frontend

# Tag for ECR
docker tag ai-task-management-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/ai-task-management-backend:latest
docker tag ai-task-management-frontend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/ai-task-management-frontend:latest

# Push to ECR
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/ai-task-management-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/ai-task-management-frontend:latest
```

3. **Set up RDS PostgreSQL**
```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier ai-task-management-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password your_secure_password \
  --allocated-storage 20
```

4. **Create ECS Task Definition**
```json
{
  "family": "ai-task-management",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::<account-id>:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/ai-task-management-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://postgres:password@your-rds-endpoint:5432/task_management"
        },
        {
          "name": "GEMINI_API_KEY",
          "value": "your_gemini_api_key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-task-management",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Platform Deployment

#### Using Cloud Run

1. **Build and Deploy Backend**
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/ai-task-management-backend ./backend

# Deploy to Cloud Run
gcloud run deploy ai-task-management-backend \
  --image gcr.io/PROJECT-ID/ai-task-management-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql://user:pass@host:5432/db,GEMINI_API_KEY=your_key
```

2. **Set up Cloud SQL**
```bash
# Create Cloud SQL instance
gcloud sql instances create ai-task-management-db \
  --database-version=POSTGRES_13 \
  --tier=db-f1-micro \
  --region=us-central1
```

### DigitalOcean Deployment

#### Using App Platform

1. **Create App Spec**
```yaml
name: ai-task-management
services:
- name: backend
  source_dir: /backend
  github:
    repo: your-username/ai-task-management
    branch: main
  run_command: uvicorn main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    value: ${db.DATABASE_URL}
  - key: GEMINI_API_KEY
    value: your_gemini_api_key
  - key: SECRET_KEY
    value: your_secret_key

- name: frontend
  source_dir: /frontend
  github:
    repo: your-username/ai-task-management
    branch: main
  run_command: npm start
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: NEXT_PUBLIC_API_URL
    value: ${backend.PUBLIC_URL}

databases:
- name: db
  engine: PG
  version: "13"
```

## 🔧 Manual Server Deployment

### Ubuntu/Debian Server Setup

1. **Install Dependencies**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx -y
```

2. **Clone and Setup Application**
```bash
# Clone repository
git clone <repository-url>
cd AI_PowerTMS

# Set up environment
cp env.example .env
nano .env  # Configure your environment variables

# Start services
docker-compose up -d --build
```

3. **Configure Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. **SSL Certificate with Let's Encrypt**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## 📊 Monitoring and Maintenance

### Health Checks
```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:3000

# Check database connection
docker-compose exec backend python -c "from database import engine; print(engine.execute('SELECT 1').scalar())"
```

### Log Management
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Log rotation
sudo nano /etc/logrotate.d/docker-compose
```

### Backup Strategy
```bash
# Database backup
docker-compose exec postgres pg_dump -U postgres task_management > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
docker-compose exec -T postgres psql -U postgres task_management < backup_file.sql
```

### Performance Monitoring
```bash
# Monitor resource usage
docker stats

# Monitor application performance
curl http://localhost:8000/metrics  # If metrics endpoint is added
```

## 🔒 Security Best Practices

### Environment Security
- Use strong, unique passwords
- Rotate API keys regularly
- Enable firewall rules
- Use HTTPS in production
- Implement rate limiting

### Database Security
- Use connection pooling
- Enable SSL connections
- Regular security updates
- Backup encryption
- Access control

### Application Security
- Input validation
- SQL injection prevention
- XSS protection
- CSRF protection
- Security headers

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Issues**
```bash
# Check database status
docker-compose exec postgres pg_isready -U postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

2. **WebSocket Connection Issues**
```bash
# Check WebSocket endpoint
wscat -c ws://localhost:8000/ws/chat

# Check firewall rules
sudo ufw status
```

3. **Memory Issues**
```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
```

### Performance Optimization

1. **Database Optimization**
- Add database indexes
- Optimize queries
- Use connection pooling
- Regular VACUUM and ANALYZE

2. **Application Optimization**
- Enable gzip compression
- Use CDN for static assets
- Implement caching
- Optimize Docker images

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
    environment:
      - DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Load Balancing
```nginx
upstream backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    location /api/ {
        proxy_pass http://backend;
    }
}
```

---

For additional support, please refer to the main [README.md](README.md) or create an issue in the repository.
