# How AI was used

Tool: Claude (Anthropic) as an agent with a shell, working in this repo. The rules it worked under are in `CLAUDE.md`. Below are the main prompts, and the points where a first answer was wrong or too easy and got corrected. Those corrections were the guardrail work.

## Main prompts (in order)

1. "Profile the four CSVs: distributions, missing values, funnel consistency, duplicates. Flag anything that looks like broken data before any analysis."
2. "Compute ROAS / CPA / funnel rates per ad. For every label, compare groups on pooled ROAS, median ROAS and pooled-without-top-ad, with bootstrap CIs."
3. "Check whether the patterns survive when other factors are held fixed: spend-weighted regression on log ROAS, with launch month, with and without LJ-004."
4. "For each creator, measure from their posts: child presenting, spoken language, kids' ages, food/routine share, paid-post reach vs organic, competitor posts in the last 90 days."
5. "Spot-check the labels I'm about to rely on against transcripts and list the disagreements."
6. "Write briefs for the 5 picks using only claims that appear in `claims_made`, copying the structure of the best-performing ads, and in each creator's native format."
7. "Write tests that fail if a brief claim or a hand-typed number doesn't match the data."

## Where the first answer was wrong, and what changed

| First pass | Check | Outcome |
|---|---|---|
| "Proteinmix is the best product (ROAS 2.25)" | Re-ran without LJ-004 | Proteinmix's lift is LJ-004 plus child-led ads; non-child Proteinmix pools at 0.98. The lesson became "child presenter", not "Proteinmix". |
| "Skits underperform" | Regression with language control | No skit effect (t=0.5). Skits are mostly the weak regional-language ads. Verdict changed to "looks worse, explained by other factors". |
| LJ-089 counted as a ₹4.3L skit failure | Cart-to-purchase rate vs every other ad | 0 of 1,544 vs at least 27.6% everywhere else: a tracking break, excluded. |
| Post `language` label used as-is | Read transcripts | Labels follow captions (drgarima_mehta: 20/20 "English", speaks Hindi/Hinglish). Re-derived spoken language from transcripts; this moved @foodies_by_neha into the top 5. |
| `product_form` used as-is | Read LJ-004 transcript | The top ad is Proteinmix in roti, labelled milk mix. Re-derived product from text. |
| "Hindi" vs "Hinglish" for romanised creator speech | Checked how the ad file transcribes them | 0 of 25 Hinglish ads use Devanagari and 7 of 10 Hindi ads do, so romanised Hindi speech maps to Hinglish to match the ad account's convention. |
| Rank creators by one blended score | Asked what a manager needs | Separated fit, reach and hard gates. Competitor conflicts became blocks, not penalties, so @sia_3vedi (best fit) is shown as blocked, with the reason. |
| Child-age verdict "Strong" | No model check exists for that pattern | Downgraded to "Moderate (not model-checked)". |

## What the AI was not trusted with

* **Final picks and gate rules:** decided by a person and written into code so they're inspectable.
* **Claims in the briefs:** constrained by a test to the brand's own claims.
* **Numbers in the report:** rendered from `results.json`, never typed in by hand.
