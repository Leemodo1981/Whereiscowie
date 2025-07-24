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
        
        # Fallback to public page scraping with browser headers
        try:
            url = f"https://www.vesselfinder.com/vessels/details/{self.ship_imo}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    logger.info(f"Successfully fetched VesselFinder page for IMO {self.ship_imo}")
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
            text_content = soup.get_text()
            
            # Extract ship data using the proven working patterns
            data = {
                'ship_name': self.ship_name,
                'imo': self.ship_imo,
                'mmsi': self.ship_mmsi,
                'error': False
            }
            
            # Extract speed - pattern: "sailing at a speed of 17.5 knots"
            speed_match = re.search(r'sailing at a speed of ([\d.]+) knots', text_content, re.IGNORECASE)
            if speed_match:
                data['speed'] = float(speed_match.group(1))
            
            # Extract destination - pattern: "en route to the port of Riga, Latvia"
            dest_match = re.search(r'en route to (?:the port of )?([^,\n]+)', text_content, re.IGNORECASE)
            if dest_match:
                data['destination'] = dest_match.group(1).strip()
            
            # Extract ETA - pattern: "expected to arrive there on Jul 16, 09:00"
            eta_match = re.search(r'expected to arrive there on ([^.\n]+)', text_content, re.IGNORECASE)
            if eta_match:
                data['eta'] = eta_match.group(1).strip()
            
            # Extract current location - multiple patterns
            location_patterns = [
                r'position.*?is\s*at ([^r]+?) reported',  # Original pattern
                r'(?:is|was)\s*at\s*([^,.]+?)(?:\s*reported|\s*,|\s*\.)',  # General "at location"
                r'current(?:ly)?\s*(?:in|at)\s*([^,.]+)',  # "currently in/at location"
                r'(?:sailing|navigating|moving)\s*(?:in|through|at)\s*([^,.]+)',  # "sailing in location"
            ]
            
            for pattern in location_patterns:
                location_match = re.search(pattern, text_content, re.IGNORECASE)
                if location_match:
                    location = location_match.group(1).strip()
                    # Clean up common artifacts
                    location = re.sub(r'\s*reported.*', '', location)
                    location = re.sub(r'\s*by AIS.*', '', location)
                    if len(location) > 3 and location.lower() not in ['the', 'and', 'was', 'now']:
                        data['current_location'] = location
                        break
            
            # Extract last update time - pattern: "reported 1 min ago"
            time_match = re.search(r'reported ([^b]+?) by AIS', text_content, re.IGNORECASE)
            if time_match:
                data['last_update'] = time_match.group(1).strip()
            
            # Set status as "Under way" if we have speed and destination
            if data.get('speed') and data.get('destination'):
                data['status'] = 'Under way'
            
            # Extract course and coordinates from the table data
            course_match = re.search(r'Course / Speed\s*([\d.]+)°', text_content, re.IGNORECASE)
            if course_match:
                data['course'] = float(course_match.group(1))
            
            # Extract coordinates from latitude/longitude patterns in the page
            # Look for patterns like "59.4237° N, 24.7536° E" or similar
            coord_patterns = [
                r'([\d.]+)°?\s*([NS])[,\s]+([\d.]+)°?\s*([EW])',
                r'Latitude[:\s]*([\d.]+)[°\s]*([NS]).*?Longitude[:\s]*([\d.]+)[°\s]*([EW])',
                r'Lat[:\s]*([\d.]+)[°\s]*([NS]).*?Lon[:\s]*([\d.]+)[°\s]*([EW])'
            ]
            
            for pattern in coord_patterns:
                coord_match = re.search(pattern, text_content, re.IGNORECASE | re.DOTALL)
                if coord_match:
                    lat = float(coord_match.group(1))
                    lat_dir = coord_match.group(2).upper()
                    lon = float(coord_match.group(3))
                    lon_dir = coord_match.group(4).upper()
                    
                    if lat_dir == 'S':
                        lat = -lat
                    if lon_dir == 'W':
                        lon = -lon
                    
                    data['latitude'] = lat
                    data['longitude'] = lon
                    break
            
            logger.info(f"Parsed ship data: speed={data.get('speed')}, dest={data.get('destination')}, eta={data.get('eta')}")
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
    
    async def fetch_cruisemapper_data(self):
        """Fetch ship data from CruiseMapper"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            
            url = f"https://www.cruisemapper.com/?imo={self.ship_imo}"
            session = await self.get_session()
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    logger.info(f"Successfully fetched CruiseMapper page for IMO {self.ship_imo}")
                    return await response.text()
                else:
                    logger.warning(f"CruiseMapper returned status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching CruiseMapper data: {e}")
            return None
    
    async def fetch_ais_data(self):
        """Fetch AIS data from multiple sources with fallback"""
        # Try CruiseMapper first (has exact coordinates)
        data = await self.fetch_cruisemapper_data()
        if data:
            parsed_data = self.parse_cruisemapper_data(data)
            if parsed_data and not parsed_data.get('error'):
                return parsed_data
        
        # Fallback to VesselFinder (web scraping works, good for general location)
        data = await self.fetch_vesselfinder_data()
        if data:
            return self.parse_vesselfinder_data(data)
        
        # Only show error if all sources failed
        return {
            'error': True,
            'message': 'Unable to fetch real-time data from vessel tracking services',
            'ship_name': self.ship_name,
            'imo': self.ship_imo
        }
    
    def parse_vesselfinder_data(self, data):
        """Parse VesselFinder data (both API and HTML scraping)"""
        try:
            # If it's HTML scraping data, return as-is (already parsed)
            if isinstance(data, dict) and not data.get('vessel'):
                return data
            
            # If it's API data, parse the vessel structure
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
    
    def parse_cruisemapper_data(self, html_content):
        """Parse ship data from CruiseMapper HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            text_content = soup.get_text()
            
            data = {
                'ship_name': self.ship_name,
                'imo': self.ship_imo,
                'mmsi': self.ship_mmsi
            }
            
            # Extract coordinates from JavaScript config
            coord_match = re.search(r'"lat":([\d.-]+),"lon":([\d.-]+)', html_content)
            if coord_match:
                lat = float(coord_match.group(1))
                lon = float(coord_match.group(2))
                data['latitude'] = lat
                data['longitude'] = lon
            
            # Extract speed - pattern: "Speed17 kn" or similar
            speed_match = re.search(r'Speed\s*([\d.]+)\s*kn', text_content, re.IGNORECASE)
            if speed_match:
                speed = float(speed_match.group(1))
                data['speed'] = speed
            
            # Extract destination and ETA - pattern: "GB DVR > GI GIB ETAJuly 27, 05:00"
            dest_eta_match = re.search(r'>\s*([A-Z]{2})\s*([A-Z]{3})\s*ETA([^S]+)', text_content)
            if dest_eta_match:
                # Map common port codes to readable names
                port_codes = {
                    'GIB': 'Gibraltar',
                    'DVR': 'Dover',
                    'SOU': 'Southampton',
                    'LIS': 'Lisbon',
                    'BAR': 'Barcelona'
                }
                dest_code = dest_eta_match.group(2)
                data['destination'] = port_codes.get(dest_code, dest_code)
                data['eta'] = dest_eta_match.group(3).strip()
            
            # Set status based on speed
            speed_val = data.get('speed')
            if speed_val and isinstance(speed_val, (int, float)) and speed_val > 0:
                data['status'] = 'Under way'
            else:
                data['status'] = 'At anchor'
            
            # Extract current location name if available
            lat_val = data.get('latitude')
            lon_val = data.get('longitude')
            if lat_val and lon_val and isinstance(lat_val, (int, float)) and isinstance(lon_val, (int, float)):
                # Determine general area based on coordinates
                if 40 < lat_val < 60 and -10 < lon_val < 30:  # European waters
                    if 48 < lat_val < 52 and -6 < lon_val < 2:  # English Channel
                        data['current_location'] = 'English Channel'
                    elif 35 < lat_val < 37 and -6 < lon_val < -5:  # Gibraltar area
                        data['current_location'] = 'Strait of Gibraltar'
                    elif 54 < lat_val < 60 and 10 < lon_val < 30:  # Baltic Sea
                        data['current_location'] = 'Baltic Sea'
                    else:
                        data['current_location'] = 'European Waters'
            
            logger.info(f"Parsed CruiseMapper data: speed={data.get('speed')}, dest={data.get('destination')}, eta={data.get('eta')}, coords=({data.get('latitude')}, {data.get('longitude')})")
            return data
            
        except Exception as e:
            logger.error(f"Error parsing CruiseMapper data: {e}")
            return {'error': True, 'message': 'Error parsing vessel data'}
    
    def format_coordinates(self, lat, lon, location=None):
        """Format latitude and longitude for display"""
        if lat is not None and lon is not None:
            lat_dir = "N" if lat >= 0 else "S"
            lon_dir = "E" if lon >= 0 else "W"
            return f"{abs(lat):.4f}°{lat_dir}, {abs(lon):.4f}°{lon_dir}"
        elif location:
            return location
        else:
            return "Unknown"
    
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
            ship_data.get('longitude'),
            ship_data.get('current_location')
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
