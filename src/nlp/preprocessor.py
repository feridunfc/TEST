# src/nlp/preprocessor.py
import re
from typing import List

URL_RE = re.compile(r"https?://\S+")
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")

def clean_text(text: str) -> str:
    text = URL_RE.sub(" ", text)
    text = MENTION_RE.sub(" ", text)
    text = text.replace("&amp;", "&")
    return re.sub(r"\s+", " ", text).strip()

def extract_hashtags(text: str) -> List[str]:
    return HASHTAG_RE.findall(text or "")
