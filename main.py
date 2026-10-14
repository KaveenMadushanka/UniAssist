import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, scrolledtext
import threading
import json
import re

import sounddevice as sd
import pyttsx3
from vosk import Model, KaldiRecognizer

from chatbot import get_response


# -------------------- Configuration --------------------
MODEL_PATH = "models/vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000
RECORD_SECONDS = 10
MICROPHONE_DEVICE = 2

BG = "#F3F6FB"
NAVY = "#123B68"
NAVY_DARK = "#0B2D50"
BLUE = "#2F80ED"
PALE_BLUE = "#EAF3FF"
TEXT = "#1F2937"
MUTED = "#64748B"
WHITE = "#FFFFFF"
GREEN = "#159B68"
RED = "#DC5555"
BORDER = "#DCE5F0"

conversation_context = {"last_message": "", "last_topic": None}
vosk_model = None
is_recording = False
is_typing = False


# -------------------- Helpers --------------------
def make_button(parent, text, command, bg=NAVY, fg=WHITE, active_bg=BLUE, **kwargs):
    # Set defaults first so callers can safely override font/padding.
    kwargs.setdefault("font", ("Segoe UI", 10, "bold"))
    kwargs.setdefault("padx", 14)
    kwargs.setdefault("pady", 10)
    return tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, activebackground=active_bg, activeforeground=WHITE,
        relief="flat", bd=0, cursor="hand2",
        **kwargs
    )


def add_chat_message(message):
    chat_area.configure(state="normal")
    chat_area.insert(tk.END, message)
    chat_area.configure(state="disabled")
    chat_area.see(tk.END)


def add_user_message(message):
    chat_area.configure(state="normal")
    chat_area.insert(tk.END, "  YOU\n", "user_label")
    chat_area.insert(tk.END, f"  {message}\n\n", "user_bubble")
    chat_area.configure(state="disabled")
    chat_area.see(tk.END)


def typewriter_response(response):
    global is_typing
    is_typing = True
    chat_area.configure(state="normal")
    chat_area.insert(tk.END, "  UNIASSIST\n", "bot_label")
    start_index = chat_area.index(tk.END)
    chat_area.insert(tk.END, "")
    chat_area.configure(state="disabled")

    threading.Thread(target=speak_answer, args=(response,), daemon=True).start()

    def show_character(index=0):
        global is_typing
        if index < len(response):
            chat_area.configure(state="normal")
            chat_area.insert(tk.END, response[index], "bot_bubble")
            chat_area.configure(state="disabled")
            chat_area.see(tk.END)
            root.after(12, show_character, index + 1)
        else:
            chat_area.configure(state="normal")
            chat_area.insert(tk.END, "\n\n")
            chat_area.configure(state="disabled")
            chat_area.see(tk.END)
            is_typing = False
            message_entry.focus_set()

    show_character()


def speak_answer(response):
    """Read English text only; Sinhala text remains visible in the chat."""
    try:
        english_text = re.sub(r"[\u0D80-\u0DFF]", " ", response)
        english_text = " ".join(english_text.split())
        if not english_text:
            return
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        for voice in voices:
            if "zira" in voice.name.casefold():
                engine.setProperty("voice", voice.id)
                break
        engine.setProperty("rate", 165)
        engine.say(english_text)
        engine.runAndWait()
        engine.stop()
    except Exception as error:
        print("Voice output error:", error)


def open_chat():
    student_type = category.get()
    university = university_choice.get()
    if not student_type:
        status_label.config(text="Please select your student category.")
        return
    status_label.config(text="")
    home_frame.pack_forget()
    chat_frame.pack(fill="both", expand=True)
    if not chat_started[0]:
        add_chat_message(
            f"  UNIASSIST  •  WELCOME\n\n"
            f"Welcome! Your category: {student_type}\n"
            f"University: {university}\n\n"
            "Ask your question in English or Sinhala.\n"
            "ඔබගේ ප්‍රශ්නය English හෝ සිංහලෙන් අහන්න.\n\n"
        )
        chat_started[0] = True
    message_entry.focus_set()


def is_university_follow_up(message):
    normalized = " ".join(message.casefold().split())
    university_names = [
        "university of colombo", "university of moratuwa",
        "university of peradeniya", "sabaragamuwa university of sri lanka",
        "sabaragamuwa university", "sabaragamuwa campus"
    ]
    return any(name in normalized for name in university_names)


