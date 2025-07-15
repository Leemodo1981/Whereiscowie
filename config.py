import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord Bot Configuration
    DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    # API Keys for vessel tracking services
    VESSELFINDER_API_KEY = os.getenv('VESSELFINDER_API_KEY', '')
    MARINETRAFFIC_API_KEY = os.getenv('MARINETRAFFIC_API_KEY', '')
    SHIPFINDER_API_KEY = os.getenv('SHIPFINDER_API_KEY', '')
    
    # Ship-specific configuration
    SPIRIT_OF_ADVENTURE_IMO = "9818084"
    SPIRIT_OF_ADVENTURE_MMSI = "232026551"
    
    # Bot configuration
    COMMAND_PREFIX = ['!', '/']
    AUTO_UPDATE_TIMES = ['06:00', '12:00', '18:00']  # UTC times for scheduled updates
    RATE_LIMIT_SECONDS = 30
    
    # API endpoints
    VESSELFINDER_BASE_URL = "https://www.vesselfinder.com/api"
    MARINETRAFFIC_BASE_URL = "https://services.marinetraffic.com/api"
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'whereiscowie.log')
    
    # Feature flags
    ENABLE_AUTO_UPDATES = os.getenv('ENABLE_AUTO_UPDATES', 'true').lower() == 'true'
    ENABLE_RATE_LIMITING = os.getenv('ENABLE_RATE_LIMITING', 'true').lower() == 'true'
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.DISCORD_BOT_TOKEN:
            errors.append("DISCORD_BOT_TOKEN is required")
        
        return errors
    
    @classmethod
    def get_available_apis(cls):
        """Get list of available API services"""
        apis = []
        
        if cls.VESSELFINDER_API_KEY:
            apis.append("VesselFinder")
        
        if cls.MARINETRAFFIC_API_KEY:
            apis.append("MarineTraffic")
        
        if cls.SHIPFINDER_API_KEY:
            apis.append("ShipFinder")
        
        return apis
