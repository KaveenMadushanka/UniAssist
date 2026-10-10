
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, scrolledtext

from chatbot import get_response


# -------------------- Chat Functions --------------------

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

    chat_area.config(state="normal")
    chat_area.insert(
        tk.END,
        f"UniAssist: Welcome! Your category: {student_type}\n"
        f"University: {university}\n\n"
        "Ask your question in English or Sinhala.\n"
        "ඔබගේ ප්‍රශ්නය English හෝ සිංහලෙන් අහන්න.\n\n"
    )
    chat_area.config(state="disabled")
    chat_area.see(tk.END)

    message_entry.focus_set()


def send_message(event=None):
    # Read the message without the final newline
    message = message_entry.get("1.0", "end-1c").strip()

    if not message:
        if event:
            return "break"
        return

    # Display the user's message
    chat_area.config(state="normal")
    chat_area.insert(tk.END, f"You: {message}\n\n")

    # Get a response from chatbot.py
    try:
        response = get_response(
            message,
            category.get(),
            university_choice.get()
        )
    except Exception as error:
        print("Chatbot error:", error)
        response = (
            "Sorry, something went wrong while finding an answer.\n\n"
            "සමාවන්න, පිළිතුර ලබාගැනීමේදී දෝෂයක් ඇති වුණා."
        )

    # Display the chatbot response
    chat_area.insert(
        tk.END,
        f"UniAssist: {response}\n\n"
    )
    chat_area.config(state="disabled")
    chat_area.see(tk.END)

    # Clear the input box
    message_entry.delete("1.0", tk.END)
    message_entry.focus_set()

    # Prevent Enter from inserting an extra newline
    if event:
        return "break"


def insert_newline(event):
    # Shift + Enter inserts a new line
    message_entry.insert(tk.INSERT, "\n")
    return "break"


def go_home():
    chat_frame.pack_forget()
    home_frame.pack(fill="both", expand=True)


# -------------------- Main Window --------------------

root = tk.Tk()
root.title("UniAssist - Student Support Chatbot")
root.geometry("800x650")
root.minsize(650, 500)
root.configure(bg="#f1f5f9")

# Set default font
default_font = tkfont.nametofont("TkDefaultFont")
default_font.configure(
    family="Nirmala UI",
    size=10
)

# Set text font
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

category = tk.StringVar(
    value="A/L Student"
)

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
    pady=(0, 18)
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

# Enter sends the message
message_entry.bind(
    "<Return>",
    send_message
)

# Shift + Enter inserts a new line
message_entry.bind(
    "<Shift-Return>",
    insert_newline
)

tk.Button(
    input_frame,
    text="Send",
    command=send_message,
    bg="#17365d",
    fg="white",
    font=("Segoe UI", 10, "bold"),
    padx=20,
    pady=8
).pack(side="left")


# -------------------- Run Application --------------------

root.mainloop()
