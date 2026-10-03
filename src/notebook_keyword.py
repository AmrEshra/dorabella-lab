"""Notebook alphabet + keyword shift (Vigenere-style) over a 24-letter alphabet.

Elgar's notebook alphabet has 24 letters (I/J and V/W share a symbol). Here each cipher symbol is
first turned into a letter index 0-23 with the notebook alphabet, then a repeating keyword
shifts it back: p = c - k (Vigenere) or p = c + k (variant Beaufort), mod 24.

Orientation conventions: the 32 rotational alignments (8 starting points x 2 directions x 2 arc
orders). Keywords: frequent English words from the corpus plus names and places from Elgar's
and Dora's lives.

Run with --selftest first: it encrypts English with a known convention and keyword and checks
that the search recovers it.
"""
import argparse
import os
import random
import re
from collections import Counter

from common import CORPUS_DIR, NgramModel, load_cipher, load_corpus

ALPHA = "abcdefghiklmnopqrstuvxyz"  # 24 letters: j->i, w->v
GROUPS = ["abc", "def", "ghi", "klm", "nop", "qrs", "tuv", "xyz"]
ORIENT = "ABCDEFGH"

PERSONAL = """dora dorabella penny dorapenny missdora misspenny elgar edward edwardelgar alice
carolinealice caroline ede eewe forli malvern greatmalvern wolverhampton worcester worcestershire
beacon worcestershirebeacon rectory stpeters alfred powell enigma variations nimrod troyte
griffith jaeger baker wmb wolves wanderers kite kites map maps races music violin cipher
cryptogram mystery mysterious hysterious liszt july fourteenth schooling pallmall gazette
dorabellacipher mozart cosifantutte""".split()


def norm(word):
    return word.lower().replace("j", "i").replace("w", "v")


def conventions():
    for rot in range(8):
        for d in (1, -1):
            for rev in (False, True):
                yield (rot, d, rev), {
                    o + str(n): ALPHA.index(GROUPS[(d * i + rot) % 8][3 - n if rev else n - 1])
                    for i, o in enumerate(ORIENT) for n in (1, 2, 3)}


def keywords(limit):
    raw = open(os.path.join(CORPUS_DIR, "big.txt"), encoding="utf-8", errors="ignore").read().lower()
    words = Counter(w for w in re.findall(r"[a-z]+", raw) if 3 <= len(w) <= 14)
    common = [w for w, _ in words.most_common(limit)]
    seen, out = set(), []
    for w in PERSONAL + common:
        k = norm(w)
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def search(cipher, model, words, top=10):
    res = []
    for conv, key in conventions():
        c = [key[t] for t in cipher]
        n = len(c)
        for w in words:
            k = [ALPHA.index(ch) for ch in w]
            L = len(k)
            for sign, name in ((-1, "vig"), (1, "beau")):
                text = "".join(ALPHA[(c[i] + sign * k[i % L]) % 24] for i in range(n))
                res.append((model.score(text), conv, w, name, text))
        res.sort(key=lambda r: -r[0])
        del res[top * 5:]
    return res[:top]


def selftest(model, words):
    rng = random.Random(3)
    corpus = load_corpus()
    i = rng.randrange(len(corpus) - 87)
    plain = norm(corpus[i:i + 87])
    conv, key = list(conventions())[rng.randrange(32)]
    inv = {v: s for s, v in key.items()}
    word = "malvern"
    k = [ALPHA.index(ch) for ch in word]
    cipher = [inv[(ALPHA.index(ch) + k[j % len(k)]) % 24] for j, ch in enumerate(plain)]
    best = search(cipher, model, words, top=1)[0]
    print(f"plain:  {plain}\nfound:  {best[4]}\nconvention {best[1]} vs true {conv}, keyword '{best[2]}' ({best[3]})")
    print("PASS" if best[4] == plain else "FAIL")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", type=int, default=5000)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    model = NgramModel(load_corpus(), 4)
    words = keywords(a.words)
    if a.selftest:
        selftest(model, words)
        return
    res = search(load_cipher(), model, words)
    print(f"Keywords tried: {len(words)} x 32 conventions x 2 directions = {len(words) * 64} decryptions\n")
    for sc, conv, w, name, text in res:
        print(f"{sc:8.1f}  {str(conv):18s} {w:14s} {name:4s}  {text}")


if __name__ == "__main__":
    main()
