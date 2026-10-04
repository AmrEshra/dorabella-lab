"""Use Elgar's 1899 Enigma programme note to attack Dorabella.

1. Keywords: every word and every run of 2-3 consecutive words of the note is tried as a
   repeating Vigenere / Beaufort key on top of the notebook alphabet (32 orientation conventions).
2. Running key: the whole note, from every starting offset, as a non-repeating key.
3. Cribs: words from the note ("enigma", "darksaying", "unguessed", "theme"...) are slid along the
   cipher. Wherever the repeat pattern of the symbols allows the word under a one-to-one
   substitution, the word is fixed there and the free solver fills in the rest.
"""
import random
import re

from common import NgramModel, load_cipher, load_corpus
from crib import anneal_fixed
from notebook_keyword import ALPHA, conventions, norm

NOTE = """The Enigma I will not explain - its dark saying must be left unguessed, and I warn you
that the connexion between the Variations and the Theme is often of the slightest texture;
further, through and over the whole set another and larger theme goes, but is not played.
So the principal Theme never appears, even as in some late dramas - e.g. Maeterlinck's L'Intruse
and Les sept Princesses - the chief character is never on the stage."""

CRIBS = """enigma darksaying darksayings unguessed theme variations explain connexion texture
another larger notplayed mystery secret hidden riddle dorabella intruse""".split()


def note_words():
    return [norm(w) for w in re.findall(r"[a-z]+", NOTE.lower())]


def score_all(cipher, model, keys, top=8):
    res = []
    for conv, key in conventions():
        c = [key[t] for t in cipher]
        for label, k in keys:
            L = len(k)
            for sign, name in ((-1, "vig"), (1, "beau")):
                text = "".join(ALPHA[(c[i] + sign * k[i % L]) % 24] for i in range(len(c)))
                res.append((model.score(text), conv, label, name, text))
        res.sort(key=lambda r: -r[0])
        del res[top * 4:]
    return res[:top]


def isomorph_positions(cipher, word):
    out = []
    for p in range(len(cipher) - len(word) + 1):
        a, b, ok = {}, {}, True
        for s, ch in zip(cipher[p:p + len(word)], word):
            if a.setdefault(s, ch) != ch or b.setdefault(ch, s) != s:
                ok = False
                break
        if ok:
            out.append((p, a))
    return out


def main():
    model = NgramModel(load_corpus(), 4)
    cipher = load_cipher()
    words = note_words()

    phrases = set(words)
    for n in (2, 3):
        phrases |= {"".join(words[i:i + n]) for i in range(len(words) - n + 1)}
    keys = [(p, [ALPHA.index(ch) for ch in p]) for p in sorted(phrases) if len(p) >= 2]
    print(f"== 1. Note words and phrases as repeating keys ({len(keys)} keys x 32 conventions x 2) ==")
    for sc, conv, w, name, text in score_all(cipher, model, keys):
        print(f"  {sc:8.1f}  {str(conv):18s} {w[:18]:18s} {name:4s}  {text}")

    stream = [ALPHA.index(ch) for ch in "".join(words)]
    run = [(f"offset {o}", stream[o:o + len(cipher)]) for o in range(len(stream) - len(cipher) + 1)]
    print(f"\n== 2. Whole note as running key ({len(run)} offsets x 32 conventions x 2) ==")
    for sc, conv, w, name, text in score_all(cipher, model, run):
        print(f"  {sc:8.1f}  {str(conv):18s} {w:18s} {name:4s}  {text}")

    print("\n== 3. Note words as cribs at every position the symbol pattern allows ==")
    rng = random.Random(0)
    found = []
    for w in CRIBS:
        pos = isomorph_positions(cipher, w)
        print(f"  {w:12s} fits at {len(pos)} positions")
        for p, fixed in pos:
            sc, text = max(anneal_fixed(cipher, model, fixed, rng, iters=8000) for _ in range(4))
            found.append((sc, w, p, text))
    found.sort(reverse=True)
    print("\n  Best crib placements (free solver reaches -400 with no crib):")
    for sc, w, p, text in found[:10]:
        print(f"  {sc:8.1f}  {w:12s} @{p:2d}  {text}")


if __name__ == "__main__":
    main()
