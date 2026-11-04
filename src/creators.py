"""Score the 20 creators against what Little Joys' own ads say works.

Three separate questions, kept separate on purpose so the brand can see trade-offs:
  1. FIT   - can this creator natively make the kind of ad that wins in the ad account?
  2. REACH - how many people will realistically see a *sponsored* post from them?
  3. GATES - is there a reason not to sign them right now, whatever the score?

Every number comes from creator_posts.csv / creators.csv / creator_audience.csv.
Where we overrode a Galvor label, the override and its evidence are listed in OVERRIDES.
"""
import re
import numpy as np
import pandas as pd

SNAPSHOT = pd.Timestamp("2026-10-29")       # creator_audience as_of date
RECENT_FROM = SNAPSHOT - pd.Timedelta(days=180)
COMPETITOR_WINDOW_DAYS = 90

# Kids' nutrition / health-food brands that compete with Nutrimix, Proteinmix or Gummies.
COMPETITORS = {
    "gritzo": "Gritzo (kids' milk mix)",
    "complan": "Complan (kids' health drink)",
    "bournvita": "Bournvita (kids' health drink)",
    "troovy": "Troovy (kids' nutrition foods)",
    "good monk": "Good Monk (protein powder for families)",
    "manna": "Manna (health mix)",
    "pediasure": "PediaSure", "horlicks": "Horlicks",
}

# ---------- label overrides, each checked by reading the transcript/caption ----------
OVERRIDES = [
    dict(handle="*", field="language (post label)",
         problem="Post `language` label mostly reflects the caption, not what is spoken. "
                 "e.g. drgarima_mehta: 20/20 posts labelled English, but every transcript is spoken Hindi/Hinglish.",
         fix="Spoken language re-derived from transcripts (script + word markers), see spoken_language()."),
    dict(handle="raja_choudhary04", field="presenter_age",
         problem="Labelled adult (25-34), but transcripts are first-person child narration "
                 "('Hello everyone, mera naam hai Raja aur main daily mini vlogs banata hoon').",
         fix="Counted as child-presented. (Does not change the outcome: he is gated on competitor posts.)"),
    dict(handle="ads LJ-004", field="product_form",
         problem="Labelled milk_mix_powder; transcript is Little Joys Proteinmix mixed into roti dough.",
         fix="Product re-derived from transcript/copy keywords for all ads (load._product)."),
]
CHILD_PRESENTER_OVERRIDE = {"raja_choudhary04": 0.75}   # share of his videos narrated as the child

HINDI_MARKERS = r"\b(hai|hain|mein|main|mujhe|nahi|kya|aur|toh|bhi|ko|ki|ke|hoon|kar|aap|yeh|ye|tha|thi|bahut|kuch|apne|hum)\b"
TELUGU_MARKERS = r"\b(undi|nenu|enduku|cheppu|kada|ledu|chesta|chestu|amma|nanna|ippudu|inka|em|meeru|ela|ante|untadi|cheyandi|chala)\b"
GUJ_MARKERS = r"\b(che|chhe|shu|tame|maro|mara|thai|gayu|apde|etle|pachi|nathi|hoy|karti|vadharva)\b"
ENGLISH_MARKERS = r"\b(the|and|is|are|you|this|that|with|for|my|it|so|but|what|of|to)\b"


def spoken_language(t: str) -> str:
    if not isinstance(t, str) or len(t) < 20:
        return "unknown"
    t = t.split("(")[0]  # drop the English translation appended to some lyric transcripts
    if re.search(r"[ఀ-౿]", t):
        return "Telugu"
    if re.search(r"[઀-૿]", t):
        return "Gujarati"
    if re.search(r"[ऀ-ॿ]", t):
        return "Hindi"
    low = t.lower()
    n = max(len(low.split()), 1)
    hi = len(re.findall(HINDI_MARKERS, low)) / n
    te = len(re.findall(TELUGU_MARKERS, low)) / n
    gu = len(re.findall(GUJ_MARKERS, low)) / n
    en = len(re.findall(ENGLISH_MARKERS, low)) / n
    if te > 0.04 and te >= hi:
        return "Telugu"
    if gu > 0.04 and gu >= hi:
        return "Gujarati"
    if hi > 0.06:
        # Romanised Hindi speech is how the ad account's "Hinglish" ads are transcribed
        # (0 of 25 Hinglish ads use Devanagari; 7 of 10 "Hindi" ads do), so we match that convention.
        return "Hinglish"
    return "English"


