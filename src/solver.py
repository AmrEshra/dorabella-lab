"""Simulated-annealing solver for a (possibly homophonic) substitution cipher.

Each cipher symbol maps to one plaintext letter. By default several symbols may map to the
same letter (homophonic); use injective=True to force a one-to-one key.
"""
import argparse
import math
import random
import string

from common import NgramModel, load_cipher, load_corpus

LETTERS = string.ascii_lowercase


def decrypt(cipher, key):
    return "".join(key[s] for s in cipher)


def anneal(cipher, model, rng, iters=20000, temp0=12.0, injective=False):
    symbols = sorted(set(cipher))
    if injective:
        letters = list(LETTERS)
        rng.shuffle(letters)
        key = dict(zip(symbols, letters))
    else:
        key = {s: rng.choice(LETTERS) for s in symbols}
    cur = model.score(decrypt(cipher, key))
    best_key, best = dict(key), cur
    for i in range(iters):
        temp = temp0 * (1 - i / iters) + 0.05
        s = rng.choice(symbols)
        old = key[s]
        new = rng.choice(LETTERS)
        if new == old:
            continue
        swapped = None
        if injective:
            for other, l in key.items():
                if l == new:
                    swapped = other
                    break
            if swapped:
                key[swapped] = old
        key[s] = new
        sc = model.score(decrypt(cipher, key))
        if sc >= cur or rng.random() < math.exp((sc - cur) / temp):
            cur = sc
            if sc > best:
                best, best_key = sc, dict(key)
        else:
            key[s] = old
            if swapped:
                key[swapped] = new
    return best, best_key


def solve(cipher, model, restarts=40, iters=20000, injective=False, seed=0):
    rng = random.Random(seed)
    results = []
    for _ in range(restarts):
        sc, key = anneal(cipher, model, rng, iters=iters, injective=injective)
        results.append((sc, decrypt(cipher, key), key))
    results.sort(key=lambda r: -r[0])
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--restarts", type=int, default=40)
    ap.add_argument("--iters", type=int, default=20000)
    ap.add_argument("--injective", action="store_true")
    ap.add_argument("--top", type=int, default=10)
    a = ap.parse_args()

    model = NgramModel(load_corpus(), 4)
    cipher = load_cipher()
    res = solve(cipher, model, a.restarts, a.iters, a.injective)
    seen = set()
    for sc, text, _ in res:
        if text in seen:
            continue
        seen.add(text)
        print(f"{sc:9.2f}  {text}")
        if len(seen) >= a.top:
            break


if __name__ == "__main__":
    main()
