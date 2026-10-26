# Metrics glossary

What each number means, how `post_stats.py` computes it, and where it lies.

## Column aliases (what the script recognises)

Headers are lower-cased and punctuation becomes `_` before matching, so `Publish Time`,
`publish_time` and `PUBLISH-TIME` are the same.

| Canonical | Accepted headers (first match wins) |
|-----------|-------------------------------------|
| date | date, posted_at, publish_time, published, publish_date, created_at, posted, post_date, timestamp, time, date_posted, video_publish_time |
| views | views, impressions, plays, reach, video_views, view_count, total_views, accounts_reached |
| likes | likes, reactions, like_count, hearts, favorites |
| comments | comments, comment_count, replies |
| shares | shares, reposts, retweets, share_count, sends |
| saves | saves, bookmarks, saved, save_count |
| avg_watch | avg_view_duration, average_view_duration, watch_time, avg_watch_time |
| duration | duration, length, video_length, video_duration |
| caption | caption, title, text, description, post_text, content, tweet |
| format | format, type, media_type, post_type, content_type |
| url | url, link, permalink, post_url |

Number formats parsed: `1,204`, `3.4K`, `1.2M`, `12%` (as 12), `1:05` and `1:02:03` (as seconds).
Dates: ISO 8601 (with `T`/`Z`), `YYYY-MM-DD[ HH:MM]`, `MM/DD/YYYY[ HH:MM]`, `Mon DD, YYYY`.
Ambiguous `DD/MM` vs `MM/DD` is read as US `MM/DD` first; check `columns_mapped` and dates in
`--json` output if the export is European.

**Mapping traps**
- If an export has both `impressions` and `reach`, the alias order picks `impressions`.
  Impressions count repeat views by the same person; reach counts people. ER by reach runs higher.
  Rename the column in a scratch copy if you want reach.
- YouTube "Watch time (hours)" is total hours, not per-view. Only map average view duration
  to `avg_watch`; drop total watch time from the scratch copy.
- LinkedIn "reactions" include all reaction types; X "likes" are favourites. Both map to likes.

## Per-post metrics

| Metric | Formula | Why it matters |
|--------|---------|----------------|
| Engagements | likes + comments + shares + saves | Raw interaction count |
| ER by views | engagements / views | Quality of the post per person reached. Best for comparing posts with different reach |
| ER by followers | engagements / followers | Comparable across accounts; inflated by viral non-follower reach |
| Weighted score | saves*3 + shares*4 + comments*2 + likes | Default ranking. Weights roughly follow effort-to-act and what platforms say they reward: a share brings new viewers, a save signals lasting value, a comment beats a tap |
| Score per 1K views | score / views * 1000 | Weighted quality independent of reach |
| % watched (retention) | avg view duration / duration | Video only. Hook + pacing quality. Comparable only between videos of similar length |
| z | (metric - mean) / std dev | How unusual a post is within this account |
| vs median | metric / account median | Robust "Nx normal" read; less distorted by one viral post than z |

The weights are a convention, not a platform formula. If the creator's goal is follower growth,
shares matter most; for a product/newsletter funnel, saves and comments (intent) matter more.
Say which goal the ranking serves.

## Baselines

The script reports median and IQR (Q1-Q3), not mean +- sd, because creator metrics are heavily
right-skewed: one viral post drags the mean far above a typical post. "Normal" = inside the IQR.

## Outliers

Flagged high if z >= 1.5 or > 2x median; low if z <= -1.5 or < 0.5x median. With skewed data the
median rule catches most real outliers; z catches the extreme ones. Viral spikes are worth reading
closely, but one spike is not a pattern.

## Group breakdowns

Each group shows n, median of the ranking metric, median ER, and lift vs the all-posts median.
`low-n` = fewer than 3 posts. Groups:

| Dimension | Buckets | Notes |
|-----------|---------|-------|
| Weekday | Mon-Sun | From the post timestamp as exported (usually the account's timezone; YouTube may be UTC) |
| Hour | 00:00-23:00 | Skipped when dates have no time |
| Format | as exported, lower-cased | Normalise `Carousel album` / `carousel` by hand if mixed |
| Caption length | 0-50, 51-150, 151-300, 301+ chars | Includes hashtags |
| Hook type | question, number, how-to, contrarian, story, other, none | First sentence of the first non-empty line |
| Hashtags | 0, 1-3, 4-10, 11+ | `#word` tokens in the caption |
| Trend | first half vs second half, chronological | Account-level drift: growth, algorithm change, topic shift |

### Hook classifier (heuristic)

Checked in this order; first match wins.

1. **question**: first sentence ends with `?`, or opens with why/what/who/which/ever wonder/have you ever
2. **number**: starts with a digit, or "N ways/tips/mistakes/steps/..."
3. **how-to**: "how to", "how I", "here's how", "step by step", "tutorial", "guide to"
4. **contrarian**: stop, don't, never, nobody, wrong, mistake, myth, unpopular, overrated, worst, avoid, ...
5. **story**: opens with I / my / we / "last year" / "N years ago"
6. **other**: everything else (often label-style captions: "Tuesday dinner")

It is a keyword heuristic. Spot-check the top/bottom posts' labels by eye before building a
claim on hook type, and re-label by hand if the classifier got a winner wrong.

## Platform naming cheat sheet

| Concept | Instagram | TikTok | YouTube | LinkedIn | X |
|---------|-----------|--------|---------|----------|---|
| views | Views (2024+ replaced plays/impressions as the headline metric) | Video views | Views | Impressions | Impressions |
| likes | Likes | Likes | Likes | Reactions | Likes |
| shares | Shares / Sends | Shares | Shares | Reposts | Reposts |
| saves | Saves | Favorites / Saves | (none public) | Saves (partial) | Bookmarks |
| retention | Avg watch time (Reels) | Avg watch time, Watched full video % | Avg view duration, Avg % viewed | n/a | n/a |

Platforms rename metrics often; trust the export's own definitions page over this table.

## Pitfalls checklist

- Posts < 7 days old are still growing: exclude or flag.
- Boosted/paid posts: exclude from organic analysis.
- Cross-posted content (same video on 3 platforms): analyse per platform, never pooled.
- Account growth over the window inflates later posts on follower-based ER and views; compare
  rates (ER by views) when the follower count moved a lot.
- Survivorship: deleted/archived flops are missing from exports. Ask.