def competitor_hits(p: pd.DataFrame) -> pd.DataFrame:
    txt = (p.caption.fillna("") + " " + p.brands_visible.fillna("") + " " + p.transcript.fillna("")).str.lower()
    rows = []
    for key, name in COMPETITORS.items():
        m = txt.str.contains(r"\b" + re.escape(key) + r"\b", regex=True) & (p.is_sponsored == "yes")
        for _, r in p[m].iterrows():
            rows.append(dict(handle=r.handle, brand=name, posted_on=r.posted_on, plays=r.plays, post_url=r.post_url))
    return pd.DataFrame(rows)


def build(c: pd.DataFrame, p: pd.DataFrame, au: pd.DataFrame) -> pd.DataFrame:
    p = p.copy()
    p["posted_on"] = pd.to_datetime(p.posted_on)
    p["spoken"] = p.transcript.map(spoken_language)
    kids = p.child_ages.fillna("")
    p["kid_3_12"] = (p.children_on_camera == "yes") & kids.str.contains("3-7|8-12")
    p["kid_8_12"] = (p.children_on_camera == "yes") & kids.str.contains("8-12")
    p["child_presents"] = p.presenter_age.isin(["3-7", "8-12"])
    food_rx = r"\b(?:food|recipe|milk|doodh|nutrition|protein|tiffin|lunchbox|breakfast|dinner|meal|snack|roti|paratha|dal|sabzi|khana|picky|fussy|healthy)\b"
    p["food_or_routine"] = (p.caption.fillna("") + " " + p.topic.fillna("") + " " + p.transcript.fillna("")).str.lower().str.contains(food_rx) \
        | p.topic.fillna("").str.lower().str.contains("routine|meal|recipe|food")

    vids = p[p.type == "video"]
    recent = vids[vids.posted_on >= RECENT_FROM]
    rows = []
    for _, cr in c.iterrows():
        h = cr.handle
        g, gv, gr = p[p.handle == h], vids[vids.handle == h], recent[recent.handle == h]
        if len(gr) < 5:          # too few recent videos: fall back to all videos
            gr = gv
        org = gr[gr.is_sponsored == "no"].plays.median()
        spo = gr[gr.is_sponsored == "yes"].plays.median()
        n_spo = (gr.is_sponsored == "yes").sum()
        lang = g.spoken[g.spoken != "unknown"]
        child_pres = CHILD_PRESENTER_OVERRIDE.get(h, g.child_presents.mean())
        rows.append(dict(
            creator_id=cr.creator_id, handle=h, name=cr["name"], followers=cr.followers,
            persona=cr.persona,
            n_posts=len(g), n_recent_videos=len(gr),
            median_plays_recent=gr.plays.median(),
            median_plays_organic=org, median_plays_sponsored=spo, n_sponsored_recent=n_spo,
            sponsored_share=(g.is_sponsored == "yes").mean(),
            share_rate=(gr.reshares / gr.plays).median(),
            comment_rate=(gr.comments / gr.plays).median(),
            like_rate=(gr.likes / gr.plays).median(),
            hidden_likes_share=(g.likes <= 5).mean(),
            child_presents=child_pres,
            kid_3_12=g.kid_3_12.mean(), kid_8_12=g.kid_8_12.mean(),
            food_or_routine=g.food_or_routine.mean(),
            transcripts=len(lang),
            eng_hinglish=(lang.isin(["English", "Hinglish"]).mean() if len(lang) else np.nan),
            main_language=(lang.value_counts().idxmax() if len(lang) else "unknown"),
            languages=", ".join(f"{k} {v}" for k, v in lang.value_counts().items()),
            child_ages_seen=", ".join(f"{k} ({v})" for k, v in g.child_ages.dropna().str.split("; ").explode().value_counts().items()),
        ))
    s = pd.DataFrame(rows)

    # Sponsored-post reach: what a paid post from them actually gets.
    # If they have >=2 recent sponsored videos use those; otherwise organic x pool-wide median retention.
    s["sponsored_retention"] = s.median_plays_sponsored / s.median_plays_organic
    pool_ret = s.loc[s.n_sponsored_recent >= 2, "sponsored_retention"].median()
    s["expected_sponsored_plays"] = np.where(
        s.n_sponsored_recent >= 2, s.median_plays_sponsored,
        s.median_plays_organic.fillna(s.median_plays_recent) * pool_ret)
    s.attrs["pool_retention"] = pool_ret

    # ---------------- FIT (0-100) ----------------
    # Weights follow the strength of evidence in the ad account (analysis.py):
    #   child presents the ad      -> strongest, survives controls & outlier removal (x1.6)   40 pts
    #   English / Hinglish spoken  -> survives controls (x1.3)                                20 pts
    #   kids aged 3-12 on camera   -> product age + ads with 6-12 kids beat under-6 & no-child  20 pts
    #   food / meal / routine feed -> winning narratives are recipe, routine, taste, protein  20 pts
    s["fit_child_presenter"] = 40 * s.child_presents.clip(0, 0.6) / 0.6
    s["fit_language"] = 20 * s.eng_hinglish.fillna(0.5)
    s["fit_kids_in_range"] = 20 * s.kid_3_12.clip(0, 0.8) / 0.8
    s["fit_food_routine"] = 20 * s.food_or_routine.clip(0, 0.6) / 0.6
    s["fit"] = s[["fit_child_presenter", "fit_language", "fit_kids_in_range", "fit_food_routine"]].sum(1)

    # ---------------- REACH (0-100), log scale 10k -> 0, 3M -> 100 ----------------
    s["reach"] = (100 * (np.log10(s.expected_sponsored_plays.clip(1e4, 3e6)) - 4) / (np.log10(3e6) - 4)).round(1)

    # ---------------- GATES ----------------
    comp = competitor_hits(p)
    comp["posted_on"] = pd.to_datetime(comp.posted_on)
    comp["days_before_snapshot"] = (SNAPSHOT - comp.posted_on).dt.days
    auidx = au.set_index("handle")
    gates, notes = {}, {}
    for _, r in s.iterrows():
        h, g_, n_ = r.handle, [], []
        cc = comp[(comp.handle == h) & (comp.days_before_snapshot <= COMPETITOR_WINDOW_DAYS)]
        if len(cc):
            g_.append("Promoted a competitor in the last 90 days: " + "; ".join(
                f"{b} ({d:%d %b %Y})" for b, d in cc.groupby("brand").posted_on.max().items()))
        old = comp[(comp.handle == h) & (comp.days_before_snapshot > COMPETITOR_WINDOW_DAYS)]
        if len(old):
            n_.append("Older competitor post: " + "; ".join(sorted(set(old.brand))))
        if r.kid_3_12 < 0.15 and r.food_or_routine < 0.5:
            g_.append(f"Children on camera are mostly outside the 3-12 product range (seen: {r.child_ages_seen or 'none'})")
        if r.sponsored_share >= 0.9 and r.share_rate < 0.0005:
            g_.append(f"{r.sponsored_share:.0%} of posts are paid and almost nobody shares them "
                      f"(median {r.share_rate*1e4:.1f} shares per 10k plays) - audience looks ad-fatigued")
        if h in auidx.index:
            a_ = auidx.loc[h]
            countries = dict(x.rsplit(" ", 1) for x in str(a_.top_countries).split("; "))
            india = float(countries.get("India", "0%").rstrip("%"))
            if india < 75:
                g_.append(f"Only {india:.0f}% of audience in India ({a_.platform}); "
                          f"{a_.top_countries}")
            if a_.men_pct >= 60:
                n_.append(f"Audience is {a_.men_pct:.0f}% men ({a_.platform}, as of {a_.as_of})")
            if isinstance(a_.brands_in_past_year, str) and "little joys" in a_.brands_in_past_year.lower():
                n_.append("Already worked with Little Joys in the past year")
        if r.sponsored_retention < 0.2 and r.n_sponsored_recent >= 2:
            g_.append(f"Sponsored posts get {r.sponsored_retention:.0%} of their usual plays")
        gates[h], notes[h] = g_, n_
    s["gates"] = s.handle.map(gates)
    s["notes"] = s.handle.map(notes)
    s["eligible"] = s.gates.map(len) == 0
    s.attrs["competitor_posts"] = comp
    return s


def rank(s: pd.DataFrame, w_fit=0.7) -> pd.DataFrame:
    s = s.copy()
    s["score"] = (w_fit * s.fit + (1 - w_fit) * s.reach).round(1)
    return s.sort_values(["eligible", "score"], ascending=[False, False]).reset_index(drop=True)
