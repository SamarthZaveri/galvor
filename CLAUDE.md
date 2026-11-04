# CLAUDE.md: working rules for this repo

Context: we are answering "which 5 of 20 creators should Little Joys work with next, and what should each say?" for a marketing manager. The answer must come from the brand's data (data/), not from general opinion.

## Rules for the agent

1. **Evidence before opinion.** Every recommendation must trace to a number in `out/results.json` or a quoted transcript/caption. If the data can't support a claim, say "no evidence" instead of filling the gap with category knowledge.
2. **Labels are hypotheses.** Galvor labels are "mostly right". Before relying on a label, spot-check it against transcripts. Log every override in `creators.OVERRIDES` (or in `load.py` for ads) with the evidence.
3. **Outliers and tracking.** Never report a pattern on pooled ROAS alone. Always show median ROAS, the result without the group's top ad, and the regression check (`model.py`). LJ-004 (30% of revenue) and LJ-089 (0 purchases from 1,544 carts) are known.
4. **Small n is said out loud.** Groups under 8 ads are "few ads". Single-pair comparisons are "a hint".
5. **No invented claims.** Creator briefs may only use product claims found in `ads.claims_made`; `tests/test_pipeline.py` enforces this. Numbers typed into brief prose must be added to `test_hand_written_numbers_in_briefs`.
6. **Gates are not scores.** Competitor conflicts, product-age mismatch, ad-fatigued feeds and audience geography block a creator outright and are shown with the reason.
7. **One source of truth.** The report renders from `out/results.json`. Don't hand-type numbers into `report_template.html`.
8. **Plain language for the brand.** Write for a marketing manager: no jargon without a gloss, and every caveat paired with what to do about it.

## Commands

- `python src/run.py`: rebuild all outputs and the report
- `python tests/test_pipeline.py`: guardrails (must pass before sharing)
