"""One command to rebuild everything:  python src/run.py

Writes:
  out/results.json        every number the report shows
  out/patterns.csv        what works in the ads
  out/creator_scores.csv  all 20 creators, every component
  out/competitor_posts.csv
  out/report.html         the brand-facing report (built by build_report.py)
"""
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from load import load_ads, load_creators, TRACKING_SUSPECT  # noqa: E402
from analysis import pattern_table, audit  # noqa: E402
from creators import build, rank, OVERRIDES  # noqa: E402
from briefs import BRIEFS, ON_HOLD  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "out"
W_FIT = 0.7  # fit matters more than reach: the brand puts paid spend behind creator videos


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if np.isnan(o) else round(float(o), 4)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (pd.Timestamp,)):
        return o.strftime("%Y-%m-%d")
    return o


def main():
    OUT.mkdir(exist_ok=True)
    ads = load_ads()
    clean_ads = ads[~ads.tracking_suspect]
    patterns = pattern_table(clean_ads)
    aud = audit(ads)

    c, p, au = load_creators()
    s = build(c, p, au)
    ranked = rank(s, W_FIT)
    picks = ranked[ranked.eligible].head(5).handle.tolist()
    assert set(picks) == set(BRIEFS), f"briefs out of sync with ranking: {picks}"
    sens = {str(w): rank(s, w)[lambda d: d.eligible].handle.head(5).tolist() for w in [0.5, 0.6, 0.7, 0.8, 0.9]}

    patterns.to_csv(OUT / "patterns.csv", index=False)
    ranked.drop(columns=["gates", "notes"]).assign(
        gates=ranked.gates.str.join(" | "), notes=ranked.notes.str.join(" | ")).to_csv(OUT / "creator_scores.csv", index=False)
    s.attrs["competitor_posts"].to_csv(OUT / "competitor_posts.csv", index=False)

    adsx = ads.set_index("ad_id")
    ref_ids = sorted({i for b in BRIEFS.values() for i in b["reference_ads"]} |
                     {"LJ-004", "LJ-089", "LJ-050", "LJ-081", "LJ-018"})
    ref = {i: dict(ad_id=i, product=adsx.loc[i, "product"], language=adsx.loc[i, "language"],
                   hook=adsx.loc[i, "hook_line"], roas=adsx.loc[i, "roas"], cpa=adsx.loc[i, "cpa"],
                   spend=adsx.loc[i, "spend_inr"], video=adsx.loc[i, "video_url"],
                   creator_type=adsx.loc[i, "creator_type"]) for i in ref_ids}

    cols = ["creator_id", "handle", "name", "persona", "followers", "eligible", "score", "fit", "reach",
            "fit_child_presenter", "fit_language", "fit_kids_in_range", "fit_food_routine",
            "child_presents", "eng_hinglish", "kid_3_12", "food_or_routine", "main_language", "languages",
            "median_plays_recent", "expected_sponsored_plays", "sponsored_retention", "n_sponsored_recent",
            "sponsored_share", "child_ages_seen", "gates", "notes"]
    creators_out = ranked[cols].to_dict("records")
    profile = c.set_index("handle")[["profile_url", "what_feels_native", "what_would_feel_foreign"]].to_dict("index")
    for r in creators_out:
        r.update(profile[r["handle"]])
        r["pick_rank"] = picks.index(r["handle"]) + 1 if r["handle"] in picks else None

    res = dict(
        picks=picks, briefs=BRIEFS, on_hold=ON_HOLD, sensitivity=sens, w_fit=W_FIT,
        patterns=patterns.to_dict("records"), audit=aud, creators=creators_out, reference_ads=ref,
        overrides=OVERRIDES, pool_retention=s.attrs["pool_retention"],
        n_ads=len(ads), n_ads_used=len(clean_ads), excluded=sorted(TRACKING_SUSPECT),
        account=dict(median_roas_used=clean_ads.roas.median(),
                     pooled_roas_used=clean_ads.revenue_inr.sum() / clean_ads.spend_inr.sum()),
        competitor_posts=s.attrs["competitor_posts"].to_dict("records"),
    )
    (OUT / "results.json").write_text(json.dumps(clean(res), indent=1, default=str))
    import build_report  # noqa: F401  (renders the HTML from results.json)
    print("Top 5:", picks)
    print("Sensitivity:", sens)


if __name__ == "__main__":
    main()
