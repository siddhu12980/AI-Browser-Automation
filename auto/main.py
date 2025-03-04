from langchain_openai import ChatOpenAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
import datetime
import logging
from PIL import Image, ImageTk
import math
import os
import logging

load_dotenv()

from browser_use import Agent, Controller
from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContext
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))    

browser = Browser(
	config=BrowserConfig(
		# NOTE: you need to close your chrome browser - so that this can open your browser in debug mode
		chrome_instance_path='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
	)
)

class GUILogHandler(logging.Handler):
        """Custom handler to route logs to the GUI"""
        def __init__(self, gui):
            super().__init__()
            self.gui = gui

        def emit(self, record):
            # Map logging levels to our GUI log levels
            level_map = {
                'DEBUG': 'info',
                'INFO': 'info',
                'WARNING': 'warning',
                'ERROR': 'error',
                'CRITICAL': 'error',
                'SUCCESS': 'success',
                'RESULT': 'result'
            }
            gui_level = level_map.get(record.levelname, 'info')
            
            # Send to GUI
            self.gui.update_browser_log(record.getMessage(), gui_level)
            

async def humanize_response(response: str, llm: ChatOpenAI) -> str:
   
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
    
    result = await llm.ainvoke(prompt)
    return result.content

class ModernScrolledText(scrolledtext.ScrolledText):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.vbar.configure(
            background=kwargs.get('bg', '#2E2E2E'),
            troughcolor=kwargs.get('bg', '#2E2E2E'),
            activebackground=kwargs.get('fg', '#FFFFFF'),
            highlightthickness=0
        )

