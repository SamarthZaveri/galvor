"""Cross-check: does each pattern survive when the others are held fixed?

Spend-weighted least squares on log(ROAS), one row per ad, with launch-month controls.
With ~98 ads this is a sanity check, not a forecast. We report the multiplier exp(beta)
and a rough t-value, with and without the single outlier ad LJ-004.
"""
import numpy as np
import pandas as pd


def features(d: pd.DataFrame) -> pd.DataFrame:
    t = d.transcript.fillna("").str.lower()
    X = pd.DataFrame(index=d.index)
    X["const"] = 1.0
    X["Child presents the ad"] = (d.creator_type == "child_presenter") * 1.0
    X["Skit format"] = (d.ad_format == "skit") * 1.0
    X["English or Hinglish"] = d.language.isin(["English", "Hinglish"]) * 1.0
    X["Gummies (vs other products)"] = (d["product"] == "Gummies") * 1.0
    X["Proteinmix (vs other products)"] = (d["product"] == "Proteinmix") * 1.0
    X["Brand named in first 3s"] = (d.brand_first_said == "under_3s") * 1.0
    X["Clear buy-now ask"] = (d.cta_type == "buy_now") * 1.0
    X["States protein in grams"] = (t.str.contains(r"\d+\s?(?:g|gm|grams?)\b") | t.str.contains("ग्राम|கிராம்")) * 1.0
    m = d.launch_date.str[:7]
    for mm in ["2026-08", "2026-10"]:
        X[f"_month_{mm}"] = (m == mm) * 1.0
    X["_month_early"] = m.isin(["2026-06", "2026-07"]) * 1.0
    return X


def fit(d: pd.DataFrame):
    d = d[d.purchases > 0]
    X = features(d)
    y = np.log(d.roas.values)
    w = d.spend_inr.values ** 0.5
    Xv = X.values
    beta = np.linalg.lstsq(Xv * w[:, None], y * w, rcond=None)[0]
    res = y - Xv @ beta
    n, k = Xv.shape
    s2 = (w ** 2 * res ** 2).sum() / (n - k)
    cov = np.linalg.inv(Xv.T @ (Xv * (w ** 2)[:, None])) * s2
    se = np.sqrt(np.diag(cov))
    out = pd.DataFrame({"feature": X.columns, "multiplier": np.exp(beta), "t": beta / se})
    return out[~out.feature.str.startswith(("const", "_"))].reset_index(drop=True)


def fit_both(a: pd.DataFrame) -> pd.DataFrame:
    full = fit(a)
    ex = fit(a[a.ad_id != "LJ-004"]).rename(columns={"multiplier": "multiplier_ex_LJ004", "t": "t_ex_LJ004"})
    return full.merge(ex, on="feature")
