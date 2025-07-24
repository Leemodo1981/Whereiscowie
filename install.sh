#!/bin/bash
# WhereIsCowie Bot Installation Script for Ubuntu Server

set -e  # Exit on any error

echo "Installing WhereIsCowie Discord Bot..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo $0"
    exit 1
fi

# Update system
echo "Updating system packages..."
apt update && apt upgrade -y

# Install required packages
echo "Installing required packages..."
apt install software-properties-common curl wget git -y

# Add Python 3.11 repository
add-apt-repository ppa:deadsnakes/ppa -y
apt update

# Install Python 3.11
apt install python3.11 python3.11-pip python3.11-venv -y

# Install Chrome for map screenshots
echo "Installing Google Chrome..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
apt update
apt install google-chrome-stable -y

# Install ChromeDriver
apt install chromium-chromedriver -y

# Install Chrome dependencies for headless mode
apt install libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2 -y

# Create bot user
echo "Creating bot user..."
if ! id "cowiebot" &>/dev/null; then
    adduser --system --group --home /opt/whereiscowie cowiebot
fi

# Create directories
mkdir -p /opt/whereiscowie
chown cowiebot:cowiebot /opt/whereiscowie

# Install Python dependencies
echo "Installing Python dependencies..."
cd /opt/whereiscowie
sudo -u cowiebot python3.11 -m venv venv
sudo -u cowiebot bash -c "source venv/bin/activate && pip install --upgrade pip"
sudo -u cowiebot bash -c "source venv/bin/activate && pip install discord.py==2.5.2 python-dotenv==1.1.1 aiohttp==3.12.14 beautifulsoup4==4.13.4 selenium==4.34.2 pillow==11.3.0 requests==2.32.4 trafilatura==1.14.3"

# Create environment file template
echo "Creating environment file..."
cat > /opt/whereiscowie/.env << EOF
DISCORD_BOT_TOKEN=your_discord_bot_token_here
EOF
chown cowiebot:cowiebot /opt/whereiscowie/.env
chmod 600 /opt/whereiscowie/.env

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/whereiscowie.service << EOF
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

# Environment variables
EnvironmentFile=/opt/whereiscowie/.env

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/whereiscowie

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Copy your bot files to /opt/whereiscowie/"
echo "2. Edit /opt/whereiscowie/.env and add your Discord bot token"
echo "3. Start the service: systemctl enable --now whereiscowie"
echo "4. Check status: systemctl status whereiscowie"
echo ""
echo "View logs: journalctl -u whereiscowie -f"