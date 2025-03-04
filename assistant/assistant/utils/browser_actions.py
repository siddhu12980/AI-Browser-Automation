from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging

logger = logging.getLogger(__name__)

class BrowserActions:
    def __init__(self):
        self.driver = None
        
    def start_browser(self):
        """Initialize the browser"""
        if not self.driver:
            self.driver = webdriver.Chrome()
            self.driver.maximize_window()
    
    def close_browser(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def navigate_to(self, url):
        """Navigate to a specific URL"""
        try:
            self.driver.get(url)
            return True, "Successfully navigated to " + url
        except Exception as e:
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