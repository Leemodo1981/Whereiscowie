#!/usr/bin/env python3
"""
Map screenshot functionality for ship tracking bot
Takes screenshots of ship locations from online maps
"""

import asyncio
import os
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

logger = logging.getLogger(__name__)

class MapScreenshotter:
    def __init__(self):
        self.driver = None
    
    def setup_driver(self):
        """Setup Chrome driver for screenshots"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1200,800")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return False
    
    def close_driver(self):
        """Close the Chrome driver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.error(f"Error closing driver: {e}")
            self.driver = None
    
    async def get_ship_map_screenshot(self, latitude, longitude, ship_name="Spirit of Adventure"):
        """
        Take a screenshot of the ship's position on a map
        Returns the file path of the screenshot or None if failed
        """
        if not latitude or not longitude:
            logger.warning("No coordinates provided for map screenshot")
            return None
        
        try:
            # Setup driver
            if not self.setup_driver():
                return None
            
            # Use OpenStreetMap with marker
            map_url = f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}&zoom=8#map=8/{latitude}/{longitude}"
            
            logger.info(f"Taking map screenshot for coordinates: {latitude}, {longitude}")
            
            # Load the map
            self.driver.get(map_url)
            
            # Wait for map to load
            time.sleep(3)
            
            # Create temporary file for screenshot
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            screenshot_path = temp_file.name
            temp_file.close()
            
            # Take screenshot
            self.driver.save_screenshot(screenshot_path)
            
            logger.info(f"Map screenshot saved to: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Error taking map screenshot: {e}")
            return None
        finally:
            self.close_driver()
    
    async def get_ship_map_screenshot_cruisemapper(self, imo):
        """
        Take a screenshot of CruiseMapper showing the ship
        Returns the file path of the screenshot or None if failed
        """
        try:
            # Setup driver
            if not self.setup_driver():
                return None
            
            # Use CruiseMapper URL
            map_url = f"https://www.cruisemapper.com/?imo={imo}"
            
            logger.info(f"Taking CruiseMapper screenshot for IMO: {imo}")
            
            # Load the map
            self.driver.get(map_url)
            
            # Wait for map to load
            time.sleep(5)
            
            # Try to remove any popups or cookie banners
            try:
                # Look for common popup/banner close buttons
                close_buttons = self.driver.find_elements(By.CSS_SELECTOR, "[class*='close'], [class*='dismiss'], [aria-label*='close']")
                for button in close_buttons[:3]:  # Only try first 3
                    try:
                        button.click()
                        time.sleep(0.5)
                    except:
                        pass
            except:
                pass
            
            # Create temporary file for screenshot
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            screenshot_path = temp_file.name
            temp_file.close()
            
            # Take screenshot
            self.driver.save_screenshot(screenshot_path)
            
            logger.info(f"CruiseMapper screenshot saved to: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            logger.error(f"Error taking CruiseMapper screenshot: {e}")
            return None
        finally:
            self.close_driver()

async def test_screenshot():
    """Test the screenshot functionality"""
    screenshotter = MapScreenshotter()
    
    # Test coordinates (English Channel)
    lat, lon = 47.18238, -7.0743
    
    screenshot_path = await screenshotter.get_ship_map_screenshot(lat, lon)
    if screenshot_path:
        print(f"Screenshot saved to: {screenshot_path}")
        return screenshot_path
    else:
        print("Failed to take screenshot")
        return None

if __name__ == "__main__":
    asyncio.run(test_screenshot())