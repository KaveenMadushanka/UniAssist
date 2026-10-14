
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

conversation_context = {
    "last_message": "",
    "last_topic": None
}

vosk_model = None
is_recording = False
is_typing = False


# -------------------- Chat Functions --------------------

def add_chat_message(message):
    """Display a complete message in the chat area."""
    chat_area.config(state="normal")
    chat_area.insert(tk.END, message)
    chat_area.config(state="disabled")
    chat_area.see(tk.END)


def typewriter_response(response):
    """Display the chatbot response one character at a time."""
    global is_typing

    is_typing = True
    add_chat_message("UniAssist: ")

    # Start English voice output separately.
    threading.Thread(
        target=speak_answer,
        args=(response,),
        daemon=True
    ).start()

    def show_character(index=0):
        global is_typing

        if index < len(response):
            chat_area.config(state="normal")
            chat_area.insert(tk.END, response[index])
            chat_area.config(state="disabled")
            chat_area.see(tk.END)

            root.after(
                15,
                show_character,
                index + 1
            )
        else:
            add_chat_message("\n\n")
            is_typing = False
            message_entry.focus_set()

    show_character()


def speak_answer(response):
    """Read the English parts of a response aloud."""
    try:
        # Sinhala text is displayed but not sent to English TTS.
        english_text = re.sub(
            r"[\u0D80-\u0DFF]",
            " ",
            response
        )

        english_text = " ".join(english_text.split())

        if not english_text:
            return

        engine = pyttsx3.init()

        # Prefer Microsoft Zira if available.
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
        status_label.config(
            text="Please select your student category."
        )
        return

    status_label.config(text="")

    home_frame.pack_forget()
    chat_frame.pack(fill="both", expand=True)

    add_chat_message(
        f"UniAssist: Welcome! Your category: {student_type}\n"
        f"University: {university}\n\n"
        "Ask your question in English or Sinhala.\n"
        "ඔබගේ ප්‍රශ්නය English හෝ සිංහලෙන් අහන්න.\n\n"
    )

    message_entry.focus_set()


def is_university_follow_up(message):
    normalized = " ".join(message.casefold().split())

    university_names = [
        "university of colombo",
        "university of moratuwa",
        "university of peradeniya",
        "sabaragamuwa university of sri lanka",
        "sabaragamuwa university",
        "sabaragamuwa campus"
    ]

    return any(
        name in normalized
        for name in university_names
    )


def send_message(event=None):
    """Send a message and display the response."""
    global is_typing

    if is_typing:
        return "break" if event else None

    message = message_entry.get(
        "1.0",
        "end-1c"
    ).strip()

    if not message:
        return "break" if event else None

    add_chat_message(f"You: {message}\n\n")

    student_type = category.get()
    university = university_choice.get()

    try:
        if (
            is_university_follow_up(message)
            and conversation_context["last_topic"]
        ):
            previous_topic = conversation_context["last_topic"]

            response = get_response(
                f"{previous_topic} {message}",
                student_type,
                university
            )
        else:
            response = get_response(
                message,
                student_type,
                university
            )

        lower_message = message.casefold()

        topic_keywords = [
            "computer science",
            "computing",
            "software engineering",
            "information technology",
            "engineering",
            "management",
            "business",
            "science degree",
            "degree courses",
            "degree programme",
            "degree programs",
            "degree"
        ]

        if any(
            keyword in lower_message
            for keyword in topic_keywords
        ):
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
    """Record English speech in a background thread."""
    global is_recording

    if is_recording:
        return

    if is_typing:
        voice_status_label.config(
            text="Please wait for the current answer."
        )
        return

    is_recording = True
    voice_button.config(state="disabled")
    voice_status_label.config(
        text="Recording... Speak in English for 10 seconds."
    )

    threading.Thread(
        target=recognize_speech,
        daemon=True
    ).start()


def recognize_speech():
    """Record audio and convert it into English text."""
    global is_recording, vosk_model

    try:
        if vosk_model is None:
            root.after(
                0,
                lambda: voice_status_label.config(
                    text="Loading English speech model..."
                )
            )

            vosk_model = Model(MODEL_PATH)

        recognizer = KaldiRecognizer(
            vosk_model,
            SAMPLE_RATE
        )

        audio = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            device=MICROPHONE_DEVICE
        )

        sd.wait()

        audio_bytes = audio.tobytes()

        if recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(recognizer.Result())
        else:
            result = json.loads(recognizer.FinalResult())

        recognized_text = result.get("text", "").strip()

        root.after(
            0,
            finish_voice_input,
            recognized_text,
            None
        )

    except Exception as error:
        print("Speech recognition error:", error)

        root.after(
            0,
            finish_voice_input,
            "",
            str(error)
        )


def finish_voice_input(recognized_text, error):
    """Update the Tkinter interface after recording."""
    global is_recording

    is_recording = False
    voice_button.config(state="normal")

    if error:
        voice_status_label.config(
            text="Voice input failed. Check the terminal."
        )
        return

    if recognized_text:
        message_entry.insert(
            tk.END,
            recognized_text + " "
        )
        message_entry.focus_set()

        voice_status_label.config(
            text="Speech recognized. Check the text and press Send."
        )
    else:
        voice_status_label.config(
            text="No speech recognized. Please try again."
        )


# -------------------- Navigation --------------------

def go_home():
    if is_recording or is_typing:
        return

    chat_frame.pack_forget()
    home_frame.pack(fill="both", expand=True)


# -------------------- Main Window --------------------

