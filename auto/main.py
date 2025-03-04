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

load_dotenv()

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

class ModernScrolledText(scrolledtext.ScrolledText):
    """Custom scrolled text widget with modern styling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure scrollbar colors
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
        self.root.geometry("1200x800")  # Increased window size
        
        # Set theme colors
        self.bg_color = "#1E1E1E"  # Darker background
        self.fg_color = "#FFFFFF"
        self.accent_color = "#007AFF"
        self.secondary_bg = "#2D2D2D"
        self.success_color = "#4CAF50"
        self.error_color = "#FF3B30"
        self.warning_color = "#FF9500"
        
        # Configure root window
        self.root.configure(bg=self.bg_color)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Configure styles
        self.setup_styles()
        
        # Create main container
        self.main_container = ttk.Frame(root, style='Dark.TFrame', padding=20)
        self.main_container.grid(row=0, column=0, sticky='nsew')
        self.main_container.grid_columnconfigure(0, weight=2)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        # Setup UI components
        self.setup_header()
        self.setup_conversation_column()
        self.setup_browser_column()
        
        # Initialize other components
        self.is_listening = False
        self.message_queue = queue.Queue()
        self.engine = pyttsx3.init()
        self.setup_voice()
        
    def setup_header(self):
        """Setup the header section"""
        # Header container
        self.header = ttk.Frame(self.main_container, style='Dark.TFrame')
        self.header.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 20))
        
        # Title and status container
        title_container = ttk.Frame(self.header, style='Dark.TFrame')
        title_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # App title
        title = ttk.Label(
            title_container,
            text="AI Voice Assistant",
            style='Title.TLabel'
        )
        title.pack(side=tk.LEFT)
        
        # Status indicator (dot)
        self.status_indicator = ttk.Label(
            title_container,
            text="●",
            style='Ready.TLabel'
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(10, 5))
        
        # Status text
        self.status_label = ttk.Label(
            title_container,
            text="Ready",
            style='Status.TLabel'
        )
        self.status_label.pack(side=tk.LEFT)
        
    def setup_conversation_column(self):
        """Setup the conversation column"""
        # Conversation container
        conv_container = ttk.Frame(self.main_container, style='Dark.TFrame')
        conv_container.grid(row=1, column=0, sticky='nsew', padx=(0, 10))
        conv_container.grid_columnconfigure(0, weight=1)
        conv_container.grid_rowconfigure(0, weight=1)
        
        # Conversation header
        conv_header = ttk.Label(
            conv_container,
            text="Conversation",
            style='Header.TLabel'
        )
        conv_header.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        # Conversation text area
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
        
        # Control frame
        control_frame = ttk.Frame(conv_container, style='Dark.TFrame')
        control_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        
        # Start button with modern styling
        self.start_button = ttk.Button(
            control_frame,
            text="Start Listening",
            command=self.toggle_listening,
            style='Accent.TButton'
        )
        self.start_button.pack(side=tk.LEFT)
        
    def setup_browser_column(self):
        """Setup the browser activity column"""
        # Browser container
        browser_container = ttk.Frame(self.main_container, style='Dark.TFrame')
        browser_container.grid(row=1, column=1, sticky='nsew')
        browser_container.grid_columnconfigure(0, weight=1)
        browser_container.grid_rowconfigure(1, weight=1)
        
        # Browser header
        browser_header = ttk.Label(
            browser_container,
            text="Browser Activity",
            style='Header.TLabel'
        )
        browser_header.grid(row=0, column=0, sticky='w', pady=(0, 10))
        
        # Browser log
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
        
        # Current action frame
        action_frame = ttk.Frame(browser_container, style='Action.TFrame')
        action_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        
        # Action indicator
        self.action_indicator = ttk.Label(
            action_frame,
            text="⚡",  # Lightning bolt for activity
            style='Action.TLabel'
        )
        self.action_indicator.pack(side=tk.LEFT, padx=(0, 5))
        
        # Action label
        self.action_label = ttk.Label(
            action_frame,
            text="No active tasks",
            style='Action.TLabel'
        )
        self.action_label.pack(side=tk.LEFT)
        
    def setup_styles(self):
        """Configure custom styles for widgets"""
        style = ttk.Style()
        
        # Frame styles
        style.configure('Dark.TFrame', background=self.bg_color)
        style.configure('Action.TFrame', background=self.bg_color)
        
        # Label styles
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
        
        # Button styles
        style.configure(
            'Accent.TButton',
            padding=(30, 15),
            font=('Segoe UI', 12, 'bold')
        )
        
    def update_status(self, status):
        """Update the status display"""
        self.status_label.config(text=status)
        
        # Update status indicator color based on state
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
        """Update the browser activity log with styled messages"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Configure tags for different message levels
        self.browser_log.tag_configure("timestamp", foreground="#666666")
        self.browser_log.tag_configure("info", foreground=self.fg_color)
        self.browser_log.tag_configure("success", foreground=self.success_color)
        self.browser_log.tag_configure("error", foreground=self.error_color)
        self.browser_log.tag_configure("action", foreground=self.accent_color)
        
        # Insert the log message with appropriate styling
        self.browser_log.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add an emoji indicator based on level
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
        """Update the current browser action display"""
        self.action_label.config(text=action)
        
    def update_conversation(self, speaker, text):
        """Add a new message to the conversation history with enhanced styling"""
        timestamp = datetime.datetime.now().strftime("%H:%M")
        
        # Configure message tags
        self.conversation_text.tag_configure("timestamp", foreground="#666666")
        self.conversation_text.tag_configure("user", foreground=self.success_color)
        self.conversation_text.tag_configure("assistant", foreground=self.accent_color)
        self.conversation_text.tag_configure("message", foreground=self.fg_color)
        
        # Insert timestamp
        self.conversation_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Insert speaker and message
        if speaker == "You":
            self.conversation_text.insert(tk.END, f"{speaker}: ", "user")
        else:
            self.conversation_text.insert(tk.END, f"{speaker}: ", "assistant")
            
        self.conversation_text.insert(tk.END, f"{text}\n\n", "message")
        self.conversation_text.see(tk.END)
        
    def toggle_listening(self):
        """Toggle between listening and not listening states"""
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
        """Process the voice command using the AI agent"""
        try:
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
            
            # Configure logging to file and GUI
            file_handler = logging.FileHandler('log.txt')
            file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', 
                                                      datefmt='%Y-%m-%d %H:%M:%S'))
            file_handler.setLevel(logging.INFO)  # Changed from getLevelName('RESULT')
            
            gui_handler = self.GUILogHandler(self)
            gui_handler.setLevel(logging.INFO)  # Changed from getLevelName('RESULT')
            
            logger = logging.getLogger('browser_use')
            logger.addHandler(file_handler)
            logger.addHandler(gui_handler)
            
            # Create and run the agent
            agent = Agent(task=task, llm=llm)
            
            # Run the agent
            result = await agent.run()
            
            # Clean up logging
            logger.removeHandler(file_handler)
            logger.removeHandler(gui_handler)
            file_handler.close()
            
            # Humanize the response
            humanized_result = await humanize_response(str(result), llm)
            return humanized_result
            
        except Exception as e:
            self.update_browser_log(f"Error: {str(e)}", "error")
            self.update_browser_action("Error occurred")
            return f"Error processing command: {str(e)}"
            
    def setup_voice(self):
        """Configure voice properties"""
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        
    def listen_loop(self):
        """Main listening loop"""
        r = sr.Recognizer()
        
        # Configure recognition parameters
        r.pause_threshold = 1.0  # Increased pause threshold
        r.phrase_threshold = 0.3  # Lower phrase threshold
        r.non_speaking_duration = 0.5  # Shorter non-speaking duration
        
        while self.is_listening:
            try:
                self.update_status("Listening...")
                with sr.Microphone() as source:
                    # Adjust for ambient noise with longer duration
                    r.adjust_for_ambient_noise(source, duration=2)
                    r.dynamic_energy_threshold = True
                    r.energy_threshold = 4000  # Increased energy threshold
                    
                    # Listen with longer timeout and phrase time limit
                    audio = r.listen(source, timeout=10, phrase_time_limit=10)
                
                self.update_status("Processing speech...")
                # Use more accurate language model
                command = r.recognize_google(audio, language="en-US", show_all=False)
                self.update_conversation("You", command)
                
                # Process the command
                self.update_status("Processing command...")
                result = asyncio.run(self.process_voice_command(command))
                
                # Update UI and speak response
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
        """Convert text to speech"""
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
    main()