APEC 2027: NEW PAPER AND MARKED COMPARISON

main.tex / main.pdf: new IEEE two-column paper, SIX pages including references.
Digest_v1.tex / Digest_v1.pdf: original digest; unchanged.
References_main.bib: bibliography for the new paper; the old bibliography stays unchanged.

APPROVED ADDITIONS
- Motor identification from PCC features while both motors operate and one is
  attacked. The shared-configuration subset contains 596 speed/load/phase/
  severity tuples represented for both attacked motors and 8,841 attack windows.
  Conditional motor identity is 100%; correct detection plus identity is 95.28%.
  The text explains that detector misses limit the joint result in this subset.
- A compact Times New Roman figure covers all 12 recorded motor-speed-load
  combinations: attack recall 94.09%-96.17%, at the same threshold 0.5.
  Normal metadata do not support condition-specific false-positive rates.

All proposed-model results use the selected epoch-45 rebalanced checkpoint and
existing 23,540-window random overlapping-window validation. No new training,
independent recording test, onset-position analysis, or other model was added.

MARKED COMPARISON
Compile/open diff.tex / diff.pdf to compare with the unchanged GitHub
Digest_v1.tex at commit dee54c454ed133d6fa18fb9492d361dbbb7ec3ce.
The comparison includes earlier local revisions absent from that digest.
It uses a one-column REVIEW layout and contains deleted text, so it is longer
than the SIX-PAGE clean main.pdf. Additions are blue, deletions red; changed
tables are marked as complete blocks. Graphics are bounded in size for review.
results/diff_baseline.json and results/diff_generation.json preserve provenance.

BUILD FROM THIS DIRECTORY
  tectonic main.tex
  tectonic diff.tex
Or use pdflatex / bibtex / pdflatex / pdflatex for each entry point.
IEEEtran.cls, IEEEtran.bst, References_main.bib and rendered figures are included.
No Times New Roman font installation is needed to compile the embedded figures.

REGENERATE THE DIFF (Python 3 and latexdiff required)
  python build_review_diff.py --baseline Digest_v1.tex --new main.tex --output diff.tex
Then compile diff.tex. Neither input is modified.

main_validation.json records page count, embedded fonts, resolved references,
absence of overfull boxes/missing glyphs, and preservation of original sources.
Local checks do not replace the conference PDF eXpress validation.
