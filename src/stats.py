"""Group comparisons that are honest about small samples.

For each label value we report:
  n            number of ads
  spend        total spend
  roas_pooled  sum(revenue)/sum(spend)  -- what the brand actually got back
  roas_median  median per-ad ROAS        -- not dominated by one big ad
  ci_lo/ci_hi  90% bootstrap interval on pooled ROAS (resampling ads)
  roas_ex_top  pooled ROAS with the single biggest-revenue ad in the group removed
A pattern is only called a "signal" if it holds on pooled AND median AND without its top ad.
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(7)


def boot_ci(spend, rev, n_boot=4000, q=(5, 95)):
    spend, rev = np.asarray(spend, float), np.asarray(rev, float)
    n = len(spend)
    if n < 2:
        return np.nan, np.nan
    idx = RNG.integers(0, n, size=(n_boot, n))
    r = rev[idx].sum(1) / spend[idx].sum(1)
    return tuple(np.percentile(r, q))


def group_table(a: pd.DataFrame, col: str, explode=False, min_n=3) -> pd.DataFrame:
    d = a.copy()
    if explode:
        d[col] = d[col].fillna("").str.split("; ")
        d = d.explode(col)
    d[col] = d[col].fillna("(blank)")
    rows = []
    base = a.revenue_inr.sum() / a.spend_inr.sum()
    for v, g in d.groupby(col):
        lo, hi = boot_ci(g.spend_inr, g.revenue_inr)
        top = g.revenue_inr.idxmax()
        gx = g.drop(index=top)
        rows.append(dict(
            label=col, value=v, n=len(g), spend=g.spend_inr.sum(),
            roas_pooled=g.revenue_inr.sum() / g.spend_inr.sum(),
            roas_median=g.roas.median(), ci_lo=lo, ci_hi=hi,
            roas_ex_top=(gx.revenue_inr.sum() / gx.spend_inr.sum()) if len(gx) else np.nan,
            hook_rate=g.video_3s_views.sum() / g.impressions.sum(),
            ctr=g.link_clicks.sum() / g.impressions.sum(),
            cart_rate=g.add_to_carts.sum() / g.link_clicks.sum(),
            ads=", ".join(sorted(g.ad_id)),
        ))
    t = pd.DataFrame(rows)
    t["vs_account"] = t.roas_pooled / base
    t = t[t.n >= min_n].sort_values("roas_pooled", ascending=False)
    return t


def verdict(row, base_pooled, base_median):
    """Plain-English strength of a pattern."""
    up = row.roas_pooled > base_pooled and row.roas_median > base_median and row.roas_ex_top > base_pooled
    down = row.roas_pooled < base_pooled and row.roas_median < base_median and row.roas_ex_top < base_pooled
    sure = (row.ci_lo > base_pooled) or (row.ci_hi < base_pooled)
    if row.n < 5:
        return "too few ads"
    if up and sure:
        return "strong: better"
    if down and sure:
        return "strong: worse"
    if up:
        return "leaning better"
    if down:
        return "leaning worse"
    return "mixed / one ad drives it"
