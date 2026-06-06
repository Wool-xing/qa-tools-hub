#!/bin/bash
# QA通关 一键部署脚本 (Ubuntu/Debian)
set -e

APP_DIR="/opt/qa-tools/v2-Pro版"
DOMAIN="${1:-localhost}"

echo "=== QA通关 生产部署 ==="

# 1. Install system dependencies
echo "[1/6] 安装依赖..."
sudo apt update -qq
sudo apt install -y python3 python3-venv nginx certbot python3-certbot-nginx

# 2. Create app directory
echo "[2/6] 创建目录..."
sudo mkdir -p "$APP_DIR" /opt/qa-tools/data /opt/qa-tools/backups
sudo cp -r . "$APP_DIR"

# 3. Setup Python venv
echo "[3/6] 配置Python环境..."
python3 -m venv "$APP_DIR/.venv"
source "$APP_DIR/.venv/bin/activate"
pip install -r "$APP_DIR/requirements.txt"

# 4. Generate SECRET_KEY if not set
if ! grep -q "SECRET_KEY=." "$APP_DIR/.env" 2>/dev/null; then
    echo "[4/6] 生成密钥..."
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/SECRET_KEY=/SECRET_KEY=$SECRET_KEY/" "$APP_DIR/.env"
fi

# 5. Setup Nginx
echo "[5/6] 配置Nginx..."
sudo cp "$APP_DIR/deploy/nginx.conf" "/etc/nginx/sites-available/qa-tools"
sudo sed -i "s/your-domain.com/$DOMAIN/g" "/etc/nginx/sites-available/qa-tools"
sudo ln -sf "/etc/nginx/sites-available/qa-tools" "/etc/nginx/sites-enabled/"
sudo nginx -t && sudo systemctl reload nginx

# 6. Setup systemd
echo "[6/6] 配置系统服务..."
sudo cp "$APP_DIR/deploy/qa-tools.service" "/etc/systemd/system/"
sudo systemctl daemon-reload
sudo systemctl enable qa-tools
sudo systemctl start qa-tools

echo ""
echo "=== 部署完成 ==="
echo "访问: https://$DOMAIN"
echo "检查: sudo systemctl status qa-tools"
echo "日志: sudo journalctl -u qa-tools -f"
