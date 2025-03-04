from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, Any, Tuple, Optional, List, TypedDict, Union
from dataclasses import dataclass
import logging
import time
from selenium.webdriver.common.keys import Keys

logger = logging.getLogger(__name__)

# Input type definitions
@dataclass
class NavigateInput:
    url: str

@dataclass
class SearchInput:
    query: str
    search_box_selector: str = 'input[name="q"]'

@dataclass
class ClickInput:
    selector: str
    by: str = By.CSS_SELECTOR
    index: int = 0
    timeout: int = 10

@dataclass
class TypeInput:
    selector: str
    text: str
    by: str = By.CSS_SELECTOR
    timeout: int = 10

@dataclass
class ReadInput:
    selector: str
    by: str = By.CSS_SELECTOR
    timeout: int = 10

@dataclass
class ScrollInput:
    direction: str = "down"
    amount: int = 300

@dataclass
class WaitInput:
    selector: str
    by: str = By.CSS_SELECTOR
    timeout: int = 10

@dataclass
class FormInput:
    fields: Dict[str, str]
    timeout: int = 10

# Standard response type
class BrowserResponse(TypedDict):
    status: str
    action: str
    message: str
    data: Optional[Any]
    error: Optional[str]

class BrowserTools:
    def __init__(self, driver):
        self.driver = driver
        self.default_timeout = 10
    
    def navigate(self, input_data: NavigateInput) -> BrowserResponse:
        """
        Navigate to a specific URL in a new tab
        
        Args:
            input_data: NavigateInput containing URL
            
        Returns:
            BrowserResponse with navigation result
        """
        try:
            url = input_data.url
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            self.driver.execute_script(f"window.open('{url}', '_blank');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            return {
                "status": "success",
                "action": "navigate",
                "message": f"Successfully navigated to {url}",
                "data": {"url": url},
                "error": None
            }
        except Exception as e:
            return {
                "status": "error",
                "action": "navigate",
                "message": f"Failed to navigate: {str(e)}",
                "data": None,
                "error": str(e)
            }
    
    def search(self, input_data: SearchInput) -> BrowserResponse:
        """
        Perform a search using the provided query
        
        Args:
            input_data: SearchInput containing query and selector
            
        Returns:
            BrowserResponse with search result
        """
        try:
            # Wait for initial page load
            WebDriverWait(self.driver, self.default_timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            # Define search box locators with multiple strategies
            search_locators = [
                (By.CSS_SELECTOR, input_data.search_box_selector),
                (By.CSS_SELECTOR, "input[name='q']"),
                (By.CSS_SELECTOR, "input#search"),
                (By.CSS_SELECTOR, "#search input"),
                (By.NAME, "q"),
                (By.TAG_NAME, "input"),
            ]
            
            search_box = None
            last_error = None
            
            # Try each locator strategy
            for by, selector in search_locators:
                try:
                    # First wait for presence
                    element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    
                    # Then wait for interactability
                    search_box = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    
                    # Verify element is truly interactive
                    if search_box.is_displayed() and search_box.is_enabled():
                        # Scroll element into view
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", search_box)
                        time.sleep(0.5)  # Let the scroll complete
                        
                        # Try to focus the element
                        self.driver.execute_script("arguments[0].focus();", search_box)
                        
                        # Try to click it
                        try:
                            search_box.click()
                        except:
                            # If direct click fails, try JavaScript click
                            self.driver.execute_script("arguments[0].click();", search_box)
                        
                        break
                except Exception as e:
                    last_error = e
                    logger.debug(f"Locator ({by}, {selector}) failed: {str(e)}")
                    continue
            
            if not search_box:
                raise Exception(f"Could not find interactive search box. Last error: {last_error}")
            
            # Clear the search box
            try:
                # Try multiple clearing methods
                search_box.clear()
                self.driver.execute_script("arguments[0].value = '';", search_box)
                search_box.send_keys(Keys.CONTROL + "a")  # Select all text
                search_box.send_keys(Keys.DELETE)         # Delete selected text
            except Exception as e:
                logger.warning(f"Clear attempt failed: {e}")
            
            # Type the search query
            try:
                # Type slowly to avoid issues
                for char in input_data.query:
                    search_box.send_keys(char)
                    time.sleep(0.1)
            except Exception as e:
                # Fallback to JavaScript if typing fails
                logger.warning(f"Normal typing failed: {e}")
                self.driver.execute_script(
                    "arguments[0].value = arguments[1];", 
                    search_box, 
                    input_data.query
                )
                
            
            # Submit the search
            try:
                # Try multiple submit methods
                search_box.send_keys(Keys.RETURN)
                time.sleep(0.5)
                
                if "google" in self.driver.current_url:
                    # Click search button for Google
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            button.click()
                            time.sleep(0.5)
                            

                            
                       
                            break
                
            except Exception as submit_error:
                logger.warning(f"Normal submit failed: {submit_error}")
                try:
                    # Try JavaScript form submit
                    self.driver.execute_script(
                        "arguments[0].form.submit();", 
                        search_box
                    )
                except Exception as js_error:
                    logger.error(f"JavaScript submit failed: {js_error}")
                    raise Exception("Failed to submit search")
            
            # Wait for results page
            WebDriverWait(self.driver, self.default_timeout).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # search_results = self.driver.find_elements(By.CSS_SELECTOR, "h3")[:3]
                    
              
            search_results = self.driver.find_elements(By.CSS_SELECTOR, "div.tF2Cxc a")[:3]  # Updated selector

      
            print("------ search results ------ \n")
            print(search_results)
            print("\n------ search results ------")
            
            # print("Top 3 Results:")
            # for i, result in enumerate(search_results, 1):
            #     parent_link = result.find_element(By.XPATH, "./ancestor::a")
            #     print(f"{i}. {parent_link.get_attribute('href')}")

            print("\nTop 3 Results:")
            for i, result in enumerate(search_results, 1):
                print(f"{i}. {result.get_attribute('href')}")
                                   
            
            return {
                "status": "success",
                "action": "search",
                "message": f"Successfully searched for '{input_data.query}'",
                "data": {
                    "query": input_data.query,
                    "url": self.driver.current_url
                },
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return {
                "status": "error",
                "action": "search",
                "message": f"Search failed: {str(e)}",
                "data": None,
                "error": str(e)
            }


    def click_element(self, input_data: ClickInput) -> BrowserResponse:
        """
        Click an element on the page
        
        Args:
            input_data: ClickInput containing selector details
            
        Returns:
            BrowserResponse with click result
        """
        try:
            elements = WebDriverWait(self.driver, input_data.timeout).until(
                EC.presence_of_all_elements_located((input_data.by, input_data.selector))
            )
            
            if 0 <= input_data.index < len(elements):
                elements[input_data.index].click()
                return {
                    "status": "success",
                    "action": "click",
                    "message": f"Successfully clicked element {input_data.selector} at index {input_data.index}",
                    "data": {"selector": input_data.selector, "index": input_data.index},
                    "error": None
                }
            else:
                return {
                    "status": "error",
                    "action": "click",
                    "message": f"Index {input_data.index} out of range",
                    "data": None,
                    "error": "IndexError"
                }
        except Exception as e:
            return {
                "status": "error",
                "action": "click",
                "message": f"Click failed: {str(e)}",
                "data": None,
                "error": str(e)
            }
    
    def type_text(self, input_data: TypeInput) -> BrowserResponse:
        """
        Type text into an input field
        
        Args:
            input_data: TypeInput containing selector and text
            
        Returns:
            BrowserResponse with typing result
        """
        try:
            element = WebDriverWait(self.driver, input_data.timeout).until(
                EC.presence_of_element_located((input_data.by, input_data.selector))
            )
            element.clear()
            element.send_keys(input_data.text)
            
            return {
                "status": "success",
                "action": "type",
                "message": f"Successfully typed text into {input_data.selector}",
                "data": {"selector": input_data.selector, "text": input_data.text},
                "error": None
            }
        except Exception as e:
            return {
                "status": "error",
                "action": "type",
                "message": f"Typing failed: {str(e)}",
                "data": None,
                "error": str(e)
            }
    
    def read_text(self, input_data: ReadInput) -> BrowserResponse:
        """
        Read text from an element
        
        Args:
            input_data: ReadInput containing selector details
            
        Returns:
            BrowserResponse with extracted text
        """
        try:
            element = WebDriverWait(self.driver, input_data.timeout).until(
                EC.presence_of_element_located((input_data.by, input_data.selector))
            )
            text = element.text
            
            return {
                "status": "success",
                "action": "read",
                "message": "Successfully read text",
                "data": {"text": text, "selector": input_data.selector},
                "error": None
            }
        except Exception as e:
            return {
                "status": "error",
                "action": "read",
                "message": f"Reading failed: {str(e)}",
                "data": None,
                "error": str(e)
            }
    
    def scroll_page(self, input_data: ScrollInput) -> BrowserResponse:
        """
        Scroll the page
        
        Args:
            input_data: ScrollInput containing direction and amount
            
        Returns:
            BrowserResponse with scroll result
        """
        try:
            amount = -input_data.amount if input_data.direction.lower() == "up" else input_data.amount
            self.driver.execute_script(f"window.scrollBy(0, {amount});")
            
            return {
                "status": "success",
                "action": "scroll",
                "message": f"Successfully scrolled {input_data.direction}",
                "data": {"direction": input_data.direction, "amount": amount},
                "error": None
            }
        except Exception as e:
            return {
                "status": "error",
                "action": "scroll",
                "message": f"Scrolling failed: {str(e)}",
                "data": None,
                "error": str(e)
            }
    
    def wait_for_element(self, input_data: WaitInput) -> BrowserResponse:
        """
        Wait for an element to appear
        
        Args:
            input_data: WaitInput containing selector details
            
        Returns:
            BrowserResponse with wait result
        """
        try:
            element = WebDriverWait(self.driver, input_data.timeout).until(
                EC.presence_of_element_located((input_data.by, input_data.selector))
            )
            
            return {
                "status": "success",
                "action": "wait",
                "message": f"Element {input_data.selector} found",
                "data": {"selector": input_data.selector},
                "error": None
            }
        except Exception as e:
            return {
                "status": "error",
                "action": "wait",
                "message": f"Wait failed: {str(e)}",
                "data": None,
                "error": str(e)
            }
    
    def fill_form(self, input_data: FormInput) -> BrowserResponse:
        """
        Fill multiple form fields
        
        Args:
            input_data: FormInput containing field mappings
            
        Returns:
            BrowserResponse with form fill result
        """
        results = []
        try:
            for selector, value in input_data.fields.items():
                element = WebDriverWait(self.driver, input_data.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                element.clear()
                element.send_keys(value)
                results.append(f"Filled {selector}")
            
            return {
                "status": "success",
                "action": "fill_form",
                "message": "Successfully filled form",
                "data": {"fields": input_data.fields, "results": results},
                "error": None
            }
        except Exception as e:
            return {
                "status": "error",
                "action": "fill_form",
                "message": f"Form fill failed: {str(e)}",
                "data": {"partial_results": results},
                "error": str(e)
            }