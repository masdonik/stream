#!/bin/bash

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== Streaming Manager Installation Script ===${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

# Update system
echo -e "${YELLOW}Updating system...${NC}"
apt update && apt upgrade -y

# Install required packages
echo -e "${YELLOW}Installing required packages...${NC}"
apt install -y python3-pip python3-venv ffmpeg nginx certbot python3-certbot-nginx

# Create application directory
echo -e "${YELLOW}Creating application directory...${NC}"
mkdir -p /opt/streaming-manager
cp -r . /opt/streaming-manager/

# Set permissions
echo -e "${YELLOW}Setting permissions...${NC}"
chown -R www-data:www-data /opt/streaming-manager
chmod -R 755 /opt/streaming-manager

# Create and activate virtual environment
echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
cd /opt/streaming-manager
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Setup environment variables
echo -e "${YELLOW}Setting up environment variables...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}.env file not found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit /opt/streaming-manager/.env with your configuration${NC}"
fi

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
python3 << EOF
from app import app, db
with app.app_context():
    db.create_all()
EOF

# Setup systemd service
echo -e "${YELLOW}Setting up systemd service...${NC}"
cp streaming-manager.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable streaming-manager
systemctl start streaming-manager

# Setup Nginx
echo -e "${YELLOW}Setting up Nginx...${NC}"
cat > /etc/nginx/sites-available/streaming-manager << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/streaming-manager/static;
        expires 30d;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/streaming-manager /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx

# Create backup directory
echo -e "${YELLOW}Creating backup directory...${NC}"
mkdir -p /opt/streaming-manager/backup

# Setup log rotation
echo -e "${YELLOW}Setting up log rotation...${NC}"
cat > /etc/logrotate.d/streaming-manager << 'EOF'
/opt/streaming-manager/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload streaming-manager
    endscript
}
EOF

# Final instructions
echo -e "${GREEN}Installation completed!${NC}"
echo -e "${YELLOW}Please follow these steps:${NC}"
echo -e "1. Edit the configuration in /opt/streaming-manager/.env"
echo -e "2. Set up your domain and SSL certificate using:"
echo -e "   ${GREEN}certbot --nginx -d yourdomain.com${NC}"
echo -e "3. Restart the application:"
echo -e "   ${GREEN}systemctl restart streaming-manager${NC}"
echo -e "\nApplication logs can be viewed with:"
echo -e "${GREEN}journalctl -u streaming-manager -f${NC}"
echo -e "\nNginx logs can be viewed in:"
echo -e "${GREEN}/var/log/nginx/access.log${NC}"
echo -e "${GREEN}/var/log/nginx/error.log${NC}"