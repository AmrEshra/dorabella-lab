"""Shared helpers: load the cipher, fetch an English corpus, build an n-gram model."""
import math
import os
import re
import urllib.request
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
CORPUS_DIR = os.path.join(DATA, "corpus")
CORPUS_URL = "https://raw.githubusercontent.com/norvig/pytudes/main/data/text/big.txt"


def load_cipher(path=os.path.join(DATA, "dorabella.txt")):
    """Return the cipher as a flat list of tokens like 'F2' (orientation A-H + semicircle count)."""
    with open(path) as f:
        return f.read().split()


def load_corpus():
    """Download (once) and return a public-domain English corpus as lowercase a-z only."""
    os.makedirs(CORPUS_DIR, exist_ok=True)
    path = os.path.join(CORPUS_DIR, "big.txt")
    if not os.path.exists(path):
        urllib.request.urlretrieve(CORPUS_URL, path)
    with open(path, encoding="utf-8", errors="ignore") as f:
        text = f.read().lower()
    return re.sub(r"[^a-z]", "", text)


class NgramModel:
    """Log-probability scorer over letter n-grams with simple floor smoothing."""

    def __init__(self, text, n=4):
        self.n = n
        counts = Counter(text[i:i + n] for i in range(len(text) - n + 1))
        total = sum(counts.values())
        self.logp = {g: math.log10(c / total) for g, c in counts.items()}
        self.floor = math.log10(0.01 / total)

    def score(self, s):
        n, lp, fl = self.n, self.logp, self.floor
        return sum(lp.get(s[i:i + n], fl) for i in range(len(s) - n + 1))