root = tk.Tk()
root.title("UniAssist - Student Support Chatbot")
root.geometry("900x700")
root.minsize(700, 550)
root.configure(bg="#f1f5f9")

default_font = tkfont.nametofont("TkDefaultFont")
default_font.configure(
    family="Nirmala UI",
    size=10
)

text_font = tkfont.Font(
    root=root,
    family="Nirmala UI",
    size=12
)


# -------------------- Home Screen --------------------

home_frame = tk.Frame(
    root,
    bg="#f1f5f9"
)
home_frame.pack(fill="both", expand=True)

tk.Label(
    home_frame,
    text="UniAssist",
    font=("Segoe UI", 28, "bold"),
    bg="#f1f5f9",
    fg="#17365d"
).pack(pady=(35, 5))

tk.Label(
    home_frame,
    text="University Student Support Chatbot",
    font=("Segoe UI", 13),
    bg="#f1f5f9",
    fg="#475569"
).pack()

tk.Label(
    home_frame,
    text="සිංහල සහ English භාෂා දෙකෙන්ම ප්‍රශ්න අහන්න",
    font=text_font,
    bg="#f1f5f9",
    fg="#475569"
).pack(pady=(5, 25))

tk.Label(
    home_frame,
    text="Who are you?",
    font=("Segoe UI", 14, "bold"),
    bg="#f1f5f9",
    fg="#17365d"
).pack()

category = tk.StringVar(value="A/L Student")

tk.Radiobutton(
    home_frame,
    text="A/L Completed - University Admission",
    variable=category,
    value="A/L Student",
    font=("Segoe UI", 11),
    bg="#f1f5f9"
).pack(pady=5)

tk.Radiobutton(
    home_frame,
    text="Current University Student",
    variable=category,
    value="University Student",
    font=("Segoe UI", 11),
    bg="#f1f5f9"
).pack(pady=5)

tk.Radiobutton(
    home_frame,
    text="General University Information",
    variable=category,
    value="General",
    font=("Segoe UI", 11),
    bg="#f1f5f9"
).pack(pady=5)

tk.Label(
    home_frame,
    text="Select your university (optional)",
    font=("Segoe UI", 11, "bold"),
    bg="#f1f5f9"
).pack(pady=(20, 5))

university_choice = tk.StringVar(
    value="General / Any University"
)

university_list = [
    "General / Any University",
    "University of Colombo",
    "University of Moratuwa",
    "University of Peradeniya",
    "Sabaragamuwa University of Sri Lanka",
    "Other / Not Listed"
]

university_box = ttk.Combobox(
    home_frame,
    textvariable=university_choice,
    values=university_list,
    state="readonly",
    width=42
)
university_box.pack(pady=5)

tk.Label(
    home_frame,
    text=(
        "Campus-specific information will be added "
        "after verification."
    ),
    font=("Segoe UI", 9),
    bg="#f1f5f9",
    fg="#64748b"
).pack(pady=5)

status_label = tk.Label(
    home_frame,
    text="",
    bg="#f1f5f9",
    fg="red"
)
status_label.pack()

tk.Button(
    home_frame,
    text="Start Chatting",
    command=open_chat,
    font=("Segoe UI", 12, "bold"),
    bg="#17365d",
    fg="white",
    padx=25,
    pady=10
).pack(pady=22)


# -------------------- Chat Screen --------------------

chat_frame = tk.Frame(
    root,
    bg="#f1f5f9"
)

chat_header = tk.Frame(
    chat_frame,
    bg="#17365d"
)
chat_header.pack(fill="x")

tk.Label(
    chat_header,
    text="UniAssist Chat",
    font=("Segoe UI", 18, "bold"),
    bg="#17365d",
    fg="white"
).pack(side="left", padx=18, pady=12)

tk.Button(
    chat_header,
    text="Home",
    command=go_home
).pack(side="right", padx=15, pady=12)

chat_area = scrolledtext.ScrolledText(
    chat_frame,
    wrap=tk.WORD,
    font=text_font,
    bg="white",
    fg="#172033",
    padx=12,
    pady=12,
    state="disabled"
)

chat_area.pack(
    fill="both",
    expand=True,
    padx=18,
    pady=15
)


# -------------------- Message Input --------------------

input_frame = tk.Frame(
    chat_frame,
    bg="#f1f5f9"
)
input_frame.pack(
    fill="x",
    padx=18,
    pady=(0, 5)
)

message_entry = tk.Text(
    input_frame,
    font=text_font,
    height=2,
    wrap=tk.WORD,
    undo=True,
    padx=8,
    pady=6
)

message_entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(0, 8)
)

message_entry.bind("<Return>", send_message)
message_entry.bind("<Shift-Return>", insert_newline)

button_frame = tk.Frame(
    input_frame,
    bg="#f1f5f9"
)
button_frame.pack(side="left")

voice_button = tk.Button(
    button_frame,
    text="Speak English",
    command=start_voice_input,
    bg="#0f766e",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    padx=10,
    pady=8
)
voice_button.pack(fill="x", pady=(0, 5))

tk.Button(
    button_frame,
    text="Send",
    command=send_message,
    bg="#17365d",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    padx=20,
    pady=8
).pack(fill="x")

voice_status_label = tk.Label(
    chat_frame,
    text="",
    bg="#f1f5f9",
    fg="#475569",
    anchor="w"
)
voice_status_label.pack(
    fill="x",
    padx=20,
    pady=(0, 10)
)


# -------------------- Run Application --------------------

root.mainloop()
