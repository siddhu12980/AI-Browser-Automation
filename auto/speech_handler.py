import speech_recognition as sr
import pyttsx3
import asyncio
from typing import Optional

class SpeechHandler:
    def __init__(self):
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        # Set properties (optional)
        self.engine.setProperty('rate', 150)    # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume (0-1)

    async def listen_for_command(self) -> Optional[str]:
        """Listen for voice input and convert to text."""
        with sr.Microphone() as source:
            print("Listening... Speak your command")
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio)
                print(f"Recognized: {text}")
                return text
            except sr.WaitTimeoutError:
                print("No speech detected")
                return None
            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                return None

    def speak_response(self, text: str) -> None:
        """Convert text to speech and speak it."""
        print(f"Speaking: {text}")
        self.engine.say(text)
        self.engine.runAndWait() 