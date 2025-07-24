# WhereIsCowie Bot - Ubuntu Server Installation Guide

## Prerequisites

Your Ubuntu server needs:
- Ubuntu 18.04 or newer
- Root or sudo access
- Internet connection

## Step 1: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

## Step 2: Install Required System Packages

```bash
# Install Python 3.11 and pip
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Install Chrome and dependencies for map screenshots
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable -y

# Install ChromeDriver
sudo apt install chromium-chromedriver -y

# Install additional dependencies
sudo apt install git curl -y
```

## Step 3: Create Bot User (Optional but Recommended)

```bash
sudo adduser --system --group --home /opt/whereiscowie cowiebot
sudo mkdir -p /opt/whereiscowie
sudo chown cowiebot:cowiebot /opt/whereiscowie
```

## Step 4: Download Bot Files

```bash
# Switch to bot directory
cd /opt/whereiscowie

# Clone or download your bot files
# If you have the files locally, copy them to this directory
sudo -u cowiebot git clone <your-repo-url> .
# OR copy files manually:
# sudo cp -r /path/to/your/bot/files/* /opt/whereiscowie/
# sudo chown -R cowiebot:cowiebot /opt/whereiscowie
```

## Step 5: Install Python Dependencies

```bash
cd /opt/whereiscowie

# Create virtual environment
sudo -u cowiebot python3.11 -m venv venv

# Activate virtual environment and install dependencies
sudo -u cowiebot bash -c "source venv/bin/activate && pip install --upgrade pip"
sudo -u cowiebot bash -c "source venv/bin/activate && pip install discord.py python-dotenv aiohttp beautifulsoup4 selenium pillow requests"
```

## Step 6: Configure Environment Variables

```bash
# Create environment file
sudo -u cowiebot touch /opt/whereiscowie/.env

# Edit the environment file
sudo nano /opt/whereiscowie/.env
```

Add the following content to `.env`:
```
DISCORD_BOT_TOKEN=your_discord_bot_token_here
```

## Step 7: Create Systemd Service

Create the service file:
```bash
sudo nano /etc/systemd/system/whereiscowie.service
```

Add this content:
```ini
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
```

## Step 8: Start the Bot Service

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable whereiscowie

# Start the service
sudo systemctl start whereiscowie

# Check status
sudo systemctl status whereiscowie
```

## Step 9: Monitor Logs

```bash
# View real-time logs
sudo journalctl -u whereiscowie -f

# View recent logs
sudo journalctl -u whereiscowie --since "1 hour ago"
```

## Step 10: Bot Management Commands

```bash
# Start the bot
sudo systemctl start whereiscowie

# Stop the bot
sudo systemctl stop whereiscowie

# Restart the bot
sudo systemctl restart whereiscowie

# Check if bot is running
sudo systemctl is-active whereiscowie

# View detailed status
sudo systemctl status whereiscowie
```

## Troubleshooting

### Bot Won't Start
1. Check logs: `sudo journalctl -u whereiscowie -n 50`
2. Verify token: `sudo cat /opt/whereiscowie/.env`
3. Test manually: 
   ```bash
   sudo -u cowiebot bash
   cd /opt/whereiscowie
   source venv/bin/activate
   python main.py
   ```

### Chrome/Screenshot Issues
1. Install missing dependencies:
   ```bash
   sudo apt install libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2 -y
   ```

2. Test Chrome:
   ```bash
   google-chrome --headless --no-sandbox --dump-dom https://www.google.com
   ```

### Permission Issues
```bash
sudo chown -R cowiebot:cowiebot /opt/whereiscowie
sudo chmod +x /opt/whereiscowie/main.py
```

## Updating the Bot

```bash
# Stop the service
sudo systemctl stop whereiscowie

# Update files (if using git)
cd /opt/whereiscowie
sudo -u cowiebot git pull

# Or copy new files manually
# sudo cp -r /path/to/new/files/* /opt/whereiscowie/
# sudo chown -R cowiebot:cowiebot /opt/whereiscowie

# Update dependencies if needed
sudo -u cowiebot bash -c "source venv/bin/activate && pip install --upgrade discord.py python-dotenv aiohttp beautifulsoup4 selenium pillow requests"

# Start the service
sudo systemctl start whereiscowie
```

## Security Notes

- The bot runs as a dedicated user with limited permissions
- Chrome runs in no-sandbox mode for screenshots (required in containers/limited environments)
- Keep your Discord bot token secure and never share it
- Regularly update the system and bot dependencies

## Discord Bot Setup

1. Go to https://discord.com/developers/applications
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token to your `.env` file
5. Enable required intents: "Message Content Intent"
6. Go to OAuth2 > URL Generator
7. Select scopes: `bot`
8. Select permissions: `Send Messages`, `Embed Links`, `Attach Files`
9. Use the generated URL to invite the bot to your Discord server

## Testing

Once installed, test these commands in Discord:
- `!cowie` - Get ship status with map
- `!track` - Enable auto-updates (admin only)
- `!commands` - List all commands

The bot will automatically send updates at 06:00, 12:00, and 16:00 UTC daily.