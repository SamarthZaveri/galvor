# Little Joys: which 5 creators next, and what should they say?

A small, reproducible pipeline that answers the question using only the brand's data: 100 ads, 20 creators, 392 creator posts and 3 audience files. The output is a report for the marketing manager: `out/report.html`, also published as a hosted page.

## The answer

| # | Creator | Role | Lead product | One-line reason |
|---|---|---|---|---|
| 1 | @storiesbyvihaa | Lead bet | Proteinmix | Child presenter (14 of her 20 posts); paid posts keep 91% of her normal reach |
| 2 | @hello_ps8 | Strong fit | Proteinmix pancakes | English/Hinglish; son on camera; paid posts beat her organic ones (1.3x) |
| 3 | @the_mum_wife_playbook | Low-cost creative test | Nutrimix 2+ | Daughter already talks to camera; Hinglish |
| 4 | @ohmother.in | Creative test | Proteinmix | School-morning routine format, English, two school-age kids |
| 5 | @foodies_by_neha | Recipe specialist | Proteinmix | 1M followers; Hinglish kids' tiffin series |

Picks 1 to 3 hold at every fit/reach weighting from 50/50 to 90/10. Slots 4 and 5 rotate with @mumma_and_ridhu (all within about 1 point). The best fit of all 20, @sia_3vedi, is on hold because she posted a paid Gritzo kids'-milk video on 28 Sep 2026.

## What wins in the ads

Each pattern is checked four ways: pooled ROAS, median ROAS, pooled ROAS without the group's top ad, and a spend-weighted regression on log ROAS with launch-month controls, run with and without the outlier LJ-004.

* **Strong:** a child presents the ad (x1.64 in the model, even without LJ-004); English or Hinglish (x1.36); a clear buy-now ask (x1.20).
* **Moderate:** saying protein in grams; naming the brand in the first 3 seconds; a child aged 6 to 12 rather than under 6.
* **Works against:** Gummies as the lead product; selling on immunity or "overall growth".
* **A trap:** skits look bad in raw numbers (median 0.87 vs 1.27), but the model shows no skit effect (t=0.5). Skits are mostly the weak regional-language ads.

## How it works

```
data/                 raw CSVs as given (+ DATA_README.md)
src/load.py           loads ads, derives metrics (ROAS, CPA, funnel rates) and a corrected product label
src/stats.py          bootstrap CIs, group tables
src/model.py          spend-weighted log-ROAS regression (sanity check, not a forecast)
src/analysis.py       the pattern table + data audit
src/creators.py       creator fit / reach / gates, re-derived spoken language, competitor detection
src/briefs.py         the 5 briefs (hand-written from the evidence) + on-hold list
src/run.py            runs everything -> out/results.json, CSVs, report
src/build_report.py   renders out/report.html from results.json (no hand-typed numbers in the page)
tests/test_pipeline.py guardrails (see below)
```

```bash
pip install pandas numpy          # Python 3.10+
python src/run.py                 # rebuilds out/
python tests/test_pipeline.py     # or: python -m pytest -q
open out/report.html
```

### Creator scoring

* **Fit (0-100):** child presents (40), English/Hinglish speech (20), kids aged 3 to 12 on camera (20), food or routine posts (20). The weights follow the ranking of evidence strength in the ads.
* **Reach (0-100):** expected plays for a *paid* post: the median of recent sponsored videos, or organic plays times the pool's sponsored retention (0.65). Log scale from 10k to 3M.
* **Score** = 0.7 x fit + 0.3 x reach. Fit carries more weight because the brand runs creator videos as paid ads, so the video matters more than the creator's own audience.
* **Gates** (hard blocks): a paid post for a kids' nutrition competitor in the last 90 days; kids on camera mostly outside the 3 to 12 product range; an ad-fatigued feed (nearly all paid, almost no shares); under 75% of audience in India; paid posts getting under 20% of usual plays.

### Guardrails (tests)

* The funnel is monotonic (impressions ≥ 3s views ≥ ThruPlays; clicks ≥ carts ≥ purchases).
* LJ-089 is the only ad with 100+ carts and 0 purchases (a tracking break), so it is excluded.
* **Every claim in every brief already appears in some ad's `claims_made`.** The briefs can't invent product claims.
* Every number hand-written into a brief matches what the code computes.
* The picks match the ranking and none of them has a gate.

## Data problems found and handled

* **LJ-004 is 30% of all revenue.** Blended ROAS is 1.50 with it and 1.15 without. Patterns are judged on medians and re-tested without it.
* **LJ-089** spent ₹4.27L, got 1,544 carts and 0 purchases. Every other ad with 100+ carts converts at least 27.6% of them. We treat it as a tracking break and exclude it.
* **The same video run twice gives very different ROAS** (1.42 vs 2.30; 0.78 vs 1.27). Single-ad ROAS is noisy.
* **Labels corrected:** the post `language` label tracks the caption, not the speech (e.g. drgarima_mehta is 20/20 "English" but speaks Hindi/Hinglish), so spoken language is re-derived from transcripts. `product_form` lumps Proteinmix in with milk mix (LJ-004 included), so product is re-derived from text. One creator's `presenter_age` is adult, but the narration is a child's.
* **Gaps:** there is only 1 doctor-led ad, no Telugu or Gujarati ads, audience data for only 3 creators, and none of the ads are marked live.

See `NOTE.md` for the key choices and next steps, and `AI_USAGE.md` for how AI was used.
