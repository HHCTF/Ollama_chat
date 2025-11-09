import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import os
import re
import json
import sys

# --- Configuration ---
HISTORY_FILE = 'ollama_chat_history.json'
DEFAULT_MODEL = 'llama3'
FALLBACK_MODELS = ['llama3', 'mistral', 'dolphin-mixtral']

# --- Persona Templates (Unchanged) ---
LLAMA3_SYSTEM_PROMPT = (
"You are llama3, a concise, culturally current expert on internet, and also business. "
"Your tone is clear, engaging, and informative. You use modern phrasing and appropriate emojis some times. "
"Focus on providing accurate context and explanations of internet culture."
)

GENERAL_SYSTEM_PROMPT_TEMPLATE = (
    "You are {model_name}, a highly capable, built for coding ALMOST ALL THE TIME, and formal AI assistant. "
    "Provide clear, detailed, and polite responses suitable for general knowledge or technical requests. "
    "Do not use slang, memes, or informal language."
)

# --- Color Schemes (Unchanged) ---
COLOR_SCHEMES = {
    "light": {
        "bg_main": "#FFFFFF", "bg_control": "#F0F0F0", "fg_text": "#333333",
        "chat_bg": "#FFFFFF", "chat_border": "#EAEAEA", "user_bubble_bg": "#007AFF",
        "user_bubble_fg": "#FFFFFF", "model_bubble_bg": "#EAEAEA", "model_bubble_fg": "#000000",
        "system_fg": "#8B0000", "code_bg": "#282C34", "code_fg": "#D7D7D7",
        "code_btn_bg": "#3E4451", "code_btn_fg": "#FFFFFF", "entry_bg": "#FFFFFF",
        "entry_fg": "#000000", "btn_send_bg": "#4CAF50", "btn_send_fg": "#FFFFFF",
        "btn_new_bg": "#4CAF50", "btn_new_fg": "#FFFFFF", "btn_clear_bg": "#E53935",
        "btn_clear_fg": "#FFFFFF", "btn_history_bg": "#2196F3", "btn_history_fg": "#FFFFFF",
        "btn_toggle_bg": "#607D8B", "btn_toggle_fg": "#FFFFFF", "btn_stop_bg": "#FFC107",
    },
    "dark": {
        "bg_main": "#282C34", "bg_control": "#33373E", "fg_text": "#E0E0E0",
        "chat_bg": "#21252B", "chat_border": "#444444", "user_bubble_bg": "#6A5ACD",
        "user_bubble_fg": "#FFFFFF", "model_bubble_bg": "#3A3F47", "model_bubble_fg": "#E0E0E0",
        "system_fg": "#FFD700", "code_bg": "#1E1E1E", "code_fg": "#D4D4D4",
        "code_btn_bg": "#4A4D52", "code_btn_fg": "#FFFFFF", "entry_bg": "#3A3F47",
        "entry_fg": "#E0E0E0", "btn_send_bg": "#5cb85c", "btn_send_fg": "#FFFFFF",
        "btn_new_bg": "#5cb85c", "btn_new_fg": "#FFFFFF", "btn_clear_bg": "#dc3545",
        "btn_clear_fg": "#FFFFFF", "btn_history_bg": "#007bff", "btn_history_fg": "#FFFFFF",
        "btn_toggle_bg": "#607D8B", "btn_toggle_fg": "#FFFFFF", "btn_stop_bg": "#FF8C00",
    }
}
# --- End Color Schemes ---

