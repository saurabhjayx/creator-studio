#!/usr/bin/env python3
"""Post performance stats for creator-studio (creator-analyze). Stdlib only (py3.9+).

Usage:
  post_stats.py <export.csv> [--followers N] [--metric score|er|views] [--top 5] [--json]
  post_stats.py --selftest

Input: a CSV export of posts from Instagram / TikTok / YouTube / LinkedIn / X.
Column names are matched flexibly (case/space/punctuation-insensitive), e.g.
  date|posted_at|publish_time   views|impressions|plays|reach   likes|reactions
  comments   shares|reposts   saves|bookmarks   avg_view_duration|watch_time
  duration|length   caption|title|text   format|type   url|link
Numbers like "1,204", "3.4K", "1.2M", "12%" and durations like "1:05" are parsed.

Computes per-post engagement rate (by views, and by followers if --followers), a
weighted engagement score (saves*3 + shares*4 + comments*2 + likes), median/IQR
baselines, outliers (|z| >= 1.5 or > 2x / < 0.5x median), and breakdowns by weekday,
hour, format, caption length, hook type, hashtag count and first-half vs second-half.
Grouped results are correlations, not causes: small n (< 3) is flagged "low-n".
"""
import argparse
import csv
import datetime as dt
import io
import json
import math
import re
import statistics as st
import sys

ALIASES = {
    "date": ["date", "posted_at", "postedat", "publish_time", "publishtime", "published", "publish_date",
             "publishdate", "created_at", "createdat", "posted", "post_date", "postdate", "timestamp", "time",
             "date_posted", "dateposted", "video_publish_time", "content_publish_time"],
    "views": ["views", "impressions", "plays", "reach", "video_views", "videoviews", "view_count", "viewcount",
              "total_views", "accounts_reached"],
    "likes": ["likes", "reactions", "like_count", "likecount", "hearts", "favorites", "favourites"],
    "comments": ["comments", "comment_count", "commentcount", "replies"],
    "shares": ["shares", "reposts", "retweets", "share_count", "sharecount", "sends"],
    "saves": ["saves", "bookmarks", "saved", "save_count", "savecount", "favourites_saved"],
    "avg_watch": ["avg_view_duration", "average_view_duration", "avgviewduration", "watch_time", "watchtime",
                  "avg_watch_time", "average_watch_time", "avg_watch_time_s"],
    "duration": ["duration", "length", "video_length", "videolength", "video_duration", "duration_s"],
    "caption": ["caption", "title", "text", "description", "post_text", "content", "tweet", "commentary"],
    "format": ["format", "type", "media_type", "mediatype", "post_type", "posttype", "content_type"],
    "url": ["url", "link", "permalink", "post_url", "posturl", "post_link"],
}
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HOOK_WORDS = {
    "number": re.compile(r"^\W*\d|\b\d+\s+(ways|tips|things|mistakes|reasons|steps|lessons|habits|tools|ideas|"
                         r"rules|hacks|signs|books|apps|recipes|minutes?|days?|seconds?)\b", re.I),
    "how-to": re.compile(r"\b(how to|how i|here'?s how|step[- ]by[- ]step|tutorial|guide to|the way to)\b", re.I),
    "contrarian": re.compile(r"\b(stop|don'?t|never|nobody|no one|wrong|mistakes?|myths?|unpopular|overrated|"
                             r"quit|worst|lies?|lied|hate|ruin|not|isn'?t|aren'?t|can'?t|won'?t|avoid)\b", re.I),
    "story": re.compile(r"^\W*(i|i'm|i've|i'd|my|me|we|our|when i|last (year|week|month)|yesterday|"
                        r"(\d+ )?(years?|months?) ago)\b", re.I),
}
# wh-openers count even without "?"; yes/no openers ("Do this...") need the "?" to count
QUESTION_START = re.compile(r"^\W*(why|what|who|which|ever wonder|have you ever|has anyone)\b", re.I)


def norm(s):
    return re.sub(r"[^a-z0-9]+", "_", (s or "").strip().lower()).strip("_")


def map_columns(header):
    """canonical field -> original header name (first match wins)."""
    normed = {norm(h): h for h in header}
    out = {}
    for field, names in ALIASES.items():
        for n in names:
            if norm(n) in normed:
                out[field] = normed[norm(n)]
                break
    return out


