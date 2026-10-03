"""Compare Dorabella's best solver score against two baselines:

1. Real English: 87-letter passages enciphered with a random key (what success looks like).
2. Shuffled Dorabella: the same 87 symbols in random order (same frequencies, no word order).

If Dorabella scores no better than its own shuffles, the solver is finding nothing beyond
what the symbol frequencies alone allow.
"""
import random
import statistics

from common import NgramModel, load_cipher, load_corpus
from solver import solve

RESTARTS, ITERS, N = 15, 15000, 8


def best(cipher, model, seed):
    return solve(cipher, model, RESTARTS, ITERS, injective=True, seed=seed)[0][0]


def main():
    corpus = load_corpus()
    model = NgramModel(corpus, 4)
    cipher = load_cipher()
    rng = random.Random(7)
    syms = [o + n for o in "ABCDEFGH" for n in "123"]

    dora = best(cipher, model, 0)
    eng = []
    while len(eng) < N:
        i = rng.randrange(len(corpus) - 87)
        p = corpus[i:i + 87]
        if len(set(p)) > 24:
            continue
        enc = dict(zip(sorted(set(p)), rng.sample(syms, len(set(p)))))
        eng.append(best([enc[c] for c in p], model, len(eng)))
    shuf = []
    for k in range(N):
        s = cipher[:]
        rng.shuffle(s)
        shuf.append(best(s, model, 100 + k))

    print(f"Dorabella best score:        {dora:8.1f}")
    print(f"English ciphers (n={N}):       mean {statistics.mean(eng):8.1f}  range {min(eng):.1f} .. {max(eng):.1f}")
    print(f"Shuffled Dorabella (n={N}):    mean {statistics.mean(shuf):8.1f}  range {min(shuf):.1f} .. {max(shuf):.1f}")


if __name__ == "__main__":
    main()
