
import json
from pathlib import Path


DATA_FILE = Path(__file__).parent / "data" / "general_faq.json"


def load_faqs():
    """Load FAQ data from the JSON file."""
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return data.get("faqs", [])

    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"Could not load FAQ data: {error}")
        return []


def get_response(message, student_type="General", university="General"):
    """Find a suitable answer using local FAQ keywords."""
    message = message.strip().lower()

    if not message:
        return "Please enter a question. කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න."

    faqs = load_faqs()

    student_type = student_type.lower()

    if "a/l" in student_type or "al student" in student_type:
        audience = "al"
    elif "university student" in student_type:
        audience = "university"
    else:
        audience = "all"

    for faq in faqs:
        allowed_audience = faq.get("audience", "all")

        if allowed_audience not in ("all", audience):
            continue

        for keyword in faq.get("keywords", []):
            if keyword.lower() in message:
                return faq["answer"]

    return (
        "Sorry, I couldn't find an answer to that question yet.\n"
        "සමාවෙන්න, මේ ප්‍රශ්නයට පිළිතුරක් දැනට මගේ FAQ දත්තවල නැහැ. "
        "ප්‍රශ්නය වෙනත් ආකාරයකින් අහන්න හෝ නිල විශ්වවිද්‍යාල තොරතුරු පරීක්ෂා කරන්න."
    )