def send_message(event=None):
    global is_typing
    if is_typing:
        return "break" if event else None
    message = message_entry.get("1.0", "end-1c").strip()
    if not message:
        return "break" if event else None

    add_user_message(message)
    student_type = category.get()
    university = university_choice.get()
    try:
        if is_university_follow_up(message) and conversation_context["last_topic"]:
            previous_topic = conversation_context["last_topic"]
            response = get_response(
                f"{previous_topic} {message}", student_type, university
            )
        else:
            response = get_response(message, student_type, university)

        lower_message = message.casefold()
        topic_keywords = [
            "computer science", "computing", "software engineering",
            "information technology", "engineering", "management",
            "business", "science degree", "degree courses",
            "degree programme", "degree programs", "degree"
        ]
        if any(keyword in lower_message for keyword in topic_keywords):
            conversation_context["last_topic"] = message
        conversation_context["last_message"] = message
    except Exception as error:
        print("Chatbot error:", error)
        response = (
            "Sorry, something went wrong while finding an answer.\n\n"
            "සමාවන්න, පිළිතුර ලබාගැනීමේදී දෝෂයක් ඇති වුණා."
        )

    message_entry.delete("1.0", tk.END)
    typewriter_response(str(response))
    if event:
        return "break"


def insert_newline(event):
    message_entry.insert(tk.INSERT, "\n")
    return "break"


# -------------------- English Voice Input --------------------
def start_voice_input():
    global is_recording
    if is_recording:
        return
    if is_typing:
        voice_status_label.config(text="Please wait for the current answer.")
        return

    is_recording = True
    voice_button.config(state="disabled", text="Listening...")
    voice_status_label.config(text=f"Recording... Speak English for {RECORD_SECONDS} seconds.")
    threading.Thread(target=recognize_speech, daemon=True).start()


def recognize_speech():
    global is_recording, vosk_model
    try:
        if vosk_model is None:
            root.after(0, lambda: voice_status_label.config(text="Loading English speech model..."))
            vosk_model = Model(MODEL_PATH)

        recognizer = KaldiRecognizer(vosk_model, SAMPLE_RATE)
        audio = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE, channels=1, dtype="int16",
            device=MICROPHONE_DEVICE
        )
        sd.wait()
        audio_bytes = audio.tobytes()
        if recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(recognizer.Result())
        else:
            result = json.loads(recognizer.FinalResult())
        recognized_text = result.get("text", "").strip()
        root.after(0, finish_voice_input, recognized_text, None)
    except Exception as error:
        print("Speech recognition error:", error)
        root.after(0, finish_voice_input, "", str(error))


def finish_voice_input(recognized_text, error):
    global is_recording
    is_recording = False
    voice_button.config(state="normal", text="🎙  Speak English")
    if error:
        voice_status_label.config(text="Voice input failed. Check the terminal or microphone settings.")
        return
    if recognized_text:
        current_text = message_entry.get("1.0", "end-1c").strip()
        combined = f"{current_text} {recognized_text}".strip()
        message_entry.delete("1.0", tk.END)
        message_entry.insert("1.0", combined)
        message_entry.focus_set()
        voice_status_label.config(text="Speech recognized. Review the text, then press Send.")
    else:
        voice_status_label.config(text="No speech recognized. Please try again.")


# -------------------- Navigation --------------------
def go_home():
    if is_recording or is_typing:
        return
    chat_frame.pack_forget()
    home_frame.pack(fill="both", expand=True)


# -------------------- Main Window --------------------
root = tk.Tk()
root.title("UniAssist | Student Support Chatbot")
root.geometry("1100x760")
root.minsize(780, 600)
root.configure(bg=BG)

default_font = tkfont.nametofont("TkDefaultFont")
default_font.configure(family="Segoe UI", size=10)
text_font = tkfont.Font(root=root, family="Segoe UI", size=11)
chat_started = [False]

style = ttk.Style(root)
try:
    style.theme_use("clam")
except tk.TclError:
    pass
style.configure("Uni.TCombobox", padding=9, fieldbackground=WHITE, background=WHITE)
style.map("Uni.TCombobox", fieldbackground=[("readonly", WHITE)])


