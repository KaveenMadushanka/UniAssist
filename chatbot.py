
import json
import re
from pathlib import Path


# Locate the FAQ file relative to this Python file.
DATA_FILE = Path(__file__).parent / "data" / "general_faq.json"


def load_faqs():
    """Load FAQ data from the local JSON file."""

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        faqs = data.get("faqs", [])

        if not isinstance(faqs, list):
            print("FAQ error: 'faqs' must be a list.")
            return []

        return faqs

    except FileNotFoundError:
        print(f"FAQ file not found: {DATA_FILE}")
        return []

    except json.JSONDecodeError as error:
        print(f"Invalid JSON in FAQ file: {error}")
        return []

    except OSError as error:
        print(f"Could not read FAQ file: {error}")
        return []


def normalize_text(text):
    """Normalize text for consistent keyword matching."""

    text = text.casefold().strip()
    text = re.sub(r"\s+", " ", text)

    return text


def get_audience(student_type):
    """Convert the selected student category to an audience."""

    student_type = normalize_text(student_type)

    if "a/l" in student_type or "al student" in student_type:
        return "al"

    if "university student" in student_type:
        return "university"

    return "all"


def keyword_matches(message, keyword):
    """Check whether a keyword matches the user's message."""

    message = normalize_text(message)
    keyword = normalize_text(keyword)

    if not message or not keyword:
        return False

    # Sinhala text and other non-English keywords can use substring matching.
    # English words use word boundaries to avoid accidental partial matches.
    if re.fullmatch(r"[a-z0-9]+(?:[ '-][a-z0-9]+)*", keyword):
        pattern = r"(?<![a-z0-9])" + re.escape(keyword) + r"(?![a-z0-9])"
        return re.search(pattern, message) is not None

    return keyword in message


def get_response(message, student_type="General",
                 university="General"):
    """Return a suitable answer from the local FAQ data."""

    if not isinstance(message, str):
        return "Please enter a question. කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න."

    message = normalize_text(message)

    if not message:
        return "Please enter a question. කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න."

    faqs = load_faqs()

    if not faqs:
        return (
            "Sorry, the FAQ data could not be loaded.\n"
            "FAQ දත්ත කියවීමට නොහැකි වුණා. JSON file එක පරීක්ෂා කරන්න."
        )

    audience = get_audience(student_type)

    # First, find matching FAQs that are allowed for this audience.
    matches = []

    for faq in faqs:
        allowed_audience = faq.get("audience", "all")

        if allowed_audience not in ("all", audience):
            continue

        keywords = faq.get("keywords", [])

        for keyword in keywords:
            if keyword_matches(message, keyword):
                matches.append((faq, keyword))
                break

    if matches:
        # Prefer the most specific matching keyword.
        # This helps avoid choosing a generic FAQ when a specific one matches.
        best_match = max(
            matches,
            key=lambda item: len(normalize_text(item[1]))
        )

        faq = best_match[0]

        print("Matched FAQ:", faq.get("id", "unknown"))

        return faq.get(
            "answer",
            "Sorry, an answer is not available yet."
        )

    return (
        "Sorry, I couldn't find an answer to that question yet.\n"
        "සමාවෙන්න, මේ ප්‍රශ්නයට පිළිතුරක් දැනට මගේ FAQ දත්තවල නැහැ. "
        "ප්‍රශ්නය වෙනත් ආකාරයකින් අහන්න හෝ නිල විශ්වවිද්‍යාල "
        "තොරතුරු පරීක්ෂා කරන්න."
    )
