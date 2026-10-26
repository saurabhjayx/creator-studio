#!/usr/bin/env python3
"""Free, keyless trend fetcher for creator-studio skills. Stdlib only (py3.9+).

Usage:
  trends.py google  [--geo US] [--limit 20]          Google Trends daily trending searches
  trends.py news    --q "ai tools" [--days 7] [--geo US]   Google News headlines for a query
  trends.py reddit  --sub fitness [--t week] [--limit 15]  Top posts in a subreddit
  trends.py hn      [--q ai] [--limit 15]               Hacker News front page / search
  trends.py wiki    [--days-ago 1] [--limit 25]          Most-viewed Wikipedia articles
  trends.py suggest --q "keto" [--deep]                  Google autocomplete (what people ask)
  trends.py youtube --channel UCxxxx [--limit 10]       Latest uploads of a YouTube channel
  trends.py niche   --q "keto" [--subs keto,loseit] [--geo US]  All niche sources in one call
  trends.py pulse   [--geo US]                          General "what's hot now" bundle

Output: JSON on stdout. Each source fails soft: {"source":..., "error":...}.
"""
import argparse
import datetime as dt
import json
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

UA = "Mozilla/5.0 (compatible; creator-studio/1.0; +https://github.com/saurabhjayx/creator-studio)"
TIMEOUT = 12
HT = "{https://trends.google.com/trending/rss}"
ATOM = "{http://www.w3.org/2005/Atom}"


def get(url, retries=2):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for i in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == retries:
                raise
            time.sleep(3 * (i + 1))  # Reddit rate-limits bursts


def soft(source, fn):
    try:
        return {"source": source, "items": fn()}
    except Exception as e:  # network / parse errors must not kill the bundle
        return {"source": source, "error": "%s: %s" % (type(e).__name__, e)}


def google(geo="US", limit=20):
    root = ET.fromstring(get("https://trends.google.com/trending/rss?geo=" + geo))
    out = []
    for it in root.iter("item"):
        out.append({
            "title": it.findtext("title"),
            "traffic": it.findtext(HT + "approx_traffic"),
            "started": it.findtext("pubDate"),
            "news": [n.findtext(HT + "news_item_title") for n in it.findall(HT + "news_item")][:2],
        })
    return out[:limit]


def news(q, days=7, geo="US", limit=15):
    qs = urllib.parse.quote("%s when:%dd" % (q, days))
    url = "https://news.google.com/rss/search?q=%s&hl=en-%s&gl=%s&ceid=%s:en" % (qs, geo, geo, geo)
    root = ET.fromstring(get(url))
    return [{"title": i.findtext("title"), "date": i.findtext("pubDate"),
             "source": i.findtext("source"), "link": i.findtext("link")}
            for i in root.iter("item")][:limit]


def reddit(sub, t="week", limit=15):
    root = ET.fromstring(get("https://www.reddit.com/r/%s/top/.rss?t=%s&limit=%d" % (sub, t, limit)))
    return [{"title": e.findtext(ATOM + "title"), "updated": e.findtext(ATOM + "updated"),
             "link": (e.find(ATOM + "link").get("href") if e.find(ATOM + "link") is not None else None)}
            for e in root.iter(ATOM + "entry")][:limit]


def hn(q=None, limit=15):
    if q:
        url = "https://hn.algolia.com/api/v1/search?tags=story&typoTolerance=false&restrictSearchableAttributes=title&numericFilters=created_at_i>%d&query=%s" % (
            int((dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)).timestamp()), urllib.parse.quote(q))
    else:
        url = "https://hn.algolia.com/api/v1/search?tags=front_page"
    hits = json.loads(get(url))["hits"]
    return [{"title": h.get("title"), "points": h.get("points"), "comments": h.get("num_comments"),
             "url": h.get("url")} for h in hits][:limit]


