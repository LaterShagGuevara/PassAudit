from typing import List
import csv


def load_passwords_from_file(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def load_wordlist(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f if line.strip()]


def load_passwords_from_csv(file_path: str) -> List[str]:
    """Load passwords from a browser export CSV."""
    passwords: List[str] = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key in row:
                if key.lower() == 'password':
                    pw = row[key].strip()
                    if pw:
                        passwords.append(pw)
                    break
    return passwords
