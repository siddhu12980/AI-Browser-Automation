import speech_recognition as sr
import pyttsx3
import logging
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        
        # Configure voice properties
        self.engine.setProperty('rate', 150)    # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        # Get available voices and set a good voice
        voices = self.engine.getProperty('voices')
        # Try to find a female voice (usually sounds more natural)
        female_voice = next((voice for voice in voices if 'female' in voice.name.lower()), None)
        if female_voice:
            self.engine.setProperty('voice', female_voice.id)
        elif voices:
            # If no female voice found, use the first available voice
            self.engine.setProperty('voice', voices[0].id)

        # Initialize Groq client
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        self.client = OpenAI(
            api_key=groq_api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        
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
        Get response from Groq API
        """
        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",  # Using Mixtral model
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant. Keep your responses concise and natural."},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting response from Groq: {e}")
            return "I apologize, but I'm having trouble generating a response right now."

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
            # Using Google's speech recognition
            text = self.recognizer.recognize_google(audio)
            logger.info(f"You said: {text}")
            
            # Get AI response using Groq
            response = self.get_ai_response(text)
            logger.info(f"AI response: {response}")
            
            # Speak the response
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

def main():
    speech_handler = SpeechHandler()
    while True:
        success, response = speech_handler.listen_and_respond()
        if not success:
            print(f"Error: {response}")
        
        user_input = input("Press Enter to continue or 'q' to quit: ")
        if user_input.lower() == 'q':
            break

if __name__ == "__main__":
    main() 