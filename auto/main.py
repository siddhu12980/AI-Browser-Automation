from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3

load_dotenv()

def speak_text(text):
    # Initialize text-to-speech engine
    engine = pyttsx3.init()
    # Configure voice properties
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # Use female voice
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 0.9)  # Volume level
    # Convert text to speech
    if isinstance(text, str):
        engine.say(text)
    else:
        engine.say(str(text))
    # Play the speech
    engine.runAndWait()

async def humanize_response(response: str, llm: ChatOpenAI) -> str:
    """
    Process the response through GPT to make it more conversational and human-friendly
    """
    prompt = f"""
    You are a helpful AI assistant having a natural conversation. Transform the following response into clear, concise, and friendly speech. The response may be in a non-English language, code, JSON, markdown or other formats:

    {response}

    Guidelines:
    - Convert any formatted text (markdown, code blocks etc.) into natural speech
    - Get straight to the key information without filler phrases
    - Use a warm, conversational tone while being succinct
    - If the response is in another language, translate it naturally to English
    - Remove any formatting characters (**, --, etc.)
    - Focus on clarity and brevity while maintaining a helpful demeanor
    """
    
    result = await llm.ainvoke(prompt) # Changed invoke to ainvoke for async support
    return result.content

def get_voice_command():
    # Initialize recognizer
    r = sr.Recognizer()
    
    # Use microphone as source
    with sr.Microphone() as source:
        print("Listening for your command...")
        # Adjust for ambient noise
        r.adjust_for_ambient_noise(source, duration=1)
        # Set dynamic energy threshold
        r.dynamic_energy_threshold = True
        # Listen for audio input
        audio = r.listen(source)
        
        try:
            command = r.recognize_google(audio)
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

async def main():
    # Get voice command
    task = get_voice_command()
    
    if task:
        # Initialize the language model
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0) # Fixed model name typo
        
        agent = Agent(
            task=task,
            llm=llm,
        )
        result = await agent.run()
        
        # Humanize the response
        humanized_result = await humanize_response(str(result), llm)
        
        # Convert the humanized result to speech
        speak_text(humanized_result)
    else:
        print("No valid command received")
        speak_text("No valid command received")

asyncio.run(main())