def num(v):
    if v is None:
        return None
    s = str(v).strip().replace(",", "").replace("%", "")
    if not s or s.lower() in ("-", "n/a", "na", "none", "null", "--"):
        return None
    if ":" in s:  # duration "m:ss" or "h:mm:ss" -> seconds
        try:
            parts = [float(p) for p in s.split(":")]
        except ValueError:
            return None
        return sum(p * 60 ** i for i, p in enumerate(reversed(parts)))
    mult = {"k": 1e3, "m": 1e6, "b": 1e9}.get(s[-1].lower())
    if mult:
        s = s[:-1]
    try:
        return float(s) * (mult or 1)
    except ValueError:
        return None


DATE_FORMATS = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%m/%d/%Y %H:%M", "%m/%d/%Y %I:%M %p",
                "%m/%d/%Y", "%d/%m/%Y %H:%M", "%b %d, %Y %I:%M %p", "%b %d, %Y", "%d %b %Y", "%Y/%m/%d %H:%M"]


def parse_date(v):
    """-> (datetime or None, has_time)."""
    s = (v or "").strip()
    if not s:
        return None, False
    try:  # ISO 8601 incl. "T" and "Z"
        d = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d.replace(tzinfo=None), ("T" in s or " " in s)
    except ValueError:
        pass
    for f in DATE_FORMATS:
        try:
            return dt.datetime.strptime(s, f), ("%H" in f or "%I" in f)
        except ValueError:
            continue
    return None, False


def hook_type(caption):
    line = next((ln.strip() for ln in (caption or "").splitlines() if ln.strip()), "")
    if not line:
        return "none"
    # judge the opening sentence only, so a trailing CTA question does not count
    first = re.split(r"(?<=[.!?])\s", line, maxsplit=1)[0]
    if first.rstrip().endswith("?") or QUESTION_START.match(first):
        return "question"
    for name in ("number", "how-to", "contrarian", "story"):
        if HOOK_WORDS[name].search(first):
            return name
    return "other"


def length_bucket(n):
    return "0-50" if n <= 50 else "51-150" if n <= 150 else "151-300" if n <= 300 else "301+"


def hashtag_bucket(n):
    return "0" if n == 0 else "1-3" if n <= 3 else "4-10" if n <= 10 else "11+"


def load(text, followers=None):
    rows = list(csv.DictReader(io.StringIO(text.lstrip("﻿"))))
    if not rows:
        raise ValueError("CSV has no data rows")
    cols = map_columns(rows[0].keys())
    if not any(k in cols for k in ("views", "likes", "comments", "shares", "saves")):
        raise ValueError("no metric columns recognised; headers were: %s" % list(rows[0].keys()))
    posts = []
    for i, r in enumerate(rows, 1):
        g = lambda f: r.get(cols[f]) if f in cols else None  # noqa: E731
        d, has_time = parse_date(g("date"))
        m = {f: num(g(f)) for f in ("views", "likes", "comments", "shares", "saves", "avg_watch", "duration")}
        likes, comments, shares, saves = (m[f] or 0 for f in ("likes", "comments", "shares", "saves"))
        cap = (g("caption") or "").strip()
        eng = likes + comments + shares + saves
        p = {
            "row": i, "date": d.isoformat(sep=" ") if d else None, "_dt": d, "_has_time": has_time,
            "format": (g("format") or "unknown").strip().lower() or "unknown",
            "caption": cap, "url": (g("url") or "").strip() or None,
            "views": m["views"], "likes": likes, "comments": comments, "shares": shares, "saves": saves,
            "engagements": eng,
            "score": saves * 3 + shares * 4 + comments * 2 + likes,
            "er_views": (eng / m["views"]) if m["views"] else None,
            "er_followers": (eng / followers) if followers else None,
            "retention": (m["avg_watch"] / m["duration"]) if m["avg_watch"] and m["duration"] else None,
            "hook": hook_type(cap),
            "caption_len": len(cap),
            "hashtags": len(re.findall(r"#\w+", cap)),
        }
        p["score_per_1k"] = (p["score"] / m["views"] * 1000) if m["views"] else None
        posts.append(p)
    return posts, cols


def metric_of(p, metric):
    return {"score": p["score"], "er": p["er_views"], "views": p["views"]}[metric]


def summary(vals):
    vals = sorted(v for v in vals if v is not None)
    if not vals:
        return None
    q = st.quantiles(vals, n=4) if len(vals) >= 2 else [vals[0]] * 3
    return {"n": len(vals), "median": st.median(vals), "mean": st.mean(vals), "q1": q[0], "q3": q[2],
            "iqr": q[2] - q[0], "min": vals[0], "max": vals[-1]}


