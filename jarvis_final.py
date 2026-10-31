import customtkinter as ctk
import tkinter as tk
import speech_recognition as sr
import pyttsx3
import pywhatkit
import pythoncom
import threading
import urllib.request
import json
import math
import queue
import re
from datetime import datetime
import webbrowser
from urllib.parse import quote_plus
import os
import time
import shutil
import subprocess
from pathlib import Path
import ast
import operator
import difflib

import pyautogui
import pyperclip

# ==========================================
# JARVIS SETTINGS
# ==========================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

MODEL = "llama3.2:1b"

BACKGROUND = "#050B18"
CYAN = "#00D9FF"
PANEL = "#101D30"


# ==========================================
# JARVIS DASHBOARD
# ==========================================

class JarvisDashboard(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.user_name = "Diya"

        self.title("J.A.R.V.I.S - AI Assistant")
        self.geometry("1000x720")
        self.minsize(700, 550)
        self.configure(fg_color=BACKGROUND)

        self.running = False
        self.pending_whatsapp = None
        self.angle = 0
        self.worker = None
        self.closing = False

        self.events = queue.Queue()
        self.recognizer = sr.Recognizer()

        self.conversation = [
    {
        "role": "system",
        "content": (
            "You are JARVIS, an intelligent personal "
            "AI assistant. Answer questions clearly "
            "and briefly because your answers are "
            "spoken aloud."
        )
    }
]

        # ==================================
        # MAIN LAYOUT
        # ==================================

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # ==================================
        # TITLE
        # ==================================

        self.header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.header.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(15, 5)
        )

        self.heading = ctk.CTkLabel(
            self.header,
            text="J.A.R.V.I.S",
            font=("Arial", 42, "bold"),
            text_color=CYAN
        )

        self.heading.pack()

        self.subtitle = ctk.CTkLabel(
            self.header,
            text="JUST A RATHER VERY INTELLIGENT SYSTEM",
            font=("Arial", 12),
            text_color="#8AAFC4"
        )

        self.subtitle.pack()

        # ==================================
        # START AND STOP BUTTONS
        # ==================================

        self.button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.button_frame.grid(
            row=1,
            column=0,
            pady=12
        )

        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="▶ START JARVIS",
            width=180,
            height=45,
            fg_color="#0077B6",
            hover_color="#005F8F",
            command=self.start_jarvis
        )

        self.start_button.grid(
            row=0,
            column=0,
            padx=10
        )

        self.stop_button = ctk.CTkButton(
            self.button_frame,
            text="■ STOP JARVIS",
            width=180,
            height=45,
            fg_color="#B22222",
            hover_color="#8B0000",
            command=self.stop_jarvis
        )

        self.stop_button.grid(
            row=0,
            column=1,
            padx=10
        )

        # ==================================
        # STATUS AND ANIMATION
        # ==================================

        self.visual_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.visual_frame.grid(
            row=2,
            column=0,
            pady=5
        )

        self.status = ctk.CTkLabel(
            self.visual_frame,
            text="● SYSTEM STANDBY",
            font=("Arial", 17, "bold"),
            text_color=CYAN
        )

        self.status.pack(pady=5)

        self.canvas = tk.Canvas(
            self.visual_frame,
            width=280,
            height=230,
            bg=BACKGROUND,
            highlightthickness=0
        )

        self.canvas.pack()

        # ==================================
        # CONVERSATION PANEL
        # ==================================

        self.chat_frame = ctk.CTkFrame(
            self,
            fg_color=PANEL
        )

        self.chat_frame.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=25,
            pady=(5, 15)
        )

        self.chat_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.chat_frame.grid_rowconfigure(
            1,
            weight=1
        )

        self.chat_heading = ctk.CTkLabel(
            self.chat_frame,
            text="JARVIS CONVERSATION",
            font=("Arial", 15, "bold"),
            text_color=CYAN
        )

        self.chat_heading.grid(
            row=0,
            column=0,
            pady=8
        )

        self.chatbox = ctk.CTkTextbox(
            self.chat_frame,
            font=("Arial", 14),
            fg_color=PANEL,
            text_color="white",
            wrap="word"
        )

        self.chatbox.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 10)
        )

        self.chatbox.insert(
            "end",
            "JARVIS SYSTEM INITIALIZED\n"
            "AI MODEL: LLAMA 3.2\n"
            "VOICE SYSTEM: READY\n"
            "MICROPHONE: READY\n\n"
            "Click START JARVIS to begin.\n\n"
        )

        self.chatbox.configure(
            state="disabled"
        )

        # ==================================
        # START UI SERVICES
        # ==================================

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )

        self.process_events()
        self.animate()

    # ==========================================
    # DASHBOARD MESSAGES
    # ==========================================

    def add_message(self, message):

        self.chatbox.configure(state="normal")

        self.chatbox.insert(
            "end",
            str(message) + "\n\n"
        )

        self.chatbox.see("end")

        self.chatbox.configure(state="disabled")

    def set_status(self, message):

        self.status.configure(
            text="● " + message
        )

    def post_event(self, event_type, message):

        self.events.put(
            (event_type, message)
        )

    def process_events(self):

        if self.closing:
            return

        try:
            while True:

                event_type, message = (
                    self.events.get_nowait()
                )

                if event_type == "status":
                    self.set_status(message)

                elif event_type == "message":
                    self.add_message(message)

                elif event_type == "finished":
                    self.start_button.configure(state="normal")

        except queue.Empty:
            pass

        self.after(
            100,
            self.process_events
        )

    # ==========================================
    # ANIMATED AI CORE
    # ==========================================

    def animate(self):

        if self.closing:
            return

        self.canvas.delete("all")

        cx = 140
        cy = 115

        for radius in [90, 72, 55]:

            self.canvas.create_oval(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                outline="#007FA8",
                width=2
            )

        for i in range(12):

            angle = math.radians(
                self.angle + i * 30
            )

            x = cx + 90 * math.cos(angle)
            y = cy + 90 * math.sin(angle)

            self.canvas.create_oval(
                x - 4,
                y - 4,
                x + 4,
                y + 4,
                fill=CYAN,
                outline=""
            )

        self.canvas.create_text(
            cx,
            cy,
            text="AI",
            fill=CYAN,
            font=("Arial", 32, "bold")
        )

        if self.running:
            self.angle += 3
        else:
            self.angle += 0.5

        self.after(
            40,
            self.animate
        )

    # ==========================================
    # VOICE OUTPUT
    # ==========================================

    def speak(self, text):

        self.post_event(
            "status",
            "SPEAKING"
        )

        self.post_event(
            "message",
            "JARVIS: " + str(text)
        )

        print("JARVIS:", text)

        initialized = False

        try:
            pythoncom.CoInitialize()
            initialized = True

            voice = pyttsx3.init("sapi5")

            voice.setProperty(
                "rate",
                170
            )

            voice.setProperty(
                "volume",
                1.0
            )

            voice.say(str(text))
            voice.runAndWait()
            voice.stop()

        except Exception as error:

            print("VOICE ERROR:", error)

            self.post_event(
                "message",
                "VOICE ERROR: " + str(error)
            )

        finally:

            if initialized:
                pythoncom.CoUninitialize()

    # ==========================================
    # MICROPHONE
    # ==========================================

    def listen(self, timeout=8):

        self.post_event(
            "status",
            "LISTENING"
        )

        try:
            with sr.Microphone() as source:

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=0.5
                )

                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=8
                )

            command = (
                self.recognizer.recognize_google(audio)
            )

            print("YOU:", command)

            self.post_event(
                "message",
                "YOU: " + command
            )

            return command.lower().strip()

        except sr.WaitTimeoutError:
            return ""

        except sr.UnknownValueError:
            return ""

        except sr.RequestError:

            self.post_event(
                "message",
                "Speech recognition service unavailable."
            )

            return ""

        except Exception as error:

            print("MIC ERROR:", error)

            self.post_event(
                "message",
                "MIC ERROR: " + str(error)
            )

            return ""
        # ==========================================
    # REAL-TIME CLOCK
    # ==========================================

    def tell_time(self):

        current_time = datetime.now().strftime("%I:%M %p")

        self.post_event(
            "status",
            "PERFORMING TASK"
        )

        self.speak(
            "The current time is " + current_time
        )
    # ==========================================
    # OLLAMA AI BRAIN
    # ==========================================

    def ask_ai(self, question):

        self.post_event(
            "status",
            "AI THINKING"
        )

        messages = self.conversation + [
            {
                "role": "user",
                "content": question
            }
        ]

        data = {
            "model": MODEL,
            "messages": messages,
            "stream": False
        }

        request = urllib.request.Request(
            "http://localhost:11434/api/chat",
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        try:
            print("JARVIS AI THINKING...")

            with urllib.request.urlopen(
                request,
                timeout=120
            ) as response:

                result = json.loads(
                    response.read().decode("utf-8")
                )

            answer = result["message"]["content"]

            self.conversation.append({
                "role": "user",
                "content": question
            })

            self.conversation.append({
                "role": "assistant",
                "content": answer
            })

            if len(self.conversation) > 11:

                self.conversation = (
                    self.conversation[:1]
                    + self.conversation[-10:]
                )

            return answer

        except Exception as error:

            print("AI ERROR:", error)

            self.post_event(
                "message",
                "AI ERROR: " + str(error)
            )

            return (
                "Sorry, I cannot connect to my "
                "AI brain. Please check Ollama."
            )

    # ==========================================
    # YOUTUBE MUSIC PLAYBACK
    # ==========================================

        # ==========================================
    # YOUTUBE TASK EXECUTION
    # ==========================================

    def play_youtube(self, command):

        self.post_event(
            "status",
            "PERFORMING TASK"
        )

        song = command.lower().strip()

        song = re.sub(
            r"^(please\s+)?(play|open|search for|show)\s+",
            "",
            song
        )

        song = re.sub(
            r"\s+(on|in|from|by)\s+youtube\s*$",
            "",
            song
        )

        song = song.strip()

        if not song:
            self.speak("What should I open on YouTube?")
            return

        self.post_event(
            "message",
            "SYSTEM: Opening YouTube for " + song
        )

        print("YOUTUBE TASK:", song)

        try:

            # Open a YouTube search page
            search_url = (
                "https://www.youtube.com/results?search_query="
                + quote_plus(song)
            )

            opened = webbrowser.open(
                search_url,
                new=2
            )

            if not opened:
                raise RuntimeError(
                    "Browser did not confirm opening YouTube."
                )

            self.speak(
                "I have opened YouTube results for " + song
            )

        except Exception as error:

            print("YOUTUBE ERROR:", error)

            self.post_event(
                "message",
                "YOUTUBE ERROR: " + str(error)
            )

            self.speak(
                "Sorry, I could not open YouTube."
            )

                
        

    # ==========================================
    # WAKE WORD AND COMMAND LOOP
    # ==========================================
        # ==========================================
    # PERSONALIZED JARVIS GREETING
    # ==========================================

    def greet_user(self):

        current_hour = datetime.now().hour

        if 5 <= current_hour < 12:
            greeting = "Good morning"

        elif 12 <= current_hour < 17:
            greeting = "Good afternoon"

        else:
            greeting = "Good evening"

        message = (
            f"{greeting}, {self.user_name}! "
            "Welcome back. JARVIS is online "
            "and ready to assist you."
        )

        self.speak(message)
        # ==========================================
    # JARVIS COMMAND PROCESSING
    # ==========================================

        # ==========================================
    # JARVIS MAIN COMMAND LOOP
    # ==========================================
        # ==========================================
    # JARVIS MAIN COMMAND LOOP
    # ==========================================

    def jarvis_loop(self):
        try:
            self.greet_user()
            while self.running:
                self.post_event("status", "WAITING FOR COMMAND")
                command = self.listen(timeout=6)
                if not self.running:
                    break
                if not command:
                    continue
                command = command.lower().strip()
                if "jarvis" in command:
                    command = command.split("jarvis", 1)[1].strip(" ,.!?")
                    if not command:
                        self.speak("Yes, I'm listening.")
                        command = self.listen(timeout=10)
                if not self.running:
                    break
                command = command.lower().strip()
                if command.startswith("please "):
                    command = command[7:].strip()
                if not command:
                    continue
                print("PROCESSING COMMAND:", command)
                self.post_event("status", "PROCESSING COMMAND")
                if command in ("stop", "exit", "shutdown", "goodbye", "stop jarvis"):
                    self.running = False
                    self.speak("Goodbye. Shutting down Jarvis.")
                    break
                if re.search(r"\b(time|date)\b", command) and re.search(r"\b(what|current|tell|now|today|date|time)\b", command):
                    self.tell_time()
                    continue
                if self.pending_whatsapp and command in ("cancel message", "cancel whatsapp", "cancel draft"):
                    self.pending_whatsapp = None
                    self.speak("WhatsApp draft cancelled.")
                    continue
                if self.handle_extra_features(command):
                    continue
                # WhatsApp: opening the app must not trigger message drafting.
                if re.fullmatch(r"(?:open|launch|start|go to|show)\s+(?:the\s+)?whats\s*app(?:\s+(?:app|web|application))?", command):
                    self.open_whatsapp()
                    continue
                if ("whatsapp" in command and re.match(r"^(?:send|text|message|write)\b", command)) or command.startswith(("text ", "message ", "send a message ")):
                    self.prepare_whatsapp_message(command)
                    continue
                if "youtube" in command or command.startswith(("play ", "pause video", "resume video")):
                    self.youtube_control(command)
                    continue
                if "google" in command or command.startswith(("search for ", "search google for ")):
                    self.google_search(command)
                    continue
                if self.handle_system_command(command):
                    continue
                if command.startswith(("open ", "launch ", "start ")):
                    app_name = re.sub(r"^(open|launch|start)\s+", "", command).strip()
                    self.open_application(app_name)
                    continue
                answer = self.ask_ai(command)
                if self.running:
                    self.speak(answer)
        except Exception as error:
            print("JARVIS LOOP ERROR:", error)
            self.post_event("message", "SYSTEM ERROR: " + str(error))
        finally:
            self.running = False
            self.post_event("status", "SYSTEM STANDBY")
            self.post_event("finished", "")

        # ==========================================
    # ADDITIONAL WINDOWS VOICE CONTROLS
    # ==========================================

    def handle_system_command(self, command):
        """Handle a limited set of explicit desktop commands; never run arbitrary shell commands."""
        cmd = command.lower().strip()
        try:
            if cmd in ("volume up", "increase volume", "turn up volume"):
                pyautogui.press("volumeup", presses=4, interval=0.08)
                self.speak("Volume increased.")
            elif cmd in ("volume down", "decrease volume", "turn down volume"):
                pyautogui.press("volumedown", presses=4, interval=0.08)
                self.speak("Volume decreased.")
            elif cmd in ("mute", "mute volume", "unmute", "unmute volume"):
                pyautogui.press("volumemute")
                self.speak("Volume mute toggled.")
            elif cmd in ("take screenshot", "take a screenshot", "capture screenshot"):
                screenshots = Path.home() / "Pictures" / "JarvisScreenshots"
                screenshots.mkdir(parents=True, exist_ok=True)
                filename = screenshots / ("jarvis_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".png")
                pyautogui.screenshot().save(str(filename))
                self.post_event("message", "SCREENSHOT SAVED: " + str(filename))
                self.speak("Screenshot saved in Pictures.")
            elif cmd in ("open downloads", "open downloads folder"):
                os.startfile(str(Path.home() / "Downloads"))
                self.speak("Opening Downloads.")
            elif cmd in ("open documents", "open documents folder"):
                os.startfile(str(Path.home() / "Documents"))
                self.speak("Opening Documents.")
            elif cmd in ("open desktop", "open desktop folder"):
                desktop = Path.home() / "Desktop"
                onedrive = Path.home() / "OneDrive" / "Desktop"
                os.startfile(str(desktop if desktop.exists() else onedrive))
                self.speak("Opening Desktop.")
            elif cmd in ("open settings", "windows settings"):
                os.startfile("ms-settings:")
                self.speak("Opening Settings.")
            elif cmd in ("open task manager", "task manager"):
                subprocess.Popen(["taskmgr.exe"])
                self.speak("Opening Task Manager.")
            elif cmd in ("open paint", "launch paint"):
                subprocess.Popen(["mspaint.exe"])
                self.speak("Opening Paint.")
            elif cmd in ("open command prompt", "open terminal"):
                subprocess.Popen(["cmd.exe"])
                self.speak("Opening Command Prompt.")
            elif cmd in ("new browser tab", "open new tab"):
                pyautogui.hotkey("ctrl", "t")
                self.speak("Opened a new tab in the focused application.")
            elif cmd in ("close browser tab", "close current tab"):
                self.speak("I won't close the active tab automatically because it might contain unsaved work.")
            elif cmd in ("browser back", "go back in browser"):
                pyautogui.hotkey("alt", "left")
                self.speak("Going back.")
            elif cmd in ("browser forward", "go forward in browser"):
                pyautogui.hotkey("alt", "right")
                self.speak("Going forward.")
            elif cmd.startswith("type ") or cmd.startswith("write "):
                # Do not type into arbitrary applications from voice: sensitive fields may be focused.
                self.speak("For safety, I won't type into an unknown active window. Use a dedicated text field in the dashboard instead.")
            elif cmd in ("delete all files", "format drive", "disable antivirus", "run powershell command"):
                self.speak("I cannot execute unrestricted or destructive system commands.")
            else:
                return False
            return True
        except Exception as error:
            print("SYSTEM CONTROL ERROR:", error)
            self.post_event("message", "SYSTEM CONTROL ERROR: " + str(error))
            self.speak("I couldn't complete that system action.")
            return True

    # ==========================================
    # OPEN WHATSAPP
    # ==========================================

    def open_whatsapp(self):

        self.post_event("status", "OPENING WHATSAPP")

        try:
            import webbrowser

            opened = webbrowser.open(
                "https://web.whatsapp.com/",
                new=2
            )

            if opened:
                self.speak("Opening WhatsApp.")
            else:
                self.speak(
                    "I could not open WhatsApp automatically."
                )

        except Exception as error:
            print("WHATSAPP ERROR:", error)
            self.speak("Sorry, I could not open WhatsApp.")
    # ==========================================
    # WINDOWS SYSTEM CONTROL
    # ==========================================

    def open_application(self, app_name):
        self.post_event("status", "OPENING APPLICATION")
        name = app_name.lower().strip()
        try:
            if name in ("notepad", "notepad app"):
                subprocess.Popen(["notepad.exe"])
            elif name in ("calculator", "calc"):
                subprocess.Popen(["calc.exe"])
            elif name in ("file explorer", "explorer", "files"):
                subprocess.Popen(["explorer.exe"])
            elif name in ("wordpad", "word pad"):
                executable = shutil.which("wordpad.exe")
                if not executable:
                    self.speak("WordPad is not installed on this computer.")
                    return
                subprocess.Popen([executable])
            elif name in ("microsoft word", "word", "ms word"):
                subprocess.Popen(["cmd", "/c", "start", "", "winword"])
            else:
                self.speak("I don't have an approved shortcut for " + name)
                return
            self.speak("Opening " + app_name)
        except Exception as error:
            print("APP ERROR:", error)
            self.speak("I could not open " + app_name)


    # ==========================================
    # GOOGLE SEARCH
    # ==========================================

    def google_search(self, command):
        self.post_event("status", "SEARCHING GOOGLE")
        query = command.lower().strip()
        query = re.sub(r"^(please\s+)?(open\s+)?google\s*(and\s*)?", "", query)
        query = re.sub(r"^(search\s+google\s+for|search\s+for|search|for)\s*", "", query)
        try:
            url = "https://www.google.com/" if not query else "https://www.google.com/search?q=" + quote_plus(query)
            webbrowser.open(url)
            self.speak("Opening Google." if not query else "Searching Google for " + query)
        except Exception as error:
            print("GOOGLE ERROR:", error)
            self.speak("I could not open Google.")


    # ==========================================
    # YOUTUBE SEARCH AND PLAY
    # ==========================================

    def youtube_control(self, command):
        self.post_event("status", "PERFORMING TASK")
        command = command.lower().strip()
        try:
            if re.search(r"\b(close|exit)\s+youtube\b", command):
                self.speak("Please close the YouTube tab in your browser. I won't close unrelated tabs.")
                return
            if re.search(r"\b(pause|resume|unpause)\b", command):
                self.speak("Please select the YouTube player and press K to toggle playback.")
                return
            query = re.sub(r"^(please\s+)?(open|play|search for|search|show|watch)\s+", "", command)
            query = re.sub(r"\s+(on|in|from)\s+youtube\s*$", "", query)
            query = re.sub(r"^youtube\s*", "", query).strip()
            if not query:
                webbrowser.open("https://www.youtube.com/")
                self.speak("Opening YouTube.")
                return
            if command.startswith(("play ", "watch ")):
                self.speak("Opening a YouTube video for " + query)
                pywhatkit.playonyt(query)
            else:
                url = "https://www.youtube.com/results?search_query=" + quote_plus(query)
                webbrowser.open(url)
                self.speak("Searching YouTube for " + query)
        except Exception as error:
            print("YOUTUBE ERROR:", error)
            self.post_event("message", "YOUTUBE ERROR: " + str(error))
            self.speak("I could not open YouTube. Check your browser and internet connection.")


    # ==========================================
    # WHATSAPP MESSAGE PREPARATION
    # ==========================================

    def prepare_whatsapp_message(self, command):
        self.post_event("status", "PREPARING WHATSAPP DRAFT")
        match = re.search(
            r"^(?:send\s+)?(?:a\s+)?(?:whatsapp\s+)?(?:message\s+)?(?:text\s+)?(?:to\s+)?(.+?)\s+(?:on\s+whatsapp\s+)?(?:saying|that\s+says|message)\s+(.+)$",
            command, re.IGNORECASE
        )
        if not match:
            self.speak("Please say: text Mom on WhatsApp saying hello.")
            return
        recipient, message = match.group(1).strip(), match.group(2).strip()
        if recipient.lower().startswith("text "):
            recipient = recipient[5:].strip()
        self.pending_whatsapp = {"recipient": recipient, "message": message}
        self.post_event("message", "WHATSAPP DRAFT TO: " + recipient + " | MESSAGE: " + message)
        self.speak("Draft prepared for " + recipient + ". No message was sent. Please verify the recipient and message in the dashboard.")
        self.open_whatsapp()
    # ==========================================
    # OPTIONAL VOICE AUTOMATION FEATURES
    # ==========================================

    def calculate_expression(self, expression):
        """Evaluate arithmetic only; never execute Python code from speech."""
        operations = {
            ast.Add: operator.add, ast.Sub: operator.sub,
            ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
            ast.Pow: operator.pow, ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        def evaluate(node, depth=0):
            if depth > 15:
                raise ValueError("Expression is too complicated")
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                if abs(node.value) > 1e12:
                    raise ValueError("Number is too large")
                return node.value
            if isinstance(node, ast.UnaryOp) and type(node.op) in operations:
                return operations[type(node.op)](evaluate(node.operand, depth + 1))
            if isinstance(node, ast.BinOp) and type(node.op) in operations:
                left, right = evaluate(node.left, depth + 1), evaluate(node.right, depth + 1)
                if isinstance(node.op, ast.Pow) and abs(right) > 10:
                    raise ValueError("Exponent is too large")
                value = operations[type(node.op)](left, right)
                if abs(value) > 1e15:
                    raise ValueError("Result is too large")
                return value
            raise ValueError("Unsupported mathematical expression")
        return evaluate(ast.parse(expression, mode="eval").body)

    def handle_extra_features(self, command):
        """Handle extra commands before generic application and AI routing."""
        cmd = command.lower().strip()
        try:
            # Calculator: 'calculate 20 plus 5', 'what is 12 times 3'.
            match = re.match(r"^(?:calculate|compute|what is|what's)\s+(.+)$", cmd)
            if match:
                expr = match.group(1).rstrip(" ?.")
                substitutions = (
                    (r"\bmultiplied by\b", "*"), (r"\btimes\b", "*"),
                    (r"\bdivided by\b", "/"), (r"\bplus\b", "+"),
                    (r"\bminus\b", "-"), (r"\bto the power of\b", "**"),
                    (r"\bmodulo\b", "%"),
                )
                for pattern, replacement in substitutions:
                    expr = re.sub(pattern, replacement, expr)
                if re.fullmatch(r"[0-9.\s()+*/%\-]+", expr):
                    try:
                        self.speak("The answer is " + str(self.calculate_expression(expr)))
                    except (ValueError, ZeroDivisionError, OverflowError, SyntaxError) as error:
                        self.speak("I could not calculate that: " + str(error))
                    return True

            # Dedicated notes: never type into an unknown focused application.
            match = re.match(r"^(?:take a note|make a note|save a note|note down|remember this note)\s+(.+)$", cmd)
            if match:
                notes_dir = Path.home() / "Documents" / "JarvisNotes"
                notes_dir.mkdir(parents=True, exist_ok=True)
                path = notes_dir / "notes.txt"
                with path.open("a", encoding="utf-8") as f:
                    f.write(datetime.now().strftime("%Y-%m-%d %H:%M") + " - " + match.group(1) + "\n")
                self.post_event("message", "NOTE SAVED: " + str(path))
                self.speak("Note saved in Documents, Jarvis Notes.")
                return True
            if cmd in ("open my notes", "show my notes", "read my notes"):
                path = Path.home() / "Documents" / "JarvisNotes" / "notes.txt"
                if not path.exists():
                    self.speak("You have not saved any notes yet.")
                elif cmd == "read my notes":
                    lines = path.read_text(encoding="utf-8").splitlines()
                    self.speak("Your latest notes: " + ". ".join(lines[-3:])[-450:])
                else:
                    os.startfile(str(path))
                    self.speak("Opening your notes.")
                return True

            # Explicit memory, stored only on this computer.
            match = re.match(r"^remember that\s+(.+)$", cmd)
            if match:
                path = Path.home() / "Documents" / "JarvisNotes" / "memory.txt"
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("a", encoding="utf-8") as f:
                    f.write(match.group(1) + "\n")
                self.speak("I saved that to your local JARVIS memory.")
                return True
            if cmd in ("what do you remember", "read your memory"):
                path = Path.home() / "Documents" / "JarvisNotes" / "memory.txt"
                if path.exists():
                    items = path.read_text(encoding="utf-8").splitlines()
                    self.speak("I remember: " + ". ".join(items[-5:])[-450:])
                else:
                    self.speak("You have not asked me to remember anything yet.")
                return True

            # Mouse movements are small and deliberate. PyAutoGUI's corner failsafe stays on.
            mouse_actions = {
                "click": lambda: pyautogui.click(),
                "left click": lambda: pyautogui.click(),
                "double click": lambda: pyautogui.doubleClick(interval=0.12),
                "right click": lambda: pyautogui.click(button="right"),
                "scroll up": lambda: pyautogui.scroll(4),
                "scroll down": lambda: pyautogui.scroll(-4),
                "move mouse up": lambda: pyautogui.moveRel(0, -100, duration=0.2),
                "move mouse down": lambda: pyautogui.moveRel(0, 100, duration=0.2),
                "move mouse left": lambda: pyautogui.moveRel(-100, 0, duration=0.2),
                "move mouse right": lambda: pyautogui.moveRel(100, 0, duration=0.2),
            }
            if cmd in mouse_actions:
                mouse_actions[cmd]()
                self.speak("Done.")
                return True

            # Only a small allowlist of non-destructive keyboard shortcuts.
            shortcuts = {
                "copy": ("ctrl", "c"), "copy selection": ("ctrl", "c"),
                "paste": ("ctrl", "v"), "paste text": ("ctrl", "v"),
                "select all": ("ctrl", "a"),
                "undo": ("ctrl", "z"), "redo": ("ctrl", "y"),
                "find on page": ("ctrl", "f"),
                "switch window": ("alt", "tab"),
                "refresh page": ("ctrl", "r"),
            }
            if cmd in shortcuts:
                pyautogui.hotkey(*shortcuts[cmd])
                self.speak("Done.")
                return True

            # Type only into a fresh Notepad window that JARVIS launches itself.
            match = re.match(r"^(?:write in notepad|type in notepad|create a notepad note)\s+(.+)$", cmd)
            if match:
                content = match.group(1)
                subprocess.Popen(["notepad.exe"])
                time.sleep(1.4)
                pyperclip.copy(content)
                pyautogui.hotkey("ctrl", "v")
                self.speak("I opened Notepad and entered the text. Please check the window before saving.")
                return True

            # Browser and websites.
            if cmd in ("open browser", "launch browser"):
                webbrowser.open("https://www.google.com/", new=2)
                self.speak("Opening your browser.")
                return True
            match = re.match(r"^(?:open website|go to website|visit website)\s+([a-z0-9.-]+\.[a-z]{2,})(?:/)?$", cmd)
            if match:
                webbrowser.open("https://" + match.group(1), new=2)
                self.speak("Opening website " + match.group(1))
                return True
            if cmd in ("open weather", "show weather", "check weather", "what is the weather"):
                webbrowser.open("https://www.google.com/search?q=weather+near+me", new=2)
                self.speak("Opening the current weather in your browser.")
                return True

            # Email draft opens in the default mail app; never sends automatically.
            match = re.match(r"^(?:draft email|compose email|write an email)\s+(.+)$", cmd)
            if match:
                webbrowser.open("mailto:?body=" + quote_plus(match.group(1)), new=2)
                self.speak("Opening an email draft. Please check the recipient and content before sending.")
                return True

            # Locate files by filename in common personal folders (no deletion).
            match = re.match(r"^(?:find file|search for file|locate file)\s+(.+)$", cmd)
            if match:
                term = match.group(1).lower()
                results = []
                for folder in ("Desktop", "Downloads", "Documents"):
                    root = Path.home() / folder
                    if not root.is_dir():
                        continue
                    for base, dirs, files in os.walk(root):
                        dirs[:] = [d for d in dirs if not d.startswith(".")][:30]
                        for filename in files:
                            if term in filename.lower():
                                results.append(str(Path(base) / filename))
                                if len(results) >= 5:
                                    break
                        if len(results) >= 5:
                            break
                    if len(results) >= 5:
                        break
                if results:
                    for path in results:
                        self.post_event("message", "FOUND FILE: " + path)
                    self.speak("I found " + str(len(results)) + " matching files. Their paths are in the dashboard.")
                else:
                    self.speak("I could not find a matching file in Desktop, Downloads, or Documents.")
                return True

            return False
        except Exception as error:
            print("EXTRA FEATURE ERROR:", error)
            self.post_event("message", "EXTRA FEATURE ERROR: " + str(error))
            self.speak("I couldn't complete that action. Check the dashboard for details.")
            return True

    # ==========================================
    # START JARVIS
    # ==========================================

    def start_jarvis(self):

        if self.running:
            return

        if self.worker and self.worker.is_alive():

            self.add_message(
                "SYSTEM: Previous session is still stopping."
            )

            return

        self.running = True

        self.start_button.configure(
            state="disabled"
        )

        self.add_message(
            "SYSTEM: Starting JARVIS..."
        )

        self.worker = threading.Thread(
            target=self.jarvis_loop,
            daemon=True
        )

        self.worker.start()

    # ==========================================
    # STOP JARVIS
    # ==========================================

    def stop_jarvis(self):

        self.running = False

        self.set_status(
            "STOPPING"
        )

        self.add_message(
            "SYSTEM: Stopping JARVIS..."
        )

        self.after(
            500,
            self.check_stopped
        )

    def check_stopped(self):

        if self.closing:
            return

        if self.worker and self.worker.is_alive():

            self.after(
                500,
                self.check_stopped
            )

        else:

            self.start_button.configure(
                state="normal"
            )

            self.set_status(
                "SYSTEM STANDBY"
            )

    # ==========================================
    # CLOSE APPLICATION
    # ==========================================

    def close_app(self):

        self.running = False
        self.closing = True

        self.destroy()


# ==========================================
# MAIN PROGRAM
# ==========================================

if __name__ == "__main__":

    app = JarvisDashboard()
    app.mainloop()
     