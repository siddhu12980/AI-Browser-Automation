from assistant.utils.browser_actions import BrowserActions
from openai import OpenAI
import json
import logging
from assistant.utils.prompt import browser_task_prompt

logger = logging.getLogger(__name__)

class BrowserAgent:
    def __init__(self, client: OpenAI):
        self.browser = BrowserActions()
        self.client = client
        self.browser.start_browser()
        
    def __del__(self):
        self.browser.close_browser()
    
    def process_command(self, user_input: str) -> str:
        """
        Process user commands and execute browser actions
        """
        try:
            
            logger.info(f"User input -------- : {user_input}")
            # Get AI interpretation of the command
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": browser_task_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7
            )
            
            # Parse the response
            command = json.loads(response.choices[0].message.content)
            
            
            logger.info(f"Command -------- : {command}")
            # Execute the command
            result = self._execute_command(command)
            return result
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return f"Sorry, I couldn't process that command: {str(e)}"
    
    def _execute_command(self, command):
        """Execute the parsed browser command"""
        action = command.get("action")
        params = command.get("params", {})
        
        if action == "navigate":
            success, message = self.browser.navigate_to(params.get("url"))
        elif action == "click":
            success, message = self.browser.click_element(params.get("selector"))
        elif action == "type":
            success, message = self.browser.type_text(
                params.get("selector"),
                params.get("text")
            )
        elif action == "read":
            success, message = self.browser.get_text(params.get("selector"))
        else:
            return f"Unknown action: {action}"
        
        return message if success else f"Failed: {message}"