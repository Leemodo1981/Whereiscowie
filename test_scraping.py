#!/usr/bin/env python3
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import re

async def test_vesselfinder_scraping():
    """Test scraping VesselFinder for Spirit of Adventure data"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    ship_imo = "9818084"
    url = f"https://www.vesselfinder.com/vessels/details/{ship_imo}"
    
    async with aiohttp.ClientSession() as session:
        try:
            print(f"Testing URL: {url}")
            async with session.get(url, headers=headers) as response:
                print(f"Response status: {response.status}")
                
                if response.status == 200:
                    html = await response.text()
                    print(f"HTML length: {len(html)} characters")
                    
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    text_content = soup.get_text()
                    
                    # Look for key information patterns
                    print("\n=== SEARCHING FOR SHIP DATA ===")
                    
                    # Search for speed
                    speed_matches = re.findall(r'([\d.]+)\s*knots?', text_content, re.IGNORECASE)
                    if speed_matches:
                        print(f"Found speeds: {speed_matches}")
                    
                    # Search for destination
                    dest_matches = re.findall(r'(?:en route to|destination)[:\s]*([^,\n.]+)', text_content, re.IGNORECASE)
                    if dest_matches:
                        print(f"Found destinations: {dest_matches}")
                    
                    # Search for ETA
                    eta_matches = re.findall(r'(?:ETA|expected to arrive)[:\s]*([^,\n.]+)', text_content, re.IGNORECASE)
                    if eta_matches:
                        print(f"Found ETAs: {eta_matches}")
                    
                    # Search for coordinates
                    coord_matches = re.findall(r'([\d.]+)[°\s]*([NS])[,\s]*([\d.]+)[°\s]*([EW])', text_content, re.IGNORECASE)
                    if coord_matches:
                        print(f"Found coordinates: {coord_matches}")
                    
                    # Search for course
                    course_matches = re.findall(r'course[:\s]*([\d.]+)[°\s]', text_content, re.IGNORECASE)
                    if course_matches:
                        print(f"Found courses: {course_matches}")
                    
                    # Show first 1000 characters of text for debugging
                    print(f"\n=== FIRST 1000 CHARS OF PAGE TEXT ===")
                    print(text_content[:1000])
                    
                else:
                    print(f"Failed to fetch page: HTTP {response.status}")
                    
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_vesselfinder_scraping())