def group(posts, key, metric, overall_median, order=None):
    buckets = {}
    for p in posts:
        k = key(p)
        if k is not None:
            buckets.setdefault(k, []).append(p)
    out = []
    for k, ps in buckets.items():
        mv = [metric_of(p, metric) for p in ps if metric_of(p, metric) is not None]
        if not mv:
            continue
        med = st.median(mv)
        ers = [p["er_views"] for p in ps if p["er_views"] is not None]
        out.append({"group": k, "n": len(ps), "median": med,
                    "median_er": st.median(ers) if ers else None,
                    "lift_pct": ((med / overall_median - 1) * 100) if overall_median else None,
                    "low_n": len(ps) < 3})
    if order:
        out.sort(key=lambda g: order.index(g["group"]) if g["group"] in order else 99)
    else:
        out.sort(key=lambda g: -g["median"])
    return out


def analyze(posts, metric="score", top=5, followers=None):
    if metric != "score" and all(metric_of(p, metric) is None for p in posts):
        metric = "score"  # no views column -> fall back to weighted score
    scored = [p for p in posts if metric_of(p, metric) is not None]
    vals = [metric_of(p, metric) for p in scored]
    med = st.median(vals)
    mean = st.mean(vals)
    sd = st.pstdev(vals) or 1.0
    for p in scored:
        p["z"] = (metric_of(p, metric) - mean) / sd
        p["x_median"] = metric_of(p, metric) / med if med else None
    ranked = sorted(scored, key=lambda p: -metric_of(p, metric))
    outliers_hi = [p for p in ranked if p["z"] >= 1.5 or (p["x_median"] or 0) > 2]
    outliers_lo = [p for p in ranked if p["z"] <= -1.5 or (p["x_median"] is not None and p["x_median"] < 0.5)]

    dated = sorted([p for p in scored if p["_dt"]], key=lambda p: p["_dt"])
    trend = None
    if len(dated) >= 4:
        h = len(dated) // 2
        a, b = [metric_of(p, metric) for p in dated[:h]], [metric_of(p, metric) for p in dated[h:]]
        ma, mb = st.median(a), st.median(b)
        trend = {"first_half": {"from": dated[0]["date"], "to": dated[h - 1]["date"], "n": len(a), "median": ma},
                 "second_half": {"from": dated[h]["date"], "to": dated[-1]["date"], "n": len(b), "median": mb},
                 "change_pct": ((mb / ma - 1) * 100) if ma else None}

    timed = [p for p in scored if p["_dt"] and p["_has_time"]]
    days = sorted({p["_dt"].date() for p in dated})
    span_days = (days[-1] - days[0]).days if len(days) > 1 else 0
    return {
        "metric": metric,
        "metric_label": {"score": "weighted score (saves*3+shares*4+comments*2+likes)",
                         "er": "engagement rate by views", "views": "views"}[metric],
        "posts": len(posts), "followers": followers,
        "date_range": [dated[0]["date"], dated[-1]["date"]] if dated else None,
        "posts_per_week": round(len(dated) / (span_days / 7), 2) if span_days else None,
        "baselines": {k: summary([p[k] for p in posts]) for k in
                      ("views", "likes", "comments", "shares", "saves", "score", "er_views", "er_followers",
                       "score_per_1k", "retention")},
        "top": ranked[:top], "bottom": ranked[-top:][::-1] if len(ranked) > top else [],
        "outliers_high": outliers_hi, "outliers_low": outliers_lo,
        "by_weekday": group(scored, lambda p: WEEKDAYS[p["_dt"].weekday()] if p["_dt"] else None, metric, med,
                            WEEKDAYS),
        "by_hour": group(timed, lambda p: "%02d:00" % p["_dt"].hour, metric, med,
                         ["%02d:00" % h for h in range(24)]),
        "by_format": group(scored, lambda p: p["format"], metric, med),
        "by_caption_length": group(scored, lambda p: length_bucket(p["caption_len"]), metric, med,
                                   ["0-50", "51-150", "151-300", "301+"]),
        "by_hook": group(scored, lambda p: p["hook"], metric, med),
        "by_hashtags": group(scored, lambda p: hashtag_bucket(p["hashtags"]), metric, med, ["0", "1-3", "4-10", "11+"]),
        "trend": trend,
        "notes": ["timing table empty: dates have no time-of-day"] if dated and not timed else [],
    }


# ---------- rendering ----------

