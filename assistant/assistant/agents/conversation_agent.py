from openai import OpenAI
import logging
import json
from assistant.utils.prompt import conversation_prompt
logger = logging.getLogger(__name__)

class ConversationAgent:
    def __init__(self, client: OpenAI):
        self.client = client
    
    def process_conversation(self, user_input: str) -> str:
        """Handle general conversation"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": conversation_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7
            )
            
            # Parse the JSON response
            json_response = response.choices[0].message.content
            logger.info(f"Raw JSON response in conversation agent: {json_response}")
            
            # Convert the string to a dictionary
            response_dict = json.loads(json_response)
            
            # Extract the 'response' field
            return response_dict.get("response", "I apologize, but I'm having trouble generating a response right now.")
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return "I apologize, but I'm having trouble understanding the response format."
        except Exception as e:
            logger.error(f"Error in conversation: {e}")
            return "I apologize, but I'm having trouble processing that conversation."
