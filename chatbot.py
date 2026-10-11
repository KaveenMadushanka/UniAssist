
import json
import re
from pathlib import Path


# File paths
DATA_FOLDER = Path(__file__).parent / "data"
FAQ_FILE = DATA_FOLDER / "general_faq.json"
UNIVERSITY_FILE = DATA_FOLDER / "university_info.json"


def load_json_file(file_path, key):
    """Load data from a local JSON file."""
    try:
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        result = data.get(key, [])

        if not isinstance(result, list):
            print(f"Invalid data format in {file_path.name}")
            return []

        return result

    except (FileNotFoundError, json.JSONDecodeError, OSError) as error:
        print(f"Could not load {file_path.name}: {error}")
        return []


def load_faqs():
    """Load general FAQ information."""
    return load_json_file(FAQ_FILE, "faqs")


def load_university_data():
    """Load universities and degree categories."""
    universities = load_json_file(
        UNIVERSITY_FILE, "universities"
    )

    categories = load_json_file(
        UNIVERSITY_FILE, "degree_categories"
    )

    return universities, categories


def normalize_text(text):
    """Normalize text before matching."""
    text = str(text).casefold().strip()
    return re.sub(r"\s+", " ", text)


def keyword_matches(message, keyword):
    """Match complete English words and Sinhala keywords."""
    message = normalize_text(message)
    keyword = normalize_text(keyword)

    if not message or not keyword:
        return False

    # Match complete English words to avoid accidental matches.
    if re.fullmatch(r"[a-z0-9]+(?:[ '-][a-z0-9]+)*", keyword):
        pattern = (
            r"(?<![a-z0-9])"
            + re.escape(keyword)
            + r"(?![a-z0-9])"
        )
        return re.search(pattern, message) is not None

    # Match Sinhala keywords as text.
    return keyword in message


def get_audience(student_type):
    """Identify the selected student category."""
    student_type = normalize_text(student_type)

    if "a/l" in student_type or "al student" in student_type:
        return "al"

    if "university student" in student_type:
        return "university"

    return "all"


def find_university(message, selected_university, universities):
    """Find the university mentioned or selected by the user."""
    selected = normalize_text(selected_university)

    # Prefer a university explicitly mentioned in the question.
    for university in universities:
        name = university.get("name", "")
        university_id = university.get("id", "")

        if university_id in ("general", "other"):
            continue

        aliases = [name, university_id]

        if university_id == "sabaragamuwa":
            aliases.extend([
                "sabaragamuwa university",
                "sabaragamuwa campus"
            ])

        for alias in aliases:
            if keyword_matches(message, alias):
                return university

    # Otherwise, use the selected dropdown value.
    for university in universities:
        if normalize_text(university.get("name", "")) == selected:
            return university

    return None


def find_degree_category(message, categories):
    """Identify the degree subject area."""
    matches = []

    for category in categories:
        for keyword in category.get("keywords", []):
            # Avoid matching the ambiguous standalone word "IT".
            if normalize_text(keyword) == "it":
                continue

            if keyword_matches(message, keyword):
                matches.append((category, keyword))

    if not matches:
        return None

    # Prefer the most specific matching keyword.
    return max(
        matches,
        key=lambda item: len(normalize_text(item[1]))
    )[0]


def get_response(
    message,
    student_type="General",
    university="General / Any University"
):
    """Generate a response using local FAQ and university data."""

    if not isinstance(message, str) or not message.strip():
        return (
            "Please enter a question.\n"
            "කරුණාකර ප්‍රශ්නයක් ඇතුළත් කරන්න."
        )

    message = normalize_text(message)

    faqs = load_faqs()
    universities, categories = load_university_data()

    audience = get_audience(student_type)

    selected_uni = find_university(
        message,
        university,
        universities
    )

    # 1. Check degree subject categories.
    degree_category = find_degree_category(message, categories)

    if degree_category:
        category_name = degree_category.get(
            "name", "Degree programmes"
        )
        description = degree_category.get("description", "")

        # Give university-specific information only when a
        # particular university has been identified.
        if (
            selected_uni
            and selected_uni.get("id") not in ("general", "other")
        ):
            university_name = selected_uni.get("name", "")

            return (
                f"{category_name} — {university_name}\n\n"
                f"{description}\n\n"
                "For confirmed programmes and entry requirements, "
                "check the university's official website and the "
                "relevant UGC admission handbook."
            )

        return (
            f"{category_name}\n\n"
            f"{description}\n\n"
            "ඔයා කැමති university එක සඳහන් කළොත් තොරතුරු "
            "සොයාගැනීමට වඩාත් පහසුයි. නිල තොරතුරු අදාළ "
            "විශ්වවිද්‍යාලයේ වෙබ් අඩවියෙන් තහවුරු කරන්න."
        )

    # 2. Answer questions about a specific university.
    university_keywords = [
        "university information",
        "about university",
        "university details",
        "universities",
        "විශ්වවිද්‍යාල තොරතුරු"
    ]

    asks_about_university = any(
        keyword_matches(message, keyword)
        for keyword in university_keywords
    )

    asks_about_admission = (
        "admission" in message
        or "entry requirements" in message
        or "university entrance" in message
    )

    asks_about_degrees = (
        "degree" in message
        or "degrees" in message
        or "courses" in message
        or "course" in message
        or "පාඨමාලා" in message
        or "උපාධි" in message
    )

    if (
        selected_uni
        and selected_uni.get("id") not in ("general", "other")
        and (
            asks_about_university
            or asks_about_admission
            or asks_about_degrees
        )
    ):
        return (
            f"University: {selected_uni.get('name', 'Unknown')}\n\n"
            f"{selected_uni.get('description', '')}\n\n"
            "Available degree programmes, entry requirements and "
            "admission details must be confirmed using official "
            "university and UGC sources."
        )

    # 3. Match general FAQ keywords.
    matches = []

    for faq in faqs:
        allowed_audience = faq.get("audience", "all")

        if allowed_audience not in ("all", audience):
            continue

        for keyword in faq.get("keywords", []):
            if keyword_matches(message, keyword):
                matches.append((faq, keyword))
                break

    if matches:
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

    # 4. Helpful response when no keyword matches.
    return (
        "Sorry, I couldn't find an answer to that question yet.\n"
        "සමාවෙන්න, මේ ප්‍රශ්නයට පිළිතුරක් දැනට මගේ දත්තවල නැහැ.\n\n"
        "Try asking about university admission, degrees, "
        "computing, engineering, GPA, exams or scholarships."
    )