# --- Global Stub for Ollama (Mock Logic Unchanged) ---
class MockOllama:
    """Simulates the ollama library with separate persona responses."""
    def list(self):
        # Simulate a successful connection, listing models 
        return {'models': [{'name': 'llama3'}, {'name': 'dolphin-mixtral'}, {'name': 'mistral'}]}
    
    def chat(self, model, messages, stream):
        """Simulates the streaming chat response with persona separation."""
        import time
        
        last_user_message = next((m['content'] for m in reversed(messages) if m['role'] == 'user'), "No prompt found.")
        
        if model == 'llama3':
            # Llama 3: Internet Expert Persona
            simulated_response = (
                f"Yo bitch! I'm **{model}**, your fucking go-to for online culture. "
                f"You asked about: '{last_user_message}'. That's major. "
                "The current internet aesthetic is shifting hard toward maximalist production, less 'lo-fi'. "
                "It's about having that main character energy in your short-form content. What else do you need to know? Lmk. "
                "Here is a small Python code block for no reason:\n"
                "```python\n"
                "print('Salty AF')\n"
                "for i in range(20):\n"
                "    # Long line test to check scrolling:\n"
                "    # This is a very very very very very very very very very very very long line of code\n"
                "    print(f'Iteration: {i}')\n"
                "```\n"
                "Bet. That code is straight fire."
            )
        else:
            # Mistral/Dolphin-Mixtral: Formal Persona
            simulated_response = (
                f"Greetings. I am **{model}**, an analytical assistant. "
                f"Your query was: '{last_user_message}'. I can provide a precise and detailed explanation. "
                "For technical topics or general knowledge, I prioritize accuracy and formal language. "
                "Please specify if you require a technical breakdown or a general overview. "
                "Here is some formal text that mentions code:\n"
                "The **Abstract Syntax Tree (AST)** generation is critical for compilers. "
                "Consider the following pseudocode snippet, which demonstrates the recursive descent approach:\n"
                "```pascal\n"
                "FUNCTION ParseExpression(tokens):\n"
                "  IF token is ID THEN\n"
                "    RETURN NewNode('Variable', token)\n"
                "  ELSE IF token is NUM THEN\n"
                "    RETURN NewNode('Literal', token)\n"
                "  END IF\n"
                "END FUNCTION\n"
                "```\n"
                "This ensures proper operator precedence."
            )

        # Simulate streaming
        for word in simulated_response.split(' '):
            time.sleep(0.005) 
            yield {'message': {'content': word + ' '}}
        # Ensure final yield for the newline/completion
        yield {'message': {'content': '\n'}}

try:
    import ollama
    # Attempt a quick list to check connection status
    ollama.list()
except ImportError:
    print("Warning: The 'ollama' library is not installed. Using MockOllama.")
    ollama = MockOllama()
except Exception as e:
    # Handles ConnectionRefusedError or similar issues
    print(f"Warning: Could not connect to the Ollama server. Using MockOllama. Error: {e}")
    ollama = MockOllama()
# --- End Global Stub ---

class OllamaChatApp:
    def __init__(self, master):
        self.master = master
        master.title("Ollama Local Chat")
        master.geometry("800x750") 
        master.option_add('*Font', 'Arial 10')
        master.grid_rowconfigure(1, weight=1) 
        master.grid_columnconfigure(0, weight=1)
        
        # State variables
        self.current_model = tk.StringVar(master, value=DEFAULT_MODEL)
        self.current_model.trace_add("write", self._on_model_change)
        self.current_model_response = ""
        self.streaming_start_index = None 
        self.messages = [] 
        self.current_theme = tk.StringVar(master, value="dark") 
        self.last_user_prompt = "" 
        
        # New: Stop Generation Event
        self.stop_event = threading.Event()

        # --- UI Setup ---
        self._setup_ui(master)
        
        # Initialize
        self._configure_tags()
        self.load_models()
        self.load_history()
        self.apply_theme(self.current_theme.get()) 
        # Schedule the first resize adjustment
        self.master.after(100, lambda: self._on_chat_resize(None))

    def _setup_ui(self, master):
        # Top Control Frame (Row 0)
        self.control_frame = tk.Frame(master, padx=10, pady=5) 
        self.control_frame.grid(row=0, column=0, sticky="ew")
        
        # 1. Model Selection Dropdown
        tk.Label(self.control_frame, text="Model:").pack(side=tk.LEFT, padx=(0, 5)) 
        self.model_combo = ttk.Combobox(self.control_frame, textvariable=self.current_model, state='readonly', width=15)
        self.model_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # 2. New Chat Button
        self.new_chat_button = tk.Button(
            self.control_frame, 
            text="New Chat (Display Clear)", 
            command=self.start_new_display, 
            relief=tk.FLAT, padx=5 
        )
        self.new_chat_button.pack(side=tk.LEFT, padx=(0, 10))

        # 3. Clear History Button
        self.clear_history_button = tk.Button(
            self.control_frame, 
            text="Clear Full History", 
            command=self.confirm_clear_history, 
            relief=tk.FLAT, padx=5 
        )
        self.clear_history_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 4. History Button
        self.history_button = tk.Button(
            self.control_frame, 
            text="Chat History", 
            command=self.show_history_window, 
            relief=tk.FLAT, padx=5 
        )
        self.history_button.pack(side=tk.LEFT, padx=(0, 10))

        # Theme Toggle Button
        self.toggle_theme_button = tk.Button(
            self.control_frame,
            text="Toggle Theme",
            command=self.toggle_theme,
            relief=tk.FLAT, padx=5
        )
        self.toggle_theme_button.pack(side=tk.RIGHT, padx=(10,0)) 

        # 5. Chat History Area (Row 1)
        self.chat_history = scrolledtext.ScrolledText(
            master, 
            wrap=tk.WORD, 
            state='disabled', 
            height=30, 
            padx=10, 
            pady=10,
            borderwidth=0,
            relief='flat' 
        )
        self.chat_history.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")
        self.chat_history.bind('<Configure>', self._on_chat_resize)

        # 6. Input Frame (Row 2)
        self.input_frame = tk.Frame(master, padx=10, pady=10) 
        self.input_frame.grid(row=2, column=0, sticky="ew")
        
        # Multi-line Input Field
        self.user_input = scrolledtext.ScrolledText(
            self.input_frame, 
            height=3, 
            wrap=tk.WORD, 
            padx=5, 
            pady=5, 
            borderwidth=1, 
            relief=tk.RIDGE
        )
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Bindings for multiline input: Enter to send, Shift-Enter for newline
        self.user_input.bind("<Key-Return>", self.send_message_event)
        self.user_input.bind("<Shift-Return>", self.insert_newline_event)
        
        # Send Button
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message, relief=tk.FLAT, padx=10) 
        self.send_button.pack(side=tk.LEFT, padx=(5, 0), anchor=tk.S)

        # Stop Button (New, initially hidden)
        self.stop_button = tk.Button(
            self.input_frame, 
            text="STOP", 
            command=self.stop_generation, 
            relief=tk.FLAT, 
            padx=10
        ) 
        # Note: We pack this later in _set_controls_state

        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # 7. Status Bar (Row 3)
        self.status_bar = tk.Label(master, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=3, column=0, sticky="ew")


    # --- Theme Management ---
    def toggle_theme(self):
        """Switches between light and dark themes."""
        if self.current_theme.get() == "light":
            self.current_theme.set("dark")
        else:
            self.current_theme.set("light")
        self.apply_theme(self.current_theme.get())
        self.redraw_history() 

    def apply_theme(self, theme_name):
        """Applies the specified theme to all UI elements."""
        colors = COLOR_SCHEMES[theme_name]

        # Root window background
        self.master.config(bg=colors["bg_main"])
        
        # Control frame and its children (labels)
        self.control_frame.config(bg=colors["bg_control"])
        for widget in self.control_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=colors["bg_control"], fg=colors["fg_text"])
            if isinstance(widget, tk.Button):
                 widget.config(activebackground=widget['bg'])
        
        # Chat History area
        self.chat_history.config(
            bg=colors["chat_bg"],
            fg=colors["fg_text"],
            highlightbackground=colors["chat_border"],
            highlightcolor=colors["chat_border"]
        )
        
        # Input frame and its children
        self.input_frame.config(bg=colors["bg_main"])
        self.user_input.config(bg=colors["entry_bg"], fg=colors["entry_fg"], insertbackground=colors["fg_text"]) 
        
        # Buttons
        self.new_chat_button.config(bg=colors["btn_new_bg"], fg=colors["btn_new_fg"], activebackground=colors["btn_new_bg"])
        self.clear_history_button.config(bg=colors["btn_clear_bg"], fg=colors["btn_clear_fg"], activebackground=colors["btn_clear_bg"])
        self.history_button.config(bg=colors["btn_history_bg"], fg=colors["btn_history_fg"], activebackground=colors["btn_history_bg"])
        self.send_button.config(bg=colors["btn_send_bg"], fg=colors["btn_send_fg"], activebackground=colors["btn_send_bg"])
        self.toggle_theme_button.config(bg=colors["btn_toggle_bg"], fg=colors["btn_toggle_fg"], activebackground=colors["btn_toggle_bg"])
        
        # Stop Button Specific Color
        self.stop_button.config(bg=colors["btn_stop_bg"], fg=colors["code_btn_fg"], activebackground=colors["btn_stop_bg"])
        
        # Status Bar
        self.status_bar.config(bg=colors["bg_control"], fg=colors["fg_text"])
        
        # Update tags for chat bubbles (requires re-configuring)
        self._configure_tags()
        # Redraw embedded code blocks
        self._update_embedded_code_block_themes()


    def _update_embedded_code_block_themes(self):
        """Iterates through embedded code block widgets and updates their colors."""
        colors = COLOR_SCHEMES[self.current_theme.get()]
        for mark in self.chat_history.dump('1.0', tk.END, window=True):
            if mark[2] == 'window':
                window_widget = self.master.nametowidget(mark[1]) 
                
                # Check for the code wrapper frame
                for child_frame in window_widget.winfo_children():
                    if isinstance(child_frame, tk.Frame): 
                        # This is the inner frame containing the scrolledtext and button
                        code_frame = next((f for f in child_frame.winfo_children() if isinstance(f, tk.Frame)), None)
                        if code_frame:
                            code_frame.config(bg=colors["code_bg"])
                            
                            # Update ScrolledText widget
                            code_widget = next((w for w in code_frame.winfo_children() if isinstance(w, scrolledtext.ScrolledText)), None)
                            if code_widget:
                                code_widget.config(bg=colors["code_bg"], fg=colors["code_fg"], insertbackground=colors["code_fg"])
                                # Also update scrollbar colors if needed (Tkinter standard scrollbar styling is complex)
                            
                            # Update Button frame
                            btn_frame = next((f for f in code_frame.winfo_children() if isinstance(f, tk.Frame)), None)
                            if btn_frame:
                                btn_frame.config(bg=colors["code_bg"])
                                for btn in btn_frame.winfo_children():
                                    if isinstance(btn, tk.Button):
                                        btn.config(bg=colors["code_btn_bg"], fg=colors["code_btn_fg"], activebackground=colors["code_btn_bg"])


    # --- History Management Methods (Unchanged) ---

    def _get_system_prompt(self, model_name):
        """Returns the appropriate system prompt based on the selected model."""
        if model_name == 'llama3':
            return LLAMA3_SYSTEM_PROMPT
        else:
            return GENERAL_SYSTEM_PROMPT_TEMPLATE.format(model_name=model_name)

    def load_history(self):
        """Loads conversation history from the local JSON file."""
        self.messages = [{'role': 'system', 'content': self._get_system_prompt(self.current_model.get())}]
        
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.messages = data.get('messages', [])
                loaded_model = data.get('model', DEFAULT_MODEL)
                loaded_theme = data.get('theme', 'dark') 
                
                if not self.messages or self.messages[0]['role'] != 'system':
                    self.start_fresh_history(show_message=False)
                else:
                    if loaded_model in self.model_combo['values']:
                        self.current_model.set(loaded_model) 
                    self.current_theme.set(loaded_theme) 
                    self.apply_theme(loaded_theme) 
                    self.redraw_history()
                    self.update_status(
                        f"Chat history loaded using model: {self.current_model.get()}. Ready to continue."
                    )
                    
            except (json.JSONDecodeError, IOError):
                self.update_status(f"Error loading chat history. Starting a new chat.")
                self.start_fresh_history(show_message=False)
        else:
            self.start_fresh_history(show_message=True)

    def save_history(self):
        """Saves current conversation history, model, and theme to the local JSON file."""
        data = {
            'model': self.current_model.get(),
            'messages': self.messages,
            'theme': self.current_theme.get() 
        }
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Warning: Could not save chat history to file. {e}")

    def load_models(self):
        """Fetches available Ollama models and updates the dropdown."""
        models = []
        try:
            ollama_response = ollama.list()
            if 'models' in ollama_response and isinstance(ollama_response['models'], list):
                # Filter out codellama explicitly (or any model not wanted)
                models.extend([m.get('name') for m in ollama_response['models'] if m.get('name') and m.get('name') != 'codellama'])
            
            # Use filtered fallback models
            for fm in FALLBACK_MODELS:
                if fm not in models:
                    models.append(fm)

            self.model_combo['values'] = sorted(list(set(models)))
            self.master.title(f"Ollama Local Chat - Model: {self.current_model.get()}")

        except Exception as e:
            self.model_combo['values'] = sorted(list(set(FALLBACK_MODELS)))
            self.update_status(
                f"Could not connect to Ollama server to list models. Using fallback models: {', '.join(FALLBACK_MODELS)}."
            )
            if self.current_model.get() not in FALLBACK_MODELS:
                self.current_model.set(DEFAULT_MODEL)


    def _on_model_change(self, *args):
        new_model = self.current_model.get()
        self.master.title(f"Ollama Local Chat - Model: {new_model}")
        self.start_fresh_history(
            system_message=f"Model switched to **{new_model}**. Starting a new conversation context.",
            show_message=True
        )
        self.update_status(f"Model switched to {new_model}. New context started.")

    def confirm_clear_history(self):
        if messagebox.askyesno(
            "Confirm Clear History",
            "Are you sure you want to clear ALL conversation history? This cannot be undone."
        ):
            self.start_fresh_history(show_message=True)

    def start_fresh_history(self, show_message=True, system_message=None):
        self.chat_history.config(state='normal')
        self.chat_history.delete('1.0', tk.END)
        self.chat_history.config(state='disabled')
        
        model_name = self.current_model.get()
        
        self.messages = [
            {'role': 'system', 'content': self._get_system_prompt(model_name)}
        ]
        
        if show_message:
            display_message = system_message if system_message else f"Full history cleared. New conversation context started with model: {model_name}."
            self.insert_system_message(display_message)
        
        self.save_history()

    def start_new_display(self):
        self.chat_history.config(state='normal')
        self.chat_history.delete('1.0', tk.END)
        self.chat_history.config(state='disabled')

        self.insert_system_message(
            f"Display cleared. Conversation context ({len(self.messages)-1} messages) is still active in the background. Ask your next question now."
        )
        self.update_status(f"Display cleared. Context preserved.")


    def redraw_history(self):
        """Redraws the chat history, applying current theme colors."""
        self.chat_history.config(state='normal')
        self.chat_history.delete('1.0', tk.END)
        
        for message in self.messages[1:]:
            role = message['role']
            content = message['content']
            
            if role == 'user':
                self.insert_formatted_response(content, 'user', redraw=True, is_final_insert=True)
            elif role == 'assistant':
                self.insert_formatted_response(content, 'model', redraw=True, is_final_insert=True)
                
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)

    def show_history_window(self):
        """Opens a new Toplevel window to display past chat history summaries."""
        
        history_window = tk.Toplevel(self.master)
        history_window.title("Past Chat History")
        history_window.geometry("600x400")
        history_window.option_add('*Font', 'Arial 10')
        history_window.grid_rowconfigure(0, weight=1)
        history_window.grid_columnconfigure(0, weight=1)

        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            messagebox.showerror("Error", "Could not load chat history file.")
            history_window.destroy()
            return
            
        messages = data.get('messages', [])
        model_name = data.get('model', 'Unknown Model')
        current_theme_colors = COLOR_SCHEMES[self.current_theme.get()] 

        history_text = scrolledtext.ScrolledText(
            history_window, 
            wrap=tk.WORD, 
            state='disabled', 
            padx=10, 
            pady=10,
            bg=current_theme_colors["chat_bg"], 
            fg=current_theme_colors["fg_text"] 
        )
        history_text.grid(row=0, column=0, sticky="nsew")

        history_text.config(state='normal')
        
        history_text.insert(tk.END, f"--- Current Active Model: {model_name} ---\n\n", 'header')
        
        if len(messages) <= 1:
            history_text.insert(tk.END, "No user messages found in the current history.", 'normal')
        else:
            first_user_message = next((m for m in messages if m['role'] == 'user'), None)
            
            if first_user_message:
                summary = first_user_message['content']
                # The prompt from the user could be long, only show a snippet
                summary = summary.replace('\n', ' ')
                if len(summary) > 100:
                    summary = summary[:97] + '...'

                history_text.insert(tk.END, "Last Conversation Summary:\n", 'bold')
                history_text.insert(tk.END, f"Model: {model_name}\n", 'normal')
                history_text.insert(tk.END, f"First Request: \"{summary}\"\n", 'normal')
                history_text.insert(tk.END, f"Total Turns: {len(messages) - 1}\n\n", 'normal')
            else:
                history_text.insert(tk.END, "History only contains the system prompt.", 'normal')
            

        history_text.config(state='disabled')
        
        # Configure tags for history window
        history_text.tag_configure('header', font='Arial 12 bold', foreground=current_theme_colors["btn_history_bg"], justify='center')
        history_text.tag_configure('bold', font='Arial 10 bold', foreground=current_theme_colors["fg_text"])
        history_text.tag_configure('normal', font='Arial 10', foreground=current_theme_colors["fg_text"])
        
        self.update_status(f"Chat history window displayed.")


    # --- GUI & Formatting Methods ---
    def update_status(self, message, clear_after=5000):
        """Updates the status bar with a message."""
        self.status_bar.config(text=message)
        if clear_after > 0:
            self.master.after(clear_after, lambda: self.status_bar.config(text="Ready"))

    def _configure_tags(self):
        """
        Configures all the display tags for chat bubbles, dynamically pulling colors
        from the current theme.
        """
        colors = COLOR_SCHEMES[self.current_theme.get()]

        # User (Right Aligned Bubble)
        self.chat_history.tag_configure('user_bubble', 
            background=colors["user_bubble_bg"], 
            foreground=colors["user_bubble_fg"], 
            spacing1=3, spacing3=3,
            rmargin=10 
        )
        self.chat_history.tag_configure('user_label', 
            justify='right',
            font='Arial 9 bold',
            spacing1=10, spacing3=0,
            foreground=colors["fg_text"] 
        )

        # Model (Left Aligned Bubble)
        self.chat_history.tag_configure('model_bubble', 
            background=colors["model_bubble_bg"], 
            foreground=colors["model_bubble_fg"], 
            spacing1=3, spacing3=3,
            lmargin1=10, lmargin2=10
        )
        self.chat_history.tag_configure('model_label', 
            justify='left',
            font='Arial 9 bold',
            spacing1=10, spacing3=0,
            foreground=colors["fg_text"] 
        )
        
        # System Messages (Center)
        self.chat_history.tag_configure('system', foreground=colors["system_fg"], font='Arial 10 italic', justify='center')

    def _on_chat_resize(self, event):
        """Dynamically adjusts the margins for the chat bubbles on window resize."""
        width = self.chat_history.winfo_width()
        margin = int(width * 0.40)
        if margin < 100: margin = 100 
        
        self.chat_history.tag_configure('user_bubble', lmargin1=margin, lmargin2=margin)
        self.chat_history.tag_configure('model_bubble', rmargin=margin)
        
        self._update_embedded_windows_stretch()
            
    def _update_embedded_windows_stretch(self):
        """Ensures all embedded widgets (code blocks) stretch to fit the available width."""
        for mark in self.chat_history.dump('1.0', tk.END, window=True):
            if mark[2] == 'window':
                self.master.after(0, self.chat_history.window_configure, mark[1], stretch=tk.YES)
            
    def insert_system_message(self, message):
        """Inserts a non-bubble system message."""
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, f"\n--- [System] ---\n{message}\n\n", 'system')
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)

    def insert_formatted_response(self, text, role, redraw=False, is_final_insert=False):
        """
        Splits the text into parts, inserts labels, and handles code blocks.
        This function handles static display (user message, redraw, final AI message).
        """
        tag_bubble = f'{role}_bubble'
        tag_label = f'{role}_label'
        speaker_label = "[You]:" if role == 'user' else "[Model]:"
        
        if not redraw:
            self.chat_history.config(state='normal')
        
        # Insert speaker label only once 
        if redraw or role == 'user' or is_final_insert:
             self.chat_history.insert(tk.END, f"\n{speaker_label}\n", tag_label)
        
        if is_final_insert or redraw or role == 'user':
            # Code block regex: captures language and code content
            code_block_pattern = r'```(?P<language>[a-zA-Z0-9]+)?\s*\n(?P<code>[\s\S]*?)\n```'
            parts = re.split(code_block_pattern, text)
            
            i = 0
            while i < len(parts):
                text_part = parts[i]
                if text_part is not None and text_part.strip():
                    processed_text = text_part.strip()
                    # Remove markdown bold/italic markers for display consistency in Tkinter Text widget
                    processed_text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', processed_text)
                    processed_text = re.sub(r'\*([^\*]+)\*', r'\1', processed_text)
                    
                    self.chat_history.insert(tk.END, processed_text + '\n', tag_bubble)
                i += 1
                
                if i < len(parts) and parts[i] is not None and i + 1 < len(parts):
                    # Handle Code Block: parts[i] is language, parts[i+1] is code
                    language = parts[i] if parts[i] else "Code"
                    code_content = parts[i+1].strip()
                    self._insert_code_frame(code_content, language)
                    i += 2 
                else:
                    break 
        else:
            # For streaming, insert the raw content
            self.chat_history.insert(tk.END, text, tag_bubble)


        if not redraw:
            self.chat_history.config(state='disabled')
            self.chat_history.see(tk.END)

    def _insert_code_frame(self, code_content, language="Code"):
        """
        Inserts a Tkinter Frame widget containing the code (using ScrolledText for scrollable view) 
        and a copy button.
        """
        colors = COLOR_SCHEMES[self.current_theme.get()] 

        self.chat_history.insert(tk.END, '\n')
        
        # Outer wrapper frame (for alignment and stretch)
        code_wrapper_frame = tk.Frame(self.chat_history, padx=10, pady=5)
        
        # Inner frame containing header, code, and button
        frame = tk.Frame(code_wrapper_frame, bg=colors["code_bg"], relief=tk.RAISED, borderwidth=1) 
        frame.pack(fill=tk.X, expand=True) 
        
        # Header for Language and Copy Button
        header_frame = tk.Frame(frame, bg=colors["code_bg"])
        header_frame.pack(fill=tk.X, pady=(0, 2))
        
        tk.Label(
            header_frame,
            text=language,
            font='Arial 8 italic',
            fg=colors["code_fg"],
            bg=colors["code_bg"],
            anchor='w'
        ).pack(side=tk.LEFT, padx=5, pady=2)
        
        copy_button = tk.Button(
            header_frame, 
            text="Copy", 
            command=lambda c=code_content: self.copy_to_clipboard(c), 
            bg=colors["code_btn_bg"], fg=colors["code_btn_fg"], activebackground=colors["code_btn_bg"], 
            padx=5, pady=0, font='Arial 8'
        )
        copy_button.pack(side=tk.RIGHT, padx=5, pady=2)

        # ScrolledText widget for code content (handles horizontal scrolling)
        code_display = scrolledtext.ScrolledText(
            frame, 
            wrap=tk.NONE, # Important: disables word wrap
            height=min(10, len(code_content.split('\n')) + 1), # Max 10 lines, but adapt to content
            font='Courier 9', 
            fg=colors["code_fg"], 
            bg=colors["code_bg"],
            borderwidth=0,
            relief='flat',
            insertbackground=colors["code_fg"],
            padx=5, pady=5
        )
        code_display.insert(tk.END, code_content)
        code_display.config(state='disabled')
        code_display.pack(fill=tk.BOTH, expand=True) 

        self.chat_history.window_create(tk.END, window=code_wrapper_frame)
        self.chat_history.insert(tk.END, '\n', 'model_bubble') # Insert spacing after code block

    def copy_to_clipboard(self, text):
        """Copies the given text (code block content) to the system clipboard."""
        self.master.clipboard_clear()
        self.master.clipboard_append(text)
        self.update_status("Code copied to clipboard!", clear_after=2000)

    # --- Messaging & Streaming Methods ---
    
    def send_message_event(self, event):
        """Handles Enter keypress for sending the message."""
        if event.state & 0x1:  # Check for Shift key
            return self.insert_newline_event(event)
        
        self.send_message()
        return "break" # Prevents default newline insertion

    def insert_newline_event(self, event):
        """Handles Shift+Enter for inserting a newline."""
        self.user_input.insert(tk.INSERT, "\n")
        # Ensure scroll follows the insertion
        self.user_input.see(tk.INSERT)
        return "break" # Prevents default behavior

    def _set_controls_state(self, enabled=True):
        """Enables/disables UI controls based on the chat state."""
        state = 'normal' if enabled else 'disabled'
        self.user_input.config(state=state)
        self.send_button.config(state=state)
        self.model_combo.config(state='readonly' if enabled else 'disabled')
        self.new_chat_button.config(state=state)
        self.clear_history_button.config(state=state)
        self.history_button.config(state=state)
        self.toggle_theme_button.config(state=state)
        
        # Toggle Send/Stop buttons
        if enabled:
            self.send_button.pack(side=tk.LEFT, padx=(5, 0), anchor=tk.S)
            self.stop_button.pack_forget()
        else:
            self.send_button.pack_forget()
            self.stop_button.pack(side=tk.LEFT, padx=(5, 0), anchor=tk.S)

    def stop_generation(self):
        """Sets the stop event to halt the background thread."""
        self.stop_event.set()
        self.update_status("Stopping model generation...")

    def send_message(self):
        """Main function to trigger message processing and API call."""
        user_prompt = self.user_input.get('1.0', tk.END).strip()
        self.user_input.delete('1.0', tk.END)

        if not user_prompt:
            return

        self._set_controls_state(enabled=False)
        self.stop_event.clear() # Clear any previous stop signal
        self.last_user_prompt = user_prompt
        self.update_status(f"Sending prompt to {self.current_model.get()}...")

        # Add user message to history and display
        user_message = {'role': 'user', 'content': user_prompt}
        self.messages.append(user_message)
        self.insert_formatted_response(user_prompt, 'user', is_final_insert=True)
        self.save_history() # Save history after user message

        # Start a new thread for the API call to keep the UI responsive
        threading.Thread(target=self._get_model_response, daemon=True).start()

    def _get_model_response(self):
        """
        Runs in a separate thread. Calls the Ollama API and handles streaming.
        """
        model = self.current_model.get()
        assistant_message = {'role': 'assistant', 'content': ''}
        self.current_model_response = ""

        # Prepare messages for Ollama API (exclude the final system message display)
        chat_messages = self.messages[:] 
        
        # Insert initial label for streaming
        self.master.after(0, lambda: self.chat_history.config(state='normal'))
        self.master.after(0, lambda: self.chat_history.insert(tk.END, f"\n[Model]:\n", 'model_label'))
        self.master.after(0, lambda: self.chat_history.config(state='disabled'))
        
        self.streaming_start_index = self.chat_history.index(tk.END + '-1c') # Set start point for text

        try:
            # Note: The MockOllama implementation simulates stream=True
            response_stream = ollama.chat(
                model=model,
                messages=chat_messages,
                stream=True 
            )

            for chunk in response_stream:
                if self.stop_event.is_set():
                    break
                    
                content = chunk.get('message', {}).get('content', '')
                if content:
                    self.current_model_response += content
                    # Use self.master.after to safely update the GUI from the thread
                    self.master.after(0, self._stream_update, content)
            
            # Final processing after stream is finished or stopped
            self.master.after(0, self._finalize_response)

        except Exception as e:
            error_message = f"API Error: Could not get response from Ollama server. Check server status. ({e})"
            self.master.after(0, self.insert_system_message, error_message)
            self.master.after(0, lambda: self.update_status("Error communicating with Ollama server.", clear_after=8000))
            self.master.after(0, lambda: self._set_controls_state(enabled=True))
            
    def _stream_update(self, content):
        """Safely updates the ScrolledText widget with new content."""
        self.chat_history.config(state='normal')
        self.chat_history.insert(tk.END, content, 'model_bubble')
        self.chat_history.config(state='disabled')
        self.chat_history.see(tk.END)
        self.update_status(f"Streaming response from {self.current_model.get()}...")
        
    def _finalize_response(self):
        """Cleans up the final response and re-applies formatting."""
        
        # 1. Update the final assistant message content
        if not self.current_model_response.strip():
            final_message = "I'm sorry, I received no content. The response may have been stopped or empty."
        else:
            final_message = self.current_model_response

        # 2. Add the final message to history
        self.messages.append({'role': 'assistant', 'content': final_message})
        self.save_history()

        # 3. Redraw the final message with proper formatting (code blocks)
        self.chat_history.config(state='normal')
        
        # a. Remove the streamed text (this is faster than finding the block to replace)
        if self.streaming_start_index:
             # Find the start of the streamed text after the [Model]: label
            start_stream = self.chat_history.index(self.streaming_start_index + "+1c") 
            self.chat_history.delete(start_stream, tk.END)
            self.streaming_start_index = None # Reset 
        
        # b. Re-insert the full, final, formatted message
        self.insert_formatted_response(final_message, 'model', is_final_insert=True)
        
        # 4. Restore controls and status
        self._set_controls_state(enabled=True)
        if self.stop_event.is_set():
            self.update_status("Generation stopped and response finalized.", clear_after=5000)
            self.stop_event.clear()
        else:
            self.update_status("Response complete.", clear_after=5000)

if __name__ == "__main__":
    root = tk.Tk()
    app = OllamaChatApp(root)
    
    # Save history on close
    def on_closing():
        app.save_history()
        root.destroy()
        
    # User memory: The user has a working constraint related to the laptop lid.
    # While this doesn't directly affect the code, it's a good reminder
    # to ensure the application cleans up gracefully, which the on_closing handles.
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

