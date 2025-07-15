# WhereIsCowie Bot Invite Instructions

## Step 1: Get Your Bot's Application ID

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click on your "Whereiscowie" application
3. Copy the **Application ID** from the General Information page

## Step 2: Create Invite URL

Replace `YOUR_APPLICATION_ID` with the ID you copied:

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_APPLICATION_ID&permissions=277025770496&scope=bot
```

## Step 3: Complete Authorization

1. Open the URL in your browser
2. Select your server from the dropdown
3. Click "Authorize"
4. Complete any captcha

## Troubleshooting

If the bot still doesn't appear:

1. **Check Message Content Intent**:
   - Go to Developer Portal > Your App > Bot
   - Enable "Message Content Intent" under Privileged Gateway Intents
   - Save changes

2. **Verify Bot is Online**:
   - The bot should show as online in your server member list
   - Try `!cowie` command to test

3. **Check Permissions**:
   - Make sure the bot has permission to read/send messages in the channel
   - Check if any channel restrictions are blocking the bot

## Current Status
The bot is running and ready to connect - it just needs proper server authorization.