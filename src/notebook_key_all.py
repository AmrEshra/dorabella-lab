"""Test Elgar's notebook alphabet without assuming how the transcription letters A-H map to angles.

The notebook groups the alphabet by arc orientation: ABC DEF GHI KLM NOP QRS TUV XYZ, with the
arc count choosing the letter inside the group. The published transcription does not say which
letter A-H is which angle, so this script tries every assignment of the 8 orientations to the
8 groups (8! = 40,320) for both arc orders, and reports the most English-like results.

If even the best of these is gibberish, the notebook key cannot be the whole answer, whatever
the orientation convention.
"""
from itertools import permutations

from common import NgramModel, load_cipher, load_corpus

GROUPS = ["abc", "def", "ghi", "klm", "nop", "qrs", "tuv", "xyz"]
ORIENT = "ABCDEFGH"


def main():
    model = NgramModel(load_corpus(), 4)
    cipher = load_cipher()
    res = []
    for perm in permutations(range(8)):
        for rev in (False, True):
            key = {o + str(n): GROUPS[perm[i]][3 - n if rev else n - 1]
                   for i, o in enumerate(ORIENT) for n in (1, 2, 3)}
            text = "".join(key[t] for t in cipher)
            res.append((model.score(text), perm, rev, text))
    res.sort(key=lambda r: -r[0])
    print(f"Tried {len(res)} keys.\n")
    print("score    groups for A..H                      rev  text")
    for sc, perm, rev, text in res[:10]:
        g = " ".join(GROUPS[p] for p in perm)
        print(f"{sc:8.1f}  {g}  {int(rev)}   {text}")


if __name__ == "__main__":
    main()
