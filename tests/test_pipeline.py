"""Guardrails. Run: python -m pytest -q   (or python tests/test_pipeline.py)

These exist so the report can't quietly drift from the data:
 - the raw data behaves the way the analysis assumes
 - every claim a creator is told to say already appears in a Little Joys ad
 - every hand-written number in the briefs matches what the code computes
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from load import load_ads, load_creators  # noqa: E402
from creators import build, rank  # noqa: E402
from briefs import BRIEFS  # noqa: E402

ADS = load_ads()
C, P, AU = load_creators()
S = build(C, P, AU).set_index("handle")


def test_funnel_is_monotonic():
    a = ADS
    assert (a.video_3s_views <= a.impressions).all()
    assert (a.thruplays <= a.video_3s_views).all()
    assert (a.link_clicks <= a.impressions).all()
    assert (a.add_to_carts <= a.link_clicks).all()
    assert (a.purchases <= a.add_to_carts).all()


def test_lj089_is_the_only_tracking_break():
    big = ADS[ADS.add_to_carts >= 100]
    zero = big[big.purchases == 0]
    assert zero.ad_id.tolist() == ["LJ-089"]
    assert big[big.ad_id != "LJ-089"].cart_to_buy.min() > 0.25


def test_brief_claims_exist_in_brand_ads():
    claims = set(ADS.claims_made.dropna().str.split("; ").explode().str.strip().str.lower())
    for h, b in BRIEFS.items():
        for cl in b["claims"]:
            assert cl.lower() in claims, f"{h}: claim not found in any ad: {cl!r}"


def test_reference_ads_exist():
    ids = set(ADS.ad_id)
    for h, b in BRIEFS.items():
        for i in b["reference_ads"]:
            assert i in ids, f"{h}: unknown ad {i}"


def test_picks_have_no_gates_and_match_briefs():
    r = rank(build(C, P, AU))
    picks = r[r.eligible].head(5).handle.tolist()
    assert set(picks) == set(BRIEFS)
    assert all(len(S.loc[h, "gates"]) == 0 for h in picks)


def test_hand_written_numbers_in_briefs():
    assert round(S.loc["storiesbyvihaa", "sponsored_retention"], 2) == 0.91
    assert round(S.loc["storiesbyvihaa", "child_presents"] * 20) == 14
    assert round(S.loc["hello_ps8", "sponsored_retention"], 1) == 1.3
    assert abs(S.loc["ohmother.in", "expected_sponsored_plays"] - 23_000) < 1_000
    assert round(ADS.set_index("ad_id").loc["LJ-018", "roas"], 2) == 0.75
    assert AU.set_index("handle").loc["storiesbyvihaa", "men_pct"] == 70.1


def test_known_label_error_is_handled():
    # LJ-004 is labelled milk_mix_powder but the transcript is Proteinmix in roti.
    r = ADS.set_index("ad_id").loc["LJ-004"]
    assert r.product_form == "milk_mix_powder" and r["product"] == "Proteinmix"


def test_results_json_matches_code():
    res = json.loads((ROOT / "out" / "results.json").read_text())
    r = rank(build(C, P, AU))
    assert res["picks"] == r[r.eligible].head(5).handle.tolist()


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn(); print("ok", name)
