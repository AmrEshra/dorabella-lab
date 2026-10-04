"""Crib test: could Dorabella begin (or end) with a typical letter phrase?

Under a one-to-one substitution, equal letters must sit under equal symbols and different letters
under different symbols. Dorabella opens  A2 E3 B2 A3 A1 C2 G1 A3 ...  : the 4th and 8th symbols
match, the first seven are all different. Any opening phrase must fit that pattern.

For every candidate phrase that fits, the solver is run again with those letters fixed, to see
whether the rest of the message turns into English.
"""
import math
import random
import string

from common import NgramModel, load_cipher, load_corpus

OPENINGS = """mydear mydeardora mydearmisspenny mydearmissdora mydearestdora dear deardora dearmisspenny
dearmissdora dearestdora dora dorabella missdora misspenny mydora dearchild mydeargirl dearlady
mydeardorabella dearfriend mydearfriend thankyou thanksforthe weareback wearehome wegothome
wegotbackhome wearrived wearrivedhome wereachedhome arrivedsafe arrivedsafely homeagain
iam iwish ihope imust isend ithink thisis thecipher here hereis lookhere listen""".split()

ENDINGS = """ee edwardelgar elgar yourssincerely yours yourstruly yoursever yoursaffectionately
yoursaye ede eewe adieu goodbye farewell""".split()


def fits(cipher, crib, at_end=False):
    seg = cipher[-len(crib):] if at_end else cipher[:len(crib)]
    a, b = {}, {}
    for s, ch in zip(seg, crib):
        if a.setdefault(s, ch) != ch or b.setdefault(ch, s) != s:
            return None
    return a


def anneal_fixed(cipher, model, fixed, rng, iters=15000, temp0=12.0):
    symbols = [s for s in sorted(set(cipher)) if s not in fixed]
    free = [l for l in string.ascii_lowercase if l not in fixed.values()]
    rng.shuffle(free)
    key = dict(fixed)
    key.update(zip(symbols, free))
    spare = free[len(symbols):]
    dec = lambda: "".join(key[s] for s in cipher)
    cur = model.score(dec())
    best, best_text = cur, dec()
    for i in range(iters):
        temp = temp0 * (1 - i / iters) + 0.05
        s = rng.choice(symbols)
        if spare and rng.random() < 0.3:
            j = rng.randrange(len(spare))
            old = key[s]
            key[s], spare[j] = spare[j], old
            undo = lambda: (spare.__setitem__(j, key[s]), key.__setitem__(s, old))
        else:
            t = rng.choice(symbols)
            key[s], key[t] = key[t], key[s]
            undo = lambda: _swap(key, s, t)
        sc = model.score(dec())
        if sc >= cur or rng.random() < math.exp((sc - cur) / temp):
            cur = sc
            if sc > best:
                best, best_text = sc, dec()
        else:
            undo()
    return best, best_text


def _swap(key, s, t):
    key[s], key[t] = key[t], key[s]


def main():
    model = NgramModel(load_corpus(), 4)
    cipher = load_cipher()
    print("Opening symbols:", " ".join(cipher[:12]))
    print("Closing symbols:", " ".join(cipher[-8:]), "\n")
    rng = random.Random(0)
    for label, cribs, at_end in (("OPENINGS", OPENINGS, False), ("ENDINGS", ENDINGS, True)):
        ok = [(c, fits(cipher, c, at_end)) for c in cribs]
        print(f"== {label}: {sum(1 for _, f in ok if f)} of {len(cribs)} fit the symbol pattern ==")
        print("  ruled out:", ", ".join(c for c, f in ok if not f))
        for c, fixed in ok:
            if not fixed:
                continue
            best = max(anneal_fixed(cipher, model, fixed, rng) for _ in range(12))
            print(f"  {c:20s} {best[0]:8.1f}  {best[1]}")
        print()


if __name__ == "__main__":
    main()
