"""What works in Little Joys' own ads.

Produces one row per pattern a creator brief could act on, each compared WITH vs WITHOUT,
and checked four ways (pooled ROAS, median ROAS, pooled without the group's top ad, and a
regression that holds the other patterns and launch month fixed). Also the data audit.
"""
import numpy as np
import pandas as pd
from stats import boot_ci
from model import fit_both

PATTERNS = [
    # key, plain-English name, mask function, creator-brief implication
    ("child_presents", "A child presents the ad (speaks to camera about their own food)",
     lambda a: a.creator_type == "child_presenter", "Put the child at the centre, talking in their own words"),
    ("eng_hinglish", "Spoken in English or Hinglish",
     lambda a: a.language.isin(["English", "Hinglish"]), "Script in English/Hinglish; regional-only is unproven or weak"),
    ("buy_now", "Ends with a clear 'buy now' ask",
     lambda a: a.cta_type == "buy_now", "Close with a direct ask and the link"),
    ("grams", "Says how much protein, in grams",
     lambda a: a.transcript.fillna("").str.lower().str.contains(r"\d+\s?(?:g|gm|grams?)\b") | a.transcript.fillna("").str.contains("ग्राम|கிராம்"),
     "Say the number: '12 g protein per scoop'"),
    ("taste_same", "Says the taste doesn't change",
     lambda a: a.transcript.fillna("").str.lower().str.contains(r"taste.{0,20}(?:same|change)|no taste|bilkul same"),
     "Show it mixed into everyday food and say the taste stays the same"),
    ("brand_3s", "Brand named in the first 3 seconds",
     lambda a: a.brand_first_said == "under_3s", "Say 'Little Joys' early"),
    ("child_6_12", "Child on screen is 6-12 (vs under 6)",
     lambda a: a.child_age.isin(["6_to_9", "10_to_12"]), "Older kids who can speak full sentences do better",
     lambda a: a.child_age == "under_6"),
    ("gummies", "Product is Gummies (vs Nutrimix / Proteinmix)",
     lambda a: a["product"] == "Gummies", "Lead with Proteinmix or Nutrimix, not Gummies"),
    ("skit", "Skit / comedy format",
     lambda a: a.ad_format == "skit", "Skits are fine if the language is right; the format itself is not the problem"),
    ("growth_immunity", "Sells on immunity or 'overall growth'",
     lambda a: a.main_benefit.isin(["immunity", "overall_growth"]), "Sell protein and taste, not vague growth/immunity"),
]
MODEL_NAME = {
    "child_presents": "Child presents the ad", "eng_hinglish": "English or Hinglish",
    "buy_now": "Clear buy-now ask", "grams": "States protein in grams", "brand_3s": "Brand named in first 3s",
    "gummies": "Gummies (vs other products)", "skit": "Skit format",
}


def _pool(g):
    return g.revenue_inr.sum() / g.spend_inr.sum() if len(g) else np.nan


def pattern_table(a: pd.DataFrame) -> pd.DataFrame:
    reg = fit_both(a).set_index("feature")
    rows = []
    for spec in PATTERNS:
        key, name, fn, implication = spec[:4]
        m = fn(a).fillna(False).astype(bool)
        other = spec[4](a).fillna(False).astype(bool) if len(spec) > 4 else ~m
        yes, no = a[m], a[other]
        lo, hi = boot_ci(yes.spend_inr, yes.revenue_inr)
        yes_x = yes.drop(index=yes.revenue_inr.idxmax())
        no_x = no.drop(index=no.revenue_inr.idxmax())
        r = dict(key=key, pattern=name, implication=implication,
                 n_with=len(yes), n_without=len(no),
                 roas_with=_pool(yes), roas_without=_pool(no),
                 median_with=yes.roas.median(), median_without=no.roas.median(),
                 roas_with_ex_top=_pool(yes_x), roas_without_ex_top=_pool(no_x),
                 ci_lo=lo, ci_hi=hi,
                 share_beating_median=(yes.roas > a.roas.median()).mean(),
                 cpa_with=yes.spend_inr.sum() / max(yes.purchases.sum(), 1),
                 cpa_without=no.spend_inr.sum() / max(no.purchases.sum(), 1),
                 ads_with=", ".join(sorted(yes.ad_id)))
        if key in MODEL_NAME:
            f = reg.loc[MODEL_NAME[key]]
            r.update(model_x=f.multiplier, model_t=f.t, model_x_ex=f.multiplier_ex_LJ004, model_t_ex=f.t_ex_LJ004)
        rows.append(r)
    t = pd.DataFrame(rows)

    def verdict(r):
        checks = [r.roas_with > r.roas_without, r.median_with > r.median_without,
                  r.roas_with_ex_top > r.roas_without_ex_top]
        has_model = not pd.isna(r.get("model_t_ex", np.nan))
        if has_model:
            checks.append(r.model_x_ex > 1 and r.model_t_ex > 1.9)
            neg_model = r.model_x_ex < 1 and r.model_t_ex < -1.6
        up, down = sum(checks), 0
        down = sum([r.roas_with < r.roas_without, r.median_with < r.median_without,
                    r.roas_with_ex_top < r.roas_without_ex_top] + ([neg_model] if has_model else []))
        if r.n_with < 8:
            base = "Promising, few ads" if up >= 3 else ("Weak, few ads" if down >= 3 else "Unclear, few ads")
            return base
        if has_model and abs(r.model_t_ex) < 1 and down >= 3:
            return "Looks worse, but explained by other factors"
        if up == len(checks):
            return "Strong" if has_model else "Moderate (not model-checked)"
        if up >= 3:
            return "Moderate"
        if down >= 3:
            return "Works against"
        if has_model and abs(r.model_t_ex) < 1:
            return "No real effect"
        return "Mixed"
    t["verdict"] = t.apply(verdict, axis=1)
    return t


