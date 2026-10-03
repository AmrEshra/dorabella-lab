"""Test the cipher alphabet found in a notebook attributed to Elgar.

The notebook groups the alphabet in eights by arc orientation: ABC DEF GHI(J) KLM NOP QRS TUV(W) XYZ,
with the number of arcs choosing the letter inside the group. Which transcription letter (A-H)
matches which angle is unknown, so all 8 rotations x 2 directions x 2 arc orders are tried.
"""
from common import NgramModel, load_cipher, load_corpus

GROUPS = ["abc", "def", "ghi", "klm", "nop", "qrs", "tuv", "xyz"]


def main():
    model = NgramModel(load_corpus(), 4)
    cipher = load_cipher()
    res = []
    for rot in range(8):
        for direction in (1, -1):
            for rev in (False, True):
                text = "".join(
                    GROUPS[(direction * "ABCDEFGH".index(t[0]) + rot) % 8][3 - int(t[1]) if rev else int(t[1]) - 1]
                    for t in cipher)
                res.append((model.score(text), rot, direction, rev, text))
    res.sort(reverse=True)
    print("score    rot dir rev  text")
    for sc, rot, d, rev, text in res[:8]:
        print(f"{sc:8.1f}  {rot}  {d:+d}  {int(rev)}   {text}")


if __name__ == "__main__":
    main()
