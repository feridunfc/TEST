# src/nlp/sentiment.py
import queue
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional

import numpy as np

from .preprocessor import clean_text
from src.utils.nlp_utils import safe_import_transformers

@dataclass
class SentimentResult:
    text: str
    score: float
    label: str
    timestamp: datetime
    source: str
    asset: Optional[str] = None

class SentimentAnalyzer:
    """
    Tries to use a HF transformers model; falls back to a rule-of-thumb
    VADER-like approach if transformers is not available.
    """
    def __init__(self, model_name: str = "finiteautomata/bertweet-base-sentiment-analysis"):
        self.text_queue = queue.Queue()
        self.results: List[SentimentResult] = []
        self._stop_event = threading.Event()
        self._use_transformers = safe_import_transformers()
        self._pipeline = None
        if self._use_transformers:
            from transformers import pipeline, AutoTokenizer  # type: ignore
            self._pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                tokenizer=AutoTokenizer.from_pretrained(model_name)
            )

    def _normalize_score(self, label: str, score: float) -> float:
        if label.upper().startswith("NEG"):
            return -float(score)
        return float(score)

    def _fallback_sentiment(self, text: str) -> SentimentResult:
        """
        Very simple fallback: positive if 'up/bull' words > 'down/bear' words.
        """
        t = clean_text(text).lower()
        pos_words = sum(w in t for w in ["up", "bull", "pump", "positive", "good"])
        neg_words = sum(w in t for w in ["down", "bear", "dump", "negative", "bad"])
        raw = pos_words - neg_words
        score = max(-1.0, min(1.0, raw / 3.0))
        label = "POSITIVE" if score > 0 else ("NEGATIVE" if score < 0 else "NEUTRAL")
        return SentimentResult(text=text, score=score, label=label, timestamp=datetime.utcnow(), source="fallback")

    def analyze_batch(self, texts: List[str], sources: List[str], assets: List[str] = None) -> List[SentimentResult]:
        if assets is None:
            assets = [None] * len(texts)
        out: List[SentimentResult] = []
        for text, source, asset in zip(texts, sources, assets):
            try:
                if self._use_transformers and self._pipeline is not None:
                    res = self._pipeline(text)[0]
                    out.append(
                        SentimentResult(
                            text=text,
                            score=self._normalize_score(res["label"], res["score"]),
                            label=res["label"],
                            timestamp=datetime.utcnow(),
                            source=source,
                            asset=asset,
                        )
                    )
                else:
                    out.append(self._fallback_sentiment(text))
            except Exception:
                out.append(self._fallback_sentiment(text))
        self.results.extend(out)
        return out

    def start_realtime_analysis(self, callback):
        def worker():
            while not self._stop_event.is_set():
                try:
                    item = self.text_queue.get(timeout=1)
                    res = self.analyze_batch([item["text"]], [item.get("source", "realtime")], [item.get("asset")])[0]
                    callback(res)
                    self.text_queue.task_done()
                except queue.Empty:
                    continue
        th = threading.Thread(target=worker, daemon=True)
        th.start()
        return th

    def stop_realtime_analysis(self):
        self._stop_event.set()
