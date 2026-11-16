APEC 2027: FOCUSED REVISION OF THE ORIGINAL DIGEST

main.tex / main.pdf: clean IEEE two-column paper, SIX pages including references.
Digest_v1.tex / Digest_v1.pdf: original GitHub digest, unchanged.
diff.tex / diff.pdf: marked comparison against that unchanged Digest_v1.tex.

REVISION POLICY
This version starts from the original digest, rather than the previous rewrite.
The original section order, motivation, testbed description, attack-generation
equation and text, temporal-feature-engineering paragraph, and future-work
sentences are retained. Edits are limited to changed experimental methods and
results, necessary technical clarifications, and the required conference format.
results/focused_revision_edits.json records each substantive edit and its reason.

CHANGED EXPERIMENTAL MATERIAL
- Update the detector description to the selected rebalanced six-head CNN-BiGRU,
  its actual training/selection protocol, and its 23,540-window validation cohort.
- Replace outdated results and figures with the selected checkpoint's results.
  Explain conditional motor identity separately from detection-plus-identity,
  and evaluate raw phases on normal as well as attack windows.
- Add the approved shared-configuration motor analysis: 596 speed/load/phase/
  severity tuples represented for both attacked motors; 8,841 attack windows;
  100% conditional identity and 95.28% correct detection plus identity.
  Both motors operate while one is attacked; only PCC features enter the model.
- Add the approved operating-condition figure: all 12 recorded motor-speed-load
  combinations, with attack recall 94.09%-96.17% and sample counts.
- Keep the original illustrative phase/frequency/THD plot. The historical binary
  architecture drawings and old training curve remain in the repository; they
  are superseded in main.tex because they do not describe the selected model.

CLARIFICATIONS
Results use epoch 45 of the selected rebalanced run and random overlapping-window
validation. There is no independent-recording test or new training in this edit.
A new CPU runtime benchmark measures completed-window processing.
Class weighting, loss masks, and fixed task coefficients are distinguished.
Prior PMU/IED results provide context, rather than a direct accuracy benchmark.
Stored severity labels are distinguished from the physical injection parameter.
Auxiliary severity/timing limitations and the tested two-motor scope are stated.

RUNTIME EVIDENCE AND REMOVAL AUDIT
The original Real-Time title is restored. At the author-provided approximately
7-Hz feature rate, 128 samples imply an 18.29-s nominal data window and stride
16 implies 2.29 s between updates. On an Intel Core Ultra 9 285K CPU, TensorFlow
2.21, four intra-operation threads, batch 1, 1,000 recorded validation windows
after 50 warm-ups take 4.50 ms mean, 5.19 ms 95th percentile and 9.26 ms maximum.
Timing includes preprocessing, all six heads and output decoding. The runtime
CSV contains individual measurements, and the JSON records methods and hashes.
This supports rolling-window computational feasibility on that CPU. It excludes
sensor acquisition/transport and does not measure event-level attack-to-alarm
latency or guarantee worst-case timing on another platform.
Average precision 0.9937 and ROC-AUC 0.9758 are retained from saved predictions.
revision_audit.txt explains all substantive removals, restorations and limits.
The original digest, bibliography and original image files remain unchanged.

BENCHMARK REPRODUCTION
  python tools/benchmark_rebalanced_runtime.py
Run from the repository root with TensorFlow/NumPy installed and the selected
checkpoint, original dataset and preprocessing/split artifacts available at the
paths listed in results/rebalanced_runtime.json. Those large local training
artifacts are not included in this paper upload. The script uses the CPU only,
checks all six outputs against saved predictions, and does not train the model.

MARKED COMPARISON
Baseline: Digest_v1.tex at dee54c454ed133d6fa18fb9492d361dbbb7ec3ce.
Blue indicates additions; red strikethrough marks deletions. Unchanged text is black.
The review includes a print legend and page numbers. Deleted table cells are
struck individually, so removals remain distinguishable in a monochrome print.
The original schema has word-level changes; the replacement comparison table
and new analysis table are shown as whole blocks. Equivalent Unicode/TeX dash
spellings are normalized only for comparison. Neither input is modified.
The one-column REVIEW PDF is longer because it includes deleted text and old
figures; only the clean main.pdf is the six-page submission manuscript.
results/diff_baseline.json and results/diff_generation.json record provenance.

BUILD FROM THIS DIRECTORY
  tectonic main.tex
  tectonic diff.tex
Or use pdflatex / bibtex / pdflatex / pdflatex for each entry point.
IEEEtran.cls, IEEEtran.bst, References_main.bib, tables and figures are included.
The original bibliography is unchanged. No font installation is needed to
compile the already-embedded Times New Roman scientific figures.

REGENERATE THE DIFF (Python 3 and latexdiff required)
  python build_review_diff.py --baseline Digest_v1.tex --new main.tex --output diff.tex
Then compile diff.tex. Neither input is modified.

main_validation.json records rendering checks and preservation of original files.
These are local rendering checks; conference PDF eXpress was not performed.
