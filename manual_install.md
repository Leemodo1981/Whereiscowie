# Manual Installation Guide for Ubuntu Server

Run these commands step by step on your Ubuntu server:

## 1. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

## 2. Install Basic Packages
```bash
sudo apt install software-properties-common curl wget git -y
```

## 3. Install Python 3.11
```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv -y
```

## 4. Install Google Chrome
```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable -y
```

## 5. Install ChromeDriver and Dependencies
```bash
sudo apt install chromium-chromedriver -y
sudo apt install libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2 -y
```

## 6. Create Bot User and Directory
```bash
sudo adduser --system --group --home /opt/whereiscowie cowiebot
sudo mkdir -p /opt/whereiscowie
sudo chown cowiebot:cowiebot /opt/whereiscowie
```

## 7. Copy Bot Files
Copy these files to `/opt/whereiscowie/`:
- main.py
- ship_tracker.py
- config.py
- map_screenshot.py

```bash
sudo cp main.py ship_tracker.py config.py map_screenshot.py /opt/whereiscowie/
sudo chown cowiebot:cowiebot /opt/whereiscowie/*.py
```

## 8. Create Python Virtual Environment
```bash
cd /opt/whereiscowie
sudo -u cowiebot python3.11 -m venv venv
sudo -u cowiebot bash -c "source venv/bin/activate && pip install --upgrade pip"
```

## 9. Install Python Dependencies
```bash
sudo -u cowiebot bash -c "source venv/bin/activate && pip install discord.py==2.5.2 python-dotenv==1.1.1 aiohttp==3.12.14 beautifulsoup4==4.13.4 selenium==4.34.2 pillow==11.3.0 requests==2.32.4 trafilatura==1.14.3"
```

## 10. Create Environment File
```bash
sudo tee /opt/whereiscowie/.env << EOF
DISCORD_BOT_TOKEN=your_discord_bot_token_here
EOF
sudo chown cowiebot:cowiebot /opt/whereiscowie/.env
sudo chmod 600 /opt/whereiscowie/.env
```

## 11. Edit Discord Token
```bash
sudo nano /opt/whereiscowie/.env
```
Replace `your_discord_bot_token_here` with your actual Discord bot token.

## 12. Create Systemd Service
```bash
sudo tee /etc/systemd/system/whereiscowie.service << 'EOF'
[Unit]
Description=WhereIsCowie Discord Bot
After=network.target

[Service]
Type=simple
User=cowiebot
Group=cowiebot
WorkingDirectory=/opt/whereiscowie
Environment=PATH=/opt/whereiscowie/venv/bin
ExecStart=/opt/whereiscowie/venv/bin/python main.py
Restart=always
RestartSec=5

EnvironmentFile=/opt/whereiscowie/.env

NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/whereiscowie

[Install]
WantedBy=multi-user.target
EOF
```

## 13. Start the Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable whereiscowie
sudo systemctl start whereiscowie
```

## 14. Check Status
```bash
sudo systemctl status whereiscowie
```

## 15. View Logs
```bash
sudo journalctl -u whereiscowie -f
```

## Discord Bot Setup

1. Go to https://discord.com/developers/applications
2. Create a new application and bot
3. Enable "Message Content Intent" in Bot settings
4. Copy the bot token and paste it in `/opt/whereiscowie/.env`
5. Generate invite URL with permissions:
   - Send Messages
   - Embed Links
   - Attach Files
   - Read Message History

## Test Commands

Once running, test in Discord:
- `!cowie` - Get ship status with map
- `!track` - Enable auto-updates (admin only)
- `!commands` - List all commands

## Common Issues

**If bot won't start:**
```bash
sudo journalctl -u whereiscowie -n 50
```

**Test manually:**
```bash
sudo -u cowiebot bash
cd /opt/whereiscowie
source venv/bin/activate
python main.py
```

**Restart bot:**
```bash
sudo systemctl restart whereiscowie
```