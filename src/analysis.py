"""Basic statistics of the Dorabella cipher compared with random English samples of the same length."""
import random
from collections import Counter

from common import load_cipher, load_corpus


def ioc(seq):
    c, n = Counter(seq), len(seq)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def doubles(seq):
    return sum(seq[i] == seq[i + 1] for i in range(len(seq) - 1))


def main():
    t = load_cipher()
    n = len(t)
    c = Counter(t)
    print(f"Length: {n}   distinct symbols: {len(c)}")
    print("\nSymbol frequencies:")
    for s, k in c.most_common():
        print(f"  {s}  {k:2d}  {100 * k / n:5.1f}%  {'#' * k}")

    print("\nBy orientation:", dict(Counter(x[0] for x in t).most_common()))
    print("By arc count:  ", dict(Counter(x[1] for x in t).most_common()))

    bi = Counter(zip(t, t[1:]))
    print("\nRepeated bigrams:", ", ".join(f"{a}{b}x{k}" for (a, b), k in bi.most_common() if k > 1))

    corpus = load_corpus()
    rng = random.Random(1)
    samples = [corpus[i:i + n] for i in (rng.randrange(len(corpus) - n) for _ in range(5000))]
    e_ioc = sum(map(ioc, samples)) / len(samples)
    e_dbl = sum(map(doubles, samples)) / len(samples)
    e_dst = sum(len(set(s)) for s in samples) / len(samples)
    rnd = [[rng.randrange(24) for _ in range(n)] for _ in range(5000)]
    r_ioc = sum(map(ioc, rnd)) / len(rnd)

    print("\n                 Dorabella   English(87)   Random(24 symbols)")
    print(f"  IoC            {ioc(t):9.4f}   {e_ioc:11.4f}   {r_ioc:9.4f}")
    print(f"  Doubles        {doubles(t):9d}   {e_dbl:11.2f}")
    print(f"  Distinct       {len(c):9d}   {e_dst:11.1f}")


if __name__ == "__main__":
    main()
