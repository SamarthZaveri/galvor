"""Load the raw CSVs, derive metrics and a few cleaned labels.

Every derived column is documented here so the report can point back to it.
"""
from pathlib import Path
import re
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"

# Ads whose numbers we do not trust for pattern-finding (see audit.py for why).
# LJ-089: Rs 4.27 lakh spend, 29k clicks, 1,544 add-to-carts but exactly 0 purchases.
#         Every other ad converts 15-45% of carts; 0/1544 is a tracking break, not a creative result.
TRACKING_SUSPECT = {"LJ-089"}


def _product(row) -> str:
    t = " ".join(str(row[c]) for c in ["transcript", "ad_copy", "on_screen_text", "claims_made", "hook_line"]).lower()
    if "proteinmix" in t or "protein mix" in t or "plant protein" in t or "12g" in t or "12 g" in t or "12 gram" in t:
        return "Proteinmix"
    if "nutrimix" in t or "ragi" in t or "bajra" in t:
        return "Nutrimix"
    if "gumm" in t or "multivitamin" in t:
        return "Gummies"
    if any(k in t for k in ["spread", "jam", "ketchup", "peanut butter", "hazelnut"]):
        return "Spreads"
    if row["product_form"] == "milk_mix_powder":
        return "Nutrimix"
    if row["product_form"] == "gummies":
        return "Gummies"
    return "Other"


def load_ads() -> pd.DataFrame:
    a = pd.read_csv(DATA / "ads.csv")
    a["roas"] = a.revenue_inr / a.spend_inr
    a["cpa"] = a.spend_inr / a.purchases.replace(0, np.nan)
    a["hook_rate"] = a.video_3s_views / a.impressions       # thumb-stop
    a["hold_rate"] = a.thruplays / a.video_3s_views          # watched through
    a["ctr"] = a.link_clicks / a.impressions
    a["cart_rate"] = a.add_to_carts / a.link_clicks
    a["cart_to_buy"] = a.purchases / a.add_to_carts.replace(0, np.nan)
    a["product"] = a.apply(_product, axis=1)
    a["tracking_suspect"] = a.ad_id.isin(TRACKING_SUSPECT)
    a["child_tastes"] = a.child_role.fillna("").str.contains("reacts_to_taste")
    a["child_speaks"] = a.child_role.fillna("").str.contains("speaks")
    a["has_child"] = a.child_on_screen.fillna("none") != "none"
    a["creative_key"] = a.video_url.str.extract(r"(ad_\d+)\.mp4")[0]
    return a


def load_creators():
    c = pd.read_csv(DATA / "creators.csv")
    p = pd.read_csv(DATA / "creator_posts.csv")
    au = pd.read_csv(DATA / "creator_audience.csv")
    return c, p, au
