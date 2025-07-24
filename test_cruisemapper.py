#!/usr/bin/env python3
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

async def test_cruisemapper():
    """Test CruiseMapper data extraction"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    
    url = "https://www.cruisemapper.com/?imo=9818084"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            print(f"Status: {response.status}")
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                text = soup.get_text()
                
                print("=== SEARCHING FOR SHIP DATA ===")
                
                # Look for current position
                position_patterns = [
                    r'Current position[:\s]*([^.\n]+)',
                    r'Position[:\s]*([^.\n]+)',
                    r'Location[:\s]*([^.\n]+)',
                ]
                
                for pattern in position_patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        print(f"Position found: {match.group(1).strip()}")
                
                # Look for coordinates
                coord_patterns = [
                    r'([\d.]+)°?\s*([NS])[,\s]+([\d.]+)°?\s*([EW])',
                    r'Latitude[:\s]*([\d.]+).*?Longitude[:\s]*([\d.]+)',
                ]
                
                for pattern in coord_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        print(f"Coordinates found: {matches}")
                
                # Look for speed, destination, ETA
                speed_match = re.search(r'Speed[:\s]*([\d.]+)', text, re.IGNORECASE)
                if speed_match:
                    print(f"Speed: {speed_match.group(1)}")
                
                dest_match = re.search(r'Destination[:\s]*([^.\n]+)', text, re.IGNORECASE)
                if dest_match:
                    print(f"Destination: {dest_match.group(1).strip()}")
                
                eta_match = re.search(r'ETA[:\s]*([^.\n]+)', text, re.IGNORECASE)
                if eta_match:
                    print(f"ETA: {eta_match.group(1).strip()}")
                
                # Look for any structured data or JSON
                if 'Spirit of Adventure' in text:
                    print("Ship name found in page")
                
                # Check for any JavaScript data
                script_tags = soup.find_all('script')
                for script in script_tags:
                    if script.string and ('imo' in script.string.lower() or 'position' in script.string.lower()):
                        print("Found relevant script data:")
                        print(script.string[:500])  # First 500 chars
                        break

if __name__ == "__main__":
    asyncio.run(test_cruisemapper())