class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Voice Assistant")
        self.root.geometry("1200x800")  
        
        self.bg_color = "#1E1E1E"  
        self.fg_color = "#FFFFFF"
        self.accent_color = "#007AFF"
        self.secondary_bg = "#2D2D2D"
        self.success_color = "#4CAF50"
        self.error_color = "#FF3B30"
        self.warning_color = "#FF9500"
        
        self.root.configure(bg=self.bg_color)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        self.setup_styles()
        
        self.main_container = ttk.Frame(root, style='Dark.TFrame', padding=20)
        self.main_container.grid(row=0, column=0, sticky='nsew')
        self.main_container.grid_columnconfigure(0, weight=2)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        self.setup_header()
        self.setup_conversation_column()
        self.setup_browser_column()
        
        self.is_listening = False
        self.message_queue = queue.Queue()
        self.engine = pyttsx3.init()
        self.setup_voice()
        
    def setup_header(self):
        self.header = ttk.Frame(self.main_container, style='Dark.TFrame')
        self.header.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 20))
        
        title_container = ttk.Frame(self.header, style='Dark.TFrame')
        title_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title = ttk.Label(
            title_container,
            text="AI Voice Assistant",
            style='Title.TLabel'
        )
        title.pack(side=tk.LEFT)
        
        self.status_indicator = ttk.Label(
            title_container,
            text="●",
            style='Ready.TLabel'
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(10, 5))
        
        self.status_label = ttk.Label(
            title_container,
            text="Ready",
            style='Status.TLabel'
        )
        self.status_label.pack(side=tk.LEFT)
        
    def setup_conversation_column(self):
        
        conv_container = ttk.Frame(self.main_container, style='Dark.TFrame')
        conv_container.grid(row=1, column=0, sticky='nsew', padx=(0, 10))
        conv_container.grid_columnconfigure(0, weight=1)
        conv_container.grid_rowconfigure(0, weight=1)
        
        conv_header = ttk.Label(
            conv_container,
            text="Conversation",
            style='Header.TLabel'
        )
        conv_header.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        self.conversation_text = ModernScrolledText(
            conv_container,
            wrap=tk.WORD,
            font=('Segoe UI', 11),
            bg=self.secondary_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            selectbackground=self.accent_color,
            relief='flat',
            padx=15,
            pady=15,
            borderwidth=0
        )
        self.conversation_text.grid(row=1, column=0, sticky='nsew')
        
        control_frame = ttk.Frame(conv_container, style='Dark.TFrame')
        control_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        
        self.start_button = ttk.Button(
            control_frame,
            text="Start Listening",
            command=self.toggle_listening,
            style='Accent.TButton'
        )
        self.start_button.pack(side=tk.LEFT)
        
    def setup_browser_column(self):
        browser_container = ttk.Frame(self.main_container, style='Dark.TFrame')
        browser_container.grid(row=1, column=1, sticky='nsew')
        browser_container.grid_columnconfigure(0, weight=1)
        browser_container.grid_rowconfigure(1, weight=1)
        
        browser_header = ttk.Label(
            browser_container,
            text="Browser Activity",
            style='Header.TLabel'
        )
        browser_header.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        self.browser_log = ModernScrolledText(
            browser_container,
            wrap=tk.WORD,
            font=('Cascadia Code', 10),
            bg=self.secondary_bg,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            selectbackground=self.accent_color,
            relief='flat',
            padx=15,
            pady=15,
            borderwidth=0
        )
        self.browser_log.grid(row=1, column=0, sticky='nsew')
        
        action_frame = ttk.Frame(browser_container, style='Action.TFrame')
        action_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        
        self.action_indicator = ttk.Label(
            action_frame,
            text="⚡",  
            style='Action.TLabel'
        )
        self.action_indicator.pack(side=tk.LEFT, padx=(0, 5))
        
        self.action_label = ttk.Label(
            action_frame,
            text="No active tasks",
            style='Action.TLabel'
        )
        self.action_label.pack(side=tk.LEFT)
        
    def setup_styles(self):
        style = ttk.Style()
        
        style.configure('Dark.TFrame', background=self.bg_color)
        style.configure('Action.TFrame', background=self.bg_color)
        
        style.configure(
            'Title.TLabel',
            background=self.bg_color,
            foreground=self.fg_color,
            font=('Segoe UI', 24, 'bold')
        )
        
        style.configure(
            'Header.TLabel',
            background=self.bg_color,
            foreground=self.fg_color,
            font=('Segoe UI', 16, 'bold')
        )
        
        style.configure(
            'Status.TLabel',
            background=self.bg_color,
            foreground=self.accent_color,
            font=('Segoe UI', 12)
        )
        
        style.configure(
            'Ready.TLabel',
            background=self.bg_color,
            foreground=self.success_color,
            font=('Segoe UI', 14)
        )
        
        style.configure(
            'Action.TLabel',
            background=self.bg_color,
            foreground=self.accent_color,
            font=('Segoe UI', 12)
        )
        
        style.configure(
            'Accent.TButton',
            padding=(30, 15),
            font=('Segoe UI', 12, 'bold')
        )
        
    def update_status(self, status):
        self.status_label.config(text=status)
        
        if status == "Ready":
            self.status_indicator.configure(style='Ready.TLabel')
        elif status == "Listening...":
            self.status_indicator.configure(foreground=self.accent_color)
        elif "Error" in status:
            self.status_indicator.configure(foreground=self.error_color)
        else:
            self.status_indicator.configure(foreground=self.warning_color)
            
        self.root.update()
        
    def update_browser_log(self, message, level="info"):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        self.browser_log.tag_configure("timestamp", foreground="#666666")
        self.browser_log.tag_configure("info", foreground=self.fg_color)
        self.browser_log.tag_configure("success", foreground=self.success_color)
        self.browser_log.tag_configure("error", foreground=self.error_color)
        self.browser_log.tag_configure("action", foreground=self.accent_color)
        
        self.browser_log.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        if level == "success":
            self.browser_log.insert(tk.END, "✓ ", "success")
        elif level == "error":
            self.browser_log.insert(tk.END, "✗ ", "error")
        elif level == "action":
            self.browser_log.insert(tk.END, "→ ", "action")
        else:
            self.browser_log.insert(tk.END, "• ", "info")
            
        self.browser_log.insert(tk.END, f"{message}\n", level)
        self.browser_log.see(tk.END)
        
    def update_browser_action(self, action):
        self.action_label.config(text=action)
        
    def update_conversation(self, speaker, text):
        timestamp = datetime.datetime.now().strftime("%H:%M")
        
        self.conversation_text.tag_configure("timestamp", foreground="#666666")
        self.conversation_text.tag_configure("user", foreground=self.success_color)
        self.conversation_text.tag_configure("assistant", foreground=self.accent_color)
        self.conversation_text.tag_configure("message", foreground=self.fg_color)
        
        self.conversation_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        if speaker == "You":
            self.conversation_text.insert(tk.END, f"{speaker}: ", "user")
        else:
            self.conversation_text.insert(tk.END, f"{speaker}: ", "assistant")
            
        self.conversation_text.insert(tk.END, f"{text}\n\n", "message")
        self.conversation_text.see(tk.END)
        
    def toggle_listening(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.start_button.config(text="Stop Listening")
            threading.Thread(target=self.listen_loop, daemon=True).start()
        else:
            self.start_button.config(text="Start Listening")
            
    class GUILogHandler(logging.Handler):
        """Custom handler to route logs to the GUI"""
        def __init__(self, gui):
            super().__init__()
            self.gui = gui

        def emit(self, record):
            # Map logging levels to our GUI log levels
            level_map = {
                'DEBUG': 'info',
                'INFO': 'info',
                'WARNING': 'warning',
                'ERROR': 'error',
                'CRITICAL': 'error',
                'SUCCESS': 'success'
            }
            gui_level = level_map.get(record.levelname, 'info')
            
            # Send to GUI
            self.gui.update_browser_log(record.getMessage(), gui_level)

    async def process_voice_command(self, task):
        try:
            llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
            controller = Controller()

            file_handler = logging.FileHandler('log.txt')
            file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', 
                                                      datefmt='%Y-%m-%d %H:%M:%S'))
            file_handler.setLevel(logging.INFO)
            
            gui_handler = GUILogHandler(self)
            gui_handler.setLevel(logging.INFO)

            logger = logging.getLogger('browser_use')
            logger.addHandler(file_handler)
            logger.addHandler(gui_handler)
            
            agent = Agent(task=task, llm=llm, browser=browser, controller=controller)
            
            result = await agent.run()

            # Clean up logging
            logger.removeHandler(file_handler)
            logger.removeHandler(gui_handler)
            file_handler.close()
            
            humanized_result = await humanize_response(str(result), llm)
            return humanized_result
            
        except Exception as e:
            self.update_browser_log(f"Error: {str(e)}", "error")
            self.update_browser_action("Error occurred")
            return f"Error processing command: {str(e)}"
            
    def setup_voice(self):
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        
    def listen_loop(self):
        r = sr.Recognizer()
        
        r.pause_threshold = 1.0  
        r.phrase_threshold = 0.3  
        r.non_speaking_duration = 0.5  
        
        while self.is_listening:
            try:
                self.update_status("Listening...")
                with sr.Microphone() as source:
                    r.dynamic_energy_threshold = False
                    
                    audio = r.listen(source, timeout=10, phrase_time_limit=10)
                
                self.update_status("Processing speech...")
                command = r.recognize_google(audio, language="en-IN", show_all=False)
                self.update_conversation("You", command)
                
                self.update_status("Processing command...")
                result = asyncio.run(self.process_voice_command(command))
                
                self.update_conversation("Assistant", result)
                self.speak_text(result)
                
            except sr.WaitTimeoutError:
                self.update_status("Listening timed out - please speak")
            except sr.UnknownValueError:
                self.update_status("Could not understand audio")
            except sr.RequestError as e:
                self.update_status(f"Could not request results: {e}")
            except Exception as e:
                self.update_status(f"Error: {str(e)}")
                
    def speak_text(self, text):
        self.update_status("Speaking")
        if isinstance(text, str):
            self.engine.say(text)
        else:
            self.engine.say(str(text))
        self.engine.runAndWait()
        self.update_status("Ready")

def main():
    root = tk.Tk()
    app = VoiceAssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    asyncio.run(main())