# -------------------- Home Screen --------------------
home_frame = tk.Frame(root, bg=BG)
home_frame.pack(fill="both", expand=True)

home_top = tk.Frame(home_frame, bg=BG)
home_top.pack(fill="x", padx=42, pady=(34, 18))
tk.Label(home_top, text="🎓  UniAssist", font=("Segoe UI", 30, "bold"),
         bg=BG, fg=NAVY).pack(anchor="w")
tk.Label(home_top, text="University Student Support Chatbot",
         font=("Segoe UI", 13), bg=BG, fg=MUTED).pack(anchor="w", pady=(3, 4))
tk.Label(home_top, text="සිංහල සහ English භාෂා දෙකෙන්ම ප්‍රශ්න අහන්න",
         font=("Nirmala UI", 11), bg=BG, fg=MUTED).pack(anchor="w")

home_card = tk.Frame(home_frame, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
home_card.pack(fill="both", expand=True, padx=42, pady=(0, 34))
home_inner = tk.Frame(home_card, bg=WHITE)
home_inner.pack(fill="both", expand=True, padx=34, pady=28)

tk.Label(home_inner, text="Let's get started", font=("Segoe UI", 20, "bold"),
         bg=WHITE, fg=TEXT).pack(anchor="w")
tk.Label(home_inner, text="Personalize your experience before starting a chat.",
         font=("Segoe UI", 10), bg=WHITE, fg=MUTED).pack(anchor="w", pady=(4, 22))

tk.Label(home_inner, text="WHO ARE YOU?", font=("Segoe UI", 9, "bold"),
         bg=WHITE, fg=MUTED).pack(anchor="w", pady=(0, 8))
category = tk.StringVar(value="A/L Student")
for label, value in [
    ("A/L completed — looking for university admission", "A/L Student"),
    ("Current university student", "University Student"),
    ("General university information", "General")
]:
    tk.Radiobutton(
        home_inner, text=label, variable=category, value=value,
        font=("Segoe UI", 11), bg=WHITE, fg=TEXT, activebackground=WHITE,
        selectcolor=PALE_BLUE, padx=6, pady=5, cursor="hand2"
    ).pack(anchor="w")

tk.Label(home_inner, text="SELECT YOUR UNIVERSITY (OPTIONAL)",
         font=("Segoe UI", 9, "bold"), bg=WHITE, fg=MUTED).pack(anchor="w", pady=(20, 7))
university_choice = tk.StringVar(value="General / Any University")
university_list = [
    "General / Any University", "University of Colombo",
    "University of Moratuwa", "University of Peradeniya",
    "Sabaragamuwa University of Sri Lanka", "Other / Not Listed"
]
university_box = ttk.Combobox(
    home_inner, textvariable=university_choice, values=university_list,
    state="readonly", style="Uni.TCombobox", font=("Segoe UI", 11), width=45
)
university_box.pack(anchor="w", fill="x")
tk.Label(
    home_inner,
    text="ⓘ  Campus-specific information should be verified with official sources.",
    font=("Segoe UI", 9), bg=WHITE, fg=MUTED, wraplength=700, justify="left"
).pack(anchor="w", pady=(10, 10))

status_label = tk.Label(home_inner, text="", bg=WHITE, fg=RED, font=("Segoe UI", 10))
status_label.pack(anchor="w")
make_button(home_inner, "Start chatting   →", open_chat, bg=NAVY, active_bg=BLUE,
            font=("Segoe UI", 11, "bold"), padx=22, pady=12).pack(anchor="w", pady=(10, 0))


# -------------------- Chat Screen --------------------
chat_frame = tk.Frame(root, bg=BG)

sidebar = tk.Frame(chat_frame, bg=NAVY_DARK, width=220)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)
tk.Label(sidebar, text="🎓", font=("Segoe UI Emoji", 30),
         bg=NAVY_DARK, fg=WHITE).pack(anchor="w", padx=22, pady=(25, 0))
tk.Label(sidebar, text="UniAssist", font=("Segoe UI", 20, "bold"),
         bg=NAVY_DARK, fg=WHITE).pack(anchor="w", padx=22, pady=(2, 0))
