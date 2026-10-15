# Lead Auditor Examination — 140 Questions

**ISO 9001:2026 · ISO/IEC 17021-1:2015 · ISO 19011:2026**

A static English site built from the Takeed Academy 140-question Lead Auditor
pack: three revision papers, one by standard, plus a timed full examination.

---

## ⚠ Read before publishing

**This is a static site with no server, so the answer key ships inside
`data/questions.js` and loads in the candidate's browser.** Anyone who opens
developer tools can read it before submitting.

That makes the site suitable for:

- revision and self-study;
- in-room formative assessment;
- preparation for a supervised exam.

It is **not** suitable for:

- a graded examination that a certificate depends on;
- unsupervised remote assessment.

**Secure marking needs a server**: store the answers in a protected database,
send the candidate's selections, and grade server-side. The data is already
shaped for it — question ids are stable (`Q001` … `Q140`) and marking keys off
those ids, not screen position, so the `answer` field can simply be dropped
from what reaches the browser.

The printed answer key is written **outside** this folder on purpose
(`Lead-Auditor-140Q-Answer-Key-INSTRUCTOR-ONLY.pdf`), and the verification gate
fails if any instructor file moves into it.

---

## The four papers

| Paper | Questions | Mode | Clock | Pass |
| --- | ---: | --- | --- | --- |
| ISO 9001:2026 | 70 | Revision | — | — |
| ISO/IEC 17021-1:2015 | 35 | Revision | — | — |
| ISO 19011:2026 | 35 | Revision | — | — |
| **Full examination** | **140** | **Exam** | **180 min** | **70%** |

The revision papers carry no clock and no pass mark. The pack sets a threshold
for the full paper only, so inventing one for a revision paper would be
fabricating a rule. They report a score and a performance band instead.

Each paper keeps its own progress, so you can leave ISO 9001 half-finished and
start ISO 19011 without losing anything.

### Revision mode

Answer, then press **Next**. The first press reveals the result rather than
navigating: the correct option turns green, a wrong pick turns red, and the
panel gives the explanation and the full reference. Press **Next** again to
move on. The question locks once revealed, so the explanation cannot be used to
change the answer.

### Exam mode (the full paper)

Nothing is revealed while you work. Score, verdict and all explanations appear
only after you finish; answers stay changeable until then.

**Countdown:** the full paper shows time remaining from 180 minutes, turns red
for the last five, and **submits automatically at zero**. A time limit that
does nothing is worse than none — a candidate would believe they had been
stopped when they had not. A paper left open past its limit comes back
completed, not resumable.

The pack suggests 180–210 minutes; the lower bound is used so the clock is not
generous by default. It is one number in `tools/build_bank.py`.

---

## Random order, every sitting

Questions are drawn in a fresh order each time a paper is started. Two
candidates side by side are never on the same question, and a retake is not the
same paper in the same sequence.

The shuffle is Fisher-Yates, not `sort(() => Math.random() - 0.5)`. That
one-liner is wrong twice over: it does not produce a uniform permutation, and
because the result depends on the engine's sorting algorithm it is
*differently* wrong in each browser. The test suite scans for it.

The order is drawn once and persisted, so Resume brings back the identical
sequence rather than reshuffling.

### What does not shuffle: the options

Shuffling questions changes what you are asked next. Shuffling options would
change which letter is correct — and this pack guarantees, on its cover,
**exactly 25 correct answers for each of A, B, C and D** across its 100 MCQs.
That is a spread of zero and a 25% blind-guess ceiling: the exact floor for
four options. There is nothing to gain by touching it, and reordering would
destroy a guarantee the supplier states explicitly.

(The IMS bank elsewhere in this repository *did* need reordering — its key was
50–53% guessable section by section. The machinery is present here and
deliberately switched off; `check_fidelity.py` proves it stayed off.)

### Section skew, left alone

| Paper | MCQ | A | B | C | D | Blind guess |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ISO 9001:2026 | 56 | 11 | 15 | 15 | 15 | 27% |
| ISO/IEC 17021-1:2015 | 22 | 8 | 3 | 7 | 4 | 36% |
| ISO 19011:2026 | 22 | 6 | 7 | 3 | 6 | 32% |
| **Full paper** | **100** | **25** | **25** | **25** | **25** | **25%** |

The three revision papers are less even than the whole. This is the pack's own
distribution and is left untouched: the graded paper is the full one, which is
at the floor, and the alternative is breaking the supplier's stated 25-each
guarantee to improve a revision aid. Worth knowing if you set a revision paper
as a scored test — the 17021-1 paper is guessable at 36%.

---

## How answer mapping stays correct

1. Each question gets **one** permutation of its option indices.
2. A selection is stored as the **original** option index, never the on-screen
   position:

   ```js
   answers[questionId] = order[clickedDisplayPosition];
   ```

3. Scoring compares original indices: `answers[questionId] === question.answer`.

Nothing in the session record refers to a screen position, so the order is free
to change without touching correctness. The permutation is persisted, so
resuming restores the identical layout.

