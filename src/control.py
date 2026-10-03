"""Control experiment: can the solver crack English texts of Dorabella's length?

Takes random 87-letter English passages, encrypts each with a random one-to-one key over
24 symbols, runs the solver, and reports how many letters it recovers. If the solver
succeeds here but fails on Dorabella, Dorabella is probably not plain English under a
simple substitution.
"""
import argparse
import random

from common import NgramModel, load_corpus
from solver import solve

SYMBOLS = [o + n for o in "ABCDEFGH" for n in "123"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--restarts", type=int, default=20)
    ap.add_argument("--iters", type=int, default=15000)
    ap.add_argument("--injective", action="store_true")
    a = ap.parse_args()

    corpus = load_corpus()
    split = len(corpus) // 2
    model = NgramModel(corpus[:split], 4)  # train on first half, test on second half
    rng = random.Random(42)
    accs = []
    for t in range(a.trials):
        i = rng.randrange(split, len(corpus) - 87)
        plain = corpus[i:i + 87]
        letters = sorted(set(plain))
        syms = rng.sample(SYMBOLS, len(letters)) if len(letters) <= 24 else None
        if syms is None:
            continue
        enc = dict(zip(letters, syms))
        cipher = [enc[ch] for ch in plain]
        sc, guess, _ = solve(cipher, model, a.restarts, a.iters, a.injective, seed=t)[0]
        acc = sum(p == g for p, g in zip(plain, guess)) / len(plain)
        accs.append(acc)
        print(f"trial {t}: {100 * acc:5.1f}%\n  plain: {plain}\n  guess: {guess}")
    print(f"\nMean accuracy: {100 * sum(accs) / len(accs):.1f}%  "
          f"(>=90% in {sum(x >= 0.9 for x in accs)}/{len(accs)} trials)")


if __name__ == "__main__":
    main()