def fmt(v, kind="n"):
    if v is None:
        return "-"
    if kind == "pct":
        return "%.2f%%" % (v * 100)
    if kind == "lift":
        return "%+.0f%%" % v
    if kind == "x":
        return "%.2fx" % v
    if abs(v) >= 1e6:
        return "%.2fM" % (v / 1e6)
    if abs(v) >= 1e4:
        return "%.1fK" % (v / 1e3)
    return ("%.0f" % v) if abs(v) >= 100 or float(v).is_integer() else "%.2f" % v


def table(headers, rows):
    w = [max(len(str(h)), *(len(str(r[i])) for r in rows)) if rows else len(str(h)) for i, h in enumerate(headers)]
    line = lambda cells: "| " + " | ".join(str(c).ljust(w[i]) for i, c in enumerate(cells)) + " |"  # noqa: E731
    return "\n".join([line(headers), "|" + "|".join("-" * (x + 2) for x in w) + "|"] + [line(r) for r in rows])


def short(s, n=60):
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def render(r):
    mk = "pct" if r["metric"] == "er" else "n"
    out = ["# Post performance report", "",
           "Posts: %d | Range: %s | Cadence: %s posts/week | Ranking metric: %s" % (
               r["posts"], " to ".join(r["date_range"]) if r["date_range"] else "-",
               r["posts_per_week"] if r["posts_per_week"] is not None else "-", r["metric_label"]), ""]
    out += ["## Baselines (median, IQR)", ""]
    rows = []
    for k, label, kind in [("views", "Views", "n"), ("likes", "Likes", "n"), ("comments", "Comments", "n"),
                           ("shares", "Shares", "n"), ("saves", "Saves", "n"), ("score", "Weighted score", "n"),
                           ("score_per_1k", "Score per 1K views", "n"), ("er_views", "ER by views", "pct"),
                           ("er_followers", "ER by followers", "pct"), ("retention", "Avg % watched", "pct")]:
        s = r["baselines"][k]
        if s:
            rows.append([label, fmt(s["median"], kind), "%s - %s" % (fmt(s["q1"], kind), fmt(s["q3"], kind)),
                         fmt(s["min"], kind), fmt(s["max"], kind), s["n"]])
    out += [table(["Metric", "Median", "IQR (Q1-Q3)", "Min", "Max", "n"], rows), ""]

    def post_rows(ps):
        return [[p["row"], (p["date"] or "-")[:16], p["format"], p["hook"], fmt(p["views"]), fmt(p["score"]),
                 fmt(p["er_views"], "pct"), fmt(p.get("x_median"), "x"), "%+.1f" % p["z"], short(p["caption"], 50)]
                for p in ps]
    hdr = ["Row", "Date", "Format", "Hook", "Views", "Score", "ER", "vs med", "z", "Caption"]
    out += ["## Top posts", "", table(hdr, post_rows(r["top"])), ""]
    if r["bottom"]:
        out += ["## Bottom posts", "", table(hdr, post_rows(r["bottom"])), ""]
    out += ["## Outliers", "",
            "High (z >= 1.5 or > 2x median): rows %s" % (", ".join(str(p["row"]) for p in r["outliers_high"]) or "none"),
            "Low (z <= -1.5 or < 0.5x median): rows %s" % (", ".join(str(p["row"]) for p in r["outliers_low"]) or "none"),
            ""]
    for key, title in [("by_format", "By format"), ("by_hook", "By hook type (first sentence of caption)"),
                       ("by_weekday", "By weekday"), ("by_hour", "By hour posted"),
                       ("by_caption_length", "By caption length (chars)"), ("by_hashtags", "By hashtag count")]:
        g = r[key]
        if not g:
            continue
        out += ["## " + title, "", table(["Group", "n", "Median " + r["metric"], "Median ER", "Lift vs all", ""],
                                         [[x["group"], x["n"], fmt(x["median"], mk), fmt(x["median_er"], "pct"),
                                           fmt(x["lift_pct"], "lift"), "low-n" if x["low_n"] else ""]
                                          for x in g]), ""]
    t = r["trend"]
    if t:
        out += ["## Trend (first half vs second half)", "",
                table(["Half", "From", "To", "n", "Median " + r["metric"]],
                      [["First", t["first_half"]["from"][:10], t["first_half"]["to"][:10], t["first_half"]["n"],
                        fmt(t["first_half"]["median"], mk)],
                       ["Second", t["second_half"]["from"][:10], t["second_half"]["to"][:10], t["second_half"]["n"],
                        fmt(t["second_half"]["median"], mk)]]),
                "", "Change: %s" % fmt(t["change_pct"], "lift"), ""]
    out += ["Notes: groups are correlations, not causes. low-n = fewer than 3 posts; treat as anecdote."]
    out += ["Note: " + n for n in r["notes"]]
    return "\n".join(out)


