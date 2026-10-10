
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, scrolledtext


# -------------------- Chatbot Responses --------------------

def get_response(message, student_type, university):
    text = message.strip().lower()

    if any(word in text for word in [
        "hello", "hi", "hey", "හෙලෝ", "ආයුබෝවන්"
    ]):
        return (
            "Hello! Welcome to UniAssist. How can I help you?\n"
            "ආයුබෝවන්! UniAssist වෙත සාදරයෙන් පිළිගන්නවා."
        )

    # A/L student questions
    if student_type == "A/L Student":

        if any(word in text for word in [
            "z-score", "z score", "zscore", "z-score එක"
        ]):
            return (
                "A Z-score is used in Sri Lankan university admission "
                "to compare examination performance. Admission cut-offs "
                "depend on the course, district and admission year. "
                "Please check the latest official UGC handbook.\n\n"
                "Z-score එක විශ්වවිද්‍යාල ප්‍රවේශයේදී භාවිතා කරන "
                "ලකුණක්. Cut-off අගයන් පාඨමාලාව, දිස්ත්‍රික්කය සහ "
                "වර්ෂය අනුව වෙනස් වෙනවා. නවතම UGC තොරතුරු බලන්න."
            )

        if any(word in text for word in [
            "degree", "course", "උපාධි", "පාඨමාලා"
        ]):
            return (
                "You can explore degrees in IT, Computer Science, "
                "Engineering, Management, Science and other fields. "
                "Your eligible options depend on your A/L subjects "
                "and official admission rules.\n\n"
                "ඔබගේ A/L විෂයන් අනුව ලබාගත හැකි උපාධි වෙනස් වෙනවා. "
                "සුදුසුකම් සඳහා නවතම UGC handbook එක බලන්න."
            )

        if any(word in text for word in [
            "admission", "apply", "university",
            "ඇතුළත්", "විශ්වවිද්‍යාලයට", "අයදුම්"
        ]):
            return (
                "University admission requirements and application "
                "dates can change. Check the official UGC website:\n"
                "https://www.ugc.ac.lk/\n\n"
                "විශ්වවිද්‍යාල ප්‍රවේශය සහ අයදුම් කරන දින වෙනස් "
                "විය හැකියි. UGC නිල වෙබ් අඩවිය පරීක්ෂා කරන්න."
            )

    # Current university student questions
    if student_type == "University Student":

        if "gpa" in text:
            return (
                "GPA is usually calculated using course grade points "
                "and credits. The exact method depends on your university.\n\n"
                "GPA ගණනය කිරීමේදී grades සහ credits භාවිතා කරනවා. "
                "නිශ්චිත ක්‍රමය ඔබගේ university එක අනුව වෙනස් විය හැකියි."
            )

        if any(word in text for word in [
            "exam", "assignment", "විභාග", "පැවරුම්"
        ]):
            return (
                "Check your university LMS, course outline or official "
                "announcements for exam dates and assignment deadlines.\n\n"
                "විභාග දින සහ assignment deadlines සඳහා university "
                "LMS එක හෝ නිල නිවේදන පරීක්ෂා කරන්න."
            )

    # General questions
    if any(word in text for word in [
        "scholarship", "ශිෂ්‍යත්ව"
    ]):
        return (
            "Scholarship availability and eligibility vary. Check "
            "official university announcements and relevant student "
            "support information.\n\n"
            "ශිෂ්‍යත්ව සඳහා සුදුසුකම් සහ අවස්ථා වෙනස් වෙනවා. "
            "විශ්වවිද්‍යාලයේ නිල නිවේදන පරීක්ෂා කරන්න."
        )

    if any(word in text for word in [
        "thank", "ස්තුතියි", "ස්තූතියි"
    ]):
        return "You're welcome! / ඔබට උදව් කිරීමට සතුටුයි!"

    return (
        "Sorry, I don't have a verified answer for that question yet. "
        "Please try another question or check an official source.\n\n"
        "සමාවන්න, මේ ප්‍රශ්නයට තහවුරු කළ පිළිතුරක් තවම නැහැ. "
        "ප්‍රශ්නය වෙනත් ආකාරයකින් අහන්න හෝ නිල මූලාශ්‍රයක් බලන්න."
    )


# -------------------- Chat Functions --------------------

def open_chat():
    student_type = category.get()
    university = university_choice.get()

    if not student_type:
        status_label.config(
            text="Please select your student category."
        )
        return

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
    # Read text without the automatic final newline
    message = message_entry.get("1.0", "end-1c").strip()

    if not message:
        return "break" if event else None

    chat_area.config(state="normal")
    chat_area.insert(tk.END, f"You: {message}\n\n")

    response = get_response(
        message,
        category.get(),
        university_choice.get()
    )

    chat_area.insert(tk.END, f"UniAssist: {response}\n\n")
    chat_area.config(state="disabled")
    chat_area.see(tk.END)

    message_entry.delete("1.0", tk.END)
    message_entry.focus_set()

    # Prevent Ctrl+Enter from adding a new line
    if event:
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
default_font.configure(family="Nirmala UI", size=10)

# Set text font
text_font = tkfont.Font(
    root=root,
    family="Nirmala UI",
    size=12
)


# -------------------- Home Screen --------------------

home_frame = tk.Frame(root, bg="#f1f5f9")
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
    text="Campus-specific information will be added after verification.",
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

chat_frame = tk.Frame(root, bg="#f1f5f9")

chat_header = tk.Frame(chat_frame, bg="#17365d")
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

input_frame = tk.Frame(chat_frame, bg="#f1f5f9")
input_frame.pack(
    fill="x",
    padx=18,
    pady=(0, 18)
)

# Text widget instead of Entry
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

# Ctrl + Enter sends the message
message_entry.bind(
    "<Control-Return>",
    send_message
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

root.mainloop()
