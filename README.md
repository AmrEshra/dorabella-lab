# dorabella-lab

Experiments on the **Dorabella cipher**, the 87-symbol note Edward Elgar sent to Dora Penny in July 1897, unsolved since.

## The cipher

`data/dorabella.txt` holds a consensus transcription (Hauer et al., 2025, built from five independent transcriptions). Each symbol is written as a letter for the orientation of its arcs (`A`–`H`, eight directions) followed by the number of arcs (`1`–`3`). Line lengths are 29, 31 and 27.

```
A2 E3 B2 A3 A1 C2 G1 A3 D1 H2 B3 F2 F1 B1 F2 C3 F2 F2 C2 E3 E3 F2 B1 H1 H2 H1 C1 B3 F3
G1 F2 G1 C2 H1 A3 D1 D2 A3 B2 F2 F2 B2 C2 C1 F1 G1 F2 B3 F2 C2 G2 F3 F1 B1 H1 D1 D1 H1 B3 F3
B2 F3 C2 G2 F3 B2 B1 G2 G3 C1 F3 B2 F2 C2 G2 F1 F3 C1 A3 E3 C1 F3 C2 A3 B1 H1 A3
```

Some symbols are ambiguous in the original; other transcriptions differ in a few places.

`data/dorabella.png` is the cipher as reproduced in Dora Penny's 1937 memoir (Elgar's original card is lost).

### Orientation convention (checked against the image)
The source paper does not say which letter is which angle. Reading the first symbols of line 1 against the image (A2 E3 B2 A3 A1 C2 G1 A3 ...) gives a consistent picture. The letter names the way the arcs **open** on the page:

| Letter | Opening | Letter | Opening |
|---|---|---|---|
| A | right (like `c`) | E | left (like `ɔ`) |
| B | down-right | F | up-left |
| C | down (like `m`) | G | up (like `u`) |
| D | down-left | H | up-right |

So A→H runs clockwise in 45° steps, which confirms the rotational-order assumption used in experiment 04.

## Running

Python 3, no dependencies. The first run downloads a public-domain English corpus (Norvig's `big.txt`) into `data/corpus/`.

```bash
cd src
python3 analysis.py              # frequencies, index of coincidence, English comparison
python3 control.py --injective   # can the solver crack English of the same length?
python3 solver.py --injective    # attack Dorabella as a one-to-one substitution
python3 solver.py                # attack Dorabella as a homophonic substitution
python3 baseline.py              # Dorabella vs. English ciphers vs. shuffled Dorabella
```

## Experiment log

### 01 — Statistics (`results/01_analysis.txt`)
- 20 distinct symbols out of 24 possible; an 87-letter English passage uses about 20 letters on average.
- Most frequent symbol `F2` = 12.6%, close to English `e`.
- Index of coincidence 0.0585: between English of the same length (0.065) and random symbols (0.042).
- Orientation `F` covers 23 of 87 symbols, a strong skew worth explaining.

### 02 — Simple substitution, English (`results/02_solver_english.txt`)
- Solver: simulated annealing with a 4-gram English model.
- Control (`control.py`): on 87-letter English passages it recovers the full text in most trials.
- On Dorabella: no readable text. Restarts do not agree, and only short English-like fragments appear. The homophonic mode overfits to strings of common letters (`thereth...`), as expected with so few symbols.

### 03 — Baselines (`results/03_baseline.txt`)
| Input | Best score (higher = more English-like) |
|---|---|
| Real English ciphers | mean −353 (range −414 to −328) |
| **Dorabella** | **−402** |
| Dorabella shuffled | mean −435 (range −450 to −420) |

Dorabella scores better than every shuffle of its own symbols, so the order of the symbols carries some structure. But it scores worse than typical English. Consistent with earlier published work: it is not plain English under a simple substitution, but it is not random either.

### 04 — Elgar's notebook alphabet (`results/04_notebook_key.txt`)
- A notebook attributed to Elgar (authorship disputed) groups the alphabet by arc orientation: ABC DEF GHI(J) KLM NOP QRS TUV(W) XYZ, with the arc count picking the letter.
- All 32 alignments of that key were tried (8 rotations x 2 directions x 2 arc orders).
- Every one gives gibberish. The best scores about −634, far below the −402 the free solver reaches, so this key does not decrypt Dorabella directly.
- Caveat: that test assumed the transcription letters A–H run in rotational order, which the source paper does not state.

### 05 — Notebook alphabet, every orientation assignment (`results/05_notebook_key_all_perms.txt`)
- Removes the caveat above: tries all 8! = 40,320 ways of assigning the eight orientations to the eight letter groups, for both arc orders (80,640 keys).
- Best score −560: still gibberish, and worse even than shuffled Dorabella (mean −435).
- Conclusion: whatever the orientation convention, the notebook alphabet on its own does not decrypt Dorabella. If Elgar used it, he added another step (phonetic spelling, transposition, a keyword shift, etc.).

### 06 — Notebook alphabet + keyword shift (`results/06_notebook_keyword.txt`)
- Each symbol becomes a letter via the notebook alphabet (24 letters, I/J and V/W merged), then a repeating keyword shifts it back, Vigenere style (p = c − k) or variant Beaufort (p = c + k), mod 24.
- Keywords: about 20,000 frequent English words plus names and places from Elgar's and Dora's lives (Dora, Dorabella, Penny, Elgar, Alice, Forli, Malvern, Wolverhampton, Enigma, Beacon, Troyte, Liszt...). 32 rotational orientation conventions, two directions: 1.28 million decryptions.
- Self-test (`--selftest`): English encrypted this way with keyword "malvern" is recovered exactly.
- On Dorabella the best score is −558 (keyword "leaflets"): gibberish. No personal keyword comes near the top.
- Conclusion: a notebook alphabet with a single repeating English keyword is ruled out for the rotational conventions.

### 07 — Letter openings and endings (`results/07_cribs.txt`)
- Idea: letters of the time opened with stock phrases ("My dear ...", "Dear Miss Penny") and closed with a signature ("E.E.", "Yours ...").
- Under a one-to-one substitution, repeated letters must sit under repeated symbols. Dorabella opens `A2 E3 B2 A3 A1 C2 G1 A3`: the 4th and 8th symbols match and the first seven differ.
- That rules out 36 of 45 openings, including "my dear Dora", "dear Miss Penny", "dearest Dora", "Dorabella", "thank you". All 14 endings tested are ruled out, including "E.E.", "Elgar", "Edward Elgar" and every "Yours ..." form.
- The 9 openings that fit ("my dear", "dear", "Dora", "my Dora", "I am", "I must"...) were each fixed in place and the solver rerun: all give gibberish, scoring worse (−455 to −512) than the free solver (−402).
- Caveat: holds only for a plain one-to-one substitution, and a misread symbol near the start or end would change the pattern.

## Next ideas
- Phonetic or abbreviated English (Elgar was fond of wordplay and phonetic spellings).
- Other languages (Latin, German, French).
- Treating orientation and arc count as two separate channels.
- Testing alternative readings of the ambiguous symbols.
- Transposition before or after substitution.

## References
- Hauer et al., *Dorabella Cipher as Musical Inspiration* (arXiv:2509.17950).
- Hauer et al., *Experimental Analysis of the Dorabella Cipher with Statistical Language Models*, HistoCrypt 2021.
- Schmeh, *Examining the Dorabella Cipher with three lesser-known cryptanalysis methods*, HistoCrypt 2018.
- Sams, *Elgar's Cipher Letter to Dorabella*, The Musical Times, 1970.