`tools/check_fidelity.py` re-reads the **original pack files** and proves, for
all 140 questions, that the question text, options, option order, explanation,
standard and clause are byte-identical, and that the correct answer still
points at its original **text** — not merely the same index.

---

## The pack ships the same data four times. All four are checked.

The pack contains the master JSON, an answer-key CSV, an instructor Markdown
and three ClassMarker CSVs. That redundancy is an asset: a build error shows up
as the site disagreeing with the pack, and a pack error shows up as the copies
disagreeing with each other. The gate checks every pairing, plus:

- ClassMarker feedback cells are empty, so answers cannot leak mid-exam;
- the candidate Markdown carries no answers or rationales;
- the pack's own quality claims still hold on the shipped data — 100 MCQ + 40
  T/F, the 70/35/35 blueprint, 25 per letter, 20 True / 20 False, every stem at
  least 20 words, and no legacy clause 10.3 reference.

---

## Question ids, not numbers

Because the order is per-sitting, **"question 7" is a different question for
every candidate**. The id (`Q001` … `Q140`) is the anchor:

- every review card shows its id;
- the instructor key is sorted by id, grouped by standard;
- a trainer and a candidate discussing `Q043` are discussing the same question.

---

## What these three standards are

The site says this in its footer because conflating them is the commonest Lead
Auditor error:

- **ISO 9001:2026** — requirements for the auditee's quality management system.
- **ISO/IEC 17021-1:2015** — requirements for **certification bodies**, not for
  the auditee's QMS.
- **ISO 19011:2026** — **guidance** on auditing management systems. It is not a
  requirements standard, and a finding cannot be raised against it.

---

## Deploying to GitHub Pages

1. Push the contents of this folder to a repository's default branch.
2. **Settings → Pages → Source:** `Deploy from a branch`, branch `main`, folder
   `/ (root)`.
3. The site appears at `https://<user>.github.io/<repo>/` within a minute or two.

All paths are relative, so it also works from a subdirectory or by opening
`index.html` from disk. A `.nojekyll` file ships so Pages serves every file
as-is.

**Before uploading:** read the security note at the top.

---

## Project structure

```
Lead-Auditor-140Q/
├── index.html                  Page shell (all copy is injected by app.js)
├── styles.css                  Takeed design system
├── app.js                      Copy dictionary + exam engine
├── data/
│   ├── questions.js            140 questions + the four papers
│   └── questions.json          Identical, as JSON, for other tooling
├── assets/logos/
├── .nojekyll
└── README.md
```

Outside the published folder (not uploaded):

```
source/                         the delivery pack, unmodified
tools/build_bank.py             builds the site bank from the pack
tools/check_fidelity.py         proves nothing changed, across all four copies
tools/build_answer_key.py       instructor answer key (PDF)
tools/check_answer_key.py       proves the print matches the screen
tools/verify_all.sh             the full gate
tests/run-tests.js              137 tests against the real shipped files
Lead-Auditor-140Q-Answer-Key-INSTRUCTOR-ONLY.pdf
```

---

## Rebuilding

```
python3 tools/build_bank.py     # regenerate data/questions.js + .json
bash  tools/verify_all.sh       # the full gate
```

`verify_all.sh` runs four stages and exits non-zero on any failure:

1. rebuild the bank from the pack;
2. prove nothing was altered, cross-check all four pack representations, and
   confirm no instructor file is inside the published folder;
3. rebuild the instructor key and prove it matches the screen;
4. run 137 tests in jsdom against the real shipped HTML and JS.

---

## Instructor answer key

`tools/build_answer_key.py` produces
**`Lead-Auditor-140Q-Answer-Key-INSTRUCTOR-ONLY.pdf`** — 27 pages: a cover, a
quick key grouped by standard, then every question followed directly by its
answer, explanation and reference. Distractors are not printed.

Everything is keyed by question id. The site draws a fresh order per sitting, so
a printed position would match nobody.

True/False answers print as the word, not a letter.

---

## Source and scope

| | |
| --- | --- |
| Pack | `ISO_9001_2026_17021_19011_Lead_Auditor_140Q_FULL_PACK.zip` |
| Prepared | 2026-10-11 |
| Master | `..._Master_Question_Bank.json` (sha256 recorded in `questions.json`) |

No question, option, answer, explanation, clause or id was reworded,
translated, shortened, reordered or regenerated.

**Scope note, from the pack and worth repeating:** this content is original
paraphrase, not reproduced standard text, and importing it does not
independently verify the normative wording of the standards it references.
Technical and certification-scheme review against legitimately licensed copies
is advised before any high-stakes use. The 70% threshold is this course's own
and is not an ISO or Exemplar Global rule.

---

## Browser support

Modern evergreen browsers. The layout uses CSS logical properties and
`conic-gradient`, both supported since 2021.

Session saving uses `localStorage`. Where it is unavailable — private browsing
with storage disabled, or some browsers opening from `file://` — the site still
works fully for the current session; only resume-after-refresh is lost.

---

## Licensing

Educational practice material prepared for Takeed Academy. ISO standards are the
copyright of ISO. This tool paraphrases concepts for learning purposes and does
not reproduce the standard.
