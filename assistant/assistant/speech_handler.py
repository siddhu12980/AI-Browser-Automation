import speech_recognition as sr
import pyttsx3
import logging
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from assistant.agents.browser_agent import BrowserAgent
from assistant.agents.conversation_agent import ConversationAgent
from assistant.utils.prompt import prompt
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)    # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        # Set voice properties
        voices = self.engine.getProperty('voices')
        female_voice = next((voice for voice in voices if 'female' in voice.name.lower()), None)
        if female_voice:
            self.engine.setProperty('voice', female_voice.id)
        elif voices:
            self.engine.setProperty('voice', voices[0].id)

        # Initialize OpenAI client
        self.client = OpenAI()
        
        # Initialize agents
        self.browser_agent = BrowserAgent(self.client)
        self.conversation_agent = ConversationAgent(self.client)
        
        # Adjust for ambient noise
        with self.microphone as source:
            logger.info("Adjusting for ambient noise. Please wait...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            logger.info("Ambient noise adjustment complete.")
    
    def speak(self, text):
        """
        Convert text to speech
        """
        logger.info(f"Speaking: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def get_ai_response(self, user_input):
        """
        Get response from AI, determining whether to use browser or conversation agent
        """
        try:
            # First, determine if this is a browser automation request
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7
            )
            
            # Parse the response
            logger.info(f"Raw response: {response.choices[0].message.content}")
            
            task_type = json.loads(response.choices[0].message.content)
            
            logger.info(f"Task type: {task_type}")
            
            if task_type.get("is_browser_task"):
                
                return self.browser_agent.process_command(user_input)
            else:
                return self.conversation_agent.process_conversation(user_input)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return "I apologize, but I'm having trouble understanding the response format."
        except Exception as e:
            logger.error(f"Error getting response: {e}")
            return "I apologize, but I'm having trouble processing your request."

    def listen_and_respond(self):
        """
        Listen for speech input and respond with AI-generated voice.
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            with self.microphone as source:
                logger.info("Listening... Say something!")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
            logger.info("Processing speech...")
            text = self.recognizer.recognize_google(audio)
            logger.info(f"You said: {text}")
            
            response = self.get_ai_response(text)
            logger.info(f"AI response: {response}")
            
            self.speak(response)
            return True, response
            
        except sr.WaitTimeoutError:
            return False, "Listening timed out. Please try again."
        except sr.UnknownValueError:
            return False, "Could not understand the audio"
        except sr.RequestError as e:
            return False, f"Could not request results; {str(e)}"
        except Exception as e:
            return False, f"An error occurred: {str(e)}"

    def __del__(self):
        """Cleanup when the object is destroyed"""
        if hasattr(self, 'browser_agent'):
            del self.browser_agent