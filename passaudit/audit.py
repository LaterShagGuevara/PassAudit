import re
import hashlib
import json
import math
import requests
from typing import List, Dict, Tuple

MIN_LENGTH = 12
SPECIAL_CHARS = r"[!@#$%^&*(),.\-_=+\[\]{}|;:'\"<>/?]"


def check_length(password: str) -> bool:
    return len(password) >= MIN_LENGTH

def check_uppercase(password: str) -> bool:
    return any(c.isupper() for c in password)

def check_lowercase(password: str) -> bool:
    return any(c.islower() for c in password)

def check_digits(password: str) -> bool:
    return any(c.isdigit() for c in password)

def check_special(password: str) -> bool:
    return re.search(SPECIAL_CHARS, password) is not None

def contains_common_word(password: str, wordlist: List[str]) -> bool:
    lower = password.lower()
    return any(word in lower for word in wordlist)

def is_breached(password: str) -> bool:
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return False
        hashes = (line.split(':') for line in response.text.splitlines())
        return any(h[0] == suffix for h in hashes)
    except requests.RequestException:
        return False

def calculate_entropy(password: str) -> float:
    pool = 0
    if re.search(r"[a-z]", password): pool += 26
    if re.search(r"[A-Z]", password): pool += 26
    if re.search(r"[0-9]", password): pool += 10
    if re.search(SPECIAL_CHARS, password): pool += 32
    return round(len(password) * math.log2(pool), 2) if pool else 0.0

def load_feedback_rules() -> Dict:
    with open("data/feedback_rules.json", "r", encoding="utf-8") as f:
        return json.load(f)

def check_password(password: str, wordlist: List[str]) -> Dict[str, bool]:
    return {
        "length": check_length(password),
        "uppercase": check_uppercase(password),
        "lowercase": check_lowercase(password),
        "digits": check_digits(password),
        "special": check_special(password),
        "common_word": not contains_common_word(password, wordlist),
        "breach": not is_breached(password),
    }

def failed_checks(results: Dict[str, bool]) -> List[str]:
    return [check for check, passed in results.items() if not passed]

def score_password(results: Dict[str, bool]) -> int:
    return sum(results.values())

def analyze_password(password: str, wordlist: List[str]) -> Dict:
    rules = load_feedback_rules()
    results = check_password(password, wordlist)
    score = score_password(results)
    entropy = calculate_entropy(password)

    # Determine rating tier
    tier = next(
        (tier for tier in rules["rating_tiers"] if score >= tier["min_score"]),
        rules["rating_tiers"][-1]
    )
    rating = tier["label"]
    feedback = list(tier["feedback"])

    # Pattern-based feedback
    p = password.lower()
    for key, rule in rules["pattern_triggers"].items():
        if key == "breach_example":
            if any(p == match for match in rule["matches"]):
                feedback.append(rule["feedback"])
        elif key == "low_entropy":
            if entropy < 3:
                feedback.append(rule["feedback"])
        else:
            if re.search(rule["regex"], password, re.IGNORECASE):
                feedback.append(rule["feedback"])

    return {
        "results": results,
        "score": score,
        "rating": rating,
        "feedback": feedback[:3],
        "entropy": entropy
    }