def audit(a_all: pd.DataFrame) -> dict:
    a = a_all
    out = {}
    out["total_spend"] = float(a.spend_inr.sum()); out["total_revenue"] = float(a.revenue_inr.sum())
    out["blended_roas"] = out["total_revenue"] / out["total_spend"]
    out["median_ad_roas"] = float(a.roas.median())
    out["median_cpa"] = float(a.cpa.median())
    top = a.loc[a.revenue_inr.idxmax()]
    out["top_ad"] = dict(ad_id=top.ad_id, revenue=float(top.revenue_inr), spend=float(top.spend_inr),
                         share_of_revenue=float(top.revenue_inr / a.revenue_inr.sum()), roas=float(top.roas),
                         video=top.video_url)
    ex = a[a.ad_id != top.ad_id]
    out["blended_roas_ex_top"] = float(ex.revenue_inr.sum() / ex.spend_inr.sum())
    s = a[a.ad_id == "LJ-089"].iloc[0]
    others = a[a.ad_id != "LJ-089"]
    out["tracking_suspect"] = dict(ad_id="LJ-089", spend=float(s.spend_inr), clicks=int(s.link_clicks),
                                   carts=int(s.add_to_carts), purchases=int(s.purchases),
                                   others_cart_to_buy_min=float(others[others.add_to_carts >= 100].cart_to_buy.min()),
                                   others_with_100_carts=int((others.add_to_carts >= 100).sum()),
                                   others_cart_to_buy_median=float(others.cart_to_buy.median()))
    pairs = []
    for k, g in a.groupby("creative_key"):
        if len(g) > 1:
            pairs.append(dict(video=k, ads=list(g.ad_id), roas=[round(float(x), 2) for x in g.roas],
                              spend=[int(x) for x in g.spend_inr]))
    out["duplicate_creatives"] = pairs
    out["days_live_off_by_one"] = int(((pd.to_datetime(a.stopped_date) - pd.to_datetime(a.launch_date)).dt.days != a.days_live).sum())
    out["still_live"] = int(a.stopped_date.isna().sum())
    out["missing_labels"] = a.loc[a.ad_format.isna(), "ad_id"].tolist()
    out["product_relabelled"] = a.loc[(a["product"] == "Proteinmix") & (a.product_form == "milk_mix_powder"), "ad_id"].tolist()
    out["product_counts"] = a["product"].value_counts().to_dict()
    out["doctor_ads"] = int((a.creator_type == "medical_professional").sum())
    out["languages_in_ads"] = a.language.value_counts().to_dict()
    # Near-identical scripts, different opening line
    out["opener_test"] = [dict(ad_id=r.ad_id, hook=r.hook_line, roas=round(float(r.roas), 2), spend=int(r.spend_inr))
                          for r in a[a.ad_id.isin(["LJ-050", "LJ-081"])].itertuples()]
    by_lang = a[~a.tracking_suspect].groupby("language").apply(
        lambda g: pd.Series(dict(n=len(g), roas=_pool(g), median=g.roas.median())), include_groups=False)
    out["by_language"] = by_lang.round(3).reset_index().to_dict("records")
    by_prod = a[~a.tracking_suspect].groupby("product").apply(
        lambda g: pd.Series(dict(n=len(g), roas=_pool(g), median=g.roas.median(),
                                 roas_child=_pool(g[g.creator_type == "child_presenter"]),
                                 n_child=int((g.creator_type == "child_presenter").sum()))), include_groups=False)
    out["by_product"] = by_prod.round(3).reset_index().to_dict("records")
    return out