def to_json(r):
    def clean(p):
        return {k: v for k, v in p.items() if not k.startswith("_")}
    r = dict(r)
    for k in ("top", "bottom", "outliers_high", "outliers_low"):
        r[k] = [clean(p) for p in r[k]]
    return json.dumps(r, indent=2, default=str)


# ---------- self test ----------

SELFTEST_CSV = """Publish Time,Type,Title,Impressions,Reactions,Comments,Reposts,Bookmarks,Average View Duration,Length
2026-01-05 09:00,carousel,Why do your loaves collapse?,"10,000",500,50,20,200,,
2026-01-07 18:30,reel,5 tools I use daily #bread #baking,8.0K,300,20,10,50,0:12,0:30
01/09/2026 12:00,image,Stop kneading your dough.,4000,100,5,2,10,,
2026-01-12T20:00:00Z,reel,I failed 9 times before this worked,9000,250,30,15,40,15,30
2026-01-14,image,Sunday bake,1000,20,1,0,1,,
2026-01-16 07:15,carousel,How to shape a boule step by step,12000,600,80,40,400,,
"""


def selftest():
    posts, cols = load(SELFTEST_CSV, followers=5000)
    assert cols["date"] == "Publish Time" and cols["views"] == "Impressions" and cols["saves"] == "Bookmarks", cols
    assert len(posts) == 6
    p1 = posts[0]
    assert p1["views"] == 10000 and p1["engagements"] == 770
    assert p1["score"] == 200 * 3 + 20 * 4 + 50 * 2 + 500 == 1280
    assert abs(p1["er_views"] - 0.077) < 1e-9 and abs(p1["er_followers"] - 0.154) < 1e-9
    assert posts[1]["views"] == 8000 and posts[1]["retention"] == 0.4 and posts[1]["hashtags"] == 2
    assert posts[2]["_dt"] == dt.datetime(2026, 1, 9, 12, 0) and posts[4]["_has_time"] is False
    assert [p["hook"] for p in posts] == ["question", "number", "contrarian", "story", "other", "how-to"], \
        [p["hook"] for p in posts]
    assert hook_type("What nobody tells you about rent") == "question"
    assert hook_type("This changed my mornings. Want the recipe?") == "other"  # trailing CTA question ignored
    assert num("1.2M") == 1.2e6 and num("1:02:03") == 3723 and num("") is None and num("12%") == 12
    r = analyze(posts, "score", top=2, followers=5000)
    assert r["top"][0]["row"] == 6 and r["bottom"][0]["row"] == 5, ([p["row"] for p in r["top"]], r["bottom"])
    assert any(p["row"] == 5 for p in r["outliers_low"])
    assert r["baselines"]["score"]["median"] == st.median([p["score"] for p in posts])
    fmts = {g["group"]: g for g in r["by_format"]}
    assert fmts["carousel"]["n"] == 2 and fmts["image"]["low_n"] and r["by_format"][0]["group"] == "carousel"
    assert r["trend"]["first_half"]["n"] == 3 and r["trend"]["second_half"]["n"] == 3
    assert len(r["by_hour"]) == 5  # the date-only row is excluded from hour stats
    assert analyze(posts, "er")["metric"] == "er"
    render(r)
    json.loads(to_json(r))
    try:
        load("a,b\n1,2\n")
        raise AssertionError("expected ValueError for unknown columns")
    except ValueError:
        pass
    print("selftest OK")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?")
    ap.add_argument("--followers", type=int)
    ap.add_argument("--metric", choices=["score", "er", "views"], default="score",
                    help="ranking metric (default: weighted score; falls back to score if no views column)")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.csv:
        ap.error("csv path required (or --selftest)")
    try:
        with open(a.csv, encoding="utf-8-sig", newline="") as f:
            posts, cols = load(f.read(), a.followers)
    except (OSError, ValueError) as e:
        sys.exit("post_stats: %s" % e)
    r = analyze(posts, a.metric, a.top, a.followers)
    r["columns_mapped"] = cols
    print(to_json(r) if a.json else render(r))


if __name__ == "__main__":
    main()