def wiki(days_ago=1, limit=25):
    d = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days_ago)
    url = "https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access/%s" % d.strftime("%Y/%m/%d")
    arts = json.loads(get(url))["items"][0]["articles"]
    skip = ("Main_Page", "Special:", "Wikipedia:", "Portal:", "File:", "Help:")
    return [{"title": a["article"].replace("_", " "), "views": a["views"]}
            for a in arts if not a["article"].startswith(skip)][:limit]


def suggest(q, deep=False):
    def one(term):
        url = "https://suggestqueries.google.com/complete/search?client=firefox&q=" + urllib.parse.quote(term)
        return json.loads(get(url))[1]
    seeds = [q] + ["%s %s" % (p, q) for p in ("how to", "why", "best", "is")]
    if deep:  # ponytail: alphabet soup = 26 extra requests; fine for one-off niche research
        seeds += ["%s %s" % (q, c) for c in string.ascii_lowercase]
    seen, out = set(), []
    for s in seeds:
        try:
            for x in one(s):
                if x not in seen:
                    seen.add(x)
                    out.append(x)
        except Exception:
            continue
    return out


def youtube(channel, limit=10):
    root = ET.fromstring(get("https://www.youtube.com/feeds/videos.xml?channel_id=" + channel))
    M = "{http://search.yahoo.com/mrss/}"
    out = []
    for e in root.iter(ATOM + "entry"):
        stats = e.find(".//" + M + "statistics")
        out.append({"title": e.findtext(ATOM + "title"), "published": e.findtext(ATOM + "published"),
                    "views": int(stats.get("views")) if stats is not None else None})
    return out[:limit]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=["google", "news", "reddit", "hn", "wiki", "suggest", "youtube", "niche", "pulse"])
    p.add_argument("--geo", default="US")
    p.add_argument("--q")
    p.add_argument("--sub")
    p.add_argument("--subs", default="")
    p.add_argument("--t", default="week")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--days-ago", type=int, default=1)
    p.add_argument("--channel")
    p.add_argument("--limit", type=int, default=15)
    p.add_argument("--deep", action="store_true")
    a = p.parse_args(argv)

    need = {"news": "q", "suggest": "q", "niche": "q", "reddit": "sub", "youtube": "channel"}
    if a.cmd in need and not getattr(a, need[a.cmd]):
        p.error("%s needs --%s" % (a.cmd, need[a.cmd]))

    if a.cmd == "pulse":
        res = [soft("google_trends", lambda: google(a.geo, a.limit)),
               soft("wikipedia_top", lambda: wiki(a.days_ago, a.limit)),
               soft("hacker_news", lambda: hn(None, 10)),
               soft("reddit_popular", lambda: reddit("popular", "day", a.limit))]
    elif a.cmd == "niche":
        res = [soft("google_news", lambda: news(a.q, a.days, a.geo, a.limit)),
               soft("google_suggest", lambda: suggest(a.q, a.deep)),
               soft("hacker_news", lambda: hn(a.q, 10))]
        for i, s in enumerate([x.strip() for x in a.subs.split(",") if x.strip()]):
            if i:
                time.sleep(2)  # Reddit 429s back-to-back RSS hits
            res.append(soft("reddit_r/" + s, lambda s=s: reddit(s, a.t, a.limit)))
    else:
        fn = {
            "google": lambda: google(a.geo, a.limit),
            "news": lambda: news(a.q, a.days, a.geo, a.limit),
            "reddit": lambda: reddit(a.sub, a.t, a.limit),
            "hn": lambda: hn(a.q, a.limit),
            "wiki": lambda: wiki(a.days_ago, a.limit),
            "suggest": lambda: suggest(a.q, a.deep),
            "youtube": lambda: youtube(a.channel, a.limit),
        }[a.cmd]
        res = [soft(a.cmd, fn)]

    json.dump({"fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(), "results": res},
              sys.stdout, indent=1, ensure_ascii=False)
    print()
    return 0 if any("items" in r for r in res) else 1


if __name__ == "__main__":
    sys.exit(main())
