# QA通关 生产部署清单

## 部署前
- [ ] 服务器: Ubuntu 22.04+, 1GB+ RAM, 10GB+ 磁盘
- [ ] 域名: 已解析到服务器IP
- [ ] 防火墙: 开放 80/443 端口
- [ ] `.env` 文件: SECRET_KEY 已设置（不要用默认值）

## 一键部署
```bash
chmod +x deploy/setup.sh
sudo ./deploy/setup.sh your-domain.com
```

## 手动部署

### 1. 环境
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置 .env
```bash
cp .env.example .env
# 编辑 .env: SECRET_KEY, SMTP_HOST, CORS_ORIGINS
```

### 3. 启动
```bash
# 开发
python -m uvicorn app.main:app --reload --port 8005

# 生产 (4 workers)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8005 --workers 4
```

### 4. Nginx
```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/qa-tools
sudo ln -s /etc/nginx/sites-available/qa-tools /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 5. SSL证书
```bash
sudo certbot --nginx -d your-domain.com
```

### 6. 系统服务
```bash
sudo cp deploy/qa-tools.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now qa-tools
```

## 部署后验证
- [ ] `curl https://your-domain.com/health` 返回 `{"status":"ok"}`
- [ ] 浏览器访问首页，注册测试账号
- [ ] 完成1个关卡，确认进度保存
- [ ] SMTP 配置后测试密码重置流程

## 监控
- Prometheus: `http://127.0.0.1:8005/metrics`
- 日志: `sudo journalctl -u qa-tools -f`
- 健康检查: `http://127.0.0.1:8005/health`

## 备份
```bash
# 每日定时备份 (crontab -e)
0 3 * * * cd /opt/qa-tools/v2-Pro版 && python scripts/backup.py backup
```
