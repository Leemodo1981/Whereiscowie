# WhereIsCowie Bot 🚢

A Discord bot that tracks the **Spirit of Adventure** cruise ship in real-time using AIS (Automatic Identification System) data.

## Features

- **Real-time tracking** of Spirit of Adventure cruise ship
- **Current position**, speed, course, and destination
- **ETA information** for next port
- **Automatic scheduled updates** (06:00, 12:00, 16:00 UTC)
- **Multiple data sources** with fallback support
- **User-friendly commands** with rich Discord embeds
- **Error handling** with informative messages

## Commands

| Command | Aliases | Description | Permissions |
|---------|---------|-------------|-------------|
| `!cowie` | `!ship`, `!status`, `!location` | Get current ship status | Everyone |
| `!track` | `!follow` | Enable auto-updates in channel | Manage Channels |
| `!stop_track` | `!unfollow` | Disable auto-updates | Manage Channels |
| `!help` | - | Show help message | Everyone |
| `!info` | `!about` | Show bot and ship information | Everyone |

## Setup Instructions

### 1. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Copy the bot token
5. Enable "Message Content Intent" in the bot settings

### 2. Bot Permissions

The bot needs these permissions:
- Send Messages
- Use Slash Commands
- Embed Links
- Read Message History
- Use External Emojis

**Permission Integer:** `277025770496`

### 3. Installation

1. Clone or download the bot files
2. Install required dependencies:
   ```bash
   pip install discord.py python-dotenv aiohttp beautifulsoup4
   ```

3. Create `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` file and add your Discord bot token:
   ```bash
   DISCORD_BOT_TOKEN=your_bot_token_here
   ```

5. (Optional) Add vessel tracking API keys for enhanced data:
   ```bash
   VESSELFINDER_API_KEY=your_api_key
   MARINETRAFFIC_API_KEY=your_api_key
   ```

### 4. Run the Bot

```bash
python main.py
