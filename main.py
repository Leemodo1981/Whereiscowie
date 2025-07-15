import discord
from discord.ext import commands, tasks
import asyncio
import logging
import os
from datetime import time
from dotenv import load_dotenv
from ship_tracker import ShipTracker
from config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('whereiscowie.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WhereIsCowieBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=['!', '/'],
            intents=intents,
            description="Spirit of Adventure cruise ship tracking bot"
        )
        self.ship_tracker = ShipTracker()
        self.auto_update_channel = None
        
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("Setting up WhereIsCowieBot...")
        # Start the periodic update task
        if not self.periodic_update.is_running():
            self.periodic_update.start()
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has landed! Connected to {len(self.guilds)} servers.')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="Spirit of Adventure sail the seas"
        )
        await self.change_presence(activity=activity)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏱️ Command on cooldown. Try again in {error.retry_after:.1f}s")
        else:
            logger.error(f"Command error: {error}")
            await ctx.send("❌ An error occurred while processing your command.")
    
    @tasks.loop(time=[time(6, 0), time(12, 0), time(16, 0)])
    async def periodic_update(self):
        """Send periodic updates about the ship at 06:00, 12:00, and 16:00 UTC"""
        if self.auto_update_channel:
            try:
                embed = await self.ship_tracker.get_ship_status_embed()
                await self.auto_update_channel.send("🚢 **Scheduled Spirit of Adventure Update**", embed=embed)
                logger.info("Sent scheduled update")
            except Exception as e:
                logger.error(f"Error sending scheduled update: {e}")

# Initialize bot
bot = WhereIsCowieBot()

@bot.command(name='cowie', aliases=['ship', 'status', 'location'])
@commands.cooldown(1, 30, commands.BucketType.user)  # 30 second cooldown per user
async def get_ship_status(ctx):
    """Get current status of Spirit of Adventure"""
    logger.info(f"Ship status requested by {ctx.author} in {ctx.guild}")
    
    # Send typing indicator
    async with ctx.typing():
        try:
            embed = await bot.ship_tracker.get_ship_status_embed()
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting ship status: {e}")
            error_embed = discord.Embed(
                title="❌ Error",
                description="Unable to fetch ship data at the moment. Please try again later.",
                color=discord.Color.red()
            )
            error_embed.add_field(
                name="Possible Issues",
                value="• API service temporarily unavailable\n• Network connectivity issues\n• Ship AIS transponder offline",
                inline=False
            )
            await ctx.send(embed=error_embed)

@bot.command(name='track', aliases=['follow'])
@commands.has_permissions(manage_channels=True)
async def setup_auto_updates(ctx):
    """Setup automatic updates in current channel (Admin only)"""
    bot.auto_update_channel = ctx.channel
    
    embed = discord.Embed(
        title="🔔 Auto-Updates Enabled",
        description=f"I'll now send periodic updates about Spirit of Adventure in {ctx.channel.mention}",
        color=discord.Color.green()
    )
    embed.add_field(
        name="Update Schedule",
        value="06:00, 12:00, 16:00 UTC daily",
        inline=True
    )
    embed.add_field(
        name="Disable Updates",
        value="Use `!stop_track` command",
        inline=True
    )
    
    await ctx.send(embed=embed)
    logger.info(f"Auto-updates enabled in {ctx.channel} by {ctx.author}")

@bot.command(name='stop_track', aliases=['unfollow'])
@commands.has_permissions(manage_channels=True)
async def disable_auto_updates(ctx):
    """Disable automatic updates (Admin only)"""
    bot.auto_update_channel = None
    
    embed = discord.Embed(
        title="🔕 Auto-Updates Disabled",
        description="Periodic updates have been turned off.",
        color=discord.Color.orange()
    )
    
    await ctx.send(embed=embed)
    logger.info(f"Auto-updates disabled by {ctx.author}")

@bot.command(name='commands')
async def custom_help(ctx):
    """Show bot commands and information"""
    embed = discord.Embed(
        title="🚢 WhereIsCowie Bot - Commands",
        description="Track the Spirit of Adventure cruise ship in real-time!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🔍 **!cowie** (or !ship, !status, !location)",
        value="Get current ship location, destination, speed, and ETA",
        inline=False
    )
    
    embed.add_field(
        name="🔔 **!track** (Admin only)",
        value="Enable automatic updates in this channel at 06:00, 12:00, 16:00 UTC",
        inline=False
    )
    
    embed.add_field(
        name="🔕 **!stop_track** (Admin only)",
        value="Disable automatic updates",
        inline=False
    )
    
    embed.add_field(
        name="📋 **!commands**",
        value="Show this help message",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ About Spirit of Adventure",
        value="• IMO: 9818084\n• Built: 2020\n• Flag: United Kingdom\n• Type: Passenger Cruise Ship",
        inline=False
    )
    
    embed.set_footer(text="Data sourced from AIS vessel tracking • Updates every few minutes")
    
    await ctx.send(embed=embed)

@bot.command(name='info', aliases=['about'])
async def bot_info(ctx):
    """Show information about the bot and ship"""
    embed = discord.Embed(
        title="🚢 About WhereIsCowie Bot",
        description="I track the Spirit of Adventure cruise ship using real-time AIS data!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🚢 Spirit of Adventure Details",
        value="• **IMO:** 9818084\n• **MMSI:** 232026551\n• **Built:** 2020\n• **Flag:** United Kingdom\n• **Length:** 236m\n• **Gross Tonnage:** 58,119",
        inline=True
    )
    
    embed.add_field(
        name="📡 Data Sources",
        value="• AIS (Automatic Identification System)\n• VesselFinder API\n• Real-time position updates",
        inline=True
    )
    
    embed.add_field(
        name="🔄 Update Schedule",
        value="• Manual: On-demand via commands\n• Auto: 06:00, 12:00, 16:00 UTC daily (if enabled)",
        inline=False
    )
    
    embed.set_footer(text="Created for tracking Spirit of Adventure • Data accuracy depends on ship's AIS transponder")
    
    await ctx.send(embed=embed)

if __name__ == "__main__":
    # Get Discord bot token from environment
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        logger.error("DISCORD_BOT_TOKEN environment variable not set!")
        print("❌ Error: DISCORD_BOT_TOKEN environment variable is required!")
        print("Please set your Discord bot token in the .env file")
        exit(1)
    
    try:
        logger.info("Starting WhereIsCowie bot...")
        bot.run(token, log_handler=None)  # We handle logging ourselves
    except discord.LoginFailure:
        logger.error("Invalid Discord bot token!")
        print("❌ Error: Invalid Discord bot token!")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"❌ Error starting bot: {e}")
