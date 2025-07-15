#!/usr/bin/env python3
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

async def find_coordinates():
    """Find coordinate data in VesselFinder page"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    url = "https://www.vesselfinder.com/vessels/details/9818084"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                text = soup.get_text()
                
                print("=== SEARCHING FOR COORDINATE PATTERNS ===")
                
                # Look for any number patterns that could be coordinates
                coord_patterns = [
                    r'([\d.]+)°?\s*([NS])[,\s]+([\d.]+)°?\s*([EW])',
                    r'(\d{1,3}\.\d+)[°\s]*([NS])[,\s]*(\d{1,3}\.\d+)[°\s]*([EW])',
                    r'Latitude[:\s]*([\d.]+)',
                    r'Longitude[:\s]*([\d.]+)',
                    r'Lat[:\s]*([\d.]+)',
                    r'Lon[:\s]*([\d.]+)',
                ]
                
                for i, pattern in enumerate(coord_patterns):
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        print(f"Pattern {i+1}: {pattern}")
                        print(f"Matches: {matches[:5]}")  # Show first 5 matches
                        print()
                
                # Look for table data specifically
                print("=== SEARCHING IN VOYAGE DATA TABLE ===")
                voyage_section = re.search(r'Voyage Data.*?Recent Port Calls', text, re.DOTALL | re.IGNORECASE)
                if voyage_section:
                    voyage_text = voyage_section.group(0)
                    print("Voyage section found, searching for coordinates...")
                    
                    # Look for any decimal numbers that could be coordinates
                    decimal_numbers = re.findall(r'\b(\d{1,3}\.\d+)\b', voyage_text)
                    print(f"Decimal numbers in voyage section: {decimal_numbers}")
                
                # Search for specific coordinate indicators
                print("=== SEARCHING FOR POSITION INDICATORS ===")
                position_indicators = [
                    r'Current position.*?(\d+\.\d+).*?(\d+\.\d+)',
                    r'Position.*?(\d+\.\d+).*?(\d+\.\d+)',
                    r'coordinates.*?(\d+\.\d+).*?(\d+\.\d+)',
                ]
                
                for pattern in position_indicators:
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    if match:
                        print(f"Position found: {match.groups()}")

if __name__ == "__main__":
    asyncio.run(find_coordinates())