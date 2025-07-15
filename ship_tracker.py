import aiohttp
import asyncio
import discord
import logging
from datetime import datetime, timedelta
import json
import re
from bs4 import BeautifulSoup
from config import Config

logger = logging.getLogger(__name__)

class ShipTracker:
    def __init__(self):
        self.ship_imo = "9818084"
        self.ship_mmsi = "232026551"
        self.ship_name = "SPIRIT OF ADVENTURE"
        self.session = None
        
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'User-Agent': 'WhereIsCowieBot/1.0'}
            )
        return self.session
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def fetch_vesselfinder_data(self):
        """Fetch ship data from VesselFinder website"""
        session = await self.get_session()
        
        # Try API first if key is available
        if Config.VESSELFINDER_API_KEY:
            url = f"https://www.vesselfinder.com/api/pro/ais/{self.ship_imo}"
            try:
                headers = {'Authorization': f'Bearer {Config.VESSELFINDER_API_KEY}'}
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.warning(f"VesselFinder API returned status {response.status}")
            except Exception as e:
                logger.error(f"Error fetching VesselFinder API data: {e}")
        
        # Fallback to public page scraping
        try:
            url = f"https://www.vesselfinder.com/vessels/details/{self.ship_imo}"
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    return self.parse_vesselfinder_html(html)
                else:
                    logger.warning(f"VesselFinder website returned status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching VesselFinder website data: {e}")
            return None
    
    def parse_vesselfinder_html(self, html):
        """Parse VesselFinder HTML page for ship data"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract ship data from the HTML structure
            data = {
                'ship_name': self.ship_name,
                'imo': self.ship_imo,
                'mmsi': self.ship_mmsi,
                'error': False
            }
            
            # Try to find current position text
            position_text = soup.find('div', class_='vessel-position')
            if position_text:
                text = position_text.get_text()
                
                # Extract coordinates using regex
                lat_match = re.search(r'(\d+\.?\d*)[°\s]*([NS])', text)
                lon_match = re.search(r'(\d+\.?\d*)[°\s]*([EW])', text)
                
                if lat_match and lon_match:
                    lat = float(lat_match.group(1))
                    if lat_match.group(2) == 'S':
                        lat = -lat
                    
                    lon = float(lon_match.group(1))
                    if lon_match.group(2) == 'W':
                        lon = -lon
                    
                    data['latitude'] = lat
                    data['longitude'] = lon
            
            # Extract speed
            speed_match = re.search(r'(\d+\.?\d*)\s*knots?', html, re.IGNORECASE)
            if speed_match:
                data['speed'] = float(speed_match.group(1))
            
            # Extract course
            course_match = re.search(r'Course[:\s]*(\d+\.?\d*)[°\s]', html, re.IGNORECASE)
            if course_match:
                data['course'] = float(course_match.group(1))
            
            # Extract destination
            dest_match = re.search(r'destination[:\s]*([^<\n,]+)', html, re.IGNORECASE)
            if dest_match:
                data['destination'] = dest_match.group(1).strip()
            
            # Extract ETA
            eta_match = re.search(r'ETA[:\s]*([^<\n,]+)', html, re.IGNORECASE)
            if eta_match:
                data['eta'] = eta_match.group(1).strip()
                
            # Extract navigation status
            status_match = re.search(r'Navigation Status[:\s]*([^<\n,]+)', html, re.IGNORECASE)
            if status_match:
                data['status'] = status_match.group(1).strip()
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing VesselFinder HTML: {e}")
            return None
    
    async def fetch_marinetraffic_data(self):
        """Fetch ship data from MarineTraffic API as fallback"""
        session = await self.get_session()
        
        # Try public AIS data endpoint
        url = f"https://services.marinetraffic.com/api/exportvessel/v:8/{Config.MARINETRAFFIC_API_KEY}/protocol:jsono/imo:{self.ship_imo}"
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.warning(f"MarineTraffic API returned status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching MarineTraffic data: {e}")
            return None
    
    async def fetch_ais_data(self):
        """Fetch AIS data from multiple sources with fallback"""
        # Try VesselFinder first
        data = await self.fetch_vesselfinder_data()
        if data:
            return self.parse_vesselfinder_data(data)
        
        # Fallback to MarineTraffic
        data = await self.fetch_marinetraffic_data()
        if data:
            return self.parse_marinetraffic_data(data)
        
        # If all APIs fail, return mock data structure with error flag
        return {
            'error': True,
            'message': 'Unable to fetch real-time data from vessel tracking services',
            'ship_name': self.ship_name,
            'imo': self.ship_imo
        }
    
    def parse_vesselfinder_data(self, data):
        """Parse VesselFinder API response"""
        try:
            vessel = data.get('vessel', {})
            return {
                'ship_name': vessel.get('name', self.ship_name),
                'imo': vessel.get('imo', self.ship_imo),
                'mmsi': vessel.get('mmsi', self.ship_mmsi),
                'latitude': vessel.get('lat'),
                'longitude': vessel.get('lon'),
                'speed': vessel.get('speed'),
                'course': vessel.get('course'),
                'heading': vessel.get('heading'),
                'status': vessel.get('status'),
                'destination': vessel.get('destination'),
                'eta': vessel.get('eta'),
                'last_port': vessel.get('last_port'),
                'draught': vessel.get('draught'),
                'flag': vessel.get('flag'),
                'timestamp': vessel.get('timestamp'),
                'error': False
            }
        except Exception as e:
            logger.error(f"Error parsing VesselFinder data: {e}")
            return {'error': True, 'message': 'Error parsing vessel data'}
    
    def parse_marinetraffic_data(self, data):
        """Parse MarineTraffic API response"""
        try:
            if isinstance(data, list) and len(data) > 0:
                vessel = data[0]
                return {
                    'ship_name': vessel.get('SHIPNAME', self.ship_name),
                    'imo': vessel.get('IMO', self.ship_imo),
                    'mmsi': vessel.get('MMSI', self.ship_mmsi),
                    'latitude': vessel.get('LAT'),
                    'longitude': vessel.get('LON'),
                    'speed': vessel.get('SPEED'),
                    'course': vessel.get('COURSE'),
                    'heading': vessel.get('HEADING'),
                    'status': vessel.get('STATUS'),
                    'destination': vessel.get('DESTINATION'),
                    'eta': vessel.get('ETA'),
                    'last_port': vessel.get('LAST_PORT'),
                    'draught': vessel.get('CURRENT_DRAUGHT'),
                    'flag': vessel.get('FLAG'),
                    'timestamp': vessel.get('TIMESTAMP'),
                    'error': False
                }
            else:
                return {'error': True, 'message': 'No vessel data found'}
        except Exception as e:
            logger.error(f"Error parsing MarineTraffic data: {e}")
            return {'error': True, 'message': 'Error parsing vessel data'}
    
    def format_coordinates(self, lat, lon):
        """Format latitude and longitude for display"""
        if lat is None or lon is None:
            return "Unknown"
        
        lat_dir = "N" if lat >= 0 else "S"
        lon_dir = "E" if lon >= 0 else "W"
        
        return f"{abs(lat):.4f}°{lat_dir}, {abs(lon):.4f}°{lon_dir}"
    
    def format_speed(self, speed):
        """Format speed for display"""
        if speed is None:
            return "Unknown"
        
        try:
            speed_knots = float(speed)
            speed_kmh = speed_knots * 1.852
            return f"{speed_knots:.1f} knots ({speed_kmh:.1f} km/h)"
        except (ValueError, TypeError):
            return str(speed)
    
    def format_course(self, course):
        """Format course/heading for display"""
        if course is None:
            return "Unknown"
        
        try:
            course_deg = float(course)
            # Convert to compass direction
            directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                         "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
            direction = directions[int((course_deg + 11.25) / 22.5) % 16]
            return f"{course_deg:.1f}° ({direction})"
        except (ValueError, TypeError):
            return str(course)
    
    def format_eta(self, eta):
        """Format ETA for display"""
        if not eta:
            return "Unknown"
        
        try:
            # Try to parse various ETA formats
            if isinstance(eta, str):
                # Common format: "Jul 16, 09:00"
                return eta
            elif isinstance(eta, (int, float)):
                # Unix timestamp
                eta_dt = datetime.fromtimestamp(eta)
                return eta_dt.strftime("%b %d, %H:%M UTC")
            else:
                return str(eta)
        except Exception:
            return str(eta)
    
    def get_status_emoji(self, status):
        """Get emoji for navigation status"""
        if not status:
            return "❓"
        
        status_lower = str(status).lower()
        
        if "underway" in status_lower or "sailing" in status_lower:
            return "🚢"
        elif "anchor" in status_lower:
            return "⚓"
        elif "port" in status_lower or "dock" in status_lower:
            return "🏠"
        elif "moored" in status_lower:
            return "🔗"
        else:
            return "🚢"
    
    async def get_ship_status_embed(self):
        """Create Discord embed with ship status"""
        ship_data = await self.fetch_ais_data()
        
        if ship_data.get('error'):
            # Create error embed
            embed = discord.Embed(
                title="❌ Data Unavailable",
                description=ship_data.get('message', 'Unable to fetch ship data'),
                color=discord.Color.red()
            )
            embed.add_field(
                name="Ship Information",
                value=f"**Name:** {self.ship_name}\n**IMO:** {self.ship_imo}",
                inline=False
            )
            embed.add_field(
                name="What This Means",
                value="• Ship's AIS transponder may be offline\n• API services temporarily unavailable\n• Ship may be in port with transponder disabled",
                inline=False
            )
            embed.set_footer(text="Try again in a few minutes • Data from vessel tracking APIs")
            return embed
        
        # Create status embed with real data
        status_emoji = self.get_status_emoji(ship_data.get('status'))
        
        embed = discord.Embed(
            title=f"{status_emoji} {ship_data.get('ship_name', self.ship_name)}",
            description="Current position and voyage information",
            color=discord.Color.blue()
        )
        
        # Position information
        coordinates = self.format_coordinates(
            ship_data.get('latitude'), 
            ship_data.get('longitude')
        )
        
        embed.add_field(
            name="📍 Current Position",
            value=coordinates,
            inline=True
        )
        
        # Speed and course
        speed = self.format_speed(ship_data.get('speed'))
        course = self.format_course(ship_data.get('course'))
        
        embed.add_field(
            name="💨 Speed",
            value=speed,
            inline=True
        )
        
        embed.add_field(
            name="🧭 Course",
            value=course,
            inline=True
        )
        
        # Destination and ETA
        destination = ship_data.get('destination', 'Unknown')
        eta = self.format_eta(ship_data.get('eta'))
        
        embed.add_field(
            name="🎯 Destination",
            value=destination,
            inline=True
        )
        
        embed.add_field(
            name="⏰ ETA",
            value=eta,
            inline=True
        )
        
        # Navigation status
        status = ship_data.get('status', 'Unknown')
        embed.add_field(
            name="📊 Status",
            value=status,
            inline=True
        )
        
        # Additional information
        additional_info = []
        
        if ship_data.get('last_port'):
            additional_info.append(f"**Last Port:** {ship_data.get('last_port')}")
        
        if ship_data.get('draught'):
            additional_info.append(f"**Draught:** {ship_data.get('draught')}m")
        
        if ship_data.get('flag'):
            additional_info.append(f"**Flag:** {ship_data.get('flag')}")
        
        if additional_info:
            embed.add_field(
                name="ℹ️ Additional Info",
                value="\n".join(additional_info),
                inline=False
            )
        
        # Timestamp
        if ship_data.get('timestamp'):
            try:
                if isinstance(ship_data['timestamp'], (int, float)):
                    update_time = datetime.fromtimestamp(ship_data['timestamp'])
                    embed.set_footer(text=f"Last updated: {update_time.strftime('%Y-%m-%d %H:%M UTC')} • Data from AIS")
                else:
                    embed.set_footer(text=f"Last updated: {ship_data['timestamp']} • Data from AIS")
            except Exception:
                embed.set_footer(text="Data from vessel tracking APIs")
        else:
            embed.set_footer(text="Data from vessel tracking APIs")
        
        # Add map link if coordinates are available
        if ship_data.get('latitude') and ship_data.get('longitude'):
            map_url = f"https://www.vesselfinder.com/?imo={self.ship_imo}"
            embed.add_field(
                name="🗺️ Track on Map",
                value=f"[View on VesselFinder]({map_url})",
                inline=False
            )
        
        return embed

    def __del__(self):
        """Cleanup when object is destroyed"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            asyncio.create_task(self.session.close())
