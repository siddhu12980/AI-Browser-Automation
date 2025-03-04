from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.keys import Keys
import logging

logger = logging.getLogger(__name__)

class BrowserActions:
    def __init__(self):
        self.driver = None
        
    def start_browser(self):
        """Initialize the browser"""
        try:
            if self.driver is not None:
                try:
                    # Check if browser is still responsive
                    self.driver.current_url
                    return
                except:
                    # If not responsive, close it
                    self.close_browser()
            
            # Initialize new browser instance
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-popup-blocking')
            options.add_experimental_option("detach", True)  # Keep browser open
            
            self.driver = webdriver.Chrome(options=options)
            # Navigate to Google to ensure we have an active tab
            self.driver.get("https://www.google.com")
            logger.info("Browser started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    def close_browser(self):
        """Close the browser"""
        try:
            if self.driver:
                self.driver.quit()
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
        finally:
            self.driver = None
    
    def navigate_to(self, url):
        """Navigate to a specific URL in a new tab"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            # Open new tab
            self.driver.execute_script(f"window.open('{url}', '_blank');")
            
            # Switch to the new tab (last tab)
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Wait for the page to load
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            
            return True, f"Successfully navigated to {url}"
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False, f"Failed to navigate: {str(e)}"
    
    def click_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Click an element on the page"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            element.click()
            return True, f"Clicked element: {selector}"
        except TimeoutException:
            return False, f"Element not found: {selector}"
        except Exception as e:
            return False, f"Failed to click: {str(e)}"
    
    def type_text(self, selector, text, by=By.CSS_SELECTOR, timeout=10):
        """Type text into an input field"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            element.clear()
            element.send_keys(text)
            return True, f"Typed text into {selector}"
        except Exception as e:
            return False, f"Failed to type text: {str(e)}"
    
    def get_text(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Get text from an element"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return True, element.text
        except Exception as e:
            return False, f"Failed to get text: {str(e)}"