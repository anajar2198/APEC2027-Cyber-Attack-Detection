APEC 2027 PAPER: AUTHOR-REVIEWED REVISION

main.tex / main.pdf: clean IEEE conference manuscript, SIX US-letter pages.
diff.tex / diff.pdf: printable comparison against unchanged Digest_v1.tex.
Digest_v1.tex / Digest_v1.pdf / Bibliography.bib: original files, unchanged.

CURRENT REVISION
The author's edits and 21 agent comments from commit a0f8964a28e2 are applied.
agent_comment_responses.txt explains every resolution and preserved author edit.
results/author_review_edits.json records the changes. Earlier focused-revision
and removal audits are historical records, superseded by this current audit.
The author-edited raw diff remains in Git history at the commit above.

The main paper includes nine figures and four tables. The literature-context
table is restored, the learned comparison table is retained without an always-
attack row, and the motor table shows both 18,914 attack windows and its 8,841-
window matched-settings subset. The five-panel motor/phase figure is restored.
All figures and tables are referenced. Fixed unit outer loss weights are shown
in the final objective, separately from class weights and loss masks.
The EMU's up-to-60-Hz capability is distinguished from the approximately 7-Hz
recordings used for this experiment and its measured CPU update feasibility.
Two self-cited works among nine references give 22.22%, below the >25% threshold
specified in the author's APEC acceptance letter. The EMU manuscript is cited
as submitted for publication; its private editorial identifier is omitted.
The AI acknowledgement is retained. No new training was run for these edits.

EVIDENCE AND LIMITS
The selected rebalanced checkpoint is epoch 45. Metrics use 23,540 evaluation
windows from a stratified random overlapping-window split. This partition was
used for checkpoint selection; it is not an independent recording-level test.
Both motors operate while one is attacked. Only PCC features enter the model.
Conditional motor identity and complete detection-plus-identity are reported
separately. Phase evaluation includes normal 000 labels. Auxiliary severity/
timing limitations remain stated. No ten-motor generalization is established.

RUNTIME
results/rebalanced_runtime.json/.csv contain the previously measured CPU
benchmark: preprocessing plus all six heads and decoding, batch 1, 50 warm-ups,
1,000 measured calls, Intel Core Ultra 9 285K, TensorFlow 2.21, four threads.
Mean 4.50 ms, 95th percentile 5.19 ms, maximum 9.26 ms. At approximately 7 Hz,
128 samples imply an 18.29-s nominal window and stride 16 a 2.29-s update.
This measures completed-window processing, not live attack-to-alarm delay.
Reproduction: python tools/benchmark_rebalanced_runtime.py
The checkpoint, dataset, and saved preprocessing/predictions are local training
artifacts listed in the runtime JSON; they are not included in this paper upload.

PRINTABLE DIFF
Blue solid underlining denotes additions; red strikethrough denotes deletions.
The review includes a legend and page numbers. Table cells and the new loss
equation are marked for monochrome printing. The one-column review PDF is
longer than six pages because removed text and figures remain visible.
Only main.pdf is the six-page submission manuscript.

BUILD
  tectonic main.tex
  tectonic diff.tex
Or use pdflatex / bibtex / pdflatex / pdflatex for each entry point.
IEEEtran.cls/.bst, References_main.bib, figures and tables are included.
All scientific plot fonts are embedded in their existing PDF assets.

REGENERATE REVIEW (Python 3 and latexdiff)
  python build_review_diff.py --baseline Digest_v1.tex --new main.tex --output diff.tex
Then compile diff.tex. Neither input is modified. Use canonical main.tex for
further author changes; do not regenerate it with an older preparation script.

main_validation.json records local rendering and preservation checks.
Conference PDF eXpress checking/submission has not been performed here.