tk.Label(sidebar, text="STUDENT SUPPORT", font=("Segoe UI", 8, "bold"),
         bg=NAVY_DARK, fg="#B7D5F4").pack(anchor="w", padx=23, pady=(0, 28))
make_button(sidebar, "⌂   Home", go_home, bg="#20476F", active_bg="#2B5887").pack(fill="x", padx=14, pady=(0, 8))
tk.Label(sidebar, text="YOUR SESSION", font=("Segoe UI", 8, "bold"),
         bg=NAVY_DARK, fg="#B7D5F4").pack(anchor="w", padx=22, pady=(24, 8))
session_label = tk.Label(sidebar, text="", font=("Segoe UI", 10),
                         bg=NAVY_DARK, fg=WHITE, justify="left", wraplength=175)
session_label.pack(anchor="w", padx=22)
tk.Label(sidebar, text="Offline voice support\nEnglish speech input\nEnglish voice output",
         font=("Segoe UI", 9), bg=NAVY_DARK, fg="#C8D9EA",
         justify="left").pack(side="bottom", anchor="w", padx=22, pady=22)

main_panel = tk.Frame(chat_frame, bg=BG)
main_panel.pack(side="left", fill="both", expand=True)

chat_header = tk.Frame(main_panel, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
chat_header.pack(fill="x", padx=18, pady=(18, 10))
header_left = tk.Frame(chat_header, bg=WHITE)
header_left.pack(side="left", padx=18, pady=13)
tk.Label(header_left, text="UniAssist Chat", font=("Segoe UI", 17, "bold"),
         bg=WHITE, fg=NAVY).pack(anchor="w")
tk.Label(header_left, text="Ask questions about university life and study options",
         font=("Segoe UI", 9), bg=WHITE, fg=MUTED).pack(anchor="w", pady=(2, 0))
voice_status_label = tk.Label(chat_header, text="● Voice ready", font=("Segoe UI", 9, "bold"),
                              bg=WHITE, fg=GREEN)
voice_status_label.pack(side="right", padx=18)

chat_area = scrolledtext.ScrolledText(
    main_panel, wrap=tk.WORD, font=text_font, bg=WHITE, fg=TEXT,
    padx=20, pady=18, state="disabled", relief="flat", bd=0,
    highlightbackground=BORDER, highlightthickness=1, spacing1=3, spacing3=5
)
chat_area.pack(fill="both", expand=True, padx=18, pady=(0, 10))
chat_area.tag_configure("user_label", foreground=BLUE, font=("Segoe UI", 9, "bold"), spacing1=8)
chat_area.tag_configure("user_bubble", foreground=NAVY_DARK, background=PALE_BLUE,
                        lmargin1=10, lmargin2=10, rmargin=90, spacing1=5, spacing3=10)
chat_area.tag_configure("bot_label", foreground=GREEN, font=("Segoe UI", 9, "bold"), spacing1=8)
chat_area.tag_configure("bot_bubble", foreground=TEXT, lmargin1=10, lmargin2=10,
                        rmargin=45, spacing1=5, spacing3=8)

voice_bar = tk.Frame(main_panel, bg=BG)
voice_bar.pack(fill="x", padx=18, pady=(0, 8))
voice_button = make_button(voice_bar, "🎙  Speak English", start_voice_input,
                           bg=GREEN, active_bg="#117B54")
voice_button.pack(side="left")
tk.Label(voice_bar, text=f"Records up to {RECORD_SECONDS} seconds",
         font=("Segoe UI", 9), bg=BG, fg=MUTED).pack(side="left", padx=12)

input_card = tk.Frame(main_panel, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
input_card.pack(fill="x", padx=18, pady=(0, 18))
message_entry = tk.Text(
    input_card, font=text_font, height=3, wrap=tk.WORD, undo=True,
    padx=12, pady=10, relief="flat", bd=0, bg=WHITE, fg=TEXT,
    insertbackground=NAVY
)
message_entry.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
message_entry.bind("<Return>", send_message)
message_entry.bind("<Shift-Return>", insert_newline)
make_button(input_card, "Send  ➤", send_message, bg=NAVY, active_bg=BLUE,
            font=("Segoe UI", 10, "bold"), padx=18, pady=14).pack(side="right", padx=8, pady=8)

root.mainloop()
