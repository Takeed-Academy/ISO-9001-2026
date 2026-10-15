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

## Fixed order, the same paper for everyone

Questions appear in a fixed order, identically for every candidate and on every
attempt. Question 1 is the same question for the whole room, a retake is the
same paper again, and the printed PDFs are numbered by position because that
position now means something.

**The order is grouped by standard, then sorted by clause** — all 70 ISO 9001
questions running 4.1 → 10.2, then the 35 for ISO/IEC 17021-1, then the 35 for
ISO 19011. The three revision papers are exactly the three blocks of the full
paper, in the same sequence, and both PDFs are generated from that one order.

Within a standard each clause appears once, with its multiple-choice and
true/false items together. No section doubles back to an earlier clause — the
test suite counts back-steps and fails on any.

That is not the pack's own numbering. The pack numbers by *format*: `Q001`–
`Q100` are its multiple-choice items and `Q101`–`Q140` its true/false ones,
with all three standards interleaved through both. Taken literally that order
runs 9001 ×56, 17021-1 ×22, 19011 ×22, then 9001 again ×14, and so on — each
standard appearing twice, split by question format.

Left that way, a section reads as disordered when it is really ordered twice:
a full sweep of one standard's multiple-choice questions from 4.1 to 10.2,
then a second sweep of its true/false questions starting again at 4.1. A
candidate revising clause 8.3 would meet it once near the start and again
two-thirds of the way down.

So the bank is regrouped by standard and sorted by clause once, at build time,
and the site, both PDFs and the three revision papers all share that single
order. A clause range such as `4.2-5.2` sorts on its first clause, and clauses
compare as numbers rather than text, so `8.10` would follow `8.9` instead of
preceding it.

This is a one-flag choice in `app.js`:

```js
var SHUFFLE_QUESTIONS = false;   // true draws a fresh random order per sitting
```

The shuffle itself is still wired up behind that flag. It is Fisher-Yates, not
`sort(() => Math.random() - 0.5)` — that one-liner is wrong twice over: it does
not produce a uniform permutation, and because the result depends on the
engine's sorting algorithm it is *differently* wrong in each browser.

**The trade.** A fixed order makes the paper easy to administer, mark and talk
through, and it is what an invigilated sitting usually wants. It also means two
candidates sitting side by side are on the same question at the same time, and
that someone who has seen the paper knows what is coming. If that matters more
than convenience for a given cohort, flip the flag.

Either way the order is written into the session record when a paper starts and
persisted, so Resume brings back exactly what was on screen.

### What never shuffles: the options

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

## Question ids alongside numbers

With the order fixed, "question 7" is the same question for everyone, so the
on-screen position is now a usable reference and matches the printed paper.

The id (`Q001` … `Q140`) is kept beside it anyway, because it is the reference
that survives a change of order:

- every review card shows its id;
- the instructor key and the printed paper are both keyed by id;
- a trainer and a candidate discussing `Q043` are discussing the same question
  whether or not the order is ever shuffled again.

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

## If the site still shows the old questions

Static sites have no server to send cache headers, so a browser may keep
serving the `app.js` and `data/questions.js` it already has and never ask for
the new ones. The symptom is specific and misleading: the files on disk are
correct, but the page keeps showing the old behaviour — a different question 1
on every load, long after the shuffle was switched off.

Two guards are in place:

**Versioned asset URLs.** `index.html` references each asset with a hash of its
own contents:

```html
<script src="app.js?v=906c4f01"></script>
```

A URL the browser has never seen cannot be in its cache. Re-stamp after any
edit to `app.js`, `data/questions.js` or `styles.css`:

```
python3 tools/stamp_version.py
```

Forgetting that step is the one way to reintroduce the problem, so the test
suite fails if a stamp does not match the file it names — a stale stamp is
worse than none, because it looks handled.

**Stale sessions are rejected on load.** A session saved before the order was
fixed carries the sequence it was drawn with, and Resume would faithfully
restore it — so the paper keeps opening on the old question 1 however many
times the data is corrected, and no amount of refreshing helps because the
cache is no longer the problem.

While the order is fixed, `sanitizeSession` now requires a saved session to be
in *that* order and discards it otherwise. A future order change therefore
takes effect by itself on the next load; no storage-key bump to remember.
(`STORAGE_KEY` was bumped to `.v2` once, when this guard was added, to clear
records written before it existed.)

**And an in-progress paper can be abandoned.** A finished paper always offered
a retake; a part-finished one offered only Resume, which left anyone with an
unwanted session — stale, or just a paper opened by mistake — with no way back
to a clean start. Every in-progress card now carries **Start over**.

`index.html` itself still has a fixed URL, so the first load after an update
may need one refresh (Ctrl-F5 / Cmd-Shift-R). That is one file rather than all
of them.

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

Everything is keyed by question id. With the order fixed the printed position
also matches the screen — but the id is what stays correct if the order is ever
shuffled again, so it remains the reference.

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
