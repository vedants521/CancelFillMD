# Deployment Guide - CancelFillMD Pro

## Table of Contents
1. [Deployment Options](#deployment-options)
2. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
3. [AWS Deployment](#aws-deployment)
4. [Heroku Deployment](#heroku-deployment)
5. [Self-Hosted Deployment](#self-hosted-deployment)
6. [Production Configuration](#production-configuration)
7. [Security Hardening](#security-hardening)
8. [Monitoring & Maintenance](#monitoring--maintenance)

## Deployment Options

### Comparison Table

| Platform | Cost | Ease | Scalability | Control | Best For |
|----------|------|------|-------------|---------|----------|
| Streamlit Cloud | Free/Paid | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | Quick demos, small clinics |
| AWS EC2 | Pay-as-you-go | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Large practices, full control |
| Heroku | Free/Paid | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Medium practices |
| Self-Hosted | Hardware cost | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | Maximum control, compliance |

## Streamlit Cloud Deployment

### Prerequisites
- GitHub account
- Streamlit Cloud account
- Project in GitHub repository

### Step 1: Prepare Repository

#### 1.1 Create requirements.txt
Ensure all dependencies are listed:
```txt
streamlit==1.28.0
firebase-admin==6.1.0
pandas==2.0.3
python-dotenv==1.0.0
twilio==8.5.0
sendgrid==6.10.0
pytz==2023.3
plotly==5.17.0
numpy==1.24.3
xlsxwriter==3.1.0
reportlab==4.0.4
```

#### 1.2 Remove Sensitive Files
Create/update `.gitignore`:
```gitignore
.env
firebase-key.json
*.pem
*.key
__pycache__/
.streamlit/secrets.toml
```

#### 1.3 Push to GitHub
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud

#### 2.1 Connect Repository
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect GitHub account
4. Select repository: `yourusername/cancelfillmd-pro`
5. Branch: `main`
6. Main file: `app.py`

#### 2.2 Configure Secrets
1. Click "Advanced settings"
2. Add secrets in TOML format:

```toml
# Environment
ENVIRONMENT = "production"
DEMO_MODE = "False"

# Twilio
TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_PHONE_NUMBER = "+15551234567"

# SendGrid
SENDGRID_API_KEY = "SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
SENDER_EMAIL = "noreply@yourclinic.com"
REPLY_TO_EMAIL = "support@yourclinic.com"

# App Settings
CLINIC_NAME = "Your Clinic Name"
APP_URL = "https://your-app-name.streamlit.app"
JWT_SECRET_KEY = "your-secure-random-key"
STAFF_NOTIFICATION_EMAIL = "manager@yourclinic.com"

# Firebase
FIREBASE_URL = "https://your-project.firebaseio.com/"

[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "key-id"
private_key = """-----BEGIN PRIVATE KEY-----
your-private-key-here
-----END PRIVATE KEY-----"""
client_email = "firebase-adminsdk@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk%40your-project.iam.gserviceaccount.com"
```

#### 2.3 Deploy
1. Click "Deploy"
2. Wait for build (5-10 minutes)
3. App URL: `https://your-app-name.streamlit.app`

### Step 3: Custom Domain (Optional)

#### 3.1 In Streamlit Cloud
1. Go to app settings
2. Under "General" → "App URL"
3. Add custom domain: `app.yourclinic.com`

#### 3.2 DNS Configuration
Add CNAME record:
```
Type: CNAME
Name: app
Value: your-app-name.streamlit.app
TTL: 3600
```

## AWS Deployment

### Prerequisites
- AWS Account
- AWS CLI installed
- Basic EC2 knowledge

### Step 1: Launch EC2 Instance

#### 1.1 Choose AMI
- Ubuntu Server 22.04 LTS
- Instance type: t3.medium (minimum)

#### 1.2 Configure Security Group
```
Inbound Rules:
- SSH (22) - Your IP
- HTTP (80) - 0.0.0.0/0
- HTTPS (443) - 0.0.0.0/0
- Custom TCP (8501) - 0.0.0.0/0 (Streamlit)
```

### Step 2: Server Setup

#### 2.1 Connect to Instance
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

#### 2.2 Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.9 python3-pip python3-venv nginx -y

# Install Git
sudo apt install git -y

# Clone repository
git clone https://github.com/yourusername/cancelfillmd-pro.git
cd cancelfillmd-pro

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

#### 2.3 Configure Environment
```bash
# Create .env file
nano .env
# Add your environment variables

# Copy Firebase key
# Use SCP to transfer firebase-key.json
```

### Step 3: Configure Nginx

#### 3.1 Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/cancelfillmd
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

#### 3.2 Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/cancelfillmd /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 4: Create Systemd Service

#### 4.1 Create Service File
```bash
sudo nano /etc/systemd/system/cancelfillmd.service
```

Add:
```ini
[Unit]
Description=CancelFillMD Pro
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/cancelfillmd-pro
Environment="PATH=/home/ubuntu/cancelfillmd-pro/venv/bin"
ExecStart=/home/ubuntu/cancelfillmd-pro/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 4.2 Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable cancelfillmd
sudo systemctl start cancelfillmd
sudo systemctl status cancelfillmd
```

### Step 5: SSL Certificate

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

## Heroku Deployment

### Step 1: Prepare for Heroku

#### 1.1 Create Procfile
```
web: sh setup.sh && streamlit run app.py
```

#### 1.2 Create setup.sh
```bash
mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"your-email@domain.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = $PORT\n\
" > ~/.streamlit/config.toml
```

#### 1.3 Update requirements.txt
Add:
```
gunicorn==20.1.0
```

### Step 2: Deploy to Heroku

```bash
# Install Heroku CLI
# Create Heroku app
heroku create cancelfillmd-pro

# Set buildpack
heroku buildpacks:set heroku/python

# Configure environment variables
heroku config:set TWILIO_ACCOUNT_SID=your_sid
heroku config:set TWILIO_AUTH_TOKEN=your_token
# ... set all variables

# Deploy
git push heroku main

# Open app
heroku open
```

## Self-Hosted Deployment

### Option 1: Docker

#### 1.1 Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 1.2 Build and Run
```bash
docker build -t cancelfillmd .
docker run -p 8501:8501 --env-file .env cancelfillmd
```

### Option 2: Local Server

Similar to AWS setup but on your own hardware.

## Production Configuration

### 1. Security Settings

Update `config.py`:
```python
# Production settings
IS_PRODUCTION = True
DEMO_MODE = False

SECURITY_SETTINGS = {
    'session_timeout_minutes': 30,
    'max_login_attempts': 5,
    'lockout_duration_minutes': 30,
    'password_min_length': 12,
    'password_require_uppercase': True,
    'password_require_numbers': True,
    'password_require_special': True,
    'enable_2fa': True,
    'audit_logging': True,
    'encryption_enabled': True
}
```

### 2. Database Security

#### 2.1 Firebase Rules
In Firebase Console → Realtime Database → Rules:
```json
{
  "rules": {
    "appointments": {
      ".read": "auth != null",
      ".write": "auth != null && auth.token.role == 'admin'"
    },
    "waitlist": {
      ".read": "auth != null",
      ".write": true,
      "$patient": {
        ".validate": "newData.hasChildren(['name', 'email', 'phone'])"
      }
    },
    "users": {
      ".read": "auth != null && auth.token.role == 'admin'",
      ".write": "auth != null && auth.token.role == 'admin'"
    },
    "config": {
      ".read": "auth != null",
      ".write": "auth != null && auth.token.role == 'admin'"
    }
  }
}
```

### 3. Performance Optimization

#### 3.1 Caching Configuration
```python
# In app.py
st.set_page_config(
    page_title="CancelFillMD Pro",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "CancelFillMD Pro - Smart Appointment Management"
    }
)

# Cache database connections
@st.cache_resource
def init_firebase():
    return FirebaseDB()

# Cache expensive computations
@st.cache_data(ttl=300)  # 5 minutes
def get_analytics_data(date_range):
    return generate_analytics_summary(appointments, date_range)
```

#### 3.2 Database Indexing
In Firebase Console, add indexes for:
- appointments/date
- appointments/status
- waitlist/specialty
- waitlist/active

### 4. Backup Configuration

#### 4.1 Automated Backups
Create `scripts/backup.py`:
```python
import firebase_admin
from firebase_admin import db
import json
from datetime import datetime
import boto3  # For S3 backup

def backup_database():
    # Get all data
    ref = db.reference()
    data = ref.get()
    
    # Create backup file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'backup_{timestamp}.json'
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Upload to S3 (optional)
    s3 = boto3.client('s3')
    s3.upload_file(filename, 'cancelfillmd-backups', filename)
    
    print(f"Backup completed: {filename}")

if __name__ == "__main__":
    backup_database()
```

#### 4.2 Schedule Backups
```bash
# Add to crontab
0 2 * * * /home/ubuntu/cancelfillmd-pro/venv/bin/python /home/ubuntu/cancelfillmd-pro/scripts/backup.py
```

### 5. Environment-Specific Settings

#### 5.1 Production .env
```bash
# Production Environment
ENVIRONMENT=production
DEMO_MODE=False
DEBUG=False

# Security
SESSION_SECRET_KEY=generate-very-long-random-key
ENABLE_HTTPS_ONLY=True
SECURE_COOKIES=True

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=100
MAX_APPOINTMENTS_PER_DAY=500

# Monitoring
ENABLE_MONITORING=True
SENTRY_DSN=your-sentry-dsn
LOGFILE=/var/log/cancelfillmd/app.log
```

## Security Hardening

### 1. HTTPS Configuration

#### 1.1 Force HTTPS Redirect
In Nginx:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

#### 1.2 Security Headers
Add to Nginx:
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; style-src 'self' 'unsafe-inline' https:;" always;
```

### 2. Application Security

#### 2.1 Input Validation
Ensure all inputs are validated:
```python
# In every form
from utils.validation_utils import FormValidator, DataSanitizer

# Validate and sanitize
email = DataSanitizer.sanitize_email(email_input)
valid, msg = FormValidator.validate_email(email)
if not valid:
    st.error(msg)
    return
```

#### 2.2 SQL Injection Prevention
Using Firebase eliminates SQL injection, but always:
- Sanitize inputs
- Use parameterized queries if using SQL
- Validate data types

### 3. Authentication Hardening

#### 3.1 Implement 2FA
```python
# In utils/security_utils.py
def enable_2fa_for_user(user_id):
    # Generate QR code for authenticator app
    secret = pyotp.random_base32()
    provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_id,
        issuer_name='CancelFillMD Pro'
    )
    
    # Store secret securely
    db.reference(f'users/{user_id}/2fa_secret').set(
        encrypt(secret)
    )
    
    return provisioning_uri
```

### 4. Monitoring Setup

#### 4.1 Application Monitoring
```python
# Install monitoring
pip install sentry-sdk

# In app.py
import sentry_sdk
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    traces_sample_rate=1.0,
    environment=os.getenv('ENVIRONMENT', 'development')
)
```

#### 4.2 Server Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Install Datadog agent (optional)
DD_AGENT_MAJOR_VERSION=7 DD_API_KEY=your_api_key DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"
```

## Monitoring & Maintenance

### 1. Health Checks

#### 1.1 Create Health Check Endpoint
```python
# In app.py
@st.cache_data(ttl=60)
def health_check():
    try:
        # Check Firebase
        db = FirebaseDB()
        db.db.reference('health_check').set({
            'timestamp': datetime.now().isoformat()
        })
        
        # Check Twilio
        # Check SendGrid
        
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

#### 1.2 External Monitoring
- Use UptimeRobot or Pingdom
- Monitor endpoint: `https://your-domain.com/health`
- Alert on downtime

### 2. Log Management

#### 2.1 Centralized Logging
```python
# In utils/logging_utils.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger('cancelfillmd')
    logger.setLevel(logging.INFO)
    
    # File handler with rotation
    handler = RotatingFileHandler(
        '/var/log/cancelfillmd/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

#### 2.2 Log Analysis
```bash
# Install log analysis tools
sudo apt install goaccess

# Analyze logs
goaccess /var/log/cancelfillmd/app.log -o /var/www/html/report.html --log-format=COMBINED
```

### 3. Performance Monitoring

#### 3.1 Database Performance
```python
# Monitor query times
import time

def timed_query(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        
        if end - start > 1.0:  # Log slow queries
            logger.warning(f"Slow query: {func.__name__} took {end-start:.2f}s")
        
        return result
    return wrapper
```

#### 3.2 Resource Monitoring
```bash
# Create monitoring script
#!/bin/bash
# monitor.sh

echo "=== CancelFillMD Pro Resource Monitor ==="
echo "Time: $(date)"
echo ""
echo "Memory Usage:"
free -h
echo ""
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)"
echo ""
echo "Disk Usage:"
df -h /
echo ""
echo "Process Status:"
systemctl status cancelfillmd
```

### 4. Maintenance Tasks

#### 4.1 Regular Updates
```bash
# Update script
#!/bin/bash
cd /home/ubuntu/cancelfillmd-pro
source venv/bin/activate

# Backup before update
python scripts/backup.py

# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart cancelfillmd
```

#### 4.2 Database Cleanup
```python
# In scripts/cleanup.py
def cleanup_old_data():
    db = FirebaseDB()
    cutoff_date = datetime.now() - timedelta(days=90)
    
    # Archive old appointments
    appointments = db.get_appointments()
    for apt in appointments:
        if apt['date'] < cutoff_date.strftime('%Y-%m-%d'):
            # Move to archive
            db.archive_appointment(apt)
    
    # Clean up inactive waitlist entries
    waitlist = db.get_waitlist()
    for patient in waitlist:
        if patient['created_at'] < cutoff_date.isoformat():
            db.deactivate_waitlist_entry(patient['id'])
```

### 5. Disaster Recovery

#### 5.1 Recovery Plan
1. **Data Recovery**
   - Restore from latest backup
   - Verify data integrity
   - Update connection strings

2. **Service Recovery**
   - Spin up new server
   - Deploy application
   - Restore configuration
   - Update DNS

3. **Communication Plan**
   - Notify staff
   - Update status page
   - Communicate with patients

#### 5.2 Recovery Time Objectives
- RTO (Recovery Time Objective): 4 hours
- RPO (Recovery Point Objective): 24 hours

## Scaling Considerations

### 1. Horizontal Scaling
- Use load balancer (AWS ELB, Nginx)
- Multiple Streamlit instances
- Shared session storage (Redis)

### 2. Database Scaling
- Firebase automatically scales
- Consider Firestore for larger datasets
- Implement caching layer

### 3. Notification Scaling
- Use queue system (RabbitMQ, AWS SQS)
- Batch notifications
- Rate limit per provider

---

## Deployment Checklist

- [ ] All sensitive files in .gitignore
- [ ] Environment variables configured
- [ ] SSL certificate installed
- [ ] Firewall rules configured
- [ ] Backup system in place
- [ ] Monitoring configured
- [ ] Health checks working
- [ ] Security headers added
- [ ] Rate limiting enabled
- [ ] Error tracking setup
- [ ] Documentation updated
- [ ] Staff trained on new URL
- [ ] DNS propagated
- [ ] Old system sunset plan

## Support

For deployment support:
- Email: devops@cancelfillmd.com
- Documentation: docs.cancelfillmd.com
- Emergency: +1 (555) 